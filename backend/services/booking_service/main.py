"""
Booking Service - FastAPI application for booking management.
"""
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional

import logging

from ...common.config import settings
from ...common.database import get_mysql_session, init_mysql_db
from ...common.exceptions import handle_not_found
from ...schemas.booking_schemas import (
    BookingCreate, BookingUpdate, BookingResponse, BookingListResponse, BookingCancellation
)
from .service import BookingService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Kayak Booking Service",
    description="Unified booking microservice for flights, hotels, and cars",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Starting Booking Service...")
    init_mysql_db()
    logger.info("Booking Service started successfully")


@app.get("/health")
async def health_check():
    """Health check endpoint with database connectivity checks."""
    from ...common.health import get_comprehensive_health
    return await get_comprehensive_health(
        check_mysql=True,
        check_redis=True,
        service_name="booking-service"
    )


# ==================== Booking Endpoints ====================

@app.post("/bookings", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_mysql_session)
):
    """Create a new booking for flight, hotel, or car."""
    service = BookingService(db)
    try:
        booking = service.create_booking(booking_data)
        return service._format_booking_response(booking)
    except ValueError as e:
        logger.error(f"Booking validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error creating booking: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/bookings/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: str,
    db: Session = Depends(get_mysql_session)
):
    """Get booking by ID."""
    service = BookingService(db)
    booking = service.get_booking(booking_id)
    if not booking:
        handle_not_found("Booking", booking_id)
    return service._format_booking_response(booking)


@app.get("/bookings/user/{user_id}", response_model=BookingListResponse)
async def get_user_bookings(
    user_id: str,
    booking_type: Optional[str] = Query(None, description="Filter by booking type: flight, hotel, car"),
    status: Optional[str] = Query(None, description="Filter by status: pending, confirmed, cancelled, completed"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_mysql_session)
):
    """Get user's bookings with filtering and pagination."""
    service = BookingService(db)
    return service.get_user_bookings(user_id, booking_type, status, page, page_size)


@app.put("/bookings/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: str,
    booking_data: BookingUpdate,
    db: Session = Depends(get_mysql_session)
):
    """Update booking information."""
    service = BookingService(db)
    booking = service.get_booking(booking_id)
    if not booking:
        handle_not_found("Booking", booking_id)
    
    # Update fields
    update_data = booking_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(booking, field):
            setattr(booking, field, value)
    
    db.commit()
    db.refresh(booking)
    
    return service._format_booking_response(booking)


@app.post("/bookings/{booking_id}/cancel", response_model=dict)
async def cancel_booking(
    booking_id: str,
    cancellation: BookingCancellation,
    db: Session = Depends(get_mysql_session)
):
    """Cancel a booking (customer cancellation). Sets status to refund_pending for admin approval."""
    service = BookingService(db)
    try:
        # Customer cancellation requires admin approval - set status to refund_pending
        success = service.cancel_booking(booking_id, cancellation.reason, require_admin_approval=True)
        
        # For cancelled bookings, automatically set refund to pending if payment was completed
        # This requires admin approval before refund is processed
        refund_pending = False
        from ...services.billing_service.service import BillingService
            
        billing_service = BillingService(db)
        billing = billing_service.get_billing_by_booking_id(booking_id)
        
        if billing and billing.payment_status == "completed":
            try:
                # Set refund status to pending (requires admin approval)
                billing.payment_status = "refund_pending"
                db.commit()
                refund_pending = True
                
                # Publish event for admin notification
                from ...kafka.producer import event_publisher
                event_publisher.publish_payment_event("refund_pending", {
                    "billing_id": billing.billing_id,
                    "booking_id": booking_id,
                    "reason": cancellation.reason or "Booking cancellation requested - refund pending admin approval"
                })
            except Exception as refund_error:
                logger.error(f"Error creating pending refund for booking {booking_id}: {refund_error}")
                # Continue with cancellation even if refund fails
        
        return {
            "status": "refund_pending",
            "booking_id": booking_id,
            "refund_pending": refund_pending,
            "message": "Cancellation request submitted. Refund pending admin approval."
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8009)

