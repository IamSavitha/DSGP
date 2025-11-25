"""
Pydantic schemas for User-related requests and responses.
"""
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
import re

from ..common.validators import (
    validate_state, validate_zip_code, validate_user_id,
    validate_phone, normalize_state
)


class UserBase(BaseModel):
    """Base user schema with common fields."""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone_number: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=2)
    zip_code: Optional[str] = Field(None, max_length=10)
    profile_image_url: Optional[str] = Field(None, max_length=500)
    
    @field_validator('state')
    @classmethod
    def validate_state_field(cls, v):
        if v:
            return normalize_state(v)
        return v
    
    @field_validator('zip_code')
    @classmethod
    def validate_zip_field(cls, v):
        if v:
            validate_zip_code(v)
        return v
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_field(cls, v):
        if v:
            validate_phone(v, raise_exception=False)
        return v


class UserCreate(UserBase):
    """Schema for creating a new user."""
    user_id: str = Field(..., description="User ID in SSN format: XXX-XX-XXXX")
    password: str = Field(..., min_length=8, max_length=100)
    credit_card_number: Optional[str] = Field(None)
    credit_card_type: Optional[str] = Field(None)
    
    @field_validator('user_id')
    @classmethod
    def validate_user_id_field(cls, v):
        validate_user_id(v)
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123-45-6789",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "password": "securepassword123",
                "phone_number": "555-123-4567",
                "address": "123 Main St",
                "city": "San Jose",
                "state": "CA",
                "zip_code": "95123"
            }
        }


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=2)
    zip_code: Optional[str] = Field(None, max_length=10)
    profile_image_url: Optional[str] = Field(None, max_length=500)
    credit_card_number: Optional[str] = None
    credit_card_type: Optional[str] = None
    
    @field_validator('state')
    @classmethod
    def validate_state_field(cls, v):
        if v:
            return normalize_state(v)
        return v
    
    @field_validator('zip_code')
    @classmethod
    def validate_zip_field(cls, v):
        if v:
            validate_zip_code(v)
        return v


class UserResponse(BaseModel):
    """Schema for user response."""
    user_id: str
    first_name: str
    last_name: str
    email: str
    phone_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    profile_image_url: Optional[str] = None
    credit_card_last_four: Optional[str] = None
    credit_card_type: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserPasswordChange(BaseModel):
    """Schema for changing password."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


class UserBookingHistory(BaseModel):
    """Schema for user's booking history."""
    user_id: str
    bookings: List[dict] = []
    total_bookings: int = 0


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

