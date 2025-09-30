"""Event publisher for publishing events to the bus."""

import logging
from typing import Any, Dict, Optional
from uuid import uuid4

from ..db import get_session
from .bus import get_event_bus
from .schemas import (
    Event,
    EventType,
    EventPriority,
    RequestCreatedEvent,
    NegotiationStartedEvent,
    NegotiationRoundStartedEvent,
    VendorEnrichmentStartedEvent,
    ContractGenerationStartedEvent,
    NotificationSendEvent,
)
from .store import EventStore

logger = logging.getLogger(__name__)


class EventPublisher:
    """Publisher for emitting events."""
    
    def __init__(self):
        """Initialize event publisher."""
        self.event_bus = get_event_bus()
    
    def publish(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        user_id: Optional[int] = None,
        organization_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        priority: EventPriority = EventPriority.NORMAL,
        **kwargs,
    ) -> str:
        """
        Publish an event.
        
        Args:
            event_type: Type of event
            data: Event data
            user_id: User ID
            organization_id: Organization ID
            correlation_id: Correlation ID for tracking related events
            priority: Event priority
            **kwargs: Additional event properties
        
        Returns:
            Event ID
        """
        # Create event
        event = Event(
            event_type=event_type,
            data=data,
            user_id=user_id,
            organization_id=organization_id,
            correlation_id=correlation_id or str(uuid4()),
            priority=priority,
            **kwargs,
        )
        
        # Publish to event bus
        event_id = self.event_bus.publish(event)
        
        # Save to event store for audit trail
        try:
            with get_session() as session:
                event_store = EventStore(session)
                event_store.save_event(event)
        except Exception as e:
            logger.error(f"Failed to save event to store: {e}")
        
        return event_id
    
    def publish_request_created(
        self,
        request_id: str,
        user_id: int,
        organization_id: Optional[str] = None,
        **data,
    ) -> str:
        """Publish request created event."""
        return self.publish(
            event_type=EventType.REQUEST_CREATED,
            data={"request_id": request_id, **data},
            user_id=user_id,
            organization_id=organization_id,
        )
    
    def publish_negotiation_started(
        self,
        negotiation_id: str,
        request_id: str,
        vendor_id: str,
        user_id: int,
        correlation_id: Optional[str] = None,
        **data,
    ) -> str:
        """Publish negotiation started event."""
        return self.publish(
            event_type=EventType.NEGOTIATION_STARTED,
            data={
                "negotiation_id": negotiation_id,
                "request_id": request_id,
                "vendor_id": vendor_id,
                **data,
            },
            user_id=user_id,
            correlation_id=correlation_id,
            priority=EventPriority.HIGH,
        )
    
    def publish_negotiation_round_started(
        self,
        negotiation_id: str,
        round_number: int,
        correlation_id: str,
        **data,
    ) -> str:
        """Publish negotiation round started event."""
        return self.publish(
            event_type=EventType.NEGOTIATION_ROUND_STARTED,
            data={
                "negotiation_id": negotiation_id,
                "round_number": round_number,
                **data,
            },
            correlation_id=correlation_id,
            priority=EventPriority.HIGH,
        )
    
    def publish_vendor_enrichment_started(
        self,
        vendor_id: str,
        category: str,
        **data,
    ) -> str:
        """Publish vendor enrichment started event."""
        return self.publish(
            event_type=EventType.VENDOR_ENRICHMENT_STARTED,
            data={
                "vendor_id": vendor_id,
                "category": category,
                **data,
            },
        )
    
    def publish_contract_generation_started(
        self,
        contract_id: str,
        request_id: str,
        vendor_id: str,
        correlation_id: str,
        **data,
    ) -> str:
        """Publish contract generation started event."""
        return self.publish(
            event_type=EventType.CONTRACT_GENERATION_STARTED,
            data={
                "contract_id": contract_id,
                "request_id": request_id,
                "vendor_id": vendor_id,
                **data,
            },
            correlation_id=correlation_id,
            priority=EventPriority.HIGH,
        )
    
    def publish_notification(
        self,
        notification_type: str,
        recipient: str,
        subject: str,
        message: str,
        **data,
    ) -> str:
        """Publish notification event."""
        return self.publish(
            event_type=EventType.NOTIFICATION_SEND,
            data={
                "notification_type": notification_type,
                "recipient": recipient,
                "subject": subject,
                "message": message,
                **data,
            },
        )
