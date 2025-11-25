"""
AI Recommendation Service - FastAPI application with multi-agent travel concierge.
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging

from .api.routes import router as api_router
from .api.websocket import ConnectionManager
from .agents.deals_agent import DealsAgent
from .agents.concierge_agent import ConciergeAgent
from .services.deal_detector import DealDetectorService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# WebSocket connection manager
manager = ConnectionManager()

# Agents
deals_agent: DealsAgent = None
concierge_agent: ConciergeAgent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    global deals_agent, concierge_agent
    
    logger.info("Starting AI Recommendation Service...")
    
    # Initialize agents
    deals_agent = DealsAgent()
    concierge_agent = ConciergeAgent()
    
    # Start background deal scanning
    asyncio.create_task(deals_agent.start_scheduled_scanning())
    
    logger.info("AI Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Service...")
    if deals_agent:
        await deals_agent.stop()


app = FastAPI(
    title="Kayak AI Recommendation Service",
    description="Multi-agent travel concierge with deal detection and personalized recommendations",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ai-recommendation-service"}


# ==================== WebSocket Endpoints ====================

@app.websocket("/ws/events")
async def websocket_events(websocket: WebSocket):
    """WebSocket endpoint for real-time deal events and updates."""
    await manager.connect(websocket)
    try:
        while True:
            # Receive messages from client (e.g., watch requests)
            data = await websocket.receive_json()
            
            if data.get("action") == "watch":
                # Handle watch request
                watch_id = await concierge_agent.create_watch(
                    user_id=data.get("user_id"),
                    listing_id=data.get("listing_id"),
                    price_threshold=data.get("price_threshold"),
                    inventory_threshold=data.get("inventory_threshold")
                )
                await websocket.send_json({
                    "type": "watch_created",
                    "watch_id": watch_id
                })
            
            elif data.get("action") == "unwatch":
                await concierge_agent.remove_watch(data.get("watch_id"))
                await websocket.send_json({
                    "type": "watch_removed",
                    "watch_id": data.get("watch_id")
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time chat with concierge agent."""
    await manager.connect(websocket)
    session_context = {}
    
    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message", "")
            user_id = data.get("user_id")
            
            # Process message with concierge agent
            response = await concierge_agent.process_message(
                message=message,
                user_id=user_id,
                context=session_context
            )
            
            # Update session context
            session_context = response.get("context", {})
            
            # Send response
            await websocket.send_json({
                "type": "chat_response",
                "response": response.get("message"),
                "bundles": response.get("bundles", []),
                "clarification_needed": response.get("clarification_needed", False)
            })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)

