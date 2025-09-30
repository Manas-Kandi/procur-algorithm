#!/bin/bash
# Start monitoring stack (Jaeger, Prometheus, Grafana)

set -e

echo "Starting Procur monitoring stack..."

# Start Jaeger (all-in-one)
echo "Starting Jaeger..."
docker run -d \
  --name procur-jaeger \
  -p 5775:5775/udp \
  -p 6831:6831/udp \
  -p 6832:6832/udp \
  -p 5778:5778 \
  -p 16686:16686 \
  -p 14268:14268 \
  -p 14250:14250 \
  -p 9411:9411 \
  jaegertracing/all-in-one:latest

# Start Prometheus
echo "Starting Prometheus..."
docker run -d \
  --name procur-prometheus \
  -p 9090:9090 \
  -v $(pwd)/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml \
  -v $(pwd)/monitoring/alerting_rules.yml:/etc/prometheus/alerting_rules.yml \
  prom/prometheus:latest

# Start Grafana
echo "Starting Grafana..."
docker run -d \
  --name procur-grafana \
  -p 3000:3000 \
  -e "GF_SECURITY_ADMIN_PASSWORD=admin" \
  grafana/grafana:latest

echo ""
echo "✅ Monitoring stack started!"
echo ""
echo "Access points:"
echo "  Jaeger UI:     http://localhost:16686"
echo "  Prometheus:    http://localhost:9090"
echo "  Grafana:       http://localhost:3000 (admin/admin)"
echo ""
echo "Stop monitoring:"
echo "  docker stop procur-jaeger procur-prometheus procur-grafana"
echo "  docker rm procur-jaeger procur-prometheus procur-grafana"
