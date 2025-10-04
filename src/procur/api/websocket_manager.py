"""WebSocket connection manager for real-time negotiation streaming."""

from typing import Dict, List
from fastapi import WebSocket
import asyncio
import json
from datetime import datetime


class ConnectionManager:
    """Manages WebSocket connections for negotiation sessions."""

    def __init__(self):
        # session_id -> list of WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept and store a new WebSocket connection."""
        await websocket.accept()
        async with self._lock:
            if session_id not in self.active_connections:
                self.active_connections[session_id] = []
            self.active_connections[session_id].append(websocket)

    async def disconnect(self, websocket: WebSocket, session_id: str):
        """Remove a WebSocket connection."""
        async with self._lock:
            if session_id in self.active_connections:
                if websocket in self.active_connections[session_id]:
                    self.active_connections[session_id].remove(websocket)
                if not self.active_connections[session_id]:
                    del self.active_connections[session_id]

    async def send_event(self, session_id: str, event_type: str, data: dict):
        """Send an event to all connections for a session."""
        if session_id not in self.active_connections:
            return

        event = {
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }

        message = json.dumps(event)
        disconnected = []

        for connection in self.active_connections[session_id]:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)

        # Clean up disconnected clients
        if disconnected:
            async with self._lock:
                for conn in disconnected:
                    if conn in self.active_connections[session_id]:
                        self.active_connections[session_id].remove(conn)

    async def broadcast_to_session(self, session_id: str, message: str):
        """Broadcast a raw message to all connections for a session."""
        if session_id not in self.active_connections:
            return

        disconnected = []
        for connection in self.active_connections[session_id]:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)

        # Clean up disconnected clients
        if disconnected:
            async with self._lock:
                for conn in disconnected:
                    if conn in self.active_connections[session_id]:
                        self.active_connections[session_id].remove(conn)


# Global connection manager instance
manager = ConnectionManager()
