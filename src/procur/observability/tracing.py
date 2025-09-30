"""Distributed tracing with OpenTelemetry."""

import functools
import logging
from typing import Any, Callable, Optional

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

logger = logging.getLogger(__name__)


def setup_tracing(
    service_name: str = "procur",
    jaeger_host: str = "localhost",
    jaeger_port: int = 6831,
    enable_fastapi: bool = True,
    enable_sqlalchemy: bool = True,
    enable_redis: bool = True,
) -> None:
    """
    Setup distributed tracing with OpenTelemetry.
    
    Args:
        service_name: Service name for tracing
        jaeger_host: Jaeger agent host
        jaeger_port: Jaeger agent port
        enable_fastapi: Enable FastAPI instrumentation
        enable_sqlalchemy: Enable SQLAlchemy instrumentation
        enable_redis: Enable Redis instrumentation
    """
    # Create resource
    resource = Resource.create({
        "service.name": service_name,
        "service.version": "1.0.0",
    })
    
    # Create tracer provider
    provider = TracerProvider(resource=resource)
    
    # Create Jaeger exporter
    jaeger_exporter = JaegerExporter(
        agent_host_name=jaeger_host,
        agent_port=jaeger_port,
    )
    
    # Add span processor
    provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
    
    # Set global tracer provider
    trace.set_tracer_provider(provider)
    
    # Auto-instrumentation
    if enable_fastapi:
        FastAPIInstrumentor().instrument()
    
    if enable_sqlalchemy:
        SQLAlchemyInstrumentor().instrument()
    
    if enable_redis:
        RedisInstrumentor().instrument()
    
    logger.info(f"Distributed tracing initialized: {service_name}")


def get_tracer(name: str) -> trace.Tracer:
    """
    Get tracer instance.
    
    Args:
        name: Tracer name (usually __name__)
    
    Returns:
        Tracer instance
    """
    return trace.get_tracer(name)


def trace_function(
    name: Optional[str] = None,
    attributes: Optional[dict] = None,
):
    """
    Decorator to trace function execution.
    
    Args:
        name: Span name (defaults to function name)
        attributes: Additional span attributes
    
    Example:
        @trace_function(name="negotiate_round", attributes={"vendor": "salesforce"})
        def process_negotiation(negotiation_id):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            tracer = get_tracer(func.__module__)
            span_name = name or func.__name__
            
            with tracer.start_as_current_span(span_name) as span:
                # Add attributes
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)
                
                # Add function info
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                
                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("function.status", "success")
                    return result
                except Exception as e:
                    span.set_attribute("function.status", "error")
                    span.set_attribute("error.type", type(e).__name__)
                    span.set_attribute("error.message", str(e))
                    span.record_exception(e)
                    raise
        
        return wrapper
    return decorator


class TracingContext:
    """Context manager for tracing code blocks."""
    
    def __init__(
        self,
        name: str,
        tracer: Optional[trace.Tracer] = None,
        attributes: Optional[dict] = None,
    ):
        """
        Initialize tracing context.
        
        Args:
            name: Span name
            tracer: Tracer instance (optional)
            attributes: Span attributes
        """
        self.name = name
        self.tracer = tracer or trace.get_tracer(__name__)
        self.attributes = attributes or {}
        self.span = None
    
    def __enter__(self):
        """Enter context."""
        self.span = self.tracer.start_span(self.name)
        
        # Add attributes
        for key, value in self.attributes.items():
            self.span.set_attribute(key, value)
        
        return self.span
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        if exc_type:
            self.span.set_attribute("error", True)
            self.span.set_attribute("error.type", exc_type.__name__)
            self.span.set_attribute("error.message", str(exc_val))
            self.span.record_exception(exc_val)
        
        self.span.end()


def add_span_attributes(**attributes):
    """Add attributes to current span."""
    span = trace.get_current_span()
    if span:
        for key, value in attributes.items():
            span.set_attribute(key, value)


def add_span_event(name: str, attributes: Optional[dict] = None):
    """Add event to current span."""
    span = trace.get_current_span()
    if span:
        span.add_event(name, attributes=attributes or {})
