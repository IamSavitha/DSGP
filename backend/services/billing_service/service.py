"""
Billing Service - Business logic for payment and billing operations.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from decimal import Decimal
from datetime import datetime
import uuid
import math

from ...models.mysql_models import Billing, Booking, User, PaymentStatus, PaymentMethod, BookingType
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
        # Handle payment_method - convert to string (Billing model now uses String instead of Enum)
        payment_method_value = payment.payment_method
        if hasattr(payment_method_value, 'value'):
            payment_method_value = payment_method_value.value
        payment_method_str = str(payment_method_value).lower()  # Store as lowercase string
        
        # Handle booking_type - booking.booking_type is stored as a string
        # Billing model now uses String(20) instead of Enum, so we can use the string directly
        booking_type_str = booking.booking_type
        if isinstance(booking_type_str, str):
            # Use the string directly (already lowercase from booking)
            booking_type_value = booking_type_str.lower()
        elif hasattr(booking_type_str, 'value'):
            # If it's an enum, get its value
            booking_type_value = booking_type_str.value.lower()
        else:
            # Convert to string
            booking_type_value = str(booking_type_str).lower()
        
        # SECURITY: Only store last 4 digits of card number, never the full card number
        # Extract last 4 digits if card payment method is used
        card_last_four = None
        if payment_method_str in ['credit_card', 'debit_card'] and payment.card_number:
            # Remove any spaces or dashes from card number
            card_number_clean = payment.card_number.replace(' ', '').replace('-', '')
            # Only store last 4 digits for security compliance
            if len(card_number_clean) >= 4:
                card_last_four = card_number_clean[-4:]
            else:
                # If card number is too short, don't store anything
                card_last_four = None
        
        billing = Billing(
            billing_id=f"BILL-{uuid.uuid4().hex[:8].upper()}",
            user_id=booking.user_id,
            booking_id=booking.booking_id,
            booking_type=booking_type_value,
            subtotal=subtotal,
            tax_amount=tax_amount,
            total_amount=total_amount,
            payment_method=payment_method_str,
            payment_status=PaymentStatus.COMPLETED.value,
            card_last_four=card_last_four,  # Only last 4 digits stored, full card number NEVER stored
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
    
    def get_billing_by_booking_id(self, booking_id: str) -> Optional[Billing]:
        """Get billing record by booking_id."""
        return self.db.query(Billing).filter(Billing.booking_id == booking_id).first()
    
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
        """Process refund - approve pending refund or create new refund."""
        billing = self.get_billing(billing_id)
        if not billing:
            raise ValueError("Billing record not found")
        
        # If refund is pending, approve it. Otherwise, create new refund.
        if billing.payment_status == "refund_pending":
            billing.payment_status = PaymentStatus.REFUNDED.value
        elif billing.payment_status == "completed":
            billing.payment_status = PaymentStatus.REFUNDED.value
        else:
            raise ValueError(f"Cannot refund billing with status: {billing.payment_status}")
        
        self.db.commit()
        
        event_publisher.publish_payment_event("refunded", {
            "billing_id": billing_id,
            "reason": refund.reason
        })
        
        return {"status": "refunded", "billing_id": billing_id}
    
    def approve_refund(self, billing_id: str, reason: Optional[str] = None) -> dict:
        """Approve a pending refund. Ensures booking is cancelled and refund is completed."""
        billing = self.get_billing(billing_id)
        if not billing:
            raise ValueError("Billing record not found")
        
        if billing.payment_status != "refund_pending":
            raise ValueError(f"Billing {billing_id} is not in refund_pending status. Current status: {billing.payment_status}")
        
        # Ensure the associated booking is cancelled (approve the cancellation)
        from ...models.mysql_models import Booking, BookingStatus
        from ...services.booking_service.service import BookingService
        
        booking = self.db.query(Booking).filter(Booking.booking_id == billing.booking_id).first()
        if booking:
            if booking.status == "refund_pending":
                # Approve the cancellation - set booking to cancelled
                booking_service = BookingService(self.db)
                booking_service.approve_cancellation(booking.booking_id)
                logger.info(f"Approved cancellation for booking {booking.booking_id} during refund approval")
            elif booking.status != BookingStatus.CANCELLED.value:
                # If somehow not in refund_pending, still set to cancelled
                booking.status = BookingStatus.CANCELLED.value
                self.db.commit()
                logger.info(f"Updated booking {booking.booking_id} status to cancelled during refund approval")
        
        # Update billing status to refunded
        billing.payment_status = PaymentStatus.REFUNDED.value
        self.db.commit()
        
        event_publisher.publish_payment_event("refund_approved", {
            "billing_id": billing_id,
            "booking_id": billing.booking_id,
            "reason": reason or "Refund approved by admin"
        })
        
        return {
            "status": "refunded",
            "billing_id": billing_id,
            "booking_id": billing.booking_id,
            "booking_status": "cancelled"
        }
    
    def reject_refund(self, billing_id: str, reason: Optional[str] = None) -> dict:
        """Reject a pending refund and restore payment status."""
        billing = self.get_billing(billing_id)
        if not billing:
            raise ValueError("Billing record not found")
        
        if billing.payment_status != "refund_pending":
            raise ValueError(f"Billing {billing_id} is not in refund_pending status")
        
        billing.payment_status = "completed"  # Restore to completed
        self.db.commit()
        
        event_publisher.publish_payment_event("refund_rejected", {
            "billing_id": billing_id,
            "reason": reason or "Refund rejected by admin"
        })
        
        return {"status": "rejected", "billing_id": billing_id}
    
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
            "booking_type": billing.booking_type,  # Already a string
            "subtotal": float(billing.subtotal),
            "tax_amount": float(billing.tax_amount),
            "total_amount": float(billing.total_amount),
            "payment_method": billing.payment_method,  # Already a string
            "payment_status": billing.payment_status,  # Already a string
            "transaction_date": str(billing.transaction_date)
        }

