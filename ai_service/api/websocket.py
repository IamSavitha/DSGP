"""
WebSocket connection manager for real-time updates.
"""
from fastapi import WebSocket
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str = None):
        """Accept and store a new connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = []
            self.user_connections[user_id].append(websocket)
        
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket, user_id: str = None):
        """Remove a connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if user_id and user_id in self.user_connections:
            if websocket in self.user_connections[user_id]:
                self.user_connections[user_id].remove(websocket)
        
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Send message to all connected clients."""
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send to connection: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.active_connections.remove(conn)
    
    async def send_to_user(self, user_id: str, message: dict):
        """Send message to a specific user."""
        if user_id not in self.user_connections:
            return
        
        disconnected = []
        
        for connection in self.user_connections[user_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send to user {user_id}: {e}")
                disconnected.append(connection)
        
        for conn in disconnected:
            self.user_connections[user_id].remove(conn)
    
    async def broadcast_deal_alert(self, deal: dict):
        """Broadcast a deal alert to all users."""
        await self.broadcast({
            "type": "deal_alert",
            "deal": deal
        })
    
    async def send_watch_alert(self, user_id: str, watch_id: str, alert_type: str, data: dict):
        """Send a watch alert to a specific user."""
        await self.send_to_user(user_id, {
            "type": "watch_alert",
            "watch_id": watch_id,
            "alert_type": alert_type,
            "data": data
        })

