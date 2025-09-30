# Procur Observability & Monitoring

## Overview

Comprehensive observability system with structured logging, distributed tracing, metrics collection, error tracking, APM, dashboards, and alerting for production monitoring.

## Features

✅ **Structured Logging** - JSON format with context fields
✅ **Distributed Tracing** - OpenTelemetry with Jaeger
✅ **Metrics Collection** - Prometheus with custom metrics
✅ **Error Tracking** - Sentry integration with context
✅ **APM** - Application performance monitoring
✅ **Dashboards** - Grafana dashboards for key metrics
✅ **Alerting** - Prometheus alerts for critical events
✅ **Auto-instrumentation** - FastAPI, SQLAlchemy, Redis, Celery

## Quick Start

### 1. Install Dependencies

```bash
pip install -e .
```

New dependencies:
- `opentelemetry-api>=1.21` - Tracing API
- `opentelemetry-sdk>=1.21` - Tracing SDK
- `opentelemetry-instrumentation-*` - Auto-instrumentation
- `prometheus-client>=0.19` - Metrics
- `sentry-sdk[fastapi]>=1.39` - Error tracking
- `python-json-logger>=2.0` - JSON logging

### 2. Configure Observability

Update `.env`:

```env
# Logging
PROCUR_LOG_LEVEL=INFO
PROCUR_LOG_FORMAT=json

# Tracing
PROCUR_TRACING_ENABLED=true
PROCUR_JAEGER_HOST=localhost
PROCUR_JAEGER_PORT=6831

# Metrics
PROCUR_METRICS_ENABLED=true
PROCUR_METRICS_PORT=9090

# Error Tracking
PROCUR_SENTRY_DSN=https://your-sentry-dsn
PROCUR_SENTRY_ENVIRONMENT=production
```

### 3. Start Monitoring Stack

```bash
./scripts/start_monitoring.sh
```

This starts:
- Jaeger (tracing) at http://localhost:16686
- Prometheus (metrics) at http://localhost:9090
- Grafana (dashboards) at http://localhost:3000

### 4. Initialize Observability

```python
from procur.observability.config import setup_observability

# Setup everything
setup_observability()
```

## Structured Logging

### Features
- JSON format for machine parsing
- Context fields (user_id, negotiation_id, etc.)
- Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- File and console output

### Usage

```python
from procur.observability import setup_logging, get_logger

# Setup
setup_logging(level="INFO", json_format=True)

logger = get_logger(__name__)

# Basic logging
logger.info("Negotiation started")

# With context
logger.info("Offer received", extra={
    "negotiation_id": "neg-001",
    "vendor": "Salesforce",
    "user_id": 123,
    "amount": 50000.0,
})

# Context manager
from procur.observability.logging import LogContext

with LogContext(logger, negotiation_id="neg-001"):
    logger.info("Round 1 started")
    logger.info("Offer sent")
```

### Log Format

```json
{
  "timestamp": "2025-01-15T10:30:00",
  "level": "INFO",
  "logger": "procur.agents.buyer",
  "message": "Offer received",
  "negotiation_id": "neg-001",
  "vendor": "Salesforce",
  "user_id": 123,
  "amount": 50000.0,
  "module": "buyer",
  "function": "process_offer",
  "line": 145
}
```

## Distributed Tracing

### Features
- OpenTelemetry standard
- Jaeger backend
- Auto-instrumentation for FastAPI, SQLAlchemy, Redis
- Custom spans and attributes

### Usage

```python
from procur.observability import setup_tracing, trace_function, get_tracer

# Setup
setup_tracing(
    service_name="procur",
    jaeger_host="localhost",
    jaeger_port=6831,
)

# Decorator
@trace_function(name="process_negotiation", attributes={"vendor": "salesforce"})
def negotiate(negotiation_id):
    # Function is automatically traced
    pass

# Manual tracing
from procur.observability.tracing import TracingContext

tracer = get_tracer(__name__)

with TracingContext("negotiation_round", tracer, {"round": 1}):
    # Code is traced
    pass

# Add attributes to current span
from procur.observability.tracing import add_span_attributes

add_span_attributes(
    negotiation_id="neg-001",
    vendor="Salesforce",
    offer_amount=50000.0,
)
```

### View Traces

Open Jaeger UI at http://localhost:16686

- Search by service name: `procur`
- Filter by operation: `process_negotiation`
- View trace timeline and spans
- Inspect span attributes and events

## Metrics Collection

### Available Metrics

**Negotiation Metrics:**
- `procur_negotiation_started_total` - Total negotiations started
- `procur_negotiation_completed_total` - Total completed (by outcome)
- `procur_negotiation_duration_seconds` - Duration histogram
- `procur_negotiation_rounds` - Rounds histogram
- `procur_cost_savings_dollars` - Cost savings summary
- `procur_active_negotiations` - Current active negotiations

**Integration Metrics:**
- `procur_integration_calls_total` - API calls by integration
- `procur_integration_latency_seconds` - Latency histogram
- `procur_integration_errors_total` - Errors by integration

**Event Metrics:**
- `procur_events_published_total` - Events published
- `procur_events_processed_total` - Events processed
- `procur_event_processing_duration_seconds` - Processing time

**API Metrics:**
- `procur_http_requests_total` - HTTP requests
- `procur_http_request_duration_seconds` - Request duration

### Usage

```python
from procur.observability import setup_metrics, get_metrics_collector

# Setup
metrics = setup_metrics()

# Track negotiation
metrics.track_negotiation_started("Salesforce", "CRM")

# Complete negotiation
metrics.track_negotiation_completed(
    vendor="Salesforce",
    category="CRM",
    outcome="success",
    duration_seconds=300.5,
    rounds=3,
    cost_savings=5000.0,
)

# Track integration call
metrics.track_integration_call(
    integration="slack",
    method="send_message",
    status="success",
    duration_seconds=0.5,
)

# Track event
metrics.track_event(
    event_type="negotiation.started",
    status="published",
)
```

### Expose Metrics

```python
from fastapi import FastAPI, Response
from procur.observability.metrics import get_metrics_collector, CONTENT_TYPE_LATEST

app = FastAPI()

@app.get("/metrics")
def metrics():
    collector = get_metrics_collector()
    return Response(
        content=collector.get_metrics(),
        media_type=CONTENT_TYPE_LATEST,
    )
```

## Error Tracking

### Features
- Sentry integration
- Automatic exception capture
- Context and breadcrumbs
- User tracking
- Release tracking

### Usage

```python
from procur.observability import setup_error_tracking
from procur.observability.errors import (
    capture_exception,
    capture_message,
    set_user_context,
    add_breadcrumb,
)

# Setup
setup_error_tracking(
    dsn="https://your-sentry-dsn",
    environment="production",
    release="1.0.0",
)

# Set user context
set_user_context(
    user_id=123,
    email="user@example.com",
    organization_id="acme-corp",
)

# Add breadcrumb
add_breadcrumb(
    message="Negotiation started",
    category="negotiation",
    data={"negotiation_id": "neg-001"},
)

# Capture exception
try:
    risky_operation()
except Exception as e:
    capture_exception(e, context={
        "negotiation_id": "neg-001",
        "vendor": "Salesforce",
    })

# Capture message
capture_message(
    "Unusual negotiation pattern detected",
    level="warning",
    context={"pattern": "rapid_concessions"},
)
```

## Application Performance Monitoring

### Usage

```python
from procur.observability.apm import get_apm_monitor

apm = get_apm_monitor()

# Track negotiation
with apm.track_negotiation("neg-001", "Salesforce", "CRM"):
    # Negotiation logic
    # Automatically tracks duration, rounds, outcome
    pass

# Track integration call
with apm.track_integration_call("slack", "send_message"):
    slack.send_message(...)

# Track event processing
with apm.track_event_processing("negotiation.started"):
    process_event(event)
```

## Dashboards

### Negotiation Dashboard

Metrics:
- Success rate
- Active negotiations
- Average duration
- Total cost savings
- Negotiations by vendor
- Rounds distribution
- Cost savings by category
- Outcome breakdown

### System Health Dashboard

Metrics:
- HTTP request rate
- Request duration (p95)
- Integration latency
- Integration errors
- Event processing rate
- Database connections

### Integration Dashboard

Metrics:
- Integration success rate
- Slack notifications sent
- DocuSign envelopes created
- Calls by service
- Latency by service

### Import Dashboards

```python
from procur.observability.dashboards import export_dashboards_to_files

# Export to dashboards/
export_dashboards_to_files()
```

Import in Grafana:
1. Open Grafana at http://localhost:3000
2. Go to Dashboards → Import
3. Upload JSON files from `dashboards/`

## Alerting

### Alert Rules

**Negotiation Alerts:**
- High failure rate (>20%)
- Negotiations stalled
- Low cost savings

**Integration Alerts:**
- High error rate (>10%)
- High latency (>5s)
- Slack integration down
- DocuSign integration down
- ERP integration down

**System Alerts:**
- High API latency (>2s)
- High API error rate (>5%)
- Event processing backlog
- High event failure rate
- Database connection pool exhausted

**Security Alerts:**
- Unauthorized access attempts
- Suspicious activity
- Multiple failed logins

### Configure Alerts

```bash
# Export alerting rules
python -c "from procur.observability.alerts import export_alerting_rules; export_alerting_rules()"

# Configure Prometheus
# Add to prometheus.yml:
rule_files:
  - "monitoring/alerting_rules.yml"

# Restart Prometheus
docker restart procur-prometheus
```

### Alertmanager Configuration

```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'default'
  
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
    
    - match:
        severity: warning
      receiver: 'slack'

receivers:
  - name: 'default'
    email_configs:
      - to: 'ops@procur.ai'
  
  - name: 'slack'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#alerts'
  
  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_KEY'
```

## Production Deployment

### 1. Infrastructure Setup

```bash
# Start monitoring stack
./scripts/start_monitoring.sh

# Or use docker-compose
docker-compose -f monitoring/docker-compose.yml up -d
```

### 2. Application Configuration

```python
# In your FastAPI app
from procur.observability.config import setup_observability

@app.on_event("startup")
async def startup():
    setup_observability()
```

### 3. Metrics Endpoint

```python
from fastapi import FastAPI
from procur.observability.metrics import get_metrics_collector, CONTENT_TYPE_LATEST

app = FastAPI()

@app.get("/metrics")
def metrics():
    collector = get_metrics_collector()
    return Response(
        content=collector.get_metrics(),
        media_type=CONTENT_TYPE_LATEST,
    )
```

### 4. Health Check

```python
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }
```

## Best Practices

### 1. Logging

- Use structured logging with JSON format
- Add context fields (user_id, negotiation_id, etc.)
- Log at appropriate levels
- Don't log sensitive data (passwords, API keys)

### 2. Tracing

- Trace critical paths (negotiations, integrations)
- Add meaningful span names
- Include relevant attributes
- Don't trace every function (overhead)

### 3. Metrics

- Track business metrics (cost savings, success rate)
- Track technical metrics (latency, errors)
- Use appropriate metric types (Counter, Gauge, Histogram)
- Add labels for filtering

### 4. Error Tracking

- Capture exceptions with context
- Set user context for debugging
- Add breadcrumbs for event trail
- Filter noise (don't capture expected errors)

### 5. Alerting

- Alert on symptoms, not causes
- Set appropriate thresholds
- Avoid alert fatigue
- Include runbooks in annotations

## Troubleshooting

### Jaeger Not Receiving Traces

- Check Jaeger is running: `docker ps | grep jaeger`
- Verify port 6831/udp is open
- Check tracing is enabled in config
- Verify service name matches

### Prometheus Not Scraping Metrics

- Check `/metrics` endpoint is accessible
- Verify Prometheus config has correct target
- Check Prometheus logs: `docker logs procur-prometheus`
- Verify metrics are being generated

### Sentry Not Capturing Errors

- Verify DSN is correct
- Check Sentry project settings
- Verify sample rate is not 0
- Check network connectivity

### High Memory Usage

- Reduce trace sample rate
- Reduce metrics cardinality (fewer labels)
- Increase scrape interval
- Set retention limits

## Monitoring Checklist

- [ ] Structured logging configured
- [ ] Tracing enabled and working
- [ ] Metrics exposed at `/metrics`
- [ ] Sentry DSN configured
- [ ] Dashboards imported in Grafana
- [ ] Alert rules configured
- [ ] Alertmanager configured
- [ ] Health check endpoint working
- [ ] Runbooks created for alerts
- [ ] Team trained on dashboards

## Support

- **Documentation**: This file
- **Examples**: `examples/observability_example.py`
- **Dashboards**: `dashboards/`
- **Alerts**: `monitoring/alerting_rules.yml`

## License

Part of the Procur procurement automation platform.
