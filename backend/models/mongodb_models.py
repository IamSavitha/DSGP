"""
MongoDB document models for the Kayak Simulation system.
These models represent documents stored in MongoDB collections.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ==================== Review Models ====================

class ReviewDocument(BaseModel):
    """Review document model for MongoDB."""
    
    review_id: str = Field(..., description="Unique review identifier")
    user_id: str = Field(..., description="User who submitted the review")
    listing_id: str = Field(..., description="ID of the reviewed item")
    listing_type: str = Field(..., description="Type: flight, hotel, or car")
    
    # Review Content
    rating: float = Field(..., ge=1, le=5, description="Rating from 1-5")
    title: Optional[str] = Field(None, max_length=200)
    content: str = Field(..., max_length=2000)
    
    # Review Metadata
    pros: Optional[List[str]] = Field(default_factory=list)
    cons: Optional[List[str]] = Field(default_factory=list)
    
    # Helpful votes
    helpful_count: int = Field(default=0)
    not_helpful_count: int = Field(default=0)
    
    # Status
    is_verified: bool = Field(default=False, description="Verified purchase review")
    is_visible: bool = Field(default=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "review_id": "REV-001",
                "user_id": "123-45-6789",
                "listing_id": "AA123",
                "listing_type": "flight",
                "rating": 4.5,
                "title": "Great flight experience",
                "content": "The service was excellent and the flight was on time.",
                "pros": ["On time", "Great service", "Comfortable seats"],
                "cons": ["Small overhead bins"],
                "helpful_count": 10,
                "is_verified": True
            }
        }


# ==================== Image Models ====================

class ImageDocument(BaseModel):
    """Image document model for MongoDB."""
    
    image_id: str = Field(..., description="Unique image identifier")
    listing_id: str = Field(..., description="ID of the associated listing")
    listing_type: str = Field(..., description="Type: hotel, car")
    
    # Image Data
    url: str = Field(..., description="Image URL")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail URL")
    
    # Metadata
    caption: Optional[str] = Field(None, max_length=500)
    alt_text: Optional[str] = Field(None, max_length=200)
    category: Optional[str] = Field(None, description="e.g., room, exterior, amenity")
    
    # Order
    display_order: int = Field(default=0)
    is_primary: bool = Field(default=False)
    
    # Timestamps
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "image_id": "IMG-001",
                "listing_id": "HOTEL-001",
                "listing_type": "hotel",
                "url": "https://example.com/images/hotel1.jpg",
                "thumbnail_url": "https://example.com/images/hotel1_thumb.jpg",
                "caption": "Ocean view room",
                "category": "room",
                "is_primary": True
            }
        }


# ==================== Log Models ====================

class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class UserActionLog(BaseModel):
    """User action log document for MongoDB."""
    
    log_id: str = Field(..., description="Unique log identifier")
    user_id: Optional[str] = Field(None, description="User ID if authenticated")
    session_id: str = Field(..., description="Session identifier")
    
    # Action Details
    action: str = Field(..., description="Action type: search, view, book, etc.")
    resource_type: Optional[str] = Field(None, description="Resource type accessed")
    resource_id: Optional[str] = Field(None, description="Resource ID accessed")
    
    # Request Details
    endpoint: str = Field(..., description="API endpoint accessed")
    method: str = Field(..., description="HTTP method")
    ip_address: Optional[str] = Field(None)
    user_agent: Optional[str] = Field(None)
    
    # Request/Response
    request_params: Optional[dict] = Field(default_factory=dict)
    response_status: int = Field(..., description="HTTP response status code")
    response_time_ms: float = Field(..., description="Response time in milliseconds")
    
    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "log_id": "LOG-001",
                "user_id": "123-45-6789",
                "session_id": "sess_abc123",
                "action": "search",
                "resource_type": "flight",
                "endpoint": "/api/flights/search",
                "method": "GET",
                "response_status": 200,
                "response_time_ms": 45.5
            }
        }


class SearchLog(BaseModel):
    """Search activity log for analytics."""
    
    log_id: str
    user_id: Optional[str]
    session_id: str
    
    # Search Details
    search_type: str = Field(..., description="flight, hotel, car")
    search_params: dict = Field(..., description="Search parameters")
    results_count: int = Field(default=0)
    
    # Filters Applied
    filters_applied: Optional[dict] = Field(default_factory=dict)
    
    # User Interaction
    clicked_results: List[str] = Field(default_factory=list, description="IDs of clicked results")
    booked_result: Optional[str] = Field(None, description="ID of booked result if any")
    
    # Location
    search_location: Optional[str] = Field(None, description="User's location/city")
    
    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BookingLog(BaseModel):
    """Booking activity log."""
    
    log_id: str
    user_id: str
    booking_id: str
    
    # Booking Details
    booking_type: str
    listing_id: str
    
    # Status Changes
    status_from: Optional[str] = Field(None)
    status_to: str
    
    # Additional Info
    action: str = Field(..., description="created, updated, cancelled, completed")
    details: Optional[dict] = Field(default_factory=dict)
    
    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ==================== Analytics Models ====================

class AnalyticsDocument(BaseModel):
    """Analytics document for admin reports."""
    
    analytics_id: str
    metric_type: str = Field(..., description="revenue, bookings, users, etc.")
    
    # Time Period
    period_type: str = Field(..., description="daily, weekly, monthly, yearly")
    period_start: datetime
    period_end: datetime
    
    # Metrics
    metrics: dict = Field(..., description="Key-value pairs of metrics")
    
    # Dimensions
    dimensions: Optional[dict] = Field(default_factory=dict, description="Grouping dimensions")
    
    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "analytics_id": "ANALYTICS-001",
                "metric_type": "revenue",
                "period_type": "monthly",
                "period_start": "2025-01-01T00:00:00Z",
                "period_end": "2025-01-31T23:59:59Z",
                "metrics": {
                    "total_revenue": 150000.00,
                    "flight_revenue": 80000.00,
                    "hotel_revenue": 50000.00,
                    "car_revenue": 20000.00,
                    "total_bookings": 450
                },
                "dimensions": {
                    "city": "San Francisco"
                }
            }
        }


class ClickTrackingDocument(BaseModel):
    """Click tracking for page/section analytics."""
    
    tracking_id: str
    session_id: str
    user_id: Optional[str]
    
    # Page Details
    page_url: str
    page_name: str
    
    # Section/Element
    section_name: Optional[str] = Field(None)
    element_id: Optional[str] = Field(None)
    element_type: Optional[str] = Field(None, description="button, link, card, etc.")
    
    # Click Position
    x_position: Optional[int] = Field(None)
    y_position: Optional[int] = Field(None)
    
    # Context
    viewport_width: Optional[int] = Field(None)
    viewport_height: Optional[int] = Field(None)
    
    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class UserJourneyDocument(BaseModel):
    """User journey/trace document for cohort analysis."""
    
    journey_id: str
    user_id: Optional[str]
    session_id: str
    
    # Journey Details
    journey_start: datetime
    journey_end: Optional[datetime] = Field(None)
    
    # Steps
    steps: List[dict] = Field(default_factory=list, description="Ordered list of actions")
    
    # Outcome
    conversion: bool = Field(default=False)
    conversion_type: Optional[str] = Field(None, description="booking, signup, etc.")
    conversion_value: Optional[float] = Field(None)
    
    # User Attributes for Cohort
    user_city: Optional[str] = Field(None)
    user_state: Optional[str] = Field(None)
    device_type: Optional[str] = Field(None)
    
    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ==================== User Preferences ====================

class UserPreferencesDocument(BaseModel):
    """User preferences document for tracking user travel preferences."""
    
    user_id: str = Field(..., description="User ID (unique)")
    
    # Travel Preferences
    preferred_departure_airports: List[str] = Field(default_factory=list)
    preferred_airlines: List[str] = Field(default_factory=list)
    preferred_hotel_types: List[str] = Field(default_factory=list)
    preferred_car_types: List[str] = Field(default_factory=list)
    
    # Budget
    budget_range: Optional[dict] = Field(default_factory=lambda: {
        "flights": {"min": 0, "max": 0},
        "hotels": {"min": 0, "max": 0},
        "cars": {"min": 0, "max": 0}
    })
    
    # Behavioral Data
    travel_frequency: Optional[str] = Field(None, description="weekly, monthly, quarterly, yearly")
    average_trip_duration: Optional[int] = Field(None, description="days")
    typical_destinations: List[str] = Field(default_factory=list)
    
    # Preferences
    preferred_class: Optional[str] = Field(None, description="economy, business, first")
    seat_preference: Optional[str] = Field(None, description="window, aisle, no_preference")
    amenities_priority: List[str] = Field(default_factory=list)
    
    # ML Features (for AI)
    click_patterns: Optional[dict] = Field(default_factory=dict)
    booking_patterns: Optional[dict] = Field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123-45-6789",
                "preferred_departure_airports": ["SFO", "OAK", "SJC"],
                "preferred_airlines": ["United", "Delta"],
                "preferred_hotel_types": ["luxury", "boutique"],
                "budget_range": {
                    "flights": {"min": 200, "max": 800},
                    "hotels": {"min": 100, "max": 300}
                },
                "typical_destinations": ["NYC", "LAX", "SEA"]
            }
        }


# ==================== Price History ====================

class PriceHistoryDocument(BaseModel):
    """Price history document for tracking listing price changes."""
    
    listing_id: str = Field(..., description="Listing ID")
    listing_type: str = Field(..., description="flight, hotel, car")
    
    # Price Point
    price: float = Field(..., description="Price at this point in time")
    available_inventory: Optional[int] = Field(None, description="Seats/rooms/cars available")
    
    # Metadata
    source: str = Field(default="scheduled_scan", description="scheduled_scan, user_search, manual")
    
    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "listing_id": "AA123",
                "listing_type": "flight",
                "price": 450.00,
                "available_inventory": 25,
                "source": "scheduled_scan",
                "timestamp": "2025-01-15T10:00:00Z"
            }
        }


# ==================== Admin Audit Log ====================

class AdminAuditLog(BaseModel):
    """Admin audit log document for tracking admin actions."""
    
    audit_id: str = Field(..., description="Unique audit log identifier")
    
    # Admin Reference
    admin_id: str = Field(..., description="Admin ID")
    admin_email: Optional[str] = Field(None, description="Admin email")
    
    # Action Details
    action_type: str = Field(..., description="create, update, delete, etc.")
    action_category: str = Field(..., description="user_mgmt, inventory, financial, system")
    
    # Target Entity
    entity_type: str = Field(..., description="user, flight, hotel, car, booking, billing")
    entity_id: str = Field(..., description="ID of the entity being acted upon")
    
    # Changes Made
    changes: List[dict] = Field(default_factory=list, description="List of field changes with old/new values")
    
    # Request Details
    ip_address: Optional[str] = Field(None)
    user_agent: Optional[str] = Field(None)
    endpoint: str = Field(..., description="API endpoint")
    method: str = Field(..., description="HTTP method")
    
    # Status
    status: str = Field(default="success", description="success, failed, unauthorized")
    error_message: Optional[str] = Field(None)
    
    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "audit_id": "AUDIT-XYZ123",
                "admin_id": "ADMIN-789",
                "admin_email": "admin@kayak.com",
                "action_type": "update_flight",
                "action_category": "inventory_management",
                "entity_type": "flight",
                "entity_id": "AA123",
                "changes": [
                    {
                        "field": "base_price",
                        "old_value": 500.00,
                        "new_value": 450.00
                    }
                ],
                "ip_address": "192.168.1.100",
                "endpoint": "PUT /flights/AA123",
                "method": "PUT",
                "status": "success"
            }
        }


# ==================== Chat Session Models ====================

class ChatMessage(BaseModel):
    """Individual chat message in a conversation."""
    
    role: str = Field(..., description="user or assistant")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Structured data for assistant responses
    recommendations: Optional[List[dict]] = Field(default_factory=list, description="Bundle/recommendation data if applicable")
    clarification_needed: Optional[bool] = Field(default=False)


class ChatSessionDocument(BaseModel):
    """Chat session document for storing conversation history in MongoDB."""
    
    session_id: str = Field(..., description="Unique session identifier")
    user_id: Optional[str] = Field(None, description="User ID if authenticated")
    
    # Conversation
    messages: List[ChatMessage] = Field(default_factory=list, description="List of messages in conversation")
    
    # Context (maintains conversation state)
    context: Optional[dict] = Field(default_factory=dict, description="Session context for conversation continuity")
    
    # Session Metadata
    agent_version: str = Field(default="concierge-v1.0")
    
    # Timestamps
    started_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = Field(None, description="NULL if active")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "CHAT-789GHI",
                "user_id": "123-45-6789",
                "messages": [
                    {
                        "role": "user",
                        "content": "I want a weekend trip to Miami under $1500",
                        "timestamp": "2025-01-15T10:30:00Z"
                    },
                    {
                        "role": "assistant",
                        "content": "I found some great options for you...",
                        "timestamp": "2025-01-15T10:30:15Z",
                        "recommendations": [],
                        "clarification_needed": False
                    }
                ],
                "context": {
                    "destination": "Miami",
                    "budget": 1500,
                    "dates": "flexible"
                },
                "agent_version": "concierge-v1.0",
                "started_at": "2025-01-15T10:30:00Z",
                "last_activity": "2025-01-15T10:45:00Z",
                "ended_at": None
            }
        }

