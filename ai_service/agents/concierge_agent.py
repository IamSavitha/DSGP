"""
Concierge Agent - Chat-facing agent for personalized travel recommendations.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import re
import uuid

logger = logging.getLogger(__name__)


class ConciergeAgent:
    """
    Concierge Agent - Chat-facing agent that:
    - Understands user intent and constraints
    - Builds flight + hotel bundles from cached deals
    - Explains recommendations with tradeoffs
    - Sets price/inventory watches
    """
    
    def __init__(self):
        self.watches: Dict[str, Dict] = {}
        self.session_contexts: Dict[str, Dict] = {}
    
    async def process_message(
        self,
        message: str,
        user_id: Optional[str] = None,
        context: Dict = None
    ) -> Dict[str, Any]:
        """
        Process a user message and generate response.
        
        Args:
            message: User's natural language message
            user_id: Optional user ID for personalization
            context: Session context from previous interactions
        
        Returns:
            Response with message, bundles, and updated context
        """
        context = context or {}
        
        # Parse intent and constraints
        intent = self._parse_intent(message)
        constraints = self._extract_constraints(message, context)
        
        # Update context with new constraints
        context.update(constraints)
        
        # Check if clarification is needed
        if self._needs_clarification(intent, context):
            return {
                "message": self._generate_clarification(intent, context),
                "clarification_needed": True,
                "context": context
            }
        
        # Generate response based on intent
        if intent == "flight_query":
            flight_response = await self._handle_flight_query(message, context)
            return {
                "message": flight_response,
                "context": context
            }
        
        elif intent == "search":
            bundles = await self._find_bundles(context)
            return {
                "message": self._format_bundle_response(bundles, context),
                "bundles": bundles,
                "context": context
            }
        
        elif intent == "refine":
            bundles = await self._find_bundles(context)
            return {
                "message": self._format_refinement_response(bundles, context),
                "bundles": bundles,
                "context": context
            }
        
        elif intent == "watch":
            watch_info = self._extract_watch_params(message, context)
            return {
                "message": f"I'll keep an eye on that for you! I'll alert you if the price drops below ${watch_info.get('price_threshold', 'your threshold')} or if inventory gets low.",
                "watch_request": watch_info,
                "context": context
            }
        
        elif intent == "compare":
            comparison = self._generate_comparison(message, context)
            return {
                "message": comparison,
                "context": context
            }
        
        elif intent == "policy":
            policy_info = self._get_policy_info(message, context)
            return {
                "message": policy_info,
                "context": context
            }
        
        else:
            return {
                "message": "I'd be happy to help you find the perfect trip! Tell me where you'd like to go, your dates, and budget, and I'll find the best options for you.",
                "context": context
            }
    
    def _parse_intent(self, message: str) -> str:
        """Parse user intent from message."""
        message_lower = message.lower()
        message_upper = message.upper()
        
        # Common airport codes
        airport_codes = ["SFO", "NYC", "JFK", "LAX", "MIA", "ORD", "BOS", "SEA", "DEN", "ATL", "PHX", "LAS", "DFW", "LGA", "EWR", "IAH", "CLT"]
        has_airport_code = any(re.search(r'\b' + re.escape(code) + r'\b', message_upper) for code in airport_codes)
        
        # Check for route patterns (X to Y, from X to Y, X-Y)
        has_route_pattern = bool(re.search(r'[A-Z]{3}\s+(?:to|from)\s+[A-Z]{3}', message_upper) or 
                                 re.search(r'from\s+[A-Z]{3}\s+to\s+[A-Z]{3}', message_upper) or
                                 re.search(r'[A-Z]{3}-[A-Z]{3}', message_upper))
        
        # Check for flight-specific queries (highest priority)
        if any(word in message_lower for word in ["flight", "flights", "fly"]):
            return "flight_query"
        
        if any(phrase in message_lower for phrase in ["how many", "count", "number of", "total"]):
            if has_airport_code or has_route_pattern:
                return "flight_query"
        
        if has_route_pattern:
            return "flight_query"
        
        if has_airport_code and any(word in message_lower for word in ["to", "from", "on", "dec", "december", "jan", "january"]):
            return "flight_query"
        
        if any(word in message_lower for word in ["track", "watch", "alert", "notify"]):
            return "watch"
        
        if any(word in message_lower for word in ["compare", "vs", "versus", "difference"]):
            return "compare"
        
        if any(word in message_lower for word in ["refund", "cancel", "policy", "pet", "parking"]):
            return "policy"
        
        if any(word in message_lower for word in ["make it", "change", "instead", "but", "without"]):
            return "refine"
        
        if any(word in message_lower for word in ["find", "search", "book", "trip", "travel", "stay", "looking for"]):
            return "search"
        
        return "general"
    
    def _extract_constraints(self, message: str, context: Dict) -> Dict:
        """Extract travel constraints from message."""
        constraints = {}
        message_lower = message.lower()
        message_upper = message.upper()
        
        # Airport code to city mapping
        airport_to_city = {
            "SFO": "San Francisco", "NYC": "New York", "JFK": "New York", "LGA": "New York", "EWR": "New York",
            "LAX": "Los Angeles", "MIA": "Miami", "ORD": "Chicago", "BOS": "Boston",
            "SEA": "Seattle", "DEN": "Denver", "ATL": "Atlanta", "PHX": "Phoenix",
            "LAS": "Las Vegas", "DFW": "Dallas", "IAH": "Houston", "CLT": "Charlotte"
        }
        
        # Common airport codes (3 letters)
        airport_codes = ["SFO", "NYC", "JFK", "LAX", "MIA", "ORD", "BOS", "SEA", "DEN", "ATL", "PHX", "LAS", "DFW", "IAH", "CLT", "LGA", "EWR"]
        
        # Extract airport codes from message
        found_airports = []
        for code in airport_codes:
            if code in message_upper:
                # Make sure it's a standalone code (not part of another word)
                pattern = r'\b' + re.escape(code) + r'\b'
                if re.search(pattern, message_upper):
                    found_airports.append(code)
                    # Map to city name
                    if code in airport_to_city:
                        city = airport_to_city[code]
                        if code in ["JFK", "LGA", "EWR"]:
                            city = "New York"  # All NYC airports map to New York
        
        # Extract route pattern: "X to Y" or "from X to Y" or "X-Y"
        route_patterns = [
            r'from\s+([A-Z]{3})\s+to\s+([A-Z]{3})',
            r'([A-Z]{3})\s+to\s+([A-Z]{3})',
            r'([A-Z]{3})-([A-Z]{3})',
        ]
        
        for pattern in route_patterns:
            match = re.search(pattern, message_upper)
            if match:
                departure = match.group(1)
                arrival = match.group(2)
                constraints["departure_airport"] = departure
                constraints["arrival_airport"] = arrival
                if departure in airport_to_city:
                    constraints["origin"] = airport_to_city[departure]
                if arrival in airport_to_city:
                    constraints["destination"] = airport_to_city[arrival]
                break
        
        # If no route pattern found, try to extract airports individually
        if not constraints.get("departure_airport") and len(found_airports) >= 2:
            constraints["departure_airport"] = found_airports[0]
            constraints["arrival_airport"] = found_airports[1]
            if found_airports[0] in airport_to_city:
                constraints["origin"] = airport_to_city[found_airports[0]]
            if found_airports[1] in airport_to_city:
                constraints["destination"] = airport_to_city[found_airports[1]]
        elif len(found_airports) == 1:
            # Single airport - could be origin or destination
            if "from" in message_lower:
                constraints["departure_airport"] = found_airports[0]
                if found_airports[0] in airport_to_city:
                    constraints["origin"] = airport_to_city[found_airports[0]]
            else:
                constraints["arrival_airport"] = found_airports[0]
                if found_airports[0] in airport_to_city:
                    constraints["destination"] = airport_to_city[found_airports[0]]
        
        # Budget extraction
        budget_match = re.search(r'\$?(\d{1,5}(?:,\d{3})?(?:\.\d{2})?)', message)
        if budget_match:
            constraints["budget"] = float(budget_match.group(1).replace(',', ''))
        
        # Enhanced date extraction
        date_patterns = [
            r'(dec\s+\d{1,2})', r'(december\s+\d{1,2})',
            r'(jan\s+\d{1,2})', r'(january\s+\d{1,2})',
            r'(feb\s+\d{1,2})', r'(february\s+\d{1,2})',
            r'(\d{1,2}/\d{1,2})',
            r'(\d{4}-\d{2}-\d{2})',
        ]
        for pattern in date_patterns:
            match = re.search(pattern, message_lower if "dec" in pattern or "jan" in pattern or "feb" in pattern else message)
            if match:
                constraints["dates"] = match.group(1)
                break
        
        # Destination extraction (city names)
        cities = ["tokyo", "miami", "new york", "san francisco", "los angeles", 
                  "chicago", "seattle", "boston", "denver", "austin", "atlanta",
                  "phoenix", "las vegas", "dallas", "houston"]
        for city in cities:
            if city in message_lower:
                if not constraints.get("destination"):
                    constraints["destination"] = city.title()
                break
        
        # Origin extraction
        if "from" in message_lower:
            for city in cities:
                if f"from {city}" in message_lower:
                    if not constraints.get("origin"):
                        constraints["origin"] = city.title()
                    break
        
        # Preferences
        if "pet" in message_lower or "dog" in message_lower or "cat" in message_lower:
            constraints["pet_friendly"] = True
        
        if "red-eye" in message_lower:
            if "no" in message_lower or "avoid" in message_lower:
                constraints["no_red_eye"] = True
        
        if "refund" in message_lower:
            constraints["refundable"] = True
        
        # Number of travelers
        travelers_match = re.search(r'(\d+)\s*(?:people|travelers|guests|of us)', message_lower)
        if travelers_match:
            constraints["num_travelers"] = int(travelers_match.group(1))
        elif "two" in message_lower or "couple" in message_lower:
            constraints["num_travelers"] = 2
        
        return constraints
    
    def _needs_clarification(self, intent: str, context: Dict) -> bool:
        """Check if we need to ask for clarification."""
        if intent == "flight_query":
            # For flight queries, need at least one airport
            if not context.get("departure_airport") and not context.get("arrival_airport"):
                return True
            return False
        
        if intent in ["search", "refine"]:
            # Need at least destination, origin, or airport codes
            if (not context.get("destination") and not context.get("origin") and 
                not context.get("departure_airport") and not context.get("arrival_airport")):
                return True
        return False
    
    def _generate_clarification(self, intent: str, context: Dict) -> str:
        """Generate a clarification question."""
        if intent == "flight_query":
            if not context.get("departure_airport") and not context.get("arrival_airport"):
                return "I can help you find flights! Please tell me your route, for example: 'flights from SFO to NYC' or 'how many flights from LAX to MIA'."
            if not context.get("departure_airport"):
                return f"I see you want to go to {context.get('arrival_airport', 'your destination')}. Where are you departing from?"
            if not context.get("arrival_airport"):
                return f"I see you're departing from {context.get('departure_airport')}. Where would you like to go?"
        
        if not context.get("destination") and not context.get("arrival_airport"):
            return "Where would you like to go? I can find great deals to popular destinations! You can use airport codes like SFO, NYC, LAX, or city names."
        
        if not context.get("dates"):
            dest = context.get("destination") or context.get("arrival_airport") or "your destination"
            return f"When are you thinking of traveling to {dest}?"
        
        if not context.get("budget"):
            return "What's your budget for this trip? This helps me find the best options for you."
        
        return "Could you tell me more about what you're looking for?"
    
    async def _find_bundles(self, context: Dict) -> List[Dict]:
        """Find flight + hotel bundles matching constraints."""
        # In production, this would query the deals cache and databases
        
        budget = context.get("budget", 1500)
        destination = context.get("destination", "Miami")
        
        # Mock bundles
        bundles = [
            {
                "bundle_id": f"BDL-{uuid.uuid4().hex[:6].upper()}",
                "flight": {
                    "id": "AA789",
                    "airline": "American Airlines",
                    "route": f"SFO-{destination[:3].upper()}",
                    "price": 299,
                    "departure": "8:00 AM",
                    "duration": "5h 30m"
                },
                "hotel": {
                    "id": "HTL-001",
                    "name": f"{destination} Beach Resort",
                    "stars": 4,
                    "price_per_night": 180,
                    "amenities": ["Pool", "Beach Access", "Breakfast"]
                },
                "total_price": 659,
                "fit_score": 85,
                "why_this": f"Best value for {destination} - 18% below average with 4-star beachfront hotel",
                "what_to_watch": "Price may increase closer to dates; 4 rooms left"
            },
            {
                "bundle_id": f"BDL-{uuid.uuid4().hex[:6].upper()}",
                "flight": {
                    "id": "UA456",
                    "airline": "United Airlines",
                    "route": f"SFO-{destination[:3].upper()}",
                    "price": 349,
                    "departure": "11:30 AM",
                    "duration": "5h 15m"
                },
                "hotel": {
                    "id": "HTL-002",
                    "name": f"The {destination} Grand",
                    "stars": 5,
                    "price_per_night": 250,
                    "amenities": ["Spa", "Fine Dining", "Concierge"]
                },
                "total_price": 849,
                "fit_score": 78,
                "why_this": "Premium experience with luxury hotel and flexible flight time",
                "what_to_watch": "Refundable until 48h before; check-in at 3 PM"
            }
        ]
        
        # Filter by budget
        bundles = [b for b in bundles if b["total_price"] <= budget]
        
        # Sort by fit score
        bundles.sort(key=lambda x: x["fit_score"], reverse=True)
        
        return bundles[:3]
    
    def _format_bundle_response(self, bundles: List[Dict], context: Dict) -> str:
        """Format bundles into a readable response."""
        if not bundles:
            return "I couldn't find any bundles matching your criteria. Would you like to adjust your budget or dates?"
        
        destination = context.get("destination", "your destination")
        
        response = f"I found {len(bundles)} great options for {destination}:\n\n"
        
        for i, bundle in enumerate(bundles, 1):
            response += f"**Option {i}: ${bundle['total_price']}** (Fit Score: {bundle['fit_score']}/100)\n"
            response += f"✈️ {bundle['flight']['airline']} - {bundle['flight']['departure']} ({bundle['flight']['duration']})\n"
            response += f"🏨 {bundle['hotel']['name']} ({'⭐' * bundle['hotel']['stars']})\n"
            response += f"💡 {bundle['why_this']}\n"
            response += f"⚠️ {bundle['what_to_watch']}\n\n"
        
        return response
    
    def _format_refinement_response(self, bundles: List[Dict], context: Dict) -> str:
        """Format response for refined search."""
        if not bundles:
            return "With those additional requirements, I couldn't find matching options. Would you like me to relax some constraints?"
        
        response = "Based on your updated preferences, here are the refined options:\n\n"
        response += self._format_bundle_response(bundles, context)
        
        return response
    
    def _extract_watch_params(self, message: str, context: Dict) -> Dict:
        """Extract watch parameters from message."""
        params = {
            "listing_id": context.get("last_viewed_listing"),
            "price_threshold": context.get("budget", 800) * 0.9,  # 10% below budget
            "inventory_threshold": 5
        }
        
        # Extract specific thresholds
        price_match = re.search(r'below\s+\$?(\d+)', message.lower())
        if price_match:
            params["price_threshold"] = float(price_match.group(1))
        
        inventory_match = re.search(r'under\s+(\d+)\s+(?:rooms?|seats?)', message.lower())
        if inventory_match:
            params["inventory_threshold"] = int(inventory_match.group(1))
        
        return params
    
    def _generate_comparison(self, message: str, context: Dict) -> str:
        """Generate comparison between options."""
        return """Here's how they compare:

| Feature | Option 1 | Option 2 |
|---------|----------|----------|
| Total Price | $659 | $849 |
| Flight Time | 8:00 AM | 11:30 AM |
| Hotel Rating | 4 stars | 5 stars |
| Cancellation | Non-refundable | Refundable |

**Bottom line**: Option 1 saves you $190 but Option 2 gives you more flexibility and luxury amenities."""
    
    def _get_policy_info(self, message: str, context: Dict) -> str:
        """Get policy information for a listing."""
        if "refund" in message.lower() or "cancel" in message.lower():
            return "**Cancellation Policy**: Free cancellation until 48 hours before check-in. After that, the first night is non-refundable."
        
        if "pet" in message.lower():
            return "**Pet Policy**: Pets are welcome! There's a $50 per stay pet fee. Maximum 2 pets per room."
        
        if "parking" in message.lower():
            return "**Parking**: Self-parking is $25/night. Valet parking is $40/night. Electric vehicle charging available."
        
        return "What specific policy would you like to know about? I can help with cancellation, pets, parking, and more."
    
    async def create_watch(
        self,
        user_id: str,
        listing_id: str,
        price_threshold: float = None,
        inventory_threshold: int = None
    ) -> str:
        """Create a price/inventory watch."""
        watch_id = f"WATCH-{uuid.uuid4().hex[:8].upper()}"
        
        self.watches[watch_id] = {
            "user_id": user_id,
            "listing_id": listing_id,
            "price_threshold": price_threshold,
            "inventory_threshold": inventory_threshold,
            "created_at": datetime.utcnow().isoformat(),
            "active": True
        }
        
        logger.info(f"Created watch {watch_id} for user {user_id}")
        return watch_id
    
    async def remove_watch(self, watch_id: str):
        """Remove a watch."""
        if watch_id in self.watches:
            self.watches[watch_id]["active"] = False
            logger.info(f"Removed watch {watch_id}")
    
    async def _handle_flight_query(self, message: str, context: Dict) -> str:
        """Handle flight-specific queries like 'how many flights from X to Y'."""
        import sys
        import os
        
        # Import backend modules for database access
        backend_path = os.path.join(os.path.dirname(__file__), '../../backend')
        if os.path.exists(backend_path):
            sys.path.insert(0, os.path.abspath(backend_path))
        
        try:
            from backend.common.database import get_mysql_context
            from backend.models.mysql_models import Flight
            
            departure_airport = context.get("departure_airport")
            arrival_airport = context.get("arrival_airport")
            
            message_lower = message.lower()
            is_count_query = any(word in message_lower for word in ["how many", "count", "number of", "total"])
            
            if not departure_airport and not arrival_airport:
                return "I can help you find flights! Please tell me your departure and arrival airports, for example: 'flights from SFO to NYC' or 'how many flights from LAX to MIA'."
            
            with get_mysql_context() as db:
                query = db.query(Flight).filter(Flight.is_active == True)
                
                if departure_airport:
                    query = query.filter(Flight.departure_airport == departure_airport.upper())
                
                if arrival_airport:
                    query = query.filter(Flight.arrival_airport == arrival_airport.upper())
                
                flights = query.all()
                
                if is_count_query:
                    count = len(flights)
                    route = f"{departure_airport or 'anywhere'} to {arrival_airport or 'anywhere'}"
                    return f"I found {count} active flight(s) from {route}. Would you like me to show you the details?"
                else:
                    if not flights:
                        route = f"{departure_airport or 'anywhere'} to {arrival_airport or 'anywhere'}"
                        return f"I couldn't find any flights from {route}. Would you like to search for a different route?"
                    
                    # Format flight information
                    response = f"I found {len(flights)} flight(s):\n\n"
                    for i, flight in enumerate(flights[:5], 1):  # Show up to 5 flights
                        price = float(flight.base_price) if flight.base_price else 0
                        response += f"{i}. {flight.airline_name} - {flight.departure_airport} to {flight.arrival_airport}\n"
                        response += f"   Price: ${price:.2f} | Seats: {flight.available_seats}/{flight.total_seats}\n"
                        if flight.departure_datetime:
                            dep_time = flight.departure_datetime.strftime("%Y-%m-%d %H:%M")
                            response += f"   Departure: {dep_time}\n"
                        response += "\n"
                    
                    if len(flights) > 5:
                        response += f"... and {len(flights) - 5} more flight(s). "
                    response += "Would you like to see more details or book one of these?"
                    
                    return response
                    
        except Exception as e:
            logger.error(f"Error querying flights: {e}")
            return "I'm having trouble accessing the flight database right now. Please try again in a moment, or try a different query."

