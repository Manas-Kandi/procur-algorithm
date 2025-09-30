"""Event consumer for processing events."""

import logging
import signal
import sys
from typing import Callable, Dict, List, Optional

from .bus import get_event_bus
from .schemas import Event, EventType
from .store import EventStore
from ..db import get_session

logger = logging.getLogger(__name__)


class EventConsumer:
    """Consumer for processing events from the bus."""
    
    def __init__(self, consumer_name: str):
        """Initialize event consumer."""
        self.consumer_name = consumer_name
        self.event_bus = get_event_bus()
        self.handlers: Dict[EventType, Callable] = {}
        self.running = False
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def register_handler(self, event_type: EventType, handler: Callable):
        """
        Register event handler.
        
        Args:
            event_type: Event type to handle
            handler: Handler function
        """
        self.handlers[event_type] = handler
        logger.info(f"Registered handler for {event_type}")
    
    def start(
        self,
        event_types: Optional[List[EventType]] = None,
        batch_size: int = 10,
    ):
        """
        Start consuming events.
        
        Args:
            event_types: Optional list of event types to consume
            batch_size: Number of events to process per batch
        """
        self.running = True
        logger.info(f"Starting event consumer: {self.consumer_name}")
        
        while self.running:
            try:
                # Consume events
                events = self.event_bus.consume_events(
                    consumer_name=self.consumer_name,
                    event_types=event_types,
                    batch_size=batch_size,
                )
                
                # Process events
                for event in events:
                    self._process_event(event)
                
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
                break
            except Exception as e:
                logger.error(f"Error consuming events: {e}")
    
    def _process_event(self, event: Event):
        """Process a single event."""
        try:
            logger.info(f"Processing event: {event.event_type} (ID: {event.event_id})")
            
            # Get handler
            handler = self.handlers.get(event.event_type)
            if not handler:
                logger.warning(f"No handler for event type: {event.event_type}")
                self.event_bus.acknowledge_event(event)
                return
            
            # Execute handler
            handler(event)
            
            # Mark as processed in event store
            try:
                with get_session() as session:
                    event_store = EventStore(session)
                    event_store.mark_processed(event.event_id)
            except Exception as e:
                logger.error(f"Failed to mark event as processed: {e}")
            
            # Acknowledge event
            self.event_bus.acknowledge_event(event)
            logger.info(f"Successfully processed event: {event.event_id}")
            
        except Exception as e:
            logger.error(f"Failed to process event {event.event_id}: {e}")
            
            # Check retry count
            if event.retry_count >= event.max_retries:
                # Send to DLQ
                self.event_bus.send_to_dlq(event, str(e))
                self.event_bus.acknowledge_event(event)
            else:
                # Mark as failed for retry
                try:
                    with get_session() as session:
                        event_store = EventStore(session)
                        event_store.mark_failed(event.event_id, str(e))
                except Exception as store_error:
                    logger.error(f"Failed to mark event as failed: {store_error}")
    
    def stop(self):
        """Stop consuming events."""
        logger.info(f"Stopping event consumer: {self.consumer_name}")
        self.running = False
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}")
        self.stop()
        sys.exit(0)
