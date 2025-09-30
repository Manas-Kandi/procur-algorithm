#!/usr/bin/env python
"""
Example demonstrating event bus usage.

This example shows how to:
1. Publish events to the event bus
2. Consume events with workers
3. Monitor event processing
4. Handle failed events with DLQ
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from procur.events import EventPublisher, EventConsumer, EventType
from procur.events.monitoring import EventMonitor
from procur.events.schemas import Event, EventPriority


def main():
    """Run event bus example."""
    print("=" * 80)
    print("Procur Event Bus - Usage Example")
    print("=" * 80)
    
    # Initialize publisher
    publisher = EventPublisher()
    
    # 1. Publish various events
    print("\n1. Publishing events...")
    
    # Publish request created event
    event_id1 = publisher.publish_request_created(
        request_id="req-001",
        user_id=1,
        organization_id="acme-corp",
        description="Need CRM for 50 users",
        budget_max=75000.0,
    )
    print(f"   ✅ Published request created event: {event_id1}")
    
    # Publish negotiation started event
    event_id2 = publisher.publish_negotiation_started(
        negotiation_id="neg-001",
        request_id="req-001",
        vendor_id="salesforce",
        user_id=1,
        correlation_id="corr-001",
    )
    print(f"   ✅ Published negotiation started event: {event_id2}")
    
    # Publish vendor enrichment event
    event_id3 = publisher.publish_vendor_enrichment_started(
        vendor_id="salesforce",
        category="crm",
    )
    print(f"   ✅ Published vendor enrichment event: {event_id3}")
    
    # Publish contract generation event
    event_id4 = publisher.publish_contract_generation_started(
        contract_id="contract-001",
        request_id="req-001",
        vendor_id="salesforce",
        correlation_id="corr-001",
    )
    print(f"   ✅ Published contract generation event: {event_id4}")
    
    # Publish notification event
    event_id5 = publisher.publish_notification(
        notification_type="email",
        recipient="buyer@acme.com",
        subject="Negotiation Started",
        message="Your negotiation with Salesforce has started",
    )
    print(f"   ✅ Published notification event: {event_id5}")
    
    # 2. Monitor events
    print("\n2. Monitoring event bus...")
    monitor = EventMonitor()
    
    # Get stream metrics
    stream_metrics = monitor.get_stream_metrics()
    print(f"   • Stream length: {stream_metrics.get('length', 0)} events")
    
    # Get event type stats
    type_stats = monitor.get_event_type_stats(hours=1)
    print(f"   • Event types (last hour):")
    for event_type, count in type_stats.items():
        print(f"      - {event_type}: {count}")
    
    # Get processing stats
    processing_stats = monitor.get_processing_stats(hours=1)
    print(f"   • Processing stats:")
    print(f"      - Total events: {processing_stats.get('total_events', 0)}")
    print(f"      - Processed: {processing_stats.get('processed_events', 0)}")
    print(f"      - Failed: {processing_stats.get('failed_events', 0)}")
    print(f"      - Success rate: {processing_stats.get('success_rate', 0):.1f}%")
    
    # Get health status
    health = monitor.get_health_status()
    print(f"   • Health: {'✅ Healthy' if health['healthy'] else '❌ Unhealthy'}")
    print(f"      - Redis connected: {health['redis_connected']}")
    print(f"      - Pending events: {health['pending_events']}")
    
    # 3. Example: Create event consumer
    print("\n3. Event consumer example...")
    print("   To consume events, run:")
    print("   ```python")
    print("   from procur.events import EventConsumer, EventType")
    print("   ")
    print("   def handle_negotiation(event):")
    print("       print(f'Handling negotiation: {event.data}')")
    print("   ")
    print("   consumer = EventConsumer('my-consumer')")
    print("   consumer.register_handler(EventType.NEGOTIATION_STARTED, handle_negotiation)")
    print("   consumer.start()")
    print("   ```")
    
    # 4. Celery workers
    print("\n4. Celery workers...")
    print("   Start workers to process events asynchronously:")
    print("   ```bash")
    print("   # Start all workers")
    print("   ./scripts/start_workers.sh")
    print("   ")
    print("   # Or start individual workers")
    print("   celery -A src.procur.workers.celery_app worker --queue=negotiation")
    print("   celery -A src.procur.workers.celery_app worker --queue=enrichment")
    print("   celery -A src.procur.workers.celery_app worker --queue=contracts")
    print("   celery -A src.procur.workers.celery_app worker --queue=notifications")
    print("   ```")
    
    # 5. Monitoring with Flower
    print("\n5. Monitor workers with Flower...")
    print("   ```bash")
    print("   ./scripts/start_flower.sh")
    print("   # Open http://localhost:5555")
    print("   ```")
    
    print("\n" + "=" * 80)
    print("✅ Event Bus Example Complete!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Start Redis: redis-server")
    print("2. Start workers: ./scripts/start_workers.sh")
    print("3. Monitor with Flower: ./scripts/start_flower.sh")
    print("4. Publish events and watch them process!")


if __name__ == "__main__":
    main()
