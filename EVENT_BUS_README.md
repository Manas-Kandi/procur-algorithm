# Procur Event Bus System

## Overview

Production-ready event bus system with Redis Streams, Celery workers, event sourcing, dead letter queues, and comprehensive monitoring for async workflow processing.

## Features

✅ **Redis Streams** - Persistent, scalable event bus
✅ **Event Sourcing** - Complete audit trail in database
✅ **Celery Workers** - Async task processing with multiple queues
✅ **Dead Letter Queue** - Failed event handling and retry
✅ **Event Monitoring** - Real-time metrics and health checks
✅ **Flower Dashboard** - Visual monitoring of workers
✅ **Event Replay** - Replay events from event store
✅ **Correlation IDs** - Track related events across system
✅ **Priority Queues** - High-priority event processing
✅ **Auto-retry** - Configurable retry with exponential backoff

## Architecture

### Components

1. **Event Bus** (`src/procur/events/bus.py`)
   - Redis Streams for event storage
   - Pub/Sub for real-time notifications
   - Consumer groups for load balancing
   - Dead letter queue for failed events

2. **Event Store** (`src/procur/events/store.py`)
   - PostgreSQL persistence for audit trail
   - Event sourcing capabilities
   - Query by type, user, organization, correlation ID
   - Automatic cleanup of old events

3. **Event Publisher** (`src/procur/events/publisher.py`)
   - Publish events to bus and store
   - Correlation ID tracking
   - Priority levels
   - Helper methods for common events

4. **Event Consumer** (`src/procur/events/consumer.py`)
   - Consume events from Redis Streams
   - Register event handlers
   - Automatic acknowledgment
   - Retry and DLQ handling

5. **Celery Workers** (`src/procur/workers/`)
   - Async task processing
   - Multiple queues (negotiation, enrichment, contracts, notifications)
   - Periodic tasks
   - Task routing and priorities

6. **Event Monitoring** (`src/procur/events/monitoring.py`)
   - Stream metrics
   - Processing statistics
   - Health checks
   - DLQ monitoring

## Quick Start

### 1. Install Dependencies

```bash
pip install -e .
```

New dependencies:
- `redis>=5.0` - Redis client
- `celery>=5.3` - Distributed task queue
- `kombu>=5.3` - Messaging library
- `flower>=2.0` - Celery monitoring

### 2. Start Redis

```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# Docker
docker run -d -p 6379:6379 redis:latest
```

### 3. Configure Event Bus

Update `.env`:

```env
# Redis Configuration
PROCUR_EVENT_REDIS_HOST=localhost
PROCUR_EVENT_REDIS_PORT=6379
PROCUR_EVENT_REDIS_DB=0
PROCUR_EVENT_REDIS_PASSWORD=

# Event Stream Settings
PROCUR_EVENT_EVENT_STREAM_NAME=procur:events
PROCUR_EVENT_EVENT_CONSUMER_GROUP=procur-workers
PROCUR_EVENT_EVENT_BATCH_SIZE=10

# Dead Letter Queue
PROCUR_EVENT_DLQ_ENABLED=true
PROCUR_EVENT_DLQ_MAX_RETRIES=3

# Event Sourcing
PROCUR_EVENT_EVENT_SOURCING_ENABLED=true
PROCUR_EVENT_EVENT_STORE_RETENTION_DAYS=90
```

### 4. Run Database Migration

```bash
# Create migration for event store
alembic revision --autogenerate -m "Add event store table"

# Apply migration
alembic upgrade head
```

### 5. Start Workers

```bash
# Start all workers
./scripts/start_workers.sh

# Or start individual workers
celery -A src.procur.workers.celery_app worker --queue=negotiation --concurrency=4
celery -A src.procur.workers.celery_app worker --queue=enrichment --concurrency=2
celery -A src.procur.workers.celery_app worker --queue=contracts --concurrency=2
celery -A src.procur.workers.celery_app worker --queue=notifications --concurrency=4

# Start beat scheduler for periodic tasks
celery -A src.procur.workers.celery_app beat
```

### 6. Monitor with Flower

```bash
./scripts/start_flower.sh
# Open http://localhost:5555
```

## Usage

### Publishing Events

```python
from procur.events import EventPublisher

publisher = EventPublisher()

# Publish request created event
event_id = publisher.publish_request_created(
    request_id="req-001",
    user_id=1,
    organization_id="acme-corp",
    description="Need CRM",
    budget_max=50000.0,
)

# Publish negotiation started event
event_id = publisher.publish_negotiation_started(
    negotiation_id="neg-001",
    request_id="req-001",
    vendor_id="salesforce",
    user_id=1,
    correlation_id="corr-001",  # Track related events
)

# Publish custom event
event_id = publisher.publish(
    event_type=EventType.VENDOR_ENRICHMENT_STARTED,
    data={"vendor_id": "salesforce", "category": "crm"},
    priority=EventPriority.HIGH,
)
```

### Consuming Events

```python
from procur.events import EventConsumer, EventType

def handle_negotiation(event):
    """Handle negotiation event."""
    print(f"Processing negotiation: {event.data}")
    # Your logic here

# Create consumer
consumer = EventConsumer("my-consumer")

# Register handlers
consumer.register_handler(EventType.NEGOTIATION_STARTED, handle_negotiation)

# Start consuming
consumer.start(
    event_types=[EventType.NEGOTIATION_STARTED],
    batch_size=10,
)
```

### Celery Tasks

```python
from procur.workers.tasks import (
    process_negotiation_round,
    enrich_vendor_data,
    generate_contract,
    send_notification,
)

# Call tasks asynchronously
result = process_negotiation_round.delay(
    negotiation_id="neg-001",
    round_number=1,
    correlation_id="corr-001",
)

# Wait for result
result.get(timeout=10)

# Call task with ETA
from datetime import datetime, timedelta
eta = datetime.utcnow() + timedelta(minutes=5)
enrich_vendor_data.apply_async(
    args=["salesforce", "crm"],
    eta=eta,
)
```

### Monitoring

```python
from procur.events.monitoring import EventMonitor

monitor = EventMonitor()

# Get health status
health = monitor.get_health_status()
print(f"Healthy: {health['healthy']}")
print(f"Success rate: {health['success_rate']}%")

# Get processing stats
stats = monitor.get_processing_stats(hours=24)
print(f"Total events: {stats['total_events']}")
print(f"Processed: {stats['processed_events']}")
print(f"Failed: {stats['failed_events']}")

# Get event type distribution
type_stats = monitor.get_event_type_stats(hours=24)
for event_type, count in type_stats.items():
    print(f"{event_type}: {count}")

# Get comprehensive report
report = monitor.get_comprehensive_report()
```

## Event Types

### Request Events
- `REQUEST_CREATED` - New request created
- `REQUEST_UPDATED` - Request updated
- `REQUEST_APPROVED` - Request approved
- `REQUEST_REJECTED` - Request rejected

### Vendor Events
- `VENDOR_CREATED` - New vendor added
- `VENDOR_UPDATED` - Vendor updated
- `VENDOR_ENRICHMENT_STARTED` - Enrichment started
- `VENDOR_ENRICHMENT_COMPLETED` - Enrichment completed
- `VENDOR_ENRICHMENT_FAILED` - Enrichment failed

### Negotiation Events
- `NEGOTIATION_STARTED` - Negotiation started
- `NEGOTIATION_ROUND_STARTED` - Round started
- `NEGOTIATION_ROUND_COMPLETED` - Round completed
- `NEGOTIATION_OFFER_RECEIVED` - Offer received
- `NEGOTIATION_COMPLETED` - Negotiation completed
- `NEGOTIATION_FAILED` - Negotiation failed

### Contract Events
- `CONTRACT_CREATED` - Contract created
- `CONTRACT_GENERATION_STARTED` - Generation started
- `CONTRACT_GENERATION_COMPLETED` - Generation completed
- `CONTRACT_SIGNED` - Contract signed
- `CONTRACT_ACTIVATED` - Contract activated

### Notification Events
- `NOTIFICATION_SEND` - Send notification
- `NOTIFICATION_EMAIL` - Email notification
- `NOTIFICATION_SLACK` - Slack notification
- `NOTIFICATION_WEBHOOK` - Webhook notification

### Integration Events
- `INTEGRATION_ERP_SYNC` - ERP synchronization
- `INTEGRATION_DOCUSIGN_SEND` - DocuSign send

### System Events
- `SYSTEM_ERROR` - System error
- `SYSTEM_WARNING` - System warning

## Worker Queues

### Negotiation Queue
- **Purpose**: Process negotiation rounds
- **Concurrency**: 4 workers
- **Tasks**: `process_negotiation_round`
- **Priority**: High

### Enrichment Queue
- **Purpose**: Enrich vendor data from external sources
- **Concurrency**: 2 workers
- **Tasks**: `enrich_vendor_data`
- **Priority**: Normal

### Contracts Queue
- **Purpose**: Generate contract documents
- **Concurrency**: 2 workers
- **Tasks**: `generate_contract`
- **Priority**: High

### Notifications Queue
- **Purpose**: Send notifications (email, Slack, webhooks)
- **Concurrency**: 4 workers
- **Tasks**: `send_notification`
- **Priority**: Normal

## Event Sourcing

All events are persisted to PostgreSQL for audit trail:

```python
from procur.events.store import EventStore
from procur.db import get_session

with get_session() as session:
    event_store = EventStore(session)
    
    # Get events by type
    events = event_store.get_events_by_type(
        EventType.NEGOTIATION_STARTED,
        limit=100,
    )
    
    # Get events by correlation ID
    related_events = event_store.get_events_by_correlation_id("corr-001")
    
    # Get events by user
    user_events = event_store.get_events_by_user(user_id=1)
    
    # Get events by organization
    org_events = event_store.get_events_by_organization("acme-corp")
    
    # Get unprocessed events
    pending = event_store.get_unprocessed_events()
```

## Dead Letter Queue

Failed events are automatically sent to DLQ after max retries:

```python
from procur.events import get_event_bus

event_bus = get_event_bus()

# Get DLQ stats
dlq_info = event_bus.redis_client.xinfo_stream("procur:dlq")
print(f"DLQ length: {dlq_info['length']}")

# Read from DLQ
dlq_events = event_bus.redis_client.xread(
    {"procur:dlq": "0"},
    count=10,
)

# Replay failed event
for stream, messages in dlq_events:
    for message_id, data in messages:
        # Fix issue and republish
        event_bus.publish(event)
        # Delete from DLQ
        event_bus.redis_client.xdel("procur:dlq", message_id)
```

## Monitoring & Alerting

### Health Check Endpoint

```python
from fastapi import APIRouter
from procur.events.monitoring import EventMonitor

router = APIRouter()

@router.get("/health/events")
def event_bus_health():
    monitor = EventMonitor()
    return monitor.get_health_status()
```

### Metrics

Monitor key metrics:
- **Event throughput**: Events/second
- **Processing latency**: Time to process events
- **Success rate**: % of successfully processed events
- **Queue depth**: Pending events per queue
- **Worker utilization**: Active/idle workers
- **DLQ size**: Failed events count

### Flower Dashboard

Access Flower at `http://localhost:5555`:
- View active workers
- Monitor task execution
- See task history
- Inspect task details
- Revoke tasks
- View worker stats

## Configuration

### Redis Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `redis_host` | localhost | Redis host |
| `redis_port` | 6379 | Redis port |
| `redis_db` | 0 | Redis database |
| `redis_password` | None | Redis password |
| `redis_ssl` | false | Use SSL |

### Event Stream Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `event_stream_name` | procur:events | Stream name |
| `event_consumer_group` | procur-workers | Consumer group |
| `event_batch_size` | 10 | Events per batch |
| `event_block_time` | 1000 | Block time (ms) |

### Dead Letter Queue

| Setting | Default | Description |
|---------|---------|-------------|
| `dlq_enabled` | true | Enable DLQ |
| `dlq_stream_name` | procur:dlq | DLQ stream name |
| `dlq_max_retries` | 3 | Max retries |

### Event Sourcing

| Setting | Default | Description |
|---------|---------|-------------|
| `event_sourcing_enabled` | true | Enable event sourcing |
| `event_store_retention_days` | 90 | Retention period |

## Best Practices

### 1. Use Correlation IDs

Track related events across the system:

```python
correlation_id = str(uuid4())

# All related events use same correlation ID
publisher.publish_negotiation_started(..., correlation_id=correlation_id)
publisher.publish_negotiation_round_started(..., correlation_id=correlation_id)
publisher.publish_contract_generation_started(..., correlation_id=correlation_id)
```

### 2. Set Appropriate Priorities

Use priority levels for critical events:

```python
publisher.publish(
    event_type=EventType.NEGOTIATION_ROUND_STARTED,
    data={...},
    priority=EventPriority.HIGH,  # Process immediately
)
```

### 3. Handle Failures Gracefully

Implement proper error handling in tasks:

```python
@celery_app.task(bind=True, max_retries=3)
def my_task(self, data):
    try:
        # Process data
        pass
    except Exception as e:
        # Log error
        logger.error(f"Task failed: {e}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
```

### 4. Monitor Event Processing

Set up alerts for:
- Success rate < 95%
- Pending events > 1000
- DLQ size > 100
- Worker failures

### 5. Clean Up Old Events

Periodic cleanup task runs daily:

```python
# Configured in celery_app.py
celery_app.conf.beat_schedule = {
    "cleanup-old-events-daily": {
        "task": "cleanup_old_events",
        "schedule": 86400.0,  # Daily
        "args": (90,),  # Keep 90 days
    },
}
```

## Troubleshooting

### Redis Connection Issues

```bash
# Check Redis is running
redis-cli ping
# Should return: PONG

# Check Redis info
redis-cli info

# Monitor Redis commands
redis-cli monitor
```

### Worker Not Processing Events

```bash
# Check worker status
celery -A src.procur.workers.celery_app inspect active

# Check registered tasks
celery -A src.procur.workers.celery_app inspect registered

# Purge all tasks
celery -A src.procur.workers.celery_app purge
```

### Events Stuck in DLQ

```python
# Inspect DLQ
from procur.events import get_event_bus

event_bus = get_event_bus()
dlq_events = event_bus.redis_client.xread({"procur:dlq": "0"}, count=100)

# Replay events
for stream, messages in dlq_events:
    for message_id, data in messages:
        # Fix and republish
        pass
```

### High Memory Usage

```bash
# Check Redis memory
redis-cli info memory

# Set max memory
redis-cli config set maxmemory 2gb
redis-cli config set maxmemory-policy allkeys-lru
```

## Production Deployment

### Redis Configuration

```bash
# redis.conf
maxmemory 4gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
appendonly yes
```

### Celery Workers

```bash
# Use supervisor or systemd
[program:celery-negotiation]
command=celery -A src.procur.workers.celery_app worker --queue=negotiation --concurrency=4
directory=/app
user=procur
autostart=true
autorestart=true
```

### Monitoring

- Set up Prometheus metrics export
- Configure Grafana dashboards
- Set up PagerDuty/Opsgenie alerts
- Monitor Redis with RedisInsight

## Support

- **Event Bus Documentation**: This file
- **API Documentation**: See `API_README.md`
- **Database Documentation**: See `DATABASE_README.md`
- **Issues**: GitHub Issues

## License

Part of the Procur procurement automation platform.
