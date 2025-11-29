"""
Kafka Producer Service for publishing messages to Kafka topics.
"""
import json
import logging
from typing import Optional, Any, Dict
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import KafkaError

from ..common.config import settings

logger = logging.getLogger(__name__)


class KafkaProducerService:
    """Kafka Producer wrapper with singleton pattern."""
    
    _instance: Optional['KafkaProducerService'] = None
    _producer: Optional[KafkaProducer] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Don't initialize producer immediately
        pass

    def _initialize_producer(self):
        """Initialize Kafka producer with configuration."""
        if self._producer is not None:
            return

        try:
            self._producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS.split(','),
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',
                retries=3,
                max_in_flight_requests_per_connection=1,
                compression_type='gzip',
                linger_ms=10,
                batch_size=16384
            )
            logger.info("Kafka producer initialized successfully")
        except KafkaError as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            # Don't raise - allow service to start without Kafka
            logger.warning("Service will continue without Kafka event publishing")
    
    def send(
        self,
        topic: str,
        value: Dict[str, Any],
        key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Send a message to a Kafka topic.

        Args:
            topic: The Kafka topic to send to
            value: The message payload (dict)
            key: Optional message key for partitioning
            headers: Optional message headers

        Returns:
            True if message was sent successfully
        """
        # Lazy initialization
        if self._producer is None:
            self._initialize_producer()

        # If producer still not initialized, skip sending
        if self._producer is None:
            logger.warning(f"Kafka producer not available, skipping message to {topic}")
            return False

        try:
            # Add metadata to message
            message = {
                **value,
                "_metadata": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "source": "kayak-backend"
                }
            }

            # Convert headers to Kafka format
            kafka_headers = None
            if headers:
                kafka_headers = [(k, v.encode('utf-8')) for k, v in headers.items()]

            # Send message
            future = self._producer.send(
                topic,
                value=message,
                key=key,
                headers=kafka_headers
            )

            # Wait for send to complete (with timeout)
            record_metadata = future.get(timeout=10)

            logger.debug(
                f"Message sent to {topic} - "
                f"partition: {record_metadata.partition}, "
                f"offset: {record_metadata.offset}"
            )
            return True

        except KafkaError as e:
            logger.error(f"Failed to send message to {topic}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending message: {e}")
            return False
    
    def send_async(
        self,
        topic: str,
        value: Dict[str, Any],
        key: Optional[str] = None,
        callback: callable = None
    ):
        """
        Send a message asynchronously.

        Args:
            topic: The Kafka topic
            value: The message payload
            key: Optional message key
            callback: Optional callback function(record_metadata, exception)
        """
        # Lazy initialization
        if self._producer is None:
            self._initialize_producer()

        # If producer still not initialized, skip sending
        if self._producer is None:
            logger.warning(f"Kafka producer not available, skipping async message to {topic}")
            if callback:
                callback(None, Exception("Kafka producer not available"))
            return

        try:
            message = {
                **value,
                "_metadata": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "source": "kayak-backend"
                }
            }

            def on_success(record_metadata):
                logger.debug(f"Async message sent to {topic}")
                if callback:
                    callback(record_metadata, None)

            def on_error(exception):
                logger.error(f"Async message failed for {topic}: {exception}")
                if callback:
                    callback(None, exception)

            future = self._producer.send(topic, value=message, key=key)
            future.add_callback(on_success)
            future.add_errback(on_error)

        except Exception as e:
            logger.error(f"Failed to send async message: {e}")
            if callback:
                callback(None, e)
    
    def flush(self, timeout: float = None):
        """Flush all pending messages."""
        if self._producer:
            self._producer.flush(timeout=timeout)
    
    def close(self):
        """Close the producer."""
        if self._producer:
            self._producer.flush()
            self._producer.close()
            self._producer = None
            logger.info("Kafka producer closed")


# ==================== Event Publishers ====================

class EventPublisher:
    """Helper class for publishing specific event types."""
    
    def __init__(self):
        self.producer = KafkaProducerService()
    
    def publish_user_event(self, event_type: str, user_data: dict):
        """Publish user-related events."""
        from .topics import KafkaTopics
        
        topic_map = {
            "created": KafkaTopics.USER_CREATED,
            "updated": KafkaTopics.USER_UPDATED,
            "deleted": KafkaTopics.USER_DELETED
        }
        
        topic = topic_map.get(event_type)
        if topic:
            self.producer.send(
                topic=topic,
                value={"event_type": event_type, "data": user_data},
                key=user_data.get("user_id")
            )
    
    def publish_booking_event(self, event_type: str, booking_data: dict):
        """Publish booking-related events."""
        from .topics import KafkaTopics
        
        topic_map = {
            "created": KafkaTopics.BOOKING_CREATED,
            "updated": KafkaTopics.BOOKING_UPDATED,
            "cancelled": KafkaTopics.BOOKING_CANCELLED,
            "completed": KafkaTopics.BOOKING_COMPLETED
        }
        
        topic = topic_map.get(event_type)
        if topic:
            self.producer.send(
                topic=topic,
                value={"event_type": event_type, "data": booking_data},
                key=booking_data.get("booking_id")
            )
    
    def publish_payment_event(self, event_type: str, payment_data: dict):
        """Publish payment-related events."""
        from .topics import KafkaTopics
        
        topic_map = {
            "initiated": KafkaTopics.PAYMENT_INITIATED,
            "completed": KafkaTopics.PAYMENT_COMPLETED,
            "failed": KafkaTopics.PAYMENT_FAILED,
            "refunded": KafkaTopics.PAYMENT_REFUNDED
        }
        
        topic = topic_map.get(event_type)
        if topic:
            self.producer.send(
                topic=topic,
                value={"event_type": event_type, "data": payment_data},
                key=payment_data.get("billing_id")
            )
    
    def publish_search_event(self, search_type: str, search_data: dict):
        """Publish search events for analytics."""
        from .topics import KafkaTopics
        
        topic_map = {
            "flight": KafkaTopics.FLIGHT_SEARCH,
            "hotel": KafkaTopics.HOTEL_SEARCH,
            "car": KafkaTopics.CAR_SEARCH
        }
        
        topic = topic_map.get(search_type)
        if topic:
            self.producer.send(
                topic=topic,
                value={"search_type": search_type, "data": search_data}
            )
    
    def publish_analytics_event(self, event_type: str, event_data: dict):
        """Publish analytics events."""
        from .topics import KafkaTopics
        
        topic_map = {
            "pageview": KafkaTopics.PAGE_VIEW,
            "click": KafkaTopics.CLICK_EVENT,
            "search": KafkaTopics.SEARCH_EVENT
        }
        
        topic = topic_map.get(event_type)
        if topic:
            self.producer.send(
                topic=topic,
                value={"event_type": event_type, "data": event_data}
            )


# Global event publisher instance
event_publisher = EventPublisher()

