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
        if intent == "search":
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
        
        if any(word in message_lower for word in ["track", "watch", "alert", "notify"]):
            return "watch"
        
        if any(word in message_lower for word in ["compare", "vs", "versus", "difference"]):
            return "compare"
        
        if any(word in message_lower for word in ["refund", "cancel", "policy", "pet", "parking"]):
            return "policy"
        
        if any(word in message_lower for word in ["make it", "change", "instead", "but", "without"]):
            return "refine"
        
        if any(word in message_lower for word in ["find", "search", "book", "trip", "travel", "fly", "stay"]):
            return "search"
        
        return "general"
    
    def _extract_constraints(self, message: str, context: Dict) -> Dict:
        """Extract travel constraints from message."""
        constraints = {}
        message_lower = message.lower()
        
        # Budget extraction
        budget_match = re.search(r'\$?(\d{1,5}(?:,\d{3})?(?:\.\d{2})?)', message)
        if budget_match:
            constraints["budget"] = float(budget_match.group(1).replace(',', ''))
        
        # Date extraction (simplified)
        date_patterns = [
            r'(\w+ \d{1,2}(?:-\d{1,2})?)',
            r'(\d{1,2}/\d{1,2})',
        ]
        for pattern in date_patterns:
            match = re.search(pattern, message)
            if match:
                constraints["dates"] = match.group(1)
                break
        
        # Destination extraction
        cities = ["tokyo", "miami", "new york", "san francisco", "los angeles", 
                  "chicago", "seattle", "boston", "denver", "austin"]
        for city in cities:
            if city in message_lower:
                constraints["destination"] = city.title()
                break
        
        # Origin extraction
        if "from" in message_lower:
            for city in cities:
                if f"from {city}" in message_lower:
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
        if intent in ["search", "refine"]:
            # Need at least destination or origin
            if not context.get("destination") and not context.get("origin"):
                return True
        return False
    
    def _generate_clarification(self, intent: str, context: Dict) -> str:
        """Generate a clarification question."""
        if not context.get("destination"):
            return "Where would you like to go? I can find great deals to popular destinations!"
        
        if not context.get("dates"):
            return f"When are you thinking of traveling to {context.get('destination')}?"
        
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

