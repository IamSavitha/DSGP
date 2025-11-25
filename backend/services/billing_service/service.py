"""
Billing Service - Business logic for payment and billing operations.
"""
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal
from datetime import datetime
import uuid
import math

from ...models.mysql_models import Billing, Booking, User, PaymentStatus
from ...schemas.billing_schemas import (
    PaymentRequest, BillingResponse, BillingSearchParams,
    BillingListResponse, RefundRequest
)
from ...kafka.producer import event_publisher


class BillingService:
    def __init__(self, db: Session):
        self.db = db
    
    def process_payment(self, payment: PaymentRequest) -> Billing:
        """Process a payment for a booking."""
        # Get booking
        booking = self.db.query(Booking).filter(
            Booking.booking_id == payment.booking_id
        ).first()
        
        if not booking:
            raise ValueError("Booking not found")
        
        # Calculate amounts
        subtotal = booking.total_price
        tax_rate = Decimal("0.0875")
        tax_amount = subtotal * tax_rate
        total_amount = subtotal + tax_amount
        
        # Create billing record
        billing = Billing(
            billing_id=f"BILL-{uuid.uuid4().hex[:8].upper()}",
            user_id=booking.user_id,
            booking_id=booking.booking_id,
            booking_type=booking.booking_type,
            subtotal=subtotal,
            tax_amount=tax_amount,
            total_amount=total_amount,
            payment_method=payment.payment_method,
            payment_status=PaymentStatus.COMPLETED,
            card_last_four=payment.card_number[-4:] if payment.card_number else None,
            invoice_number=f"INV-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        )
        
        self.db.add(billing)
        
        # Update booking status
        from ...models.mysql_models import BookingStatus
        booking.status = BookingStatus.CONFIRMED
        
        self.db.commit()
        self.db.refresh(billing)
        
        # Publish event
        event_publisher.publish_payment_event("completed", {
            "billing_id": billing.billing_id,
            "booking_id": booking.booking_id,
            "amount": float(total_amount)
        })
        
        return billing
    
    def get_billing(self, billing_id: str) -> Optional[Billing]:
        return self.db.query(Billing).filter(Billing.billing_id == billing_id).first()
    
    def search_billings(self, params: BillingSearchParams) -> BillingListResponse:
        query = self.db.query(Billing)
        
        if params.user_id:
            query = query.filter(Billing.user_id == params.user_id)
        if params.booking_type:
            query = query.filter(Billing.booking_type == params.booking_type)
        if params.payment_status:
            query = query.filter(Billing.payment_status == params.payment_status)
        if params.start_date:
            query = query.filter(Billing.transaction_date >= params.start_date)
        if params.end_date:
            query = query.filter(Billing.transaction_date <= params.end_date)
        
        total_count = query.count()
        total_amount = self.db.query(
            func.sum(Billing.total_amount)
        ).filter(Billing.billing_id.in_([b.billing_id for b in query.all()])).scalar() or Decimal(0)
        
        from sqlalchemy import func
        offset = (params.page - 1) * params.page_size
        billings = query.order_by(Billing.transaction_date.desc()).offset(offset).limit(params.page_size).all()
        
        return BillingListResponse(
            billings=[BillingResponse.model_validate(b) for b in billings],
            total_count=total_count,
            total_amount=total_amount,
            page=params.page,
            page_size=params.page_size
        )
    
    def process_refund(self, billing_id: str, refund: RefundRequest) -> dict:
        billing = self.get_billing(billing_id)
        if not billing:
            raise ValueError("Billing record not found")
        
        billing.payment_status = PaymentStatus.REFUNDED
        self.db.commit()
        
        event_publisher.publish_payment_event("refunded", {
            "billing_id": billing_id,
            "reason": refund.reason
        })
        
        return {"status": "refunded", "billing_id": billing_id}
    
    def generate_invoice(self, billing_id: str) -> dict:
        billing = self.get_billing(billing_id)
        if not billing:
            raise ValueError("Billing record not found")
        
        user = self.db.query(User).filter(User.user_id == billing.user_id).first()
        
        return {
            "invoice_number": billing.invoice_number,
            "billing_id": billing.billing_id,
            "user_name": f"{user.first_name} {user.last_name}" if user else "N/A",
            "user_email": user.email if user else "N/A",
            "booking_type": billing.booking_type.value if hasattr(billing.booking_type, 'value') else billing.booking_type,
            "subtotal": float(billing.subtotal),
            "tax_amount": float(billing.tax_amount),
            "total_amount": float(billing.total_amount),
            "payment_method": billing.payment_method.value if hasattr(billing.payment_method, 'value') else billing.payment_method,
            "payment_status": billing.payment_status.value if hasattr(billing.payment_status, 'value') else billing.payment_status,
            "transaction_date": str(billing.transaction_date)
        }

