#!/usr/bin/env python
"""
Example demonstrating observability features.

This example shows how to use:
1. Structured logging with JSON format
2. Distributed tracing with OpenTelemetry
3. Metrics collection with Prometheus
4. Error tracking with Sentry
5. APM monitoring
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from procur.observability import (
    setup_logging,
    get_logger,
    setup_tracing,
    trace_function,
    setup_metrics,
    get_metrics_collector,
    setup_error_tracking,
)
from procur.observability.config import setup_observability
from procur.observability.apm import get_apm_monitor
from procur.observability.logging import LogContext


def logging_example():
    """Structured logging example."""
    print("\n" + "="*80)
    print("Structured Logging Example")
    print("="*80)
    
    # Setup logging
    setup_logging(level="INFO", json_format=True)
    
    logger = get_logger(__name__)
    
    # Basic logging
    logger.info("Application started")
    logger.warning("This is a warning")
    
    # Logging with context
    logger.info("Processing negotiation", extra={
        "negotiation_id": "neg-001",
        "vendor": "Salesforce",
        "user_id": 123,
    })
    
    # Using context manager
    with LogContext(logger, negotiation_id="neg-002", vendor="Oracle"):
        logger.info("Negotiation round started")
        logger.info("Offer received")
    
    print("✅ Logs are in JSON format with structured fields")


@trace_function(name="process_negotiation", attributes={"vendor": "salesforce"})
def traced_function():
    """Function with tracing."""
    time.sleep(0.1)
    return "success"


def tracing_example():
    """Distributed tracing example."""
    print("\n" + "="*80)
    print("Distributed Tracing Example")
    print("="*80)
    
    # Setup tracing
    setup_tracing(
        service_name="procur-example",
        jaeger_host="localhost",
        jaeger_port=6831,
    )
    
    # Trace function
    result = traced_function()
    
    print(f"✅ Function traced: {result}")
    print("   View traces at http://localhost:16686 (Jaeger UI)")


def metrics_example():
    """Metrics collection example."""
    print("\n" + "="*80)
    print("Metrics Collection Example")
    print("="*80)
    
    # Setup metrics
    metrics = setup_metrics()
    
    # Track negotiation
    metrics.track_negotiation_started("Salesforce", "CRM")
    time.sleep(0.5)
    metrics.track_negotiation_completed(
        vendor="Salesforce",
        category="CRM",
        outcome="success",
        duration_seconds=0.5,
        rounds=3,
        cost_savings=5000.0,
    )
    
    # Track integration call
    metrics.track_integration_call(
        integration="slack",
        method="send_message",
        status="success",
        duration_seconds=0.2,
    )
    
    # Track event
    metrics.track_event(
        event_type="negotiation.started",
        status="published",
    )
    
    print("✅ Metrics collected")
    print("   View metrics at http://localhost:9090/metrics")


def error_tracking_example():
    """Error tracking example."""
    print("\n" + "="*80)
    print("Error Tracking Example")
    print("="*80)
    
    # Setup error tracking (requires Sentry DSN)
    # setup_error_tracking(dsn="your-sentry-dsn")
    
    print("⚠️  Sentry not configured. Set PROCUR_SENTRY_DSN in .env")
    print("   When configured, errors are automatically captured")


def apm_example():
    """APM monitoring example."""
    print("\n" + "="*80)
    print("APM Monitoring Example")
    print("="*80)
    
    apm = get_apm_monitor()
    
    # Track negotiation
    with apm.track_negotiation("neg-001", "Salesforce", "CRM"):
        print("   Processing negotiation...")
        time.sleep(0.3)
    
    # Track integration call
    with apm.track_integration_call("slack", "send_message"):
        print("   Calling Slack API...")
        time.sleep(0.1)
    
    # Track event processing
    with apm.track_event_processing("negotiation.started"):
        print("   Processing event...")
        time.sleep(0.05)
    
    print("✅ APM tracking complete")


def complete_example():
    """Complete observability setup."""
    print("\n" + "="*80)
    print("Complete Observability Setup")
    print("="*80)
    
    # Setup everything at once
    setup_observability()
    
    logger = get_logger(__name__)
    metrics = get_metrics_collector()
    apm = get_apm_monitor()
    
    # Simulate a negotiation workflow
    logger.info("Starting negotiation workflow", extra={
        "negotiation_id": "neg-003",
        "vendor": "Microsoft",
    })
    
    with apm.track_negotiation("neg-003", "Microsoft", "Office365"):
        # Track metrics
        metrics.track_negotiation_started("Microsoft", "Office365")
        
        # Simulate rounds
        for round_num in range(1, 4):
            logger.info(f"Negotiation round {round_num}", extra={
                "negotiation_id": "neg-003",
                "round": round_num,
            })
            time.sleep(0.1)
        
        # Complete
        metrics.track_negotiation_completed(
            vendor="Microsoft",
            category="Office365",
            outcome="success",
            duration_seconds=0.3,
            rounds=3,
            cost_savings=3000.0,
        )
    
    logger.info("Negotiation completed successfully")
    
    print("✅ Complete workflow tracked with logs, traces, and metrics")


def main():
    """Run all observability examples."""
    print("=" * 80)
    print("Procur Observability - Usage Examples")
    print("=" * 80)
    print("\nThese examples demonstrate the observability stack.")
    print("Start Jaeger and Prometheus to see full functionality.\n")
    
    try:
        logging_example()
    except Exception as e:
        print(f"❌ Logging example failed: {e}")
    
    try:
        tracing_example()
    except Exception as e:
        print(f"❌ Tracing example failed: {e}")
    
    try:
        metrics_example()
    except Exception as e:
        print(f"❌ Metrics example failed: {e}")
    
    try:
        error_tracking_example()
    except Exception as e:
        print(f"❌ Error tracking example failed: {e}")
    
    try:
        apm_example()
    except Exception as e:
        print(f"❌ APM example failed: {e}")
    
    try:
        complete_example()
    except Exception as e:
        print(f"❌ Complete example failed: {e}")
    
    print("\n" + "=" * 80)
    print("✅ Observability Examples Complete!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Start Jaeger: docker run -d -p 16686:16686 -p 6831:6831/udp jaegertracing/all-in-one")
    print("2. Start Prometheus: prometheus --config.file=monitoring/prometheus.yml")
    print("3. Configure Sentry DSN in .env")
    print("4. View dashboards in Grafana")
    print("\nDocumentation: See OBSERVABILITY_README.md")


if __name__ == "__main__":
    main()
