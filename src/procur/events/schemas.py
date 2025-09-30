"""Event schemas and types."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Event types for the system."""
    
    # Request events
    REQUEST_CREATED = "request.created"
    REQUEST_UPDATED = "request.updated"
    REQUEST_APPROVED = "request.approved"
    REQUEST_REJECTED = "request.rejected"
    
    # Vendor events
    VENDOR_CREATED = "vendor.created"
    VENDOR_UPDATED = "vendor.updated"
    VENDOR_ENRICHMENT_STARTED = "vendor.enrichment.started"
    VENDOR_ENRICHMENT_COMPLETED = "vendor.enrichment.completed"
    VENDOR_ENRICHMENT_FAILED = "vendor.enrichment.failed"
    
    # Negotiation events
    NEGOTIATION_STARTED = "negotiation.started"
    NEGOTIATION_ROUND_STARTED = "negotiation.round.started"
    NEGOTIATION_ROUND_COMPLETED = "negotiation.round.completed"
    NEGOTIATION_OFFER_RECEIVED = "negotiation.offer.received"
    NEGOTIATION_COMPLETED = "negotiation.completed"
    NEGOTIATION_FAILED = "negotiation.failed"
    
    # Contract events
    CONTRACT_CREATED = "contract.created"
    CONTRACT_GENERATION_STARTED = "contract.generation.started"
    CONTRACT_GENERATION_COMPLETED = "contract.generation.completed"
    CONTRACT_SIGNED = "contract.signed"
    CONTRACT_ACTIVATED = "contract.activated"
    
    # Notification events
    NOTIFICATION_SEND = "notification.send"
    NOTIFICATION_EMAIL = "notification.email"
    NOTIFICATION_SLACK = "notification.slack"
    NOTIFICATION_WEBHOOK = "notification.webhook"
    
    # Integration events
    INTEGRATION_ERP_SYNC = "integration.erp.sync"
    INTEGRATION_DOCUSIGN_SEND = "integration.docusign.send"
    
    # System events
    SYSTEM_ERROR = "system.error"
    SYSTEM_WARNING = "system.warning"


class EventPriority(str, Enum):
    """Event priority levels."""
    
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class Event(BaseModel):
    """Base event model."""
    
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Event data
    data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Event context
    user_id: Optional[int] = None
    organization_id: Optional[str] = None
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    # Event properties
    priority: EventPriority = EventPriority.NORMAL
    retry_count: int = 0
    max_retries: int = 3
    
    # Processing status
    processed: bool = False
    processed_at: Optional[datetime] = None
    error: Optional[str] = None
    
    class Config:
        use_enum_values = True


class RequestCreatedEvent(Event):
    """Event emitted when a request is created."""
    
    event_type: EventType = EventType.REQUEST_CREATED
    
    def __init__(self, **data):
        super().__init__(event_type=EventType.REQUEST_CREATED, **data)


class NegotiationStartedEvent(Event):
    """Event emitted when negotiation starts."""
    
    event_type: EventType = EventType.NEGOTIATION_STARTED
    
    def __init__(self, **data):
        super().__init__(event_type=EventType.NEGOTIATION_STARTED, **data)


class NegotiationRoundStartedEvent(Event):
    """Event emitted when a negotiation round starts."""
    
    event_type: EventType = EventType.NEGOTIATION_ROUND_STARTED
    priority: EventPriority = EventPriority.HIGH
    
    def __init__(self, **data):
        super().__init__(
            event_type=EventType.NEGOTIATION_ROUND_STARTED,
            priority=EventPriority.HIGH,
            **data
        )


class VendorEnrichmentStartedEvent(Event):
    """Event emitted when vendor enrichment starts."""
    
    event_type: EventType = EventType.VENDOR_ENRICHMENT_STARTED
    
    def __init__(self, **data):
        super().__init__(event_type=EventType.VENDOR_ENRICHMENT_STARTED, **data)


class ContractGenerationStartedEvent(Event):
    """Event emitted when contract generation starts."""
    
    event_type: EventType = EventType.CONTRACT_GENERATION_STARTED
    priority: EventPriority = EventPriority.HIGH
    
    def __init__(self, **data):
        super().__init__(
            event_type=EventType.CONTRACT_GENERATION_STARTED,
            priority=EventPriority.HIGH,
            **data
        )


class NotificationSendEvent(Event):
    """Event emitted to send a notification."""
    
    event_type: EventType = EventType.NOTIFICATION_SEND
    
    def __init__(self, **data):
        super().__init__(event_type=EventType.NOTIFICATION_SEND, **data)
