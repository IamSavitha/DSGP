"""
API routes for AI Recommendation Service.
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class BundleRequest(BaseModel):
    """Request for trip bundles."""
    origin: Optional[str] = None
    destination: str
    departure_date: str
    return_date: Optional[str] = None
    budget: Optional[float] = None
    num_travelers: int = 1
    preferences: Optional[dict] = None


class BundleResponse(BaseModel):
    """Response with trip bundles."""
    bundles: List[dict]
    total_found: int
    query_params: dict


class ChatRequest(BaseModel):
    """Chat message request."""
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None


class DealResponse(BaseModel):
    """Deal information response."""
    listing_id: str
    listing_type: str
    current_price: float
    avg_price: float
    discount_pct: float
    deal_score: float
    tags: List[str]


@router.get("/deals", response_model=List[DealResponse])
async def get_deals(
    listing_type: Optional[str] = Query(None, description="flight or hotel"),
    min_score: float = Query(default=0, ge=0, le=100),
    limit: int = Query(default=20, ge=1, le=100)
):
    """Get current deals."""
    # In production, this would fetch from the deals agent cache
    mock_deals = [
        {
            "listing_id": "AA123",
            "listing_type": "flight",
            "current_price": 249.00,
            "avg_price": 320.00,
            "discount_pct": 22.2,
            "deal_score": 75.5,
            "tags": ["Hot Deal", "Limited Availability"]
        },
        {
            "listing_id": "HTL-001",
            "listing_type": "hotel",
            "current_price": 159.00,
            "avg_price": 220.00,
            "discount_pct": 27.7,
            "deal_score": 82.0,
            "tags": ["Hot Deal", "Pet-Friendly", "Breakfast Included"]
        }
    ]
    
    if listing_type:
        mock_deals = [d for d in mock_deals if d["listing_type"] == listing_type]
    
    mock_deals = [d for d in mock_deals if d["deal_score"] >= min_score]
    
    return mock_deals[:limit]


@router.post("/bundles", response_model=BundleResponse)
async def find_bundles(request: BundleRequest):
    """Find flight + hotel bundles."""
    # Mock bundle generation
    bundles = [
        {
            "bundle_id": "BDL-001",
            "flight": {
                "id": "AA789",
                "airline": "American Airlines",
                "price": 299,
                "route": f"SFO-{request.destination[:3].upper()}"
            },
            "hotel": {
                "id": "HTL-001",
                "name": f"{request.destination} Resort",
                "price_per_night": 180,
                "stars": 4
            },
            "total_price": 659,
            "fit_score": 85,
            "explanation": "Best value option with good amenities"
        }
    ]
    
    if request.budget:
        bundles = [b for b in bundles if b["total_price"] <= request.budget]
    
    return BundleResponse(
        bundles=bundles,
        total_found=len(bundles),
        query_params=request.model_dump()
    )


@router.post("/chat")
async def chat(request: ChatRequest):
    """Chat with the concierge agent."""
    from ..agents.concierge_agent import ConciergeAgent
    
    agent = ConciergeAgent()
    response = await agent.process_message(
        message=request.message,
        user_id=request.user_id,
        context={}
    )
    
    return response


@router.get("/deals/{listing_id}/history")
async def get_price_history(listing_id: str, days: int = Query(default=30, ge=1, le=90)):
    """Get price history for a listing."""
    # Mock price history
    from datetime import timedelta
    
    history = []
    base_price = 300
    
    for i in range(days):
        date = datetime.now() - timedelta(days=days-i)
        # Simulate price fluctuation
        price = base_price + (i % 10 - 5) * 10
        history.append({
            "date": date.strftime("%Y-%m-%d"),
            "price": price
        })
    
    return {
        "listing_id": listing_id,
        "history": history,
        "avg_price": sum(h["price"] for h in history) / len(history),
        "min_price": min(h["price"] for h in history),
        "max_price": max(h["price"] for h in history)
    }


@router.post("/watches")
async def create_watch(
    listing_id: str,
    user_id: str,
    price_threshold: Optional[float] = None,
    inventory_threshold: Optional[int] = None
):
    """Create a price/inventory watch."""
    from ..agents.concierge_agent import ConciergeAgent
    
    agent = ConciergeAgent()
    watch_id = await agent.create_watch(
        user_id=user_id,
        listing_id=listing_id,
        price_threshold=price_threshold,
        inventory_threshold=inventory_threshold
    )
    
    return {"watch_id": watch_id, "status": "active"}


@router.delete("/watches/{watch_id}")
async def delete_watch(watch_id: str):
    """Delete a watch."""
    from ..agents.concierge_agent import ConciergeAgent
    
    agent = ConciergeAgent()
    await agent.remove_watch(watch_id)
    
    return {"watch_id": watch_id, "status": "removed"}

