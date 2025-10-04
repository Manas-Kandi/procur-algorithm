"""Streaming wrapper for real-time negotiation event broadcasting."""

import asyncio
from typing import Dict, Any, List
from ..agents.buyer_agent import BuyerAgent
from ..models import Request, VendorProfile


class StreamingNegotiationWrapper:
    """Wraps BuyerAgent to emit real-time events via WebSocket."""

    def __init__(self, buyer_agent: BuyerAgent, session_id: str):
        self.buyer_agent = buyer_agent
        self.session_id = session_id
        self._manager = None

    async def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit event to WebSocket if manager is available."""
        if self._manager:
            await self._manager.send_event(self.session_id, event_type, data)

    async def negotiate_with_streaming(
        self,
        request: Request,
        vendors: List[VendorProfile],
    ) -> Dict[str, Any]:
        """
        Run negotiation with real-time event streaming.

        This is a streaming wrapper around the synchronous negotiate() method.
        We intercept the negotiation process and emit events at key points.
        """
        # Import manager here to avoid circular dependency
        from .websocket_manager import manager
        self._manager = manager

        # Emit negotiation start event
        await self._emit_event("negotiation_start", {
            "request_id": request.request_id,
            "vendor_count": len(vendors),
            "message": f"Starting negotiation with {len(vendors)} vendor(s)"
        })

        # Since BuyerAgent.negotiate() is synchronous, we need to run it in a thread pool
        # to not block the async event loop
        loop = asyncio.get_event_loop()

        # For now, we'll call the synchronous method
        # In a production system, you'd want to refactor the agent to be async
        # or emit events from within the agent itself
        offers = await loop.run_in_executor(
            None,
            self.buyer_agent.negotiate,
            request,
            vendors
        )

        # Emit completion event
        await self._emit_event("negotiation_complete", {
            "request_id": request.request_id,
            "offers_received": len(offers),
            "message": f"Negotiation completed with {len(offers)} offer(s)"
        })

        return offers

    async def stream_round_events(self, round_data: Dict[str, Any]):
        """Stream individual round events (called from agent if integrated)."""
        await self._emit_event("negotiation_round", round_data)
