"""Application Performance Monitoring integration."""

import logging
import time
from contextlib import contextmanager
from typing import Any, Dict, Optional

from .metrics import get_metrics_collector
from .tracing import add_span_attributes, add_span_event

logger = logging.getLogger(__name__)


class APMMonitor:
    """Application Performance Monitoring."""
    
    def __init__(self):
        """Initialize APM monitor."""
        self.metrics = get_metrics_collector()
    
    @contextmanager
    def track_negotiation(
        self,
        negotiation_id: str,
        vendor: str,
        category: str,
    ):
        """
        Track negotiation performance.
        
        Args:
            negotiation_id: Negotiation ID
            vendor: Vendor name
            category: Category
        """
        start_time = time.time()
        rounds = 0
        outcome = "unknown"
        
        # Add tracing context
        add_span_attributes(
            negotiation_id=negotiation_id,
            vendor=vendor,
            category=category,
        )
        
        # Track start
        self.metrics.track_negotiation_started(vendor, category)
        add_span_event("negotiation_started")
        
        try:
            yield self
            outcome = "success"
        except Exception as e:
            outcome = "failed"
            add_span_event("negotiation_failed", {"error": str(e)})
            raise
        finally:
            duration = time.time() - start_time
            
            # Track completion
            self.metrics.track_negotiation_completed(
                vendor=vendor,
                category=category,
                outcome=outcome,
                duration_seconds=duration,
                rounds=rounds,
            )
            
            add_span_event("negotiation_completed", {
                "duration": duration,
                "outcome": outcome,
            })
            
            logger.info(
                f"Negotiation {outcome}",
                extra={
                    "negotiation_id": negotiation_id,
                    "vendor": vendor,
                    "duration": duration,
                    "outcome": outcome,
                },
            )
    
    @contextmanager
    def track_integration_call(
        self,
        integration: str,
        method: str,
    ):
        """
        Track integration API call.
        
        Args:
            integration: Integration name
            method: Method name
        """
        start_time = time.time()
        status = "success"
        error_type = None
        
        add_span_attributes(
            integration=integration,
            method=method,
        )
        
        try:
            yield
        except Exception as e:
            status = "error"
            error_type = type(e).__name__
            add_span_event("integration_error", {
                "error_type": error_type,
                "error": str(e),
            })
            raise
        finally:
            duration = time.time() - start_time
            
            self.metrics.track_integration_call(
                integration=integration,
                method=method,
                status=status,
                duration_seconds=duration,
                error_type=error_type,
            )
            
            logger.info(
                f"Integration call {status}",
                extra={
                    "integration": integration,
                    "method": method,
                    "duration": duration,
                    "status": status,
                },
            )
    
    @contextmanager
    def track_event_processing(self, event_type: str):
        """
        Track event processing.
        
        Args:
            event_type: Event type
        """
        start_time = time.time()
        status = "success"
        
        add_span_attributes(event_type=event_type)
        
        try:
            yield
        except Exception as e:
            status = "failed"
            add_span_event("event_processing_failed", {"error": str(e)})
            raise
        finally:
            duration = time.time() - start_time
            
            self.metrics.track_event(
                event_type=event_type,
                status=status,
                duration_seconds=duration,
            )
    
    def track_request_created(self, category: str, user: str):
        """Track request created."""
        self.metrics.requests_created.labels(
            category=category,
            user=user,
        ).inc()
    
    def track_contract_signed(
        self,
        vendor: str,
        category: str,
        value: float,
    ):
        """Track contract signed."""
        self.metrics.contracts_signed.labels(
            vendor=vendor,
            category=category,
        ).inc()
        
        self.metrics.contract_value.labels(
            vendor=vendor,
            category=category,
        ).observe(value)


# Global APM monitor
_apm_monitor: Optional[APMMonitor] = None


def get_apm_monitor() -> APMMonitor:
    """Get global APM monitor."""
    global _apm_monitor
    if _apm_monitor is None:
        _apm_monitor = APMMonitor()
    return _apm_monitor
