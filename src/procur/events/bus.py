"""Redis-based event bus implementation."""

import json
import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

import redis
from redis.exceptions import RedisError

from .config import get_event_bus_config
from .schemas import Event, EventType

logger = logging.getLogger(__name__)


class EventBus:
    """Redis-based event bus for async workflow processing."""
    
    def __init__(self, config: Optional[Any] = None):
        """Initialize event bus."""
        self.config = config or get_event_bus_config()
        self._redis_client: Optional[redis.Redis] = None
        self._subscribers: Dict[EventType, List[Callable]] = {}
    
    @property
    def redis_client(self) -> redis.Redis:
        """Get or create Redis client."""
        if self._redis_client is None:
            self._redis_client = redis.from_url(
                self.config.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
            )
            logger.info(f"Redis client connected: {self.config.redis_host}:{self.config.redis_port}")
        return self._redis_client
    
    def publish(self, event: Event) -> str:
        """
        Publish an event to the event bus.
        
        Args:
            event: Event to publish
        
        Returns:
            Event ID
        """
        try:
            # Serialize event
            event_data = event.model_dump_json()
            
            # Add to event stream
            message_id = self.redis_client.xadd(
                self.config.event_stream_name,
                {
                    "event_id": event.event_id,
                    "event_type": event.event_type,
                    "data": event_data,
                    "timestamp": event.timestamp.isoformat(),
                    "priority": event.priority,
                },
                maxlen=100000,  # Keep last 100k events
            )
            
            # Publish to pub/sub for real-time subscribers
            self.redis_client.publish(
                f"events:{event.event_type}",
                event_data,
            )
            
            logger.info(f"Published event: {event.event_type} (ID: {event.event_id})")
            return event.event_id
            
        except RedisError as e:
            logger.error(f"Failed to publish event: {e}")
            raise
    
    def subscribe(self, event_type: EventType, handler: Callable):
        """
        Subscribe to an event type.
        
        Args:
            event_type: Event type to subscribe to
            handler: Callback function to handle events
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(handler)
        logger.info(f"Subscribed to event type: {event_type}")
    
    def consume_events(
        self,
        consumer_name: str,
        event_types: Optional[List[EventType]] = None,
        batch_size: Optional[int] = None,
        block_time: Optional[int] = None,
    ) -> List[Event]:
        """
        Consume events from the event stream.
        
        Args:
            consumer_name: Unique consumer identifier
            event_types: Optional list of event types to filter
            batch_size: Number of events to consume
            block_time: Block time in milliseconds
        
        Returns:
            List of events
        """
        batch_size = batch_size or self.config.event_batch_size
        block_time = block_time or self.config.event_block_time
        
        try:
            # Create consumer group if not exists
            try:
                self.redis_client.xgroup_create(
                    self.config.event_stream_name,
                    self.config.event_consumer_group,
                    id="0",
                    mkstream=True,
                )
            except redis.ResponseError:
                # Group already exists
                pass
            
            # Read events from stream
            messages = self.redis_client.xreadgroup(
                self.config.event_consumer_group,
                consumer_name,
                {self.config.event_stream_name: ">"},
                count=batch_size,
                block=block_time,
            )
            
            events = []
            for stream_name, stream_messages in messages:
                for message_id, message_data in stream_messages:
                    try:
                        # Deserialize event
                        event_data = json.loads(message_data["data"])
                        event = Event(**event_data)
                        
                        # Filter by event type if specified
                        if event_types and event.event_type not in event_types:
                            # Acknowledge and skip
                            self.redis_client.xack(
                                self.config.event_stream_name,
                                self.config.event_consumer_group,
                                message_id,
                            )
                            continue
                        
                        # Store message ID for acknowledgment
                        event.metadata["message_id"] = message_id
                        events.append(event)
                        
                    except Exception as e:
                        logger.error(f"Failed to deserialize event: {e}")
                        # Acknowledge bad message
                        self.redis_client.xack(
                            self.config.event_stream_name,
                            self.config.event_consumer_group,
                            message_id,
                        )
            
            return events
            
        except RedisError as e:
            logger.error(f"Failed to consume events: {e}")
            return []
    
    def acknowledge_event(self, event: Event):
        """
        Acknowledge successful event processing.
        
        Args:
            event: Event to acknowledge
        """
        message_id = event.metadata.get("message_id")
        if not message_id:
            logger.warning("No message_id in event metadata")
            return
        
        try:
            self.redis_client.xack(
                self.config.event_stream_name,
                self.config.event_consumer_group,
                message_id,
            )
            logger.debug(f"Acknowledged event: {event.event_id}")
        except RedisError as e:
            logger.error(f"Failed to acknowledge event: {e}")
    
    def send_to_dlq(self, event: Event, error: str):
        """
        Send failed event to dead letter queue.
        
        Args:
            event: Failed event
            error: Error message
        """
        if not self.config.dlq_enabled:
            return
        
        try:
            event.error = error
            event.retry_count += 1
            
            self.redis_client.xadd(
                self.config.dlq_stream_name,
                {
                    "event_id": event.event_id,
                    "event_type": event.event_type,
                    "data": event.model_dump_json(),
                    "error": error,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )
            
            logger.warning(f"Sent event to DLQ: {event.event_id} - {error}")
            
        except RedisError as e:
            logger.error(f"Failed to send event to DLQ: {e}")
    
    def get_pending_events(self, consumer_name: str) -> List[Dict]:
        """
        Get pending events for a consumer.
        
        Args:
            consumer_name: Consumer name
        
        Returns:
            List of pending events
        """
        try:
            pending = self.redis_client.xpending_range(
                self.config.event_stream_name,
                self.config.event_consumer_group,
                min="-",
                max="+",
                count=100,
                consumername=consumer_name,
            )
            return pending
        except RedisError as e:
            logger.error(f"Failed to get pending events: {e}")
            return []
    
    def get_stream_info(self) -> Dict:
        """Get event stream information."""
        try:
            info = self.redis_client.xinfo_stream(self.config.event_stream_name)
            return info
        except RedisError as e:
            logger.error(f"Failed to get stream info: {e}")
            return {}
    
    def close(self):
        """Close Redis connection."""
        if self._redis_client:
            self._redis_client.close()
            logger.info("Redis client closed")


# Global event bus instance
_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get global event bus instance."""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus
