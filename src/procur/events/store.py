"""Event store for event sourcing and audit trail."""

import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, Integer, JSON, String, Text, select
from sqlalchemy.orm import Mapped, mapped_column, Session

from ..db.base import Base, TimestampMixin
from .schemas import Event, EventType

logger = logging.getLogger(__name__)


class EventRecord(Base, TimestampMixin):
    """Event record for event sourcing."""
    
    __tablename__ = "event_store"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Event data
    data: Mapped[dict] = mapped_column(JSON, nullable=False)
    metadata: Mapped[dict] = mapped_column(JSON, nullable=True)
    
    # Event context
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    organization_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    correlation_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    causation_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    
    # Event properties
    priority: Mapped[str] = mapped_column(String(20), nullable=False)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Processing status
    processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Timestamp
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    
    def __repr__(self) -> str:
        return f"<EventRecord(id={self.id}, event_type='{self.event_type}', event_id='{self.event_id}')>"


class EventStore:
    """Event store for persisting events."""
    
    def __init__(self, session: Session):
        """Initialize event store."""
        self.session = session
    
    def save_event(self, event: Event) -> EventRecord:
        """
        Save event to store.
        
        Args:
            event: Event to save
        
        Returns:
            Event record
        """
        record = EventRecord(
            event_id=event.event_id,
            event_type=event.event_type,
            data=event.data,
            metadata=event.metadata,
            user_id=event.user_id,
            organization_id=event.organization_id,
            correlation_id=event.correlation_id,
            causation_id=event.causation_id,
            priority=event.priority,
            retry_count=event.retry_count,
            processed=event.processed,
            processed_at=event.processed_at,
            error=event.error,
            timestamp=event.timestamp,
        )
        
        self.session.add(record)
        self.session.flush()
        
        logger.debug(f"Saved event to store: {event.event_id}")
        return record
    
    def get_event(self, event_id: str) -> Optional[EventRecord]:
        """Get event by ID."""
        query = select(EventRecord).where(EventRecord.event_id == event_id)
        result = self.session.execute(query)
        return result.scalar_one_or_none()
    
    def get_events_by_type(
        self,
        event_type: EventType,
        limit: int = 100,
        offset: int = 0,
    ) -> List[EventRecord]:
        """Get events by type."""
        query = (
            select(EventRecord)
            .where(EventRecord.event_type == event_type)
            .order_by(EventRecord.timestamp.desc())
            .limit(limit)
            .offset(offset)
        )
        result = self.session.execute(query)
        return list(result.scalars().all())
    
    def get_events_by_correlation_id(
        self,
        correlation_id: str,
    ) -> List[EventRecord]:
        """Get all events with same correlation ID."""
        query = (
            select(EventRecord)
            .where(EventRecord.correlation_id == correlation_id)
            .order_by(EventRecord.timestamp.asc())
        )
        result = self.session.execute(query)
        return list(result.scalars().all())
    
    def get_events_by_user(
        self,
        user_id: int,
        limit: int = 100,
    ) -> List[EventRecord]:
        """Get events by user."""
        query = (
            select(EventRecord)
            .where(EventRecord.user_id == user_id)
            .order_by(EventRecord.timestamp.desc())
            .limit(limit)
        )
        result = self.session.execute(query)
        return list(result.scalars().all())
    
    def get_events_by_organization(
        self,
        organization_id: str,
        limit: int = 100,
    ) -> List[EventRecord]:
        """Get events by organization."""
        query = (
            select(EventRecord)
            .where(EventRecord.organization_id == organization_id)
            .order_by(EventRecord.timestamp.desc())
            .limit(limit)
        )
        result = self.session.execute(query)
        return list(result.scalars().all())
    
    def get_unprocessed_events(
        self,
        event_type: Optional[EventType] = None,
        limit: int = 100,
    ) -> List[EventRecord]:
        """Get unprocessed events."""
        query = select(EventRecord).where(EventRecord.processed == False)
        
        if event_type:
            query = query.where(EventRecord.event_type == event_type)
        
        query = query.order_by(EventRecord.timestamp.asc()).limit(limit)
        result = self.session.execute(query)
        return list(result.scalars().all())
    
    def mark_processed(self, event_id: str):
        """Mark event as processed."""
        event = self.get_event(event_id)
        if event:
            event.processed = True
            event.processed_at = datetime.utcnow()
            self.session.flush()
    
    def mark_failed(self, event_id: str, error: str):
        """Mark event as failed."""
        event = self.get_event(event_id)
        if event:
            event.error = error
            event.retry_count += 1
            self.session.flush()
    
    def cleanup_old_events(self, days: int = 90):
        """Delete events older than specified days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        query = select(EventRecord).where(EventRecord.timestamp < cutoff_date)
        result = self.session.execute(query)
        events = result.scalars().all()
        
        count = len(events)
        for event in events:
            self.session.delete(event)
        
        self.session.flush()
        logger.info(f"Cleaned up {count} old events")
        return count
