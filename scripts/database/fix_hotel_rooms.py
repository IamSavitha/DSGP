#!/usr/bin/env python3
"""
Fix Hotel Rooms Script
Ensures all hotels have at least one active room with available rooms.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from decimal import Decimal
import random

from backend.common.database import SessionLocal
from backend.models.mysql_models import Hotel, HotelRoom, RoomType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fix_hotel_rooms():
    """Ensure all hotels have at least one active room."""
    db = SessionLocal()
    
    try:
        # Get all hotels
        hotels = db.query(Hotel).filter(Hotel.is_active == True).all()
        logger.info(f"Found {len(hotels)} active hotels")
        
        fixed_count = 0
        created_count = 0
        
        for hotel in hotels:
            # Check if hotel has any active rooms with availability
            active_rooms = db.query(HotelRoom).filter(
                HotelRoom.hotel_id == hotel.hotel_id,
                HotelRoom.is_active == True,
                HotelRoom.available_rooms > 0
            ).count()
            
            if active_rooms == 0:
                logger.info(f"Hotel {hotel.hotel_id} ({hotel.hotel_name}) has no available rooms. Creating rooms...")
                
                # Create 2-3 room types for this hotel
                room_types = random.sample(
                    [RoomType.SINGLE, RoomType.DOUBLE, RoomType.SUITE, RoomType.DELUXE],
                    random.randint(2, 3)
                )
                
                for room_type in room_types:
                    price_multiplier = {
                        RoomType.SINGLE: 0.8,
                        RoomType.DOUBLE: 1.0,
                        RoomType.DELUXE: 1.5,
                        RoomType.SUITE: 2.0
                    }
                    
                    base_price = Decimal(random.randint(80, 200)) * Decimal(price_multiplier[room_type])
                    
                    # Check if room type already exists
                    existing = db.query(HotelRoom).filter(
                        HotelRoom.hotel_id == hotel.hotel_id,
                        HotelRoom.room_type == room_type.value
                    ).first()
                    
                    if existing:
                        # Update existing room to be active and available
                        existing.is_active = True
                        existing.available_rooms = random.randint(3, 10)
                        existing.price_per_night = base_price
                        logger.info(f"  Updated room {existing.room_id} ({room_type.value})")
                        fixed_count += 1
                    else:
                        # Create new room
                        room = HotelRoom(
                            room_id=f"{hotel.hotel_id}-{room_type.value}-{random.randint(1, 999)}",
                            hotel_id=hotel.hotel_id,
                            room_type=room_type.value,
                            room_number=f"{random.randint(100, 999)}",
                            price_per_night=base_price,
                            max_occupancy=random.choice([2, 4, 6]),
                            total_rooms=random.randint(5, 20),
                            available_rooms=random.randint(3, 10),
                            is_active=True
                        )
                        db.add(room)
                        logger.info(f"  Created room {room.room_id} ({room_type.value})")
                        created_count += 1
                
                db.commit()
        
        logger.info(f"✅ Fixed {fixed_count} existing rooms and created {created_count} new rooms")
        
        # Verify all hotels have rooms
        hotels_without_rooms = db.query(Hotel).filter(
            Hotel.is_active == True,
            ~Hotel.hotel_id.in_(
                db.query(HotelRoom.hotel_id).filter(
                    HotelRoom.is_active == True,
                    HotelRoom.available_rooms > 0
                ).distinct()
            )
        ).count()
        
        if hotels_without_rooms == 0:
            logger.info("✅ All hotels now have available rooms!")
        else:
            logger.warning(f"⚠️  {hotels_without_rooms} hotels still don't have available rooms")
        
    except Exception as e:
        logger.error(f"Error fixing hotel rooms: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    fix_hotel_rooms()

