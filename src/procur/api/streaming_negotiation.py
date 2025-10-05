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

    def _sync_emit_event(self, event_type: str, data: Dict[str, Any]):
        """Synchronous wrapper for emitting events from within the agent."""
        if self._manager:
            # Create a coroutine and schedule it on the event loop
            try:
                loop = asyncio.get_event_loop()
                # Use call_soon_threadsafe since we're in a different thread
                asyncio.run_coroutine_threadsafe(
                    self._manager.send_event(self.session_id, event_type, data),
                    loop
                )
            except Exception as e:
                print(f"Error emitting event {event_type}: {e}")

    async def negotiate_with_streaming(
        self,
        request: Request,
        vendors: List[VendorProfile],
    ) -> Dict[str, Any]:
        """
        Run negotiation with real-time event streaming.

        The BuyerAgent now has an event_callback that emits events during negotiation.
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

        # Set the event callback on the buyer agent
        self.buyer_agent.event_callback = self._sync_emit_event

        # Run negotiation in thread pool (agent is synchronous)
        loop = asyncio.get_event_loop()
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
