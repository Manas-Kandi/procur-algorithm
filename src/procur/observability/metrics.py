"""Metrics collection with Prometheus."""

import logging
import time
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    Summary,
    CollectorRegistry,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Centralized metrics collector."""
    
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        """Initialize metrics collector."""
        self.registry = registry or CollectorRegistry()
        
        # Negotiation metrics
        self.negotiation_started = Counter(
            'procur_negotiation_started_total',
            'Total negotiations started',
            ['vendor', 'category'],
            registry=self.registry,
        )
        
        self.negotiation_completed = Counter(
            'procur_negotiation_completed_total',
            'Total negotiations completed',
            ['vendor', 'category', 'outcome'],
            registry=self.registry,
        )
        
        self.negotiation_duration = Histogram(
            'procur_negotiation_duration_seconds',
            'Negotiation duration in seconds',
            ['vendor', 'category'],
            buckets=[60, 300, 900, 1800, 3600, 7200, 14400],
            registry=self.registry,
        )
        
        self.negotiation_rounds = Histogram(
            'procur_negotiation_rounds',
            'Number of negotiation rounds',
            ['vendor', 'category'],
            buckets=[1, 2, 3, 4, 5, 7, 10, 15],
            registry=self.registry,
        )
        
        self.cost_savings = Summary(
            'procur_cost_savings_dollars',
            'Cost savings in dollars',
            ['vendor', 'category'],
            registry=self.registry,
        )
        
        self.negotiation_success_rate = Gauge(
            'procur_negotiation_success_rate',
            'Negotiation success rate (0-1)',
            ['vendor', 'category'],
            registry=self.registry,
        )
        
        # Request metrics
        self.requests_created = Counter(
            'procur_requests_created_total',
            'Total requests created',
            ['category', 'user'],
            registry=self.registry,
        )
        
        self.requests_approved = Counter(
            'procur_requests_approved_total',
            'Total requests approved',
            ['category'],
            registry=self.registry,
        )
        
        # Contract metrics
        self.contracts_signed = Counter(
            'procur_contracts_signed_total',
            'Total contracts signed',
            ['vendor', 'category'],
            registry=self.registry,
        )
        
        self.contract_value = Summary(
            'procur_contract_value_dollars',
            'Contract value in dollars',
            ['vendor', 'category'],
            registry=self.registry,
        )
        
        # Integration metrics
        self.integration_calls = Counter(
            'procur_integration_calls_total',
            'Total integration API calls',
            ['integration', 'method', 'status'],
            registry=self.registry,
        )
        
        self.integration_latency = Histogram(
            'procur_integration_latency_seconds',
            'Integration API latency',
            ['integration', 'method'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
            registry=self.registry,
        )
        
        self.integration_errors = Counter(
            'procur_integration_errors_total',
            'Total integration errors',
            ['integration', 'error_type'],
            registry=self.registry,
        )
        
        # Event bus metrics
        self.events_published = Counter(
            'procur_events_published_total',
            'Total events published',
            ['event_type'],
            registry=self.registry,
        )
        
        self.events_processed = Counter(
            'procur_events_processed_total',
            'Total events processed',
            ['event_type', 'status'],
            registry=self.registry,
        )
        
        self.event_processing_duration = Histogram(
            'procur_event_processing_duration_seconds',
            'Event processing duration',
            ['event_type'],
            buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0],
            registry=self.registry,
        )
        
        # System metrics
        self.active_negotiations = Gauge(
            'procur_active_negotiations',
            'Number of active negotiations',
            registry=self.registry,
        )
        
        self.active_users = Gauge(
            'procur_active_users',
            'Number of active users',
            registry=self.registry,
        )
        
        self.database_connections = Gauge(
            'procur_database_connections',
            'Number of database connections',
            registry=self.registry,
        )
        
        # API metrics
        self.http_requests = Counter(
            'procur_http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry,
        )
        
        self.http_request_duration = Histogram(
            'procur_http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0],
            registry=self.registry,
        )
        
        logger.info("Metrics collector initialized")
    
    def track_negotiation_started(self, vendor: str, category: str):
        """Track negotiation started."""
        self.negotiation_started.labels(vendor=vendor, category=category).inc()
        self.active_negotiations.inc()
    
    def track_negotiation_completed(
        self,
        vendor: str,
        category: str,
        outcome: str,
        duration_seconds: float,
        rounds: int,
        cost_savings: Optional[float] = None,
    ):
        """Track negotiation completed."""
        self.negotiation_completed.labels(
            vendor=vendor,
            category=category,
            outcome=outcome,
        ).inc()
        
        self.negotiation_duration.labels(
            vendor=vendor,
            category=category,
        ).observe(duration_seconds)
        
        self.negotiation_rounds.labels(
            vendor=vendor,
            category=category,
        ).observe(rounds)
        
        if cost_savings is not None:
            self.cost_savings.labels(
                vendor=vendor,
                category=category,
            ).observe(cost_savings)
        
        self.active_negotiations.dec()
    
    def track_integration_call(
        self,
        integration: str,
        method: str,
        status: str,
        duration_seconds: float,
        error_type: Optional[str] = None,
    ):
        """Track integration API call."""
        self.integration_calls.labels(
            integration=integration,
            method=method,
            status=status,
        ).inc()
        
        self.integration_latency.labels(
            integration=integration,
            method=method,
        ).observe(duration_seconds)
        
        if error_type:
            self.integration_errors.labels(
                integration=integration,
                error_type=error_type,
            ).inc()
    
    def track_event(
        self,
        event_type: str,
        status: str,
        duration_seconds: Optional[float] = None,
    ):
        """Track event processing."""
        if status == "published":
            self.events_published.labels(event_type=event_type).inc()
        else:
            self.events_processed.labels(
                event_type=event_type,
                status=status,
            ).inc()
        
        if duration_seconds is not None:
            self.event_processing_duration.labels(
                event_type=event_type,
            ).observe(duration_seconds)
    
    def get_metrics(self) -> bytes:
        """Get Prometheus metrics."""
        return generate_latest(self.registry)


# Global metrics collector
_metrics_collector: Optional[MetricsCollector] = None


def setup_metrics(registry: Optional[CollectorRegistry] = None) -> MetricsCollector:
    """Setup metrics collector."""
    global _metrics_collector
    _metrics_collector = MetricsCollector(registry)
    return _metrics_collector


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector."""
    if _metrics_collector is None:
        return setup_metrics()
    return _metrics_collector


def track_time(metric_name: str, labels: Optional[Dict[str, str]] = None):
    """Decorator to track function execution time."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                collector = get_metrics_collector()
                
                # Track based on metric name
                if metric_name == "integration":
                    collector.track_integration_call(
                        integration=labels.get("integration", "unknown"),
                        method=labels.get("method", "unknown"),
                        status="success",
                        duration_seconds=duration,
                    )
        
        return wrapper
    return decorator
