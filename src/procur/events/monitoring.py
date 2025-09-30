"""Event bus monitoring and metrics."""

import logging
from datetime import datetime, timedelta
from typing import Dict, List

from ..db import get_session
from .bus import get_event_bus
from .store import EventStore, EventRecord
from .schemas import EventType

logger = logging.getLogger(__name__)


class EventMonitor:
    """Monitor event bus health and metrics."""
    
    def __init__(self):
        """Initialize event monitor."""
        self.event_bus = get_event_bus()
    
    def get_stream_metrics(self) -> Dict:
        """Get event stream metrics."""
        try:
            info = self.event_bus.get_stream_info()
            
            return {
                "length": info.get("length", 0),
                "first_entry": info.get("first-entry"),
                "last_entry": info.get("last-entry"),
                "groups": info.get("groups", 0),
                "max_deleted_entry_id": info.get("max-deleted-entry-id"),
            }
        except Exception as e:
            logger.error(f"Failed to get stream metrics: {e}")
            return {}
    
    def get_consumer_metrics(self, consumer_name: str) -> Dict:
        """Get consumer metrics."""
        try:
            pending = self.event_bus.get_pending_events(consumer_name)
            
            return {
                "pending_count": len(pending),
                "pending_events": [
                    {
                        "message_id": p["message_id"],
                        "consumer": p["consumer"],
                        "time_since_delivered": p["time_since_delivered"],
                        "times_delivered": p["times_delivered"],
                    }
                    for p in pending
                ],
            }
        except Exception as e:
            logger.error(f"Failed to get consumer metrics: {e}")
            return {}
    
    def get_event_type_stats(self, hours: int = 24) -> Dict[str, int]:
        """Get event type statistics."""
        try:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            
            with get_session() as session:
                event_store = EventStore(session)
                
                # Get all events in time window
                from sqlalchemy import select, func
                query = (
                    select(
                        EventRecord.event_type,
                        func.count(EventRecord.id).label("count")
                    )
                    .where(EventRecord.timestamp >= cutoff)
                    .group_by(EventRecord.event_type)
                )
                
                result = session.execute(query)
                stats = {row[0]: row[1] for row in result}
                
                return stats
                
        except Exception as e:
            logger.error(f"Failed to get event type stats: {e}")
            return {}
    
    def get_processing_stats(self, hours: int = 24) -> Dict:
        """Get event processing statistics."""
        try:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            
            with get_session() as session:
                event_store = EventStore(session)
                
                from sqlalchemy import select, func
                
                # Total events
                total_query = select(func.count(EventRecord.id)).where(
                    EventRecord.timestamp >= cutoff
                )
                total = session.execute(total_query).scalar()
                
                # Processed events
                processed_query = select(func.count(EventRecord.id)).where(
                    EventRecord.timestamp >= cutoff,
                    EventRecord.processed == True
                )
                processed = session.execute(processed_query).scalar()
                
                # Failed events
                failed_query = select(func.count(EventRecord.id)).where(
                    EventRecord.timestamp >= cutoff,
                    EventRecord.error.isnot(None)
                )
                failed = session.execute(failed_query).scalar()
                
                # Average processing time
                avg_time_query = select(
                    func.avg(
                        func.extract("epoch", EventRecord.processed_at - EventRecord.timestamp)
                    )
                ).where(
                    EventRecord.timestamp >= cutoff,
                    EventRecord.processed == True
                )
                avg_time = session.execute(avg_time_query).scalar() or 0
                
                return {
                    "total_events": total or 0,
                    "processed_events": processed or 0,
                    "failed_events": failed or 0,
                    "pending_events": (total or 0) - (processed or 0),
                    "success_rate": (processed / total * 100) if total else 0,
                    "failure_rate": (failed / total * 100) if total else 0,
                    "avg_processing_time_seconds": float(avg_time),
                }
                
        except Exception as e:
            logger.error(f"Failed to get processing stats: {e}")
            return {}
    
    def get_dlq_stats(self) -> Dict:
        """Get dead letter queue statistics."""
        try:
            # Get DLQ stream info
            dlq_info = self.event_bus.redis_client.xinfo_stream(
                self.event_bus.config.dlq_stream_name
            )
            
            return {
                "length": dlq_info.get("length", 0),
                "first_entry": dlq_info.get("first-entry"),
                "last_entry": dlq_info.get("last-entry"),
            }
        except Exception as e:
            logger.error(f"Failed to get DLQ stats: {e}")
            return {"length": 0}
    
    def get_health_status(self) -> Dict:
        """Get overall health status."""
        try:
            # Check Redis connection
            self.event_bus.redis_client.ping()
            redis_healthy = True
        except Exception:
            redis_healthy = False
        
        # Get processing stats
        stats = self.get_processing_stats(hours=1)
        
        # Determine health
        is_healthy = (
            redis_healthy and
            stats.get("success_rate", 0) > 95 and
            stats.get("pending_events", 0) < 1000
        )
        
        return {
            "healthy": is_healthy,
            "redis_connected": redis_healthy,
            "success_rate": stats.get("success_rate", 0),
            "pending_events": stats.get("pending_events", 0),
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def get_comprehensive_report(self) -> Dict:
        """Get comprehensive monitoring report."""
        return {
            "health": self.get_health_status(),
            "stream_metrics": self.get_stream_metrics(),
            "processing_stats": self.get_processing_stats(hours=24),
            "event_type_stats": self.get_event_type_stats(hours=24),
            "dlq_stats": self.get_dlq_stats(),
        }
