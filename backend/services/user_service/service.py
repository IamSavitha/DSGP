"""
User Service - Business logic for user operations.
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from passlib.context import CryptContext
import bcrypt as bcrypt_lib
import logging

from ...models.mysql_models import User, Booking
from ...schemas.user_schemas import UserCreate, UserUpdate
from ...common.cache import RedisCache, CacheKeys
from ...common.exceptions import DuplicateUserException
from ...kafka.producer import event_publisher

logger = logging.getLogger(__name__)

# Password hashing - use bcrypt directly to avoid passlib bug detection issue
import bcrypt as bcrypt_lib
pwd_context = None  # Will use bcrypt_lib directly


class UserService:
    """Service class for user operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.cache = RedisCache()
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        # Check for existing user
        existing = self.db.query(User).filter(
            or_(
                User.user_id == user_data.user_id,
                User.email == user_data.email
            )
        ).first()
        
        if existing:
            raise DuplicateUserException(user_data.user_id)
        
        # Hash password using bcrypt directly (avoid passlib bug detection issue)
        password_bytes = user_data.password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        password_hash = bcrypt_lib.hashpw(password_bytes, bcrypt_lib.gensalt()).decode('utf-8')
        
        # Create user
        user = User(
            user_id=user_data.user_id,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            phone_number=user_data.phone_number,
            address=user_data.address,
            city=user_data.city,
            state=user_data.state,
            zip_code=user_data.zip_code,
            profile_image_url=user_data.profile_image_url,
            password_hash=password_hash
        )
        
        # Handle credit card (store only last 4 digits)
        if user_data.credit_card_number:
            user.credit_card_last_four = user_data.credit_card_number[-4:]
            user.credit_card_type = user_data.credit_card_type
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Publish event
        event_publisher.publish_user_event("created", {
            "user_id": user.user_id,
            "email": user.email
        })
        
        logger.info(f"Created user: {user.user_id}")
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID with caching."""
        # Try cache first
        cache_key = CacheKeys.user(user_id)
        cached = self.cache.get(cache_key)
        if cached:
            return User(**cached)
        
        # Query database
        user = self.db.query(User).filter(User.user_id == user_id).first()
        
        # Cache result
        if user:
            self.cache.set(cache_key, {
                "user_id": user.user_id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone_number": user.phone_number,
                "address": user.address,
                "city": user.city,
                "state": user.state,
                "zip_code": user.zip_code,
                "profile_image_url": user.profile_image_url,
                "credit_card_last_four": user.credit_card_last_four,
                "credit_card_type": user.credit_card_type,
                "is_active": user.is_active,
                "created_at": str(user.created_at),
                "updated_at": str(user.updated_at)
            })
        
        return user
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()
    
    def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """Update user information."""
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return None
        
        # Update fields
        update_data = user_data.model_dump(exclude_unset=True)
        
        # Handle credit card update
        if 'credit_card_number' in update_data:
            card_num = update_data.pop('credit_card_number')
            if card_num:
                user.credit_card_last_four = card_num[-4:]
        
        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        
        # Invalidate cache
        self.cache.delete(CacheKeys.user(user_id))
        
        # Publish event
        event_publisher.publish_user_event("updated", {
            "user_id": user.user_id,
            "updated_fields": list(update_data.keys())
        })
        
        logger.info(f"Updated user: {user_id}")
        return user
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return False
        
        # Soft delete - set inactive
        user.is_active = False
        self.db.commit()
        
        # Invalidate cache
        self.cache.delete(CacheKeys.user(user_id))
        
        # Publish event
        event_publisher.publish_user_event("deleted", {
            "user_id": user_id
        })
        
        logger.info(f"Deleted user: {user_id}")
        return True
    
    def list_users(
        self,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None
    ) -> List[User]:
        """List users with pagination and search."""
        query = self.db.query(User).filter(User.is_active == True)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    User.first_name.ilike(search_pattern),
                    User.last_name.ilike(search_pattern),
                    User.email.ilike(search_pattern)
                )
            )
        
        return query.offset(skip).limit(limit).all()
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        user = self.get_user_by_email(email)
        if not user:
            return None
        
        if not bcrypt_lib.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return None
        
        return user
    
    def get_user_bookings(
        self,
        user_id: str,
        booking_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[dict]:
        """Get user's booking history."""
        query = self.db.query(Booking).filter(Booking.user_id == user_id)
        
        if booking_type:
            query = query.filter(Booking.booking_type == booking_type)
        
        if status:
            query = query.filter(Booking.status == status)
        
        bookings = query.order_by(Booking.booking_date.desc()).all()
        
        return [
            {
                "booking_id": b.booking_id,
                "booking_type": b.booking_type.value if hasattr(b.booking_type, 'value') else b.booking_type,
                "listing_id": b.listing_id,
                "check_in_date": str(b.check_in_date),
                "check_out_date": str(b.check_out_date) if b.check_out_date else None,
                "status": b.status.value if hasattr(b.status, 'value') else b.status,
                "total_price": float(b.total_price),
                "booking_date": str(b.booking_date)
            }
            for b in bookings
        ]
    
    async def get_user_reviews(self, user_id: str) -> List[dict]:
        """Get reviews submitted by user (from MongoDB)."""
        from ...common.database import get_async_mongodb, MongoCollections
        
        db = get_async_mongodb()
        reviews = await db[MongoCollections.REVIEWS].find(
            {"user_id": user_id}
        ).to_list(100)
        
        return reviews

