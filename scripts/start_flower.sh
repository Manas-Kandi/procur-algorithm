#!/bin/bash
# Start Flower monitoring dashboard for Celery

set -e

echo "Starting Flower monitoring dashboard..."

celery -A src.procur.workers.celery_app flower \
  --port=5555 \
  --broker_api=http://localhost:6379

echo "✅ Flower started at http://localhost:5555"
