# Procur Platform - Operational Setup Guide

This guide covers the complete setup process to transform Procur from a development blueprint into a fully operational platform.

## 🎯 Overview

The platform now includes:
- ✅ Fixed database session handling (works as both FastAPI dependency and context manager)
- ✅ Complete Alembic migrations for all models
- ✅ Fully wired agent workflows in Celery tasks
- ✅ Consolidated event bus (Redis-backed, deprecated in-memory version)
- ✅ Integration tests for API/DB/worker flows
- ✅ Observability hooks throughout the codebase

## 📋 Prerequisites

1. **PostgreSQL 12+**
   ```bash
   # macOS
   brew install postgresql@14
   brew services start postgresql@14
   
   # Ubuntu/Debian
   sudo apt-get install postgresql-14
   sudo systemctl start postgresql
   ```

2. **Redis 6+**
   ```bash
   # macOS
   brew install redis
   brew services start redis
   
   # Ubuntu/Debian
   sudo apt-get install redis-server
   sudo systemctl start redis
   ```

3. **Python 3.11+**
   ```bash
   python --version  # Should be 3.11 or higher
   ```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# At minimum, configure:
# - PROCUR_DB_* (database credentials)
# - NVIDIA_API_KEY (for LLM integration)
# - PROCUR_EVENT_REDIS_* (Redis connection)
```

### 2. Database Initialization

```bash
# Make setup script executable
chmod +x scripts/setup_database.sh

# Run database setup (creates user, database, grants privileges)
bash scripts/setup_database.sh

# Run migrations
alembic upgrade head
```

### 3. Start Services

```bash
# Terminal 1: Start API server
python run_api.py

# Terminal 2: Start Celery workers
bash scripts/start_workers.sh

# Terminal 3: Start Flower (Celery monitoring)
bash scripts/start_flower.sh
```

### 4. Verify Installation

```bash
# Check API health
curl http://localhost:8000/health

# Check database connection
curl http://localhost:8000/ready

# Check Flower dashboard
open http://localhost:5555
```

## 🏗️ Architecture

### Database Layer
- **Session Management**: Fixed `get_session()` works as both FastAPI dependency and context manager
- **Migrations**: Complete Alembic migrations in `alembic/versions/`
- **Repositories**: Full CRUD operations for all entities

### Agent Workflows
All Celery tasks now invoke real agent logic:

1. **`process_negotiation_round`**
   - Initializes BuyerAgent and SellerAgent
   - Executes negotiation round with opponent modeling
   - Updates negotiation session with history
   - Publishes events to Redis

2. **`enrich_vendor_data`**
   - Scrapes G2, pricing, and compliance data
   - Updates vendor profiles with enriched information
   - Tracks confidence scores

3. **`generate_contract`**
   - Uses LLM to generate contract documents
   - Stores terms and conditions
   - Publishes completion events

4. **`send_notification`**
   - Supports email, Slack, and webhook notifications
   - Integrates with real services (SendGrid, Slack API)

### Event Bus
- **Production**: Redis-backed event bus (`src/procur/events/bus.py`)
- **Development**: In-memory bus deprecated with warnings
- **Features**: Event sourcing, DLQ, consumer groups

### Observability
- **Metrics**: Prometheus-compatible metrics via `track_metric()`
- **Logging**: Structured JSON logging with correlation IDs
- **Tracing**: OpenTelemetry integration ready

## 🧪 Testing

### Run Integration Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest tests/integration/ -v

# Run with coverage
pytest tests/integration/ --cov=src/procur --cov-report=html
```

### Test Individual Components
```bash
# Test API flows
pytest tests/integration/test_api_flows.py -v

# Test worker flows
pytest tests/integration/test_worker_flows.py -v

# Test negotiation logic
pytest tests/test_negotiation_logic.py -v
```

## 📊 Monitoring

### Celery Tasks
- **Flower Dashboard**: http://localhost:5555
- **Metrics**: Task success/failure rates, execution times
- **Queues**: Monitor queue depths and consumer lag

### Database
```bash
# Check connection pool
psql -h localhost -U procur_user -d procur -c "SELECT * FROM pg_stat_activity;"

# Check table sizes
psql -h localhost -U procur_user -d procur -c "
  SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
  FROM pg_tables WHERE schemaname = 'public';"
```

### Redis
```bash
# Check Redis connection
redis-cli ping

# Monitor event stream
redis-cli XINFO STREAM procur:events

# Check consumer groups
redis-cli XINFO GROUPS procur:events
```

## 🔧 Configuration

### Database Config
All database settings use `PROCUR_DB_*` prefix:
- `PROCUR_DB_HOST`: Database host (default: localhost)
- `PROCUR_DB_PORT`: Database port (default: 5432)
- `PROCUR_DB_DATABASE`: Database name (default: procur)
- `PROCUR_DB_USERNAME`: Database user
- `PROCUR_DB_PASSWORD`: Database password

### Event Bus Config
Redis event bus settings use `PROCUR_EVENT_*` prefix:
- `PROCUR_EVENT_REDIS_HOST`: Redis host
- `PROCUR_EVENT_REDIS_PORT`: Redis port
- `PROCUR_EVENT_EVENT_STREAM_NAME`: Event stream name
- `PROCUR_EVENT_DLQ_ENABLED`: Enable dead letter queue

### API Config
API settings use `PROCUR_API_*` prefix:
- `PROCUR_API_HOST`: API host (default: 0.0.0.0)
- `PROCUR_API_PORT`: API port (default: 8000)
- `PROCUR_API_WORKERS`: Number of workers
- `PROCUR_API_SECRET_KEY`: JWT secret key

## 🔐 Security

### Secrets Management
Never commit secrets to git. Use environment variables or secret managers:

```bash
# Development: Use .env file (gitignored)
cp .env.example .env
# Edit .env with real credentials

# Production: Use secret manager
# - AWS Secrets Manager
# - HashiCorp Vault
# - Kubernetes Secrets
```

### API Keys
Remove hard-coded API keys from examples:
```python
# ❌ Bad
api_key = "nvapi-abc123..."

# ✅ Good
from src.procur.config import get_config
api_key = get_config().nvidia_api_key
```

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Check user exists
psql -U postgres -c "\du"

# Check database exists
psql -U postgres -c "\l"

# Test connection
psql -h localhost -U procur_user -d procur
```

### Migration Issues
```bash
# Check current migration version
alembic current

# Check migration history
alembic history

# Rollback one migration
alembic downgrade -1

# Upgrade to latest
alembic upgrade head
```

### Worker Issues
```bash
# Check Celery workers are running
celery -A src.procur.workers.celery_app inspect active

# Check task queue
celery -A src.procur.workers.celery_app inspect reserved

# Purge all tasks
celery -A src.procur.workers.celery_app purge
```

### Redis Issues
```bash
# Check Redis is running
redis-cli ping

# Check memory usage
redis-cli INFO memory

# Clear all data (CAUTION!)
redis-cli FLUSHALL
```

## 📈 Performance Tuning

### Database
```sql
-- Add indexes for common queries
CREATE INDEX idx_requests_user_status ON requests(user_id, status);
CREATE INDEX idx_negotiations_status_round ON negotiation_sessions(status, current_round);
CREATE INDEX idx_offers_request_vendor ON offers(request_id, vendor_id);
```

### Celery
```python
# Adjust worker concurrency
celery -A src.procur.workers.celery_app worker --concurrency=8

# Use prefork pool for CPU-bound tasks
celery -A src.procur.workers.celery_app worker --pool=prefork

# Use gevent for I/O-bound tasks
celery -A src.procur.workers.celery_app worker --pool=gevent --concurrency=100
```

### Redis
```bash
# Increase max memory
redis-cli CONFIG SET maxmemory 2gb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

## 🚢 Deployment

### Docker Compose
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: procur
      POSTGRES_USER: procur_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
  
  api:
    build: .
    command: python run_api.py
    environment:
      - PROCUR_DB_HOST=postgres
      - PROCUR_EVENT_REDIS_HOST=redis
    depends_on:
      - postgres
      - redis
  
  worker:
    build: .
    command: celery -A src.procur.workers.celery_app worker
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:
  redis_data:
```

### Kubernetes
See `k8s/` directory for Kubernetes manifests (coming soon).

## 📚 Additional Resources

- [Architecture Documentation](docs/architecture.md)
- [API Documentation](API_README.md)
- [Database Schema](DATABASE_README.md)
- [Event Bus Guide](EVENT_BUS_README.md)
- [Authentication Guide](AUTHENTICATION_README.md)

## 🤝 Contributing

1. Run tests before committing
2. Follow code style guidelines
3. Update documentation for new features
4. Add integration tests for new workflows

## 📝 License

Copyright © 2025 Procur. All rights reserved.
