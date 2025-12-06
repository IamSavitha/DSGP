"""
Deals Agent - Backend worker for discovering and processing travel deals.
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json

# Import database models and session
try:
    from backend.common.database import get_mysql_context
    from backend.models.mysql_models import Flight, Hotel, HotelRoom
except ImportError:
    # Fallback for local development
    import sys
    import os
    backend_path = os.path.join(os.path.dirname(__file__), '../../backend')
    if os.path.exists(backend_path):
        sys.path.insert(0, os.path.abspath(backend_path))
    from backend.common.database import get_mysql_context
    from backend.models.mysql_models import Flight, Hotel, HotelRoom

logger = logging.getLogger(__name__)


class DealsAgent:
    """
    Deals Agent - Backend worker that:
    - Ingests supplier feeds (CSV/mock data)
    - Detects deals using rules (price drops, limited inventory, promos)
    - Tags offers with metadata
    - Emits deal events via Kafka/WebSocket
    """
    
    def __init__(self):
        self.running = False
        self.producer: Optional[AIOKafkaProducer] = None
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.cached_deals: Dict[str, Any] = {}
        self.price_history: Dict[str, List[float]] = {}
        
        # Deal detection thresholds
        self.PRICE_DROP_THRESHOLD = 0.15  # 15% below average
        self.LIMITED_INVENTORY_THRESHOLD = 5
        self.DEAL_SCORE_WEIGHTS = {
            "price_drop": 40,
            "limited_inventory": 30,
            "promo": 20,
            "rating": 10
        }
    
    async def start_scheduled_scanning(self):
        """Start periodic deal scanning."""
        self.running = True
        logger.info("Starting deals agent scheduled scanning...")
        
        while self.running:
            try:
                await self.scan_for_deals()
                await asyncio.sleep(300)  # Scan every 5 minutes
            except Exception as e:
                logger.error(f"Error in deal scanning: {e}")
                await asyncio.sleep(60)
    
    async def stop(self):
        """Stop the deals agent."""
        self.running = False
        if self.producer:
            await self.producer.stop()
        if self.consumer:
            await self.consumer.stop()
    
    async def scan_for_deals(self):
        """Scan all listings for deals."""
        logger.info("Scanning for deals...")
        
        # Scan flights
        flight_deals = await self._scan_flight_deals()
        
        # Scan hotels
        hotel_deals = await self._scan_hotel_deals()
        
        # Process and emit deals
        all_deals = flight_deals + hotel_deals
        
        for deal in all_deals:
            # Normalize
            normalized = self._normalize_deal(deal)
            
            # Score
            scored = self._score_deal(normalized)
            
            # Tag
            tagged = self._tag_deal(scored)
            
            # Emit
            await self._emit_deal(tagged)
        
        logger.info(f"Found {len(all_deals)} potential deals")
    
    async def _scan_flight_deals(self) -> List[Dict]:
        """Scan flight listings for deals."""
        deals = []
        
        try:
            with get_mysql_context() as db:
                # Query active flights with available seats
                flights = db.query(Flight).filter(
                    Flight.is_active == True,
                    Flight.available_seats > 0,
                    Flight.departure_datetime >= datetime.now()  # Only future flights
                ).limit(100).all()
                
                for flight in flights:
                    current_price = float(flight.base_price)
                    # Estimate average price as 1.2x current price (simplified heuristic)
                    # In production, this would be calculated from historical data
                    avg_30d_price = current_price * 1.2
                    
                    flight_deal = {
                        "listing_id": flight.flight_id,
                        "listing_type": "flight",
                        "route": f"{flight.departure_airport}-{flight.arrival_airport}",
                        "airline": flight.airline_name,
                        "current_price": current_price,
                        "avg_30d_price": avg_30d_price,
                        "available_seats": flight.available_seats,
                        "departure_date": flight.departure_datetime.isoformat() if flight.departure_datetime else None,
                        "flight_class": flight.flight_class,
                        "rating": float(flight.rating) if flight.rating else 0.0
                    }
                    
                    # Check if it's a deal
                    if self._is_deal(flight_deal):
                        deals.append(flight_deal)
        except Exception as e:
            logger.error(f"Error scanning flight deals: {e}")
        
        return deals
    
    async def _scan_hotel_deals(self) -> List[Dict]:
        """Scan hotel listings for deals."""
        deals = []
        
        try:
            with get_mysql_context() as db:
                # Query active hotels with available rooms
                hotels = db.query(Hotel).filter(
                    Hotel.is_active == True
                ).limit(100).all()
                
                for hotel in hotels:
                    # Get total available rooms for this hotel
                    from sqlalchemy import func
                    total_available = db.query(func.sum(HotelRoom.available_rooms)).filter(
                        HotelRoom.hotel_id == hotel.hotel_id,
                        HotelRoom.is_active == True
                    ).scalar() or 0
                    
                    if total_available == 0:
                        continue
                    
                    # Get minimum price per night from rooms
                    min_price = db.query(func.min(HotelRoom.price_per_night)).filter(
                        HotelRoom.hotel_id == hotel.hotel_id,
                        HotelRoom.is_active == True
                    ).scalar() or 0
                    
                    if min_price == 0:
                        continue
                    
                    current_price = float(min_price)
                    # Estimate average price as 1.25x current price (simplified heuristic)
                    avg_30d_price = current_price * 1.25
                    
                    # Parse amenities
                    amenities_list = []
                    if hotel.amenities:
                        amenities_list = [a.strip() for a in hotel.amenities.split(',')]
                    
                    hotel_deal = {
                        "listing_id": hotel.hotel_id,
                        "listing_type": "hotel",
                        "name": hotel.hotel_name,
                        "city": hotel.city,
                        "current_price": current_price,
                        "avg_30d_price": avg_30d_price,
                        "available_rooms": int(total_available),
                        "amenities": amenities_list,
                        "pet_friendly": "pet" in hotel.amenities.lower() if hotel.amenities else False,
                        "refundable": True,  # Assume refundable by default
                        "star_rating": hotel.star_rating or 0,
                        "rating": float(hotel.rating) if hotel.rating else 0.0
                    }
                    
                    # Check if it's a deal
                    if self._is_deal(hotel_deal):
                        deals.append(hotel_deal)
        except Exception as e:
            logger.error(f"Error scanning hotel deals: {e}")
        
        return deals
    
    def _is_deal(self, listing: Dict) -> bool:
        """Determine if a listing qualifies as a deal."""
        current_price = listing.get("current_price", 0)
        avg_price = listing.get("avg_30d_price", current_price)
        
        # Price drop check
        if avg_price > 0:
            price_drop = (avg_price - current_price) / avg_price
            if price_drop >= self.PRICE_DROP_THRESHOLD:
                return True
        
        # Limited inventory check
        availability = listing.get("available_seats", listing.get("available_rooms", 100))
        if availability <= self.LIMITED_INVENTORY_THRESHOLD:
            return True
        
        return False
    
    def _normalize_deal(self, deal: Dict) -> Dict:
        """Normalize deal data."""
        return {
            **deal,
            "normalized_at": datetime.utcnow().isoformat(),
            "currency": "USD",
            "price_per_unit": deal.get("current_price", 0)
        }
    
    def _score_deal(self, deal: Dict) -> Dict:
        """Calculate deal score (0-100)."""
        score = 0
        
        # Price drop score
        current = deal.get("current_price", 0)
        avg = deal.get("avg_30d_price", current)
        if avg > 0 and current > 0:
            drop_pct = (avg - current) / avg
            # Scale price drop score (max 40 points)
            price_score = min(drop_pct * 100, self.DEAL_SCORE_WEIGHTS["price_drop"])
            score += price_score
        
        # Limited inventory score
        availability = deal.get("available_seats", deal.get("available_rooms", 100))
        if availability <= self.LIMITED_INVENTORY_THRESHOLD:
            inventory_score = (self.LIMITED_INVENTORY_THRESHOLD - availability + 1) * 6
            score += min(inventory_score, self.DEAL_SCORE_WEIGHTS["limited_inventory"])
        
        # Rating score (if available)
        rating = deal.get("rating", 0)
        if rating > 0:
            rating_score = (rating / 5.0) * self.DEAL_SCORE_WEIGHTS["rating"]
            score += rating_score
        
        return {
            **deal,
            "deal_score": round(score, 1)
        }
    
    def _tag_deal(self, deal: Dict) -> Dict:
        """Add tags to deal based on metadata."""
        tags = []
        
        # Price tags
        current = deal.get("current_price", 0)
        avg = deal.get("avg_30d_price", current)
        if avg > 0:
            drop_pct = (avg - current) / avg
            if drop_pct >= 0.25:
                tags.append("Hot Deal")
            elif drop_pct >= 0.15:
                tags.append("Good Price")
        
        # Availability tags
        availability = deal.get("available_seats", deal.get("available_rooms", 100))
        if availability <= 3:
            tags.append("Almost Gone")
        elif availability <= 5:
            tags.append("Limited Availability")
        
        # Amenity tags
        amenities = deal.get("amenities", [])
        if "breakfast" in amenities:
            tags.append("Breakfast Included")
        if deal.get("pet_friendly"):
            tags.append("Pet-Friendly")
        if deal.get("refundable"):
            tags.append("Refundable")
        
        return {
            **deal,
            "tags": tags,
            "tagged_at": datetime.utcnow().isoformat()
        }
    
    async def _emit_deal(self, deal: Dict):
        """Emit deal event."""
        # Store in cache
        self.cached_deals[deal["listing_id"]] = deal
        
        # In production, emit to Kafka
        logger.debug(f"Emitting deal: {deal['listing_id']} - Score: {deal.get('deal_score')}")
    
    def get_cached_deals(self, listing_type: Optional[str] = None) -> List[Dict]:
        """Get cached deals, optionally filtered by type."""
        deals = list(self.cached_deals.values())
        
        if listing_type:
            deals = [d for d in deals if d.get("listing_type") == listing_type]
        
        # Sort by score
        deals.sort(key=lambda x: x.get("deal_score", 0), reverse=True)
        
        return deals

