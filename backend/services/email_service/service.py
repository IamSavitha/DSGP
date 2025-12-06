"""
Email Service - Business logic for sending email notifications.
"""
import logging
import json
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending email notifications."""
    
    def __init__(self):
        # In production, initialize email client (SendGrid, SES, etc.)
        # For now, we'll just log emails
        self.enabled = True
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        template: str,
        context: Dict[str, Any]
    ) -> bool:
        """
        Send an email using a template.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            template: Template name
            context: Template variables
        
        Returns:
            True if email sent successfully
        """
        if not self.enabled:
            logger.warning(f"Email service disabled, skipping email to {to_email}")
            return False
        
        try:
            # In production, this would:
            # 1. Load email template
            # 2. Render template with context
            # 3. Send via email service provider
            
            # Enhanced logging for testing
            logger.info(f"📧 EMAIL SENT - To: {to_email}, Subject: {subject}")
            logger.info(f"   Template: {template}")
            logger.info(f"   Context: {json.dumps(context, indent=2, default=str)}")
            
            # Mock email sending (in production, this would send via email provider)
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    async def send_booking_confirmation(self, booking_data: Dict[str, Any]) -> bool:
        """Send booking confirmation email."""
        user_email = booking_data.get("user_email")
        booking_id = booking_data.get("booking_id")
        booking_type = booking_data.get("booking_type")
        total_price = booking_data.get("total_price")
        
        subject = f"Booking Confirmation - {booking_id}"
        
        context = {
            "booking_id": booking_id,
            "booking_type": booking_type,
            "total_price": total_price,
            "booking_date": booking_data.get("booking_date", datetime.now().isoformat()),
            "listing_details": booking_data.get("listing_details", {})
        }
        
        return await self.send_email(
            to_email=user_email,
            subject=subject,
            template="booking_confirmation",
            context=context
        )
    
    async def send_payment_confirmation(self, payment_data: Dict[str, Any]) -> bool:
        """Send payment confirmation email."""
        user_email = payment_data.get("user_email")
        billing_id = payment_data.get("billing_id")
        invoice_number = payment_data.get("invoice_number")
        total_amount = payment_data.get("amount")
        
        subject = f"Payment Confirmation - Invoice {invoice_number}"
        
        context = {
            "billing_id": billing_id,
            "invoice_number": invoice_number,
            "total_amount": total_amount,
            "payment_date": payment_data.get("payment_date", datetime.now().isoformat()),
            "booking_details": payment_data.get("booking_details", {})
        }
        
        return await self.send_email(
            to_email=user_email,
            subject=subject,
            template="payment_confirmation",
            context=context
        )
    
    async def send_price_drop_alert(self, alert_data: Dict[str, Any]) -> bool:
        """Send price drop alert email."""
        user_email = alert_data.get("user_email")
        listing_id = alert_data.get("listing_id")
        old_price = alert_data.get("old_price")
        new_price = alert_data.get("new_price")
        discount_percent = alert_data.get("discount_percent")
        
        subject = f"💰 Price Drop Alert - {discount_percent}% Off!"
        
        context = {
            "listing_id": listing_id,
            "listing_type": alert_data.get("listing_type"),
            "old_price": old_price,
            "new_price": new_price,
            "discount_percent": discount_percent,
            "listing_details": alert_data.get("listing_details", {})
        }
        
        return await self.send_email(
            to_email=user_email,
            subject=subject,
            template="price_drop_alert",
            context=context
        )

