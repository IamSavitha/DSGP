"""
Pydantic schemas for Booking requests and responses.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum


class BookingType(str, Enum):
    FLIGHT = "flight"
    HOTEL = "hotel"
    CAR = "car"


class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class BookingCreate(BaseModel):
    """Schema for creating a new booking."""
    user_id: str = Field(..., description="User ID")
    booking_type: BookingType
    listing_id: str = Field(..., description="ID of the flight/hotel/car")
    check_in_date: datetime
    check_out_date: Optional[datetime] = None
    
    # Flight-specific
    num_passengers: int = Field(default=1, ge=1, le=9)
    flight_class: Optional[str] = None
    
    # Hotel-specific
    num_rooms: int = Field(default=1, ge=1, le=10)
    room_type: Optional[str] = None
    
    # Car-specific (num_days calculated from dates)
    
    @field_validator('check_out_date')
    @classmethod
    def validate_checkout(cls, v, info):
        check_in = info.data.get('check_in_date')
        if v and check_in and v <= check_in:
            raise ValueError('Check-out date must be after check-in date')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123-45-6789",
                "booking_type": "flight",
                "listing_id": "AA123",
                "check_in_date": "2025-12-01T08:00:00",
                "num_passengers": 2
            }
        }


class BookingUpdate(BaseModel):
    """Schema for updating a booking."""
    check_in_date: Optional[datetime] = None
    check_out_date: Optional[datetime] = None
    num_passengers: Optional[int] = Field(None, ge=1, le=9)
    num_rooms: Optional[int] = Field(None, ge=1, le=10)
    status: Optional[BookingStatus] = None


class BookingResponse(BaseModel):
    """Schema for booking response."""
    booking_id: str
    user_id: str
    booking_type: str
    listing_id: str
    check_in_date: datetime
    check_out_date: Optional[datetime] = None
    num_passengers: int = 1
    num_rooms: int = 1
    num_nights: int = 1
    status: str
    total_price: Decimal
    booking_date: datetime
    created_at: datetime
    updated_at: datetime
    
    # Include listing details
    listing_details: Optional[dict] = None
    
    class Config:
        from_attributes = True


class BookingListResponse(BaseModel):
    """Schema for booking list response."""
    bookings: list[BookingResponse]
    total_count: int
    page: int
    page_size: int


class BookingCancellation(BaseModel):
    """Schema for booking cancellation request."""
    reason: Optional[str] = Field(None, max_length=500)
    refund_requested: bool = True

