"""
Booking Service - Business logic for booking operations.
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import logging
import math

from ...models.mysql_models import (
    Booking, BookingType, BookingStatus,
    Flight, Hotel, HotelRoom, Car, User
)
from ...schemas.booking_schemas import (
    BookingCreate, BookingUpdate, BookingResponse, BookingListResponse, BookingCancellation
)
from ...common.cache import RedisCache, CacheKeys
from ...kafka.producer import event_publisher

logger = logging.getLogger(__name__)


class BookingService:
    """Service class for booking operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.cache = RedisCache()
    
    def create_booking(self, booking_data: BookingCreate) -> Booking:
        """Create a new booking with availability checking and price calculation."""
        # Validate user exists
        user = self.db.query(User).filter(User.user_id == booking_data.user_id).first()
        if not user:
            raise ValueError(f"User {booking_data.user_id} not found")
        
        if not user.is_active:
            raise ValueError(f"User {booking_data.user_id} is inactive")
        
        # Calculate price and validate availability based on booking type
        booking_info = None
        if booking_data.booking_type == BookingType.FLIGHT:
            booking_info = self._create_flight_booking(booking_data)
        elif booking_data.booking_type == BookingType.HOTEL:
            booking_info = self._create_hotel_booking(booking_data)
        elif booking_data.booking_type == BookingType.CAR:
            booking_info = self._create_car_booking(booking_data)
        else:
            raise ValueError(f"Invalid booking type: {booking_data.booking_type}")
        
        # Create booking record
        booking_id = f"BK-{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate number of nights for hotels
        num_nights = 1
        if booking_data.check_out_date and booking_data.booking_type == BookingType.HOTEL:
            delta = booking_data.check_out_date - booking_data.check_in_date
            num_nights = max(1, delta.days)
        
        booking = Booking(
            booking_id=booking_id,
            user_id=booking_data.user_id,
            booking_type=booking_data.booking_type.value,  # Store as string value
            listing_id=booking_data.listing_id,
            check_in_date=booking_data.check_in_date,
            check_out_date=booking_data.check_out_date,
            num_passengers=booking_data.num_passengers if booking_data.booking_type == BookingType.FLIGHT else 1,
            num_rooms=booking_data.num_rooms if booking_data.booking_type == BookingType.HOTEL else 1,
            num_nights=num_nights,
            status=BookingStatus.PENDING.value,  # Use .value to get string instead of enum
            total_price=booking_info["total_price"]
        )
        
        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        
        # Invalidate user bookings cache
        self.cache.delete(CacheKeys.user_bookings(booking_data.user_id))
        
        # Publish booking created event
        event_publisher.publish_booking_event("created", {
            "booking_id": booking.booking_id,
            "user_id": booking.user_id,
            "booking_type": booking.booking_type,  # Already a string from database
            "listing_id": booking.listing_id,
            "total_price": float(booking.total_price)
        })
        
        # Update user preferences based on booking (asynchronously)
        import asyncio
        from ...services.analytics_service.service import AnalyticsService
        
        try:
            analytics = AnalyticsService()
            
            # Build search params from booking for preferences
            search_params = {"listing_id": booking.listing_id}
            
            # Extract additional params based on booking type
            if booking.booking_type == BookingType.FLIGHT.value:
                flight = self.db.query(Flight).filter(Flight.flight_id == booking.listing_id.upper()).first()
                if flight:
                    search_params["departure_airport"] = flight.departure_airport
                    search_params["arrival_airport"] = flight.arrival_airport
                    search_params["airline_name"] = flight.airline_name
            elif booking.booking_type == BookingType.HOTEL.value:
                hotel = self.db.query(Hotel).filter(Hotel.hotel_id == booking.listing_id).first()
                if hotel:
                    search_params["city"] = hotel.city
                    search_params["hotel_type"] = getattr(hotel, 'hotel_type', None)
            elif booking.booking_type == BookingType.CAR.value:
                car = self.db.query(Car).filter(Car.car_id == booking.listing_id).first()
                if car:
                    search_params["car_type"] = car.car_type
            
            # Update preferences asynchronously (non-blocking)
            asyncio.create_task(analytics.update_user_preferences_from_search(
                user_id=booking.user_id,
                search_type=booking.booking_type,
                search_params=search_params,
                booking_price=float(booking.total_price)
            ))
            logger.debug(f"User preferences update queued for user {booking.user_id}")
        except Exception as e:
            logger.error(f"Failed to update user preferences: {e}")
        
        # Log booking activity to MongoDB (asynchronously)
        import asyncio
        from ...services.analytics_service.service import AnalyticsService
        
        try:
            analytics = AnalyticsService()
            asyncio.create_task(analytics.log_booking(
                user_id=booking.user_id,
                booking_id=booking.booking_id,
                booking_type=booking.booking_type,
                listing_id=booking.listing_id,
                status_from=None,
                status_to=booking.status,
                action="created",
                details={
                    "num_passengers": booking.num_passengers,
                    "num_rooms": booking.num_rooms,
                    "total_price": float(booking.total_price)
                }
            ))
            logger.debug(f"Booking log queued for booking {booking.booking_id}")
        except Exception as e:
            logger.error(f"Failed to log booking activity: {e}")
        
        logger.info(f"Created booking: {booking.booking_id} for user {booking.user_id}")
        return booking
    
    def _create_flight_booking(self, booking_data: BookingCreate) -> dict:
        """Create a flight booking with seat availability check."""
        flight = self.db.query(Flight).filter(
            Flight.flight_id == booking_data.listing_id.upper()
        ).with_for_update().first()
        
        if not flight:
            raise ValueError(f"Flight {booking_data.listing_id} not found")
        
        if not flight.is_active:
            raise ValueError(f"Flight {booking_data.listing_id} is not active")
        
        # Check seat availability
        if flight.available_seats < booking_data.num_passengers:
            raise ValueError(
                f"Insufficient seats. Available: {flight.available_seats}, "
                f"Requested: {booking_data.num_passengers}"
            )
        
        # Check date match
        flight_date = flight.departure_datetime.date()
        booking_date = booking_data.check_in_date.date()
        if flight_date != booking_date:
            raise ValueError(
                f"Flight date mismatch. Flight departs on {flight_date}, "
                f"booking requested for {booking_date}"
            )
        
        # Calculate price
        total_price = flight.base_price * booking_data.num_passengers
        
        # Reserve seats (will be committed with booking)
        flight.available_seats -= booking_data.num_passengers
        
        return {
            "total_price": total_price,
            "listing_details": {
                "flight_id": flight.flight_id,
                "airline": flight.airline_name,
                "route": f"{flight.departure_airport}-{flight.arrival_airport}",
                "departure": str(flight.departure_datetime)
            }
        }
    
    def _create_hotel_booking(self, booking_data: BookingCreate) -> dict:
        """Create a hotel booking with room availability check."""
        hotel = self.db.query(Hotel).filter(
            Hotel.hotel_id == booking_data.listing_id
        ).first()
        
        if not hotel:
            raise ValueError(f"Hotel {booking_data.listing_id} not found")
        
        if not hotel.is_active:
            raise ValueError(f"Hotel {booking_data.listing_id} is not active")
        
        # Get room type (default to first available room type if not specified)
        room_query = self.db.query(HotelRoom).filter(
            HotelRoom.hotel_id == booking_data.listing_id,
            HotelRoom.is_active == True
        )
        
        if booking_data.room_type:
            room_query = room_query.filter(HotelRoom.room_type == booking_data.room_type)
        
        room = room_query.with_for_update().first()
        
        if not room:
            raise ValueError(f"No available room type found for hotel {booking_data.listing_id}")
        
        # Check availability and date overlap
        if not booking_data.check_out_date:
            raise ValueError("Check-out date is required for hotel bookings")
        
        # Check room availability
        if room.available_rooms < booking_data.num_rooms:
            raise ValueError(
                f"Insufficient rooms. Available: {room.available_rooms}, "
                f"Requested: {booking_data.num_rooms}"
            )
        
        # Check for overlapping bookings (prevent double booking)
        overlapping = self.db.query(Booking).filter(
            and_(
                Booking.listing_id == booking_data.listing_id,
                Booking.booking_type == BookingType.HOTEL.value,
                Booking.status.in_([BookingStatus.PENDING.value, BookingStatus.CONFIRMED.value]),
                or_(
                    # Check-in during existing booking
                    and_(
                        Booking.check_in_date <= booking_data.check_in_date,
                        Booking.check_out_date > booking_data.check_in_date
                    ),
                    # Check-out during existing booking
                    and_(
                        Booking.check_in_date < booking_data.check_out_date,
                        Booking.check_out_date >= booking_data.check_out_date
                    ),
                    # Booking completely contains existing booking
                    and_(
                        Booking.check_in_date >= booking_data.check_in_date,
                        Booking.check_out_date <= booking_data.check_out_date
                    )
                )
            )
        ).count()
        
        if overlapping > 0:
            raise ValueError(
                f"Room is already booked for the selected dates. "
                f"Please choose different dates."
            )
        
        # Calculate number of nights
        delta = booking_data.check_out_date - booking_data.check_in_date
        num_nights = max(1, delta.days)
        
        # Calculate price (price_per_night * num_nights * num_rooms)
        total_price = room.price_per_night * Decimal(num_nights) * Decimal(booking_data.num_rooms)
        
        # Reserve rooms (will be committed with booking)
        room.available_rooms -= booking_data.num_rooms
        
        return {
            "total_price": total_price,
            "listing_details": {
                "hotel_id": hotel.hotel_id,
                "hotel_name": hotel.hotel_name,
                "city": hotel.city,
                "room_type": room.room_type.value if hasattr(room.room_type, 'value') else str(room.room_type),
                "num_nights": num_nights
            }
        }
    
    def _create_car_booking(self, booking_data: BookingCreate) -> dict:
        """Create a car rental booking with availability check."""
        car = self.db.query(Car).filter(
            Car.car_id == booking_data.listing_id
        ).with_for_update().first()
        
        if not car:
            raise ValueError(f"Car {booking_data.listing_id} not found")
        
        if not car.is_active:
            raise ValueError(f"Car {booking_data.listing_id} is not active")
        
        if not car.is_available:
            raise ValueError(f"Car {booking_data.listing_id} is not available")
        
        if not booking_data.check_out_date:
            raise ValueError("Return date is required for car bookings")
        
        # Check for overlapping bookings
        overlapping = self.db.query(Booking).filter(
            and_(
                Booking.listing_id == booking_data.listing_id,
                Booking.booking_type == BookingType.CAR.value,
                Booking.status.in_([BookingStatus.PENDING.value, BookingStatus.CONFIRMED.value]),
                or_(
                    and_(
                        Booking.check_in_date <= booking_data.check_in_date,
                        Booking.check_out_date > booking_data.check_in_date
                    ),
                    and_(
                        Booking.check_in_date < booking_data.check_out_date,
                        Booking.check_out_date >= booking_data.check_out_date
                    )
                )
            )
        ).count()
        
        if overlapping > 0:
            raise ValueError(
                f"Car is already booked for the selected dates. "
                f"Please choose different dates."
            )
        
        # Calculate number of days
        delta = booking_data.check_out_date - booking_data.check_in_date
        num_days = max(1, delta.days)
        
        # Calculate price (daily_rental_price * num_days)
        total_price = car.daily_rental_price * Decimal(num_days)
        
        # Mark car as unavailable (will be committed with booking)
        car.is_available = False
        
        return {
            "total_price": total_price,
            "listing_details": {
                "car_id": car.car_id,
                "make": car.make,
                "model": car.model,
                "provider": car.provider_name,
                "num_days": num_days
            }
        }
    
    def get_booking(self, booking_id: str) -> Optional[Booking]:
        """Get booking by ID."""
        return self.db.query(Booking).filter(Booking.booking_id == booking_id).first()
    
    def get_user_bookings(
        self,
        user_id: str,
        booking_type: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> BookingListResponse:
        """Get user's bookings with filtering and pagination."""
        query = self.db.query(Booking).filter(Booking.user_id == user_id)
        
        if booking_type:
            query = query.filter(Booking.booking_type == booking_type)
        
        if status:
            query = query.filter(Booking.status == status)
        
        total_count = query.count()
        
        offset = (page - 1) * page_size
        bookings = query.order_by(Booking.booking_date.desc()).offset(offset).limit(page_size).all()
        
        return BookingListResponse(
            bookings=[self._format_booking_response(b) for b in bookings],
            total_count=total_count,
            page=page,
            page_size=page_size
        )
    
    def cancel_booking(self, booking_id: str, reason: Optional[str] = None, require_admin_approval: bool = False) -> bool:
        """Cancel a booking and restore inventory.
        
        If require_admin_approval is True, sets status to 'refund_pending' instead of 'cancelled'.
        This is used when customer cancels - admin must approve before booking is fully cancelled.
        """
        booking = self.db.query(Booking).filter(
            Booking.booking_id == booking_id
        ).with_for_update().first()
        
        if not booking:
            raise ValueError(f"Booking {booking_id} not found")
        
        if booking.status == BookingStatus.CANCELLED.value:
            raise ValueError(f"Booking {booking_id} is already cancelled")
        
        if booking.status == "refund_pending":
            raise ValueError(f"Booking {booking_id} is already pending refund approval")
        
        if booking.status == BookingStatus.COMPLETED.value:
            raise ValueError(f"Cannot cancel completed booking {booking_id}")
        
        # Restore inventory
        if booking.booking_type == BookingType.FLIGHT.value:
            flight = self.db.query(Flight).filter(
                Flight.flight_id == booking.listing_id.upper()
            ).with_for_update().first()
            if flight:
                flight.available_seats += booking.num_passengers
        
        elif booking.booking_type == BookingType.HOTEL.value:
            # Find the room and restore availability
            room = self.db.query(HotelRoom).filter(
                HotelRoom.hotel_id == booking.listing_id
            ).with_for_update().first()
            if room:
                room.available_rooms += booking.num_rooms
        
        elif booking.booking_type == BookingType.CAR.value:
            car = self.db.query(Car).filter(
                Car.car_id == booking.listing_id
            ).with_for_update().first()
            if car:
                car.is_available = True
        
        # Update booking status
        # If require_admin_approval is True, set to refund_pending (customer cancellation)
        # Otherwise, set to cancelled directly (admin cancellation)
        if require_admin_approval:
            booking.status = "refund_pending"
        else:
            booking.status = BookingStatus.CANCELLED.value
        
        self.db.commit()
        
        # Invalidate cache
        self.cache.delete(CacheKeys.user_bookings(booking.user_id))
        
        # Publish cancellation event
        event_publisher.publish_booking_event("cancelled" if not require_admin_approval else "refund_pending", {
            "booking_id": booking_id,
            "user_id": booking.user_id,
            "reason": reason,
            "status": booking.status
        })
        
        logger.info(f"Booking {booking_id} set to {booking.status}")
        return True
    
    def approve_cancellation(self, booking_id: str) -> bool:
        """Approve a pending cancellation - sets booking status to cancelled."""
        booking = self.db.query(Booking).filter(
            Booking.booking_id == booking_id
        ).with_for_update().first()
        
        if not booking:
            raise ValueError(f"Booking {booking_id} not found")
        
        if booking.status != "refund_pending":
            raise ValueError(f"Booking {booking_id} is not in refund_pending status")
        
        booking.status = BookingStatus.CANCELLED.value
        self.db.commit()
        
        # Invalidate cache
        self.cache.delete(CacheKeys.user_bookings(booking.user_id))
        
        # Publish approval event
        event_publisher.publish_booking_event("cancellation_approved", {
            "booking_id": booking_id,
            "user_id": booking.user_id
        })
        
        logger.info(f"Approved cancellation for booking {booking_id}")
        return True
    
    def _format_booking_response(self, booking: Booking) -> BookingResponse:
        """Format booking with listing details and billing information."""
        listing_details = None
        
        if booking.booking_type == BookingType.FLIGHT.value:
            flight = self.db.query(Flight).filter(Flight.flight_id == booking.listing_id).first()
            if flight:
                listing_details = {
                    "flight_id": flight.flight_id,
                    "airline": flight.airline_name,
                    "route": f"{flight.departure_airport}-{flight.arrival_airport}",
                    "departure_datetime": str(flight.departure_datetime)
                }
        
        elif booking.booking_type == BookingType.HOTEL.value:
            hotel = self.db.query(Hotel).filter(Hotel.hotel_id == booking.listing_id).first()
            if hotel:
                listing_details = {
                    "hotel_id": hotel.hotel_id,
                    "hotel_name": hotel.hotel_name,
                    "city": hotel.city,
                    "address": hotel.address
                }
        
        elif booking.booking_type == BookingType.CAR.value:
            car = self.db.query(Car).filter(Car.car_id == booking.listing_id).first()
            if car:
                listing_details = {
                    "car_id": car.car_id,
                    "make": car.make,
                    "model": car.model,
                    "provider": car.provider_name
                }
        
        # Get billing information if payment was completed
        from ...models.mysql_models import Billing
        billing = self.db.query(Billing).filter(Billing.booking_id == booking.booking_id).first()
        
        subtotal = None
        tax_amount = None
        total_amount = None
        invoice_number = None
        
        if billing:
            subtotal = billing.subtotal
            tax_amount = billing.tax_amount
            total_amount = billing.total_amount
            invoice_number = billing.invoice_number
        
        return BookingResponse(
            booking_id=booking.booking_id,
            user_id=booking.user_id,
            booking_type=booking.booking_type,  # Already a string from database
            listing_id=booking.listing_id,
            check_in_date=booking.check_in_date,
            check_out_date=booking.check_out_date,
            num_passengers=booking.num_passengers,
            num_rooms=booking.num_rooms,
            num_nights=booking.num_nights,
            status=booking.status,  # Already a string from database
            total_price=booking.total_price,
            booking_date=booking.booking_date,
            created_at=booking.created_at,
            updated_at=booking.updated_at,
            listing_details=listing_details,
            subtotal=subtotal,
            tax_amount=tax_amount,
            total_amount=total_amount,
            invoice_number=invoice_number
        )
