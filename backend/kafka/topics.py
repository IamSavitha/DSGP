"""
Kafka topic definitions for the Kayak Simulation system.
"""


class KafkaTopics:
    """Centralized Kafka topic names."""
    
    # User Events
    USER_CREATED = "kayak.user.created"
    USER_UPDATED = "kayak.user.updated"
    USER_DELETED = "kayak.user.deleted"
    
    # Search Events
    FLIGHT_SEARCH = "kayak.search.flight"
    HOTEL_SEARCH = "kayak.search.hotel"
    CAR_SEARCH = "kayak.search.car"
    
    # Booking Events
    BOOKING_CREATED = "kayak.booking.created"
    BOOKING_UPDATED = "kayak.booking.updated"
    BOOKING_CANCELLED = "kayak.booking.cancelled"
    BOOKING_COMPLETED = "kayak.booking.completed"
    
    # Payment Events
    PAYMENT_INITIATED = "kayak.payment.initiated"
    PAYMENT_COMPLETED = "kayak.payment.completed"
    PAYMENT_FAILED = "kayak.payment.failed"
    PAYMENT_REFUNDED = "kayak.payment.refunded"
    
    # Listing Events
    FLIGHT_CREATED = "kayak.listing.flight.created"
    FLIGHT_UPDATED = "kayak.listing.flight.updated"
    HOTEL_CREATED = "kayak.listing.hotel.created"
    HOTEL_UPDATED = "kayak.listing.hotel.updated"
    CAR_CREATED = "kayak.listing.car.created"
    CAR_UPDATED = "kayak.listing.car.updated"
    
    # Review Events
    REVIEW_CREATED = "kayak.review.created"
    REVIEW_UPDATED = "kayak.review.updated"
    REVIEW_DELETED = "kayak.review.deleted"
    
    # Analytics Events
    PAGE_VIEW = "kayak.analytics.pageview"
    CLICK_EVENT = "kayak.analytics.click"
    SEARCH_EVENT = "kayak.analytics.search"
    
    # AI Service Events
    RAW_SUPPLIER_FEEDS = "kayak.ai.raw_supplier_feeds"
    DEALS_NORMALIZED = "kayak.ai.deals.normalized"
    DEALS_SCORED = "kayak.ai.deals.scored"
    DEALS_TAGGED = "kayak.ai.deals.tagged"
    DEAL_EVENTS = "kayak.ai.deal.events"
    
    # Notification Events
    NOTIFICATION_EMAIL = "kayak.notification.email"
    NOTIFICATION_SMS = "kayak.notification.sms"
    NOTIFICATION_PUSH = "kayak.notification.push"
    
    @classmethod
    def all_topics(cls) -> list:
        """Get all topic names."""
        return [
            value for name, value in vars(cls).items()
            if not name.startswith('_') and isinstance(value, str)
        ]
    
    @classmethod
    def user_topics(cls) -> list:
        """Get user-related topics."""
        return [cls.USER_CREATED, cls.USER_UPDATED, cls.USER_DELETED]
    
    @classmethod
    def booking_topics(cls) -> list:
        """Get booking-related topics."""
        return [
            cls.BOOKING_CREATED, cls.BOOKING_UPDATED,
            cls.BOOKING_CANCELLED, cls.BOOKING_COMPLETED
        ]
    
    @classmethod
    def payment_topics(cls) -> list:
        """Get payment-related topics."""
        return [
            cls.PAYMENT_INITIATED, cls.PAYMENT_COMPLETED,
            cls.PAYMENT_FAILED, cls.PAYMENT_REFUNDED
        ]
    
    @classmethod
    def ai_topics(cls) -> list:
        """Get AI service topics."""
        return [
            cls.RAW_SUPPLIER_FEEDS, cls.DEALS_NORMALIZED,
            cls.DEALS_SCORED, cls.DEALS_TAGGED, cls.DEAL_EVENTS
        ]

