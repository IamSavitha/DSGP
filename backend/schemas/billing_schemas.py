"""
Pydantic schemas for Billing and Payment requests and responses.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum


class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentRequest(BaseModel):
    """Schema for payment request."""
    booking_id: str
    payment_method: PaymentMethod
    card_number: Optional[str] = Field(None, description="Card number (will be masked)")
    card_expiry: Optional[str] = Field(None, description="MM/YY format")
    card_cvv: Optional[str] = Field(None, min_length=3, max_length=4)
    cardholder_name: Optional[str] = Field(None, max_length=100)
    
    # PayPal
    paypal_email: Optional[str] = None
    
    # Billing address
    billing_address: Optional[str] = None
    billing_city: Optional[str] = None
    billing_state: Optional[str] = None
    billing_zip: Optional[str] = None
    
    @field_validator('card_expiry')
    @classmethod
    def validate_expiry(cls, v):
        if v:
            import re
            if not re.match(r'^(0[1-9]|1[0-2])\/([0-9]{2})$', v):
                raise ValueError('Card expiry must be in MM/YY format')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "booking_id": "BK-001",
                "payment_method": "credit_card",
                "card_number": "4111111111111111",
                "card_expiry": "12/26",
                "card_cvv": "123",
                "cardholder_name": "John Doe"
            }
        }


class BillingCreate(BaseModel):
    """Schema for creating billing record."""
    user_id: str
    booking_id: str
    booking_type: str
    subtotal: Decimal = Field(..., gt=0)
    tax_rate: Decimal = Field(default=Decimal("0.0875"))  # 8.75% default tax
    payment_method: PaymentMethod
    card_last_four: Optional[str] = Field(None, min_length=4, max_length=4)


class BillingResponse(BaseModel):
    """Schema for billing response."""
    billing_id: str
    user_id: str
    booking_id: str
    booking_type: str
    transaction_date: datetime
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    payment_method: str
    payment_status: str
    card_last_four: Optional[str] = None
    invoice_number: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BillingSearchParams(BaseModel):
    """Schema for billing search parameters."""
    user_id: Optional[str] = None
    booking_type: Optional[str] = None
    payment_status: Optional[PaymentStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class BillingListResponse(BaseModel):
    """Schema for billing list response."""
    billings: list[BillingResponse]
    total_count: int
    total_amount: Decimal
    page: int
    page_size: int


class RefundRequest(BaseModel):
    """Schema for refund request."""
    billing_id: str
    reason: str = Field(..., max_length=500)
    refund_amount: Optional[Decimal] = Field(None, description="Partial refund amount")


class RefundApprovalRequest(BaseModel):
    """Schema for refund approval/rejection request."""
    reason: Optional[str] = Field(None, max_length=500, description="Reason for approval/rejection")


class RefundResponse(BaseModel):
    """Schema for refund response."""
    refund_id: str
    billing_id: str
    original_amount: Decimal
    refund_amount: Decimal
    reason: str
    status: str
    processed_at: Optional[datetime] = None
    created_at: datetime


class InvoiceResponse(BaseModel):
    """Schema for invoice details."""
    invoice_number: str
    billing_id: str
    user_id: str
    booking_id: str
    
    # User details
    user_name: str
    user_email: str
    
    # Booking details
    booking_type: str
    listing_details: dict
    
    # Financial
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    
    # Payment
    payment_method: str
    payment_status: str
    transaction_date: datetime
    
    # Invoice metadata
    invoice_date: datetime
    due_date: Optional[datetime] = None

