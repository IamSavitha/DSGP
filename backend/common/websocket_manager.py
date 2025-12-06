"""
WebSocket connection manager for real-time price updates.
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Set
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class PriceUpdateManager:
    """Manage WebSocket connections for real-time price updates."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.active_connections: List[WebSocket] = []
            cls._instance.listing_subscriptions: Dict[str, Set[WebSocket]] = {}  # listing_id -> set of websockets
        return cls._instance
    
    async def connect(self, websocket: WebSocket):
        """Accept and store a new connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove from all subscriptions
        for listing_id, connections in self.listing_subscriptions.items():
            if websocket in connections:
                connections.remove(websocket)
        
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def subscribe(self, websocket: WebSocket, listing_id: str, listing_type: str = "flight"):
        """Subscribe to price updates for a specific listing."""
        full_id = f"{listing_type}:{listing_id}"
        
        if full_id not in self.listing_subscriptions:
            self.listing_subscriptions[full_id] = set()
        
        self.listing_subscriptions[full_id].add(websocket)
        logger.info(f"Subscribed to {full_id}. Total subscribers: {len(self.listing_subscriptions[full_id])}")
    
    async def unsubscribe(self, websocket: WebSocket, listing_id: str, listing_type: str = "flight"):
        """Unsubscribe from price updates for a specific listing."""
        full_id = f"{listing_type}:{listing_id}"
        
        if full_id in self.listing_subscriptions:
            self.listing_subscriptions[full_id].discard(websocket)
            if not self.listing_subscriptions[full_id]:
                del self.listing_subscriptions[full_id]
            logger.info(f"Unsubscribed from {full_id}")
    
    async def broadcast_price_update(
        self, 
        listing_id: str, 
        listing_type: str,
        new_price: float,
        old_price: float = None
    ):
        """Broadcast price update to all subscribers of a listing."""
        full_id = f"{listing_type}:{listing_id}"
        
        message = {
            "type": "price_update",
            "listing_type": listing_type,
            "listing_id": listing_id,
            "new_price": new_price,
            "old_price": old_price,
            "timestamp": None  # Will be set by caller
        }
        
        if full_id in self.listing_subscriptions:
            disconnected = []
            for connection in self.listing_subscriptions[full_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.warning(f"Failed to send price update to connection: {e}")
                    disconnected.append(connection)
            
            # Clean up disconnected clients
            for conn in disconnected:
                self.listing_subscriptions[full_id].discard(conn)
                self.disconnect(conn)
            
            logger.info(f"Broadcasted price update for {full_id} to {len(self.listing_subscriptions[full_id])} subscribers")
        else:
            logger.debug(f"No subscribers for {full_id}")
    
    async def broadcast_to_all(self, message: dict):
        """Broadcast message to all connected clients."""
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send to connection: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)
        
        logger.info(f"Broadcasted message to {len(self.active_connections)} connections")

