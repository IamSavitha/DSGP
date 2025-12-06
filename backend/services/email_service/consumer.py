"""
Email Service - Kafka consumer for processing email events.
"""
import asyncio
import json
import logging
from typing import Dict, Any
from datetime import datetime

from aiokafka import AIOKafkaConsumer
from ...common.config import settings
from ...kafka.topics import KafkaTopics
from ...common.database import get_mysql_session
from .service import EmailService

logger = logging.getLogger(__name__)


class EmailConsumerService:
    """Kafka consumer service for email notifications."""
    
    def __init__(self):
        self.consumer: AIOKafkaConsumer = None
        self.email_service = EmailService()
        self.running = False
    
    async def start(self):
        """Start the email consumer service."""
        self.running = True
        
        try:
            self.consumer = AIOKafkaConsumer(
                KafkaTopics.BOOKING_CREATED,
                KafkaTopics.PAYMENT_COMPLETED,
                KafkaTopics.PAYMENT_REFUNDED,
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS.split(','),
                group_id="email-service-group",
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                enable_auto_commit=True,
                auto_commit_interval_ms=1000
            )
            
            await self.consumer.start()
            logger.info("Email service consumer started")
            
            # Start consuming messages
            await self._consume_messages()
            
        except Exception as e:
            logger.error(f"Failed to start email consumer: {e}")
            self.running = False
    
    async def _consume_messages(self):
        """Consume messages from Kafka topics."""
        try:
            async for message in self.consumer:
                if not self.running:
                    break
                
                topic = message.topic
                value = message.value
                
                logger.debug(f"Received message from topic: {topic}")
                
                # Route to appropriate handler
                if topic == KafkaTopics.BOOKING_CREATED:
                    await self._handle_booking_created(value)
                elif topic == KafkaTopics.PAYMENT_COMPLETED:
                    await self._handle_payment_completed(value)
                elif topic == KafkaTopics.PAYMENT_REFUNDED:
                    await self._handle_payment_refunded(value)
        
        except Exception as e:
            logger.error(f"Error consuming messages: {e}")
    
    async def _handle_booking_created(self, event_data: Dict[str, Any]):
        """Handle booking created event."""
        try:
            data = event_data.get("data", {})
            booking_id = data.get("booking_id")
            user_id = data.get("user_id")
            
            # Get user email from database
            from sqlalchemy.orm import Session
            from ...common.database import SessionLocal
            from ...models.mysql_models import User
            
            db: Session = SessionLocal()
            try:
                user = db.query(User).filter(User.user_id == user_id).first()
                if not user:
                    logger.warning(f"User {user_id} not found for booking {booking_id}")
                    return
                
                email_data = {
                    "user_email": user.email,
                    "booking_id": booking_id,
                    "booking_type": data.get("booking_type"),
                    "total_price": data.get("total_price"),
                    "booking_date": datetime.now().isoformat(),
                    "listing_details": {}
                }
                
                await self.email_service.send_booking_confirmation(email_data)
                logger.info(f"Sent booking confirmation email for {booking_id}")
            
            finally:
                db.close()
        
        except Exception as e:
            logger.error(f"Error handling booking created event: {e}")
    
    async def _handle_payment_completed(self, event_data: Dict[str, Any]):
        """Handle payment completed event."""
        try:
            data = event_data.get("data", {})
            billing_id = data.get("billing_id")
            booking_id = data.get("booking_id")
            
            # Get user and billing details
            from sqlalchemy.orm import Session
            from ...common.database import SessionLocal
            from ...models.mysql_models import User, Billing, Booking
            
            db: Session = SessionLocal()
            try:
                billing = db.query(Billing).filter(Billing.billing_id == billing_id).first()
                if not billing:
                    logger.warning(f"Billing {billing_id} not found")
                    return
                
                user = db.query(User).filter(User.user_id == billing.user_id).first()
                if not user:
                    return
                
                booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
                
                # Handle booking_type - it's stored as a string in database
                booking_type_str = booking.booking_type if booking else None
                if booking_type_str and hasattr(booking_type_str, 'value'):
                    booking_type_str = booking_type_str.value
                
                email_data = {
                    "user_email": user.email,
                    "billing_id": billing_id,
                    "invoice_number": billing.invoice_number,
                    "amount": float(billing.total_amount),
                    "payment_date": billing.transaction_date.isoformat() if billing.transaction_date else None,
                    "booking_details": {
                        "booking_id": booking_id,
                        "booking_type": booking_type_str  # Already a string from database
                    }
                }
                
                await self.email_service.send_payment_confirmation(email_data)
                logger.info(f"Sent payment confirmation email for billing {billing_id}")
            
            finally:
                db.close()
        
        except Exception as e:
            logger.error(f"Error handling payment completed event: {e}")
    
    async def _handle_payment_refunded(self, event_data: Dict[str, Any]):
        """Handle payment refunded event."""
        try:
            data = event_data.get("data", {})
            billing_id = data.get("billing_id")
            
            # Similar to payment completed but with refund context
            logger.info(f"Processing refund notification for billing {billing_id}")
            # Implementation similar to payment_completed
        
        except Exception as e:
            logger.error(f"Error handling payment refunded event: {e}")
    
    async def stop(self):
        """Stop the consumer service."""
        self.running = False
        if self.consumer:
            await self.consumer.stop()
            logger.info("Email service consumer stopped")

