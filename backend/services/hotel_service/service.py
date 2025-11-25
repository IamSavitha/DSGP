"""
Hotel Service - Business logic for hotel operations.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import math
import logging

from ...models.mysql_models import Hotel, HotelRoom
from ...schemas.hotel_schemas import (
    HotelCreate, HotelUpdate, HotelSearchParams, 
    HotelSearchResponse, HotelResponse
)
from ...common.cache import RedisCache, CacheKeys

logger = logging.getLogger(__name__)


class HotelService:
    """Service class for hotel operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.cache = RedisCache()
    
    def create_hotel(self, hotel_data: HotelCreate) -> Hotel:
        """Create a new hotel."""
        hotel = Hotel(
            hotel_id=hotel_data.hotel_id,
            hotel_name=hotel_data.hotel_name,
            description=hotel_data.description,
            address=hotel_data.address,
            city=hotel_data.city,
            state=hotel_data.state,
            zip_code=hotel_data.zip_code,
            star_rating=hotel_data.star_rating,
            amenities=hotel_data.amenities,
            phone_number=hotel_data.phone_number,
            email=hotel_data.email,
            website=hotel_data.website
        )
        
        self.db.add(hotel)
        self.db.commit()
        self.db.refresh(hotel)
        
        logger.info(f"Created hotel: {hotel.hotel_id}")
        return hotel
    
    def get_hotel(self, hotel_id: str) -> Optional[Hotel]:
        """Get hotel by ID."""
        return self.db.query(Hotel).filter(Hotel.hotel_id == hotel_id).first()
    
    def update_hotel(self, hotel_id: str, hotel_data: HotelUpdate) -> Optional[Hotel]:
        """Update hotel information."""
        hotel = self.db.query(Hotel).filter(Hotel.hotel_id == hotel_id).first()
        if not hotel:
            return None
        
        update_data = hotel_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(hotel, field):
                setattr(hotel, field, value)
        
        self.db.commit()
        self.db.refresh(hotel)
        self.cache.delete(CacheKeys.hotel(hotel_id))
        
        return hotel
    
    def delete_hotel(self, hotel_id: str) -> bool:
        """Delete a hotel (soft delete)."""
        hotel = self.db.query(Hotel).filter(Hotel.hotel_id == hotel_id).first()
        if not hotel:
            return False
        
        hotel.is_active = False
        self.db.commit()
        self.cache.delete(CacheKeys.hotel(hotel_id))
        
        return True
    
    def search_hotels(self, params: HotelSearchParams) -> HotelSearchResponse:
        """Search hotels with filters."""
        query = self.db.query(Hotel).filter(Hotel.is_active == True)
        
        if params.city:
            query = query.filter(Hotel.city.ilike(f"%{params.city}%"))
        
        if params.state:
            query = query.filter(Hotel.state == params.state.upper())
        
        if params.min_star_rating:
            query = query.filter(Hotel.star_rating >= params.min_star_rating)
        
        if params.max_star_rating:
            query = query.filter(Hotel.star_rating <= params.max_star_rating)
        
        if params.amenities:
            for amenity in params.amenities:
                query = query.filter(Hotel.amenities.ilike(f"%{amenity}%"))
        
        total_count = query.count()
        
        # Sorting
        if params.sort_by == "rating":
            order_col = Hotel.rating
        elif params.sort_by == "stars":
            order_col = Hotel.star_rating
        else:
            order_col = Hotel.hotel_name
        
        if params.sort_order == "desc":
            query = query.order_by(order_col.desc())
        else:
            query = query.order_by(order_col.asc())
        
        offset = (params.page - 1) * params.page_size
        hotels = query.offset(offset).limit(params.page_size).all()
        
        return HotelSearchResponse(
            hotels=[HotelResponse.model_validate(h) for h in hotels],
            total_count=total_count,
            page=params.page,
            page_size=params.page_size,
            total_pages=math.ceil(total_count / params.page_size) if total_count > 0 else 1,
            filters_applied=params.model_dump(exclude_none=True)
        )

