"""
Search Service - Business logic for unified search across all services.
"""
import httpx
import logging
from typing import Optional, Dict, List, Any
from datetime import date
from decimal import Decimal

from ...common.config import settings
from ...common.cache import RedisCache, CacheKeys, generate_cache_key

logger = logging.getLogger(__name__)


class UnifiedSearchService:
    """Service for unified search across flights, hotels, and cars."""
    
    def __init__(self):
        self.cache = RedisCache()
        self.timeout = 10.0  # 10 second timeout for service calls
    
    async def unified_search(
        self,
        query: Optional[str] = None,
        search_type: Optional[str] = None,  # "flight", "hotel", "car", or None for all
        city: Optional[str] = None,
        check_in: Optional[date] = None,
        check_out: Optional[date] = None,
        departure_airport: Optional[str] = None,
        arrival_airport: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Perform unified search across flights, hotels, and cars."""
        
        # Generate cache key
        cache_params = {
            "query": query,
            "search_type": search_type,
            "city": city,
            "check_in": str(check_in) if check_in else None,
            "check_out": str(check_out) if check_out else None,
            "departure_airport": departure_airport,
            "arrival_airport": arrival_airport,
            "min_price": min_price,
            "max_price": max_price,
            "page": page,
            "page_size": page_size
        }
        
        cache_key = f"unified_search:{generate_cache_key(**cache_params)}"
        
        # Check cache
        cached = self.cache.get(cache_key)
        if cached:
            logger.debug("Cache hit for unified search")
            return cached
        
        results = {
            "flights": [],
            "hotels": [],
            "cars": [],
            "total_results": 0,
            "query": query,
            "filters": cache_params
        }
        
        # Search flights
        if not search_type or search_type == "flight":
            flights = await self._search_flights(
                departure_airport=departure_airport,
                arrival_airport=arrival_airport,
                departure_date=check_in,
                min_price=min_price,
                max_price=max_price,
                page=page,
                page_size=page_size
            )
            results["flights"] = flights.get("flights", [])
        
        # Search hotels
        if not search_type or search_type == "hotel":
            hotels = await self._search_hotels(
                city=city,
                check_in=check_in,
                check_out=check_out,
                min_price=min_price,
                max_price=max_price,
                page=page,
                page_size=page_size
            )
            results["hotels"] = hotels.get("hotels", [])
        
        # Search cars
        if not search_type or search_type == "car":
            cars = await self._search_cars(
                city=city,
                check_in=check_in,
                check_out=check_out,
                min_price=min_price,
                max_price=max_price,
                page=page,
                page_size=page_size
            )
            results["cars"] = cars.get("cars", [])
        
        # Calculate total results
        results["total_results"] = (
            len(results["flights"]) +
            len(results["hotels"]) +
            len(results["cars"])
        )
        
        # Cache results (5 minutes)
        self.cache.set(cache_key, results, ttl=300)
        
        return results
    
    async def _search_flights(
        self,
        departure_airport: Optional[str] = None,
        arrival_airport: Optional[str] = None,
        departure_date: Optional[date] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Search flights by calling flight service."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {
                    "page": page,
                    "page_size": page_size
                }
                
                if departure_airport:
                    params["departure_airport"] = departure_airport
                if arrival_airport:
                    params["arrival_airport"] = arrival_airport
                if departure_date:
                    params["departure_date"] = str(departure_date)
                if min_price:
                    params["min_price"] = min_price
                if max_price:
                    params["max_price"] = max_price
                
                response = await client.get(
                    f"{settings.FLIGHT_SERVICE_URL}/flights/search",
                    params=params
                )
                response.raise_for_status()
                return response.json()
        
        except Exception as e:
            logger.error(f"Error searching flights: {e}")
            return {"flights": [], "total_count": 0}
    
    async def _search_hotels(
        self,
        city: Optional[str] = None,
        check_in: Optional[date] = None,
        check_out: Optional[date] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Search hotels by calling hotel service."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {
                    "page": page,
                    "page_size": page_size
                }
                
                if city:
                    params["city"] = city
                if min_price:
                    params["min_price"] = min_price
                if max_price:
                    params["max_price"] = max_price
                
                response = await client.get(
                    f"{settings.HOTEL_SERVICE_URL}/hotels/search",
                    params=params
                )
                response.raise_for_status()
                return response.json()
        
        except Exception as e:
            logger.error(f"Error searching hotels: {e}")
            return {"hotels": [], "total_count": 0}
    
    async def _search_cars(
        self,
        city: Optional[str] = None,
        check_in: Optional[date] = None,
        check_out: Optional[date] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Search cars by calling car service."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {
                    "page": page,
                    "page_size": page_size
                }
                
                if city:
                    params["city"] = city
                if min_price:
                    params["min_price"] = min_price
                if max_price:
                    params["max_price"] = max_price
                
                response = await client.get(
                    f"{settings.CAR_SERVICE_URL}/cars/search",
                    params=params
                )
                response.raise_for_status()
                return response.json()
        
        except Exception as e:
            logger.error(f"Error searching cars: {e}")
            return {"cars": [], "total_count": 0}

