#!/bin/bash
# Start Celery workers for async task processing

set -e

echo "Starting Procur Celery workers..."

# Start negotiation worker
celery -A src.procur.workers.celery_app worker \
  --queue=negotiation \
  --concurrency=4 \
  --loglevel=info \
  --hostname=negotiation@%h &

# Start enrichment worker
celery -A src.procur.workers.celery_app worker \
  --queue=enrichment \
  --concurrency=2 \
  --loglevel=info \
  --hostname=enrichment@%h &

# Start contracts worker
celery -A src.procur.workers.celery_app worker \
  --queue=contracts \
  --concurrency=2 \
  --loglevel=info \
  --hostname=contracts@%h &

# Start notifications worker
celery -A src.procur.workers.celery_app worker \
  --queue=notifications \
  --concurrency=4 \
  --loglevel=info \
  --hostname=notifications@%h &

# Start beat scheduler for periodic tasks
celery -A src.procur.workers.celery_app beat \
  --loglevel=info &

echo "✅ All workers started"
echo ""
echo "Monitor workers with Flower:"
echo "  celery -A src.procur.workers.celery_app flower --port=5555"
echo ""
echo "Stop all workers:"
echo "  pkill -f 'celery worker'"
