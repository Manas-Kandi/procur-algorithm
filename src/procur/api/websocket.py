"""
WebSocket API for Real-time Updates
Handles real-time negotiation events and notifications
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Set, Optional, Any
from uuid import uuid4

from fastapi import WebSocket, WebSocketDisconnect, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_async_db
from ..auth.jwt import verify_token
from ..events import EventBus, Event

logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()


class ConnectionManager:
    """Manages WebSocket connections and message broadcasting"""
    
    def __init__(self):
        # Active connections by user_id
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Subscriptions by channel
        self.subscriptions: Dict[str, Set[str]] = {}
        # Connection metadata
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str, metadata: Dict[str, Any] = None):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        
        # Add to active connections
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        
        # Store metadata
        self.connection_metadata[websocket] = {
            "user_id": user_id,
            "connected_at": datetime.utcnow().isoformat(),
            "subscriptions": set(),
            **(metadata or {})
        }
        
        logger.info(f"WebSocket connected for user {user_id}")
        
        # Send connection confirmation
        await self.send_personal_message(
            websocket,
            {
                "type": "connection.established",
                "payload": {
                    "user_id": user_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        )
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        metadata = self.connection_metadata.get(websocket)
        if not metadata:
            return
        
        user_id = metadata["user_id"]
        
        # Remove from active connections
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        # Remove from subscriptions
        for channel in metadata.get("subscriptions", set()):
            if channel in self.subscriptions:
                self.subscriptions[channel].discard(user_id)
                if not self.subscriptions[channel]:
                    del self.subscriptions[channel]
        
        # Remove metadata
        del self.connection_metadata[websocket]
        
        logger.info(f"WebSocket disconnected for user {user_id}")
    
    async def send_personal_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """Send a message to a specific WebSocket connection"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message to websocket: {e}")
    
    async def send_user_message(self, user_id: str, message: Dict[str, Any]):
        """Send a message to all connections of a specific user"""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await self.send_personal_message(connection, message)
    
    async def broadcast(self, message: Dict[str, Any], exclude_user: str = None):
        """Broadcast a message to all connected users"""
        for user_id, connections in self.active_connections.items():
            if exclude_user and user_id == exclude_user:
                continue
            for connection in connections:
                await self.send_personal_message(connection, message)
    
    async def broadcast_to_channel(self, channel: str, message: Dict[str, Any]):
        """Broadcast a message to all users subscribed to a channel"""
        if channel in self.subscriptions:
            for user_id in self.subscriptions[channel]:
                await self.send_user_message(user_id, message)
    
    def subscribe_to_channel(self, websocket: WebSocket, channel: str):
        """Subscribe a connection to a channel"""
        metadata = self.connection_metadata.get(websocket)
        if not metadata:
            return False
        
        user_id = metadata["user_id"]
        
        # Add to channel subscriptions
        if channel not in self.subscriptions:
            self.subscriptions[channel] = set()
        self.subscriptions[channel].add(user_id)
        
        # Add to connection metadata
        metadata["subscriptions"].add(channel)
        
        logger.info(f"User {user_id} subscribed to channel {channel}")
        return True
    
    def unsubscribe_from_channel(self, websocket: WebSocket, channel: str):
        """Unsubscribe a connection from a channel"""
        metadata = self.connection_metadata.get(websocket)
        if not metadata:
            return False
        
        user_id = metadata["user_id"]
        
        # Remove from channel subscriptions
        if channel in self.subscriptions:
            self.subscriptions[channel].discard(user_id)
            if not self.subscriptions[channel]:
                del self.subscriptions[channel]
        
        # Remove from connection metadata
        metadata["subscriptions"].discard(channel)
        
        logger.info(f"User {user_id} unsubscribed from channel {channel}")
        return True


# Global connection manager instance
manager = ConnectionManager()


class WebSocketEventHandler:
    """Handles events from the EventBus and broadcasts them via WebSocket"""
    
    def __init__(self, manager: ConnectionManager):
        self.manager = manager
        self.event_bus = EventBus()
        self._setup_event_listeners()
    
    def _setup_event_listeners(self):
        """Setup listeners for various event types"""
        
        # Negotiation events
        self.event_bus.subscribe("negotiation.started", self._handle_negotiation_event)
        self.event_bus.subscribe("negotiation.offer_received", self._handle_negotiation_event)
        self.event_bus.subscribe("negotiation.counter_offer", self._handle_negotiation_event)
        self.event_bus.subscribe("negotiation.round_complete", self._handle_negotiation_event)
        self.event_bus.subscribe("negotiation.completed", self._handle_negotiation_event)
        self.event_bus.subscribe("negotiation.failed", self._handle_negotiation_event)
        
        # Approval events
        self.event_bus.subscribe("approval.required", self._handle_approval_event)
        self.event_bus.subscribe("approval.granted", self._handle_approval_event)
        self.event_bus.subscribe("approval.rejected", self._handle_approval_event)
        
        # Contract events
        self.event_bus.subscribe("contract.generated", self._handle_contract_event)
        self.event_bus.subscribe("contract.signed", self._handle_contract_event)
        
        # AI events
        self.event_bus.subscribe("ai.reasoning", self._handle_ai_event)
    
    async def _handle_negotiation_event(self, event: Event):
        """Handle negotiation-related events"""
        request_id = event.data.get("request_id")
        if not request_id:
            return
        
        # Broadcast to negotiation channel
        channel = f"negotiation.{request_id}"
        message = {
            "type": event.event_type,
            "payload": event.data,
            "timestamp": event.timestamp.isoformat(),
            "id": str(uuid4())
        }
        
        await self.manager.broadcast_to_channel(channel, message)
        
        # Also send to specific users if needed
        buyer_id = event.data.get("buyer_id")
        seller_id = event.data.get("seller_id")
        
        if buyer_id:
            await self.manager.send_user_message(buyer_id, message)
        if seller_id:
            await self.manager.send_user_message(seller_id, message)
    
    async def _handle_approval_event(self, event: Event):
        """Handle approval-related events"""
        approver_id = event.data.get("approver_id")
        requester_id = event.data.get("requester_id")
        
        message = {
            "type": event.event_type,
            "payload": event.data,
            "timestamp": event.timestamp.isoformat(),
            "id": str(uuid4())
        }
        
        if approver_id:
            await self.manager.send_user_message(approver_id, message)
        if requester_id:
            await self.manager.send_user_message(requester_id, message)
    
    async def _handle_contract_event(self, event: Event):
        """Handle contract-related events"""
        user_ids = event.data.get("user_ids", [])
        
        message = {
            "type": event.event_type,
            "payload": event.data,
            "timestamp": event.timestamp.isoformat(),
            "id": str(uuid4())
        }
        
        for user_id in user_ids:
            await self.manager.send_user_message(user_id, message)
    
    async def _handle_ai_event(self, event: Event):
        """Handle AI-related events"""
        request_id = event.data.get("request_id")
        if request_id:
            channel = f"negotiation.{request_id}"
            message = {
                "type": event.event_type,
                "payload": event.data,
                "timestamp": event.timestamp.isoformat(),
                "id": str(uuid4())
            }
            await self.manager.broadcast_to_channel(channel, message)


# Global event handler instance
event_handler = WebSocketEventHandler(manager)


async def get_current_user_ws(websocket: WebSocket) -> Optional[Dict[str, Any]]:
    """Extract and verify user from WebSocket connection"""
    try:
        # Try to get token from query params
        token = websocket.query_params.get("token")
        if not token:
            # Try to get from first message
            return None
        
        # Verify token
        payload = verify_token(token)
        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "role": payload.get("role")
        }
    except Exception as e:
        logger.error(f"WebSocket authentication failed: {e}")
        return None


async def websocket_endpoint(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_async_db)
):
    """Main WebSocket endpoint"""
    
    # Authenticate user
    user = await get_current_user_ws(websocket)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # Connect
    await manager.connect(websocket, user["user_id"], {"role": user["role"]})
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            # Handle different message types
            message_type = data.get("type")
            payload = data.get("payload", {})
            
            if message_type == "ping":
                # Heartbeat
                await manager.send_personal_message(
                    websocket,
                    {
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
            
            elif message_type == "subscribe":
                # Subscribe to channel
                channel = payload.get("channel")
                if channel:
                    success = manager.subscribe_to_channel(websocket, channel)
                    await manager.send_personal_message(
                        websocket,
                        {
                            "type": "subscription.confirmed" if success else "subscription.failed",
                            "payload": {"channel": channel}
                        }
                    )
            
            elif message_type == "unsubscribe":
                # Unsubscribe from channel
                channel = payload.get("channel")
                if channel:
                    success = manager.unsubscribe_from_channel(websocket, channel)
                    await manager.send_personal_message(
                        websocket,
                        {
                            "type": "unsubscription.confirmed" if success else "unsubscription.failed",
                            "payload": {"channel": channel}
                        }
                    )
            
            elif message_type == "message":
                # Handle custom messages
                # This could be used for chat, comments, etc.
                pass
            
            else:
                # Unknown message type
                await manager.send_personal_message(
                    websocket,
                    {
                        "type": "error",
                        "payload": {"message": f"Unknown message type: {message_type}"}
                    }
                )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
        await websocket.close()


def setup_websocket_routes(app):
    """Setup WebSocket routes on the FastAPI app"""
    app.add_api_websocket_route("/ws", websocket_endpoint)
