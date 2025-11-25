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
        
        # In production, this would query the flight database
        # For now, return mock deals
        mock_flights = [
            {
                "listing_id": "AA123",
                "listing_type": "flight",
                "route": "SFO-JFK",
                "airline": "American Airlines",
                "current_price": 249.00,
                "avg_30d_price": 320.00,
                "available_seats": 3,
                "departure_date": (datetime.now() + timedelta(days=14)).isoformat()
            },
            {
                "listing_id": "UA456",
                "listing_type": "flight",
                "route": "LAX-ORD",
                "airline": "United Airlines",
                "current_price": 189.00,
                "avg_30d_price": 210.00,
                "available_seats": 12,
                "departure_date": (datetime.now() + timedelta(days=7)).isoformat()
            }
        ]
        
        for flight in mock_flights:
            # Check if it's a deal
            if self._is_deal(flight):
                deals.append(flight)
        
        return deals
    
    async def _scan_hotel_deals(self) -> List[Dict]:
        """Scan hotel listings for deals."""
        deals = []
        
        mock_hotels = [
            {
                "listing_id": "HTL-001",
                "listing_type": "hotel",
                "name": "Grand Plaza Hotel",
                "city": "San Francisco",
                "current_price": 159.00,
                "avg_30d_price": 220.00,
                "available_rooms": 2,
                "amenities": ["wifi", "breakfast", "parking"],
                "pet_friendly": True,
                "refundable": True
            },
            {
                "listing_id": "HTL-002",
                "listing_type": "hotel",
                "name": "Downtown Suites",
                "city": "New York",
                "current_price": 299.00,
                "avg_30d_price": 350.00,
                "available_rooms": 8,
                "amenities": ["wifi", "gym", "pool"],
                "pet_friendly": False,
                "refundable": True
            }
        ]
        
        for hotel in mock_hotels:
            if self._is_deal(hotel):
                deals.append(hotel)
        
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
        if avg > 0:
            drop_pct = (avg - current) / avg
            score += min(drop_pct * 100, self.DEAL_SCORE_WEIGHTS["price_drop"])
        
        # Limited inventory score
        availability = deal.get("available_seats", deal.get("available_rooms", 100))
        if availability <= self.LIMITED_INVENTORY_THRESHOLD:
            inventory_score = (self.LIMITED_INVENTORY_THRESHOLD - availability + 1) * 6
            score += min(inventory_score, self.DEAL_SCORE_WEIGHTS["limited_inventory"])
        
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

