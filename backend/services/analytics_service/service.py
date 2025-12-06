"""
Analytics Service - Store analytics data in MongoDB.
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from ...common.database import get_async_mongodb, MongoCollections
from ...models.mongodb_models import (
    UserActionLog, SearchLog, BookingLog, ClickTrackingDocument,
    UserPreferencesDocument, PriceHistoryDocument, AdminAuditLog
)

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for storing analytics data in MongoDB."""
    
    def __init__(self):
        self.db = get_async_mongodb()
    
    async def log_user_action(
        self,
        user_id: Optional[str],
        session_id: str,
        action: str,
        resource_type: Optional[str],
        resource_id: Optional[str],
        endpoint: str,
        method: str,
        ip_address: Optional[str],
        user_agent: Optional[str],
        request_params: Optional[Dict],
        response_status: int,
        response_time_ms: float
    ):
        """Log user action to MongoDB."""
        try:
            log = UserActionLog(
                log_id=f"LOG-{uuid.uuid4().hex[:8].upper()}",
                user_id=user_id,
                session_id=session_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                endpoint=endpoint,
                method=method,
                ip_address=ip_address,
                user_agent=user_agent,
                request_params=request_params or {},
                response_status=response_status,
                response_time_ms=response_time_ms,
                timestamp=datetime.utcnow()
            )
            
            await self.db[MongoCollections.USER_LOGS].insert_one(log.model_dump())
            logger.debug(f"Logged user action: {action} for user {user_id}")
        
        except Exception as e:
            logger.error(f"Error logging user action: {e}")
    
    async def log_search(
        self,
        user_id: Optional[str],
        session_id: str,
        search_type: str,
        search_params: Dict[str, Any],
        results_count: int,
        filters_applied: Optional[Dict] = None,
        clicked_results: Optional[list] = None,
        booked_result: Optional[str] = None,
        search_location: Optional[str] = None
    ):
        """Log search activity to MongoDB."""
        try:
            log = SearchLog(
                log_id=f"SEARCH-{uuid.uuid4().hex[:8].upper()}",
                user_id=user_id,
                session_id=session_id,
                search_type=search_type,
                search_params=search_params,
                results_count=results_count,
                filters_applied=filters_applied or {},
                clicked_results=clicked_results or [],
                booked_result=booked_result,
                search_location=search_location,
                timestamp=datetime.utcnow()
            )
            
            await self.db[MongoCollections.SEARCH_LOGS].insert_one(log.model_dump())
            logger.debug(f"Logged search: {search_type}")
        
        except Exception as e:
            logger.error(f"Error logging search: {e}")
    
    async def log_booking(
        self,
        user_id: str,
        booking_id: str,
        booking_type: str,
        listing_id: str,
        status_from: Optional[str],
        status_to: str,
        action: str,
        details: Optional[Dict] = None
    ):
        """Log booking activity to MongoDB."""
        try:
            log = BookingLog(
                log_id=f"BOOKING-{uuid.uuid4().hex[:8].upper()}",
                user_id=user_id,
                booking_id=booking_id,
                booking_type=booking_type,
                listing_id=listing_id,
                status_from=status_from,
                status_to=status_to,
                action=action,
                details=details or {},
                timestamp=datetime.utcnow()
            )
            
            await self.db[MongoCollections.BOOKING_LOGS].insert_one(log.model_dump())
            logger.debug(f"Logged booking action: {action} for booking {booking_id}")
        
        except Exception as e:
            logger.error(f"Error logging booking: {e}")
    
    async def log_click(
        self,
        session_id: str,
        user_id: Optional[str],
        page_url: str,
        page_name: str,
        section_name: Optional[str] = None,
        element_id: Optional[str] = None,
        element_type: Optional[str] = None,
        x_position: Optional[int] = None,
        y_position: Optional[int] = None
    ):
        """Log click tracking to MongoDB."""
        try:
            click = ClickTrackingDocument(
                tracking_id=f"CLICK-{uuid.uuid4().hex[:8].upper()}",
                session_id=session_id,
                user_id=user_id,
                page_url=page_url,
                page_name=page_name,
                section_name=section_name,
                element_id=element_id,
                element_type=element_type,
                x_position=x_position,
                y_position=y_position,
                timestamp=datetime.utcnow()
            )
            
            await self.db[MongoCollections.LOGS].insert_one(click.model_dump())
            logger.debug(f"Logged click on {page_name}")
        
        except Exception as e:
            logger.error(f"Error logging click: {e}")
    
    async def update_user_preferences_from_search(
        self,
        user_id: str,
        search_type: str,
        search_params: Dict[str, Any],
        booking_price: Optional[float] = None
    ):
        """Update user preferences based on search and booking behavior."""
        try:
            db = self.db
            collection = db[MongoCollections.USER_PREFERENCES]
            
            # Get existing preferences or create new
            existing = await collection.find_one({"user_id": user_id})
            
            if existing:
                prefs = UserPreferencesDocument(**existing)
            else:
                prefs = UserPreferencesDocument(user_id=user_id)
            
            # Update preferences based on search type
            if search_type == "flight":
                # Extract departure/arrival airports
                departure = search_params.get("departure_airport")
                arrival = search_params.get("arrival_airport")
                
                if departure and departure not in prefs.preferred_departure_airports:
                    prefs.preferred_departure_airports.append(departure)
                
                if arrival and arrival not in prefs.typical_destinations:
                    prefs.typical_destinations.append(arrival)
                
                # Update budget range
                if booking_price:
                    if not prefs.budget_range:
                        prefs.budget_range = {"flights": {"min": 0, "max": 0}}
                    
                    flight_min = prefs.budget_range.get("flights", {}).get("min", booking_price)
                    flight_max = prefs.budget_range.get("flights", {}).get("max", booking_price)
                    
                    prefs.budget_range["flights"] = {
                        "min": min(flight_min, booking_price),
                        "max": max(flight_max, booking_price)
                    }
            
            elif search_type == "hotel":
                # Update hotel preferences
                hotel_type = search_params.get("hotel_type")
                if hotel_type and hotel_type not in prefs.preferred_hotel_types:
                    prefs.preferred_hotel_types.append(hotel_type)
                
                if booking_price:
                    if not prefs.budget_range:
                        prefs.budget_range = {"hotels": {"min": 0, "max": 0}}
                    
                    hotel_min = prefs.budget_range.get("hotels", {}).get("min", booking_price)
                    hotel_max = prefs.budget_range.get("hotels", {}).get("max", booking_price)
                    
                    prefs.budget_range["hotels"] = {
                        "min": min(hotel_min, booking_price),
                        "max": max(hotel_max, booking_price)
                    }
            
            elif search_type == "car":
                car_type = search_params.get("car_type")
                if car_type and car_type not in prefs.preferred_car_types:
                    prefs.preferred_car_types.append(car_type)
                
                if booking_price:
                    if not prefs.budget_range:
                        prefs.budget_range = {"cars": {"min": 0, "max": 0}}
                    
                    car_min = prefs.budget_range.get("cars", {}).get("min", booking_price)
                    car_max = prefs.budget_range.get("cars", {}).get("max", booking_price)
                    
                    prefs.budget_range["cars"] = {
                        "min": min(car_min, booking_price),
                        "max": max(car_max, booking_price)
                    }
            
            prefs.last_updated = datetime.utcnow()
            
            # Upsert preferences
            await collection.update_one(
                {"user_id": user_id},
                {"$set": prefs.model_dump(by_alias=True, exclude={"user_id", "created_at"})},
                upsert=True
            )
            
            logger.debug(f"Updated preferences for user {user_id}")
        
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
    
    async def log_price_history(
        self,
        listing_id: str,
        listing_type: str,
        price: float,
        available_inventory: Optional[int] = None,
        source: str = "scheduled_scan"
    ):
        """Log price history for a listing."""
        try:
            price_history = PriceHistoryDocument(
                listing_id=listing_id,
                listing_type=listing_type,
                price=price,
                available_inventory=available_inventory,
                source=source,
                timestamp=datetime.utcnow()
            )
            
            await self.db[MongoCollections.PRICE_HISTORY].insert_one(price_history.model_dump())
            logger.debug(f"Logged price history for {listing_type} {listing_id}: ${price}")
        
        except Exception as e:
            logger.error(f"Error logging price history: {e}")
    
    async def log_admin_action(
        self,
        admin_id: str,
        admin_email: Optional[str],
        action_type: str,
        action_category: str,
        entity_type: str,
        entity_id: str,
        changes: List[dict],
        endpoint: str,
        method: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "success",
        error_message: Optional[str] = None
    ):
        """Log admin action to audit log."""
        try:
            audit_log = AdminAuditLog(
                audit_id=f"AUDIT-{uuid.uuid4().hex[:8].upper()}",
                admin_id=admin_id,
                admin_email=admin_email,
                action_type=action_type,
                action_category=action_category,
                entity_type=entity_type,
                entity_id=entity_id,
                changes=changes,
                endpoint=endpoint,
                method=method,
                ip_address=ip_address,
                user_agent=user_agent,
                status=status,
                error_message=error_message,
                timestamp=datetime.utcnow()
            )
            
            await self.db[MongoCollections.ADMIN_AUDIT_LOGS].insert_one(audit_log.model_dump())
            logger.info(f"Logged admin action: {action_type} on {entity_type} {entity_id} by {admin_id}")
        
        except Exception as e:
            logger.error(f"Error logging admin action: {e}")

