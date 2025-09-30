"""Error tracking with Sentry."""

import logging
from typing import Any, Dict, Optional

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

logger = logging.getLogger(__name__)


def setup_error_tracking(
    dsn: str,
    environment: str = "production",
    release: Optional[str] = None,
    traces_sample_rate: float = 0.1,
    profiles_sample_rate: float = 0.1,
    enable_fastapi: bool = True,
    enable_sqlalchemy: bool = True,
    enable_redis: bool = True,
    enable_celery: bool = True,
) -> None:
    """
    Setup error tracking with Sentry.
    
    Args:
        dsn: Sentry DSN
        environment: Environment name (production, staging, development)
        release: Release version
        traces_sample_rate: Percentage of transactions to trace (0.0-1.0)
        profiles_sample_rate: Percentage of transactions to profile (0.0-1.0)
        enable_fastapi: Enable FastAPI integration
        enable_sqlalchemy: Enable SQLAlchemy integration
        enable_redis: Enable Redis integration
        enable_celery: Enable Celery integration
    """
    integrations = []
    
    # Logging integration
    integrations.append(LoggingIntegration(
        level=logging.INFO,
        event_level=logging.ERROR,
    ))
    
    # FastAPI integration
    if enable_fastapi:
        integrations.append(FastApiIntegration(
            transaction_style="endpoint",
        ))
    
    # SQLAlchemy integration
    if enable_sqlalchemy:
        integrations.append(SqlalchemyIntegration())
    
    # Redis integration
    if enable_redis:
        integrations.append(RedisIntegration())
    
    # Celery integration
    if enable_celery:
        integrations.append(CeleryIntegration())
    
    # Initialize Sentry
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        release=release,
        integrations=integrations,
        traces_sample_rate=traces_sample_rate,
        profiles_sample_rate=profiles_sample_rate,
        send_default_pii=False,
        attach_stacktrace=True,
        before_send=before_send_filter,
    )
    
    logger.info(f"Error tracking initialized: {environment}")


def before_send_filter(event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Filter events before sending to Sentry.
    
    Args:
        event: Sentry event
        hint: Event hint with exception info
    
    Returns:
        Modified event or None to drop
    """
    # Drop events from specific modules
    if 'exc_info' in hint:
        exc_type, exc_value, tb = hint['exc_info']
        
        # Drop known non-critical exceptions
        if exc_type.__name__ in ['KeyboardInterrupt', 'SystemExit']:
            return None
    
    return event


def capture_exception(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    level: str = "error",
) -> str:
    """
    Capture exception with context.
    
    Args:
        error: Exception to capture
        context: Additional context
        level: Error level (fatal, error, warning, info, debug)
    
    Returns:
        Event ID
    """
    with sentry_sdk.push_scope() as scope:
        # Set level
        scope.level = level
        
        # Add context
        if context:
            for key, value in context.items():
                scope.set_context(key, value)
        
        # Capture exception
        event_id = sentry_sdk.capture_exception(error)
        
        logger.debug(f"Captured exception: {event_id}")
        return event_id


def capture_message(
    message: str,
    level: str = "info",
    context: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Capture message with context.
    
    Args:
        message: Message to capture
        level: Message level
        context: Additional context
    
    Returns:
        Event ID
    """
    with sentry_sdk.push_scope() as scope:
        scope.level = level
        
        if context:
            for key, value in context.items():
                scope.set_context(key, value)
        
        event_id = sentry_sdk.capture_message(message, level)
        return event_id


def set_user_context(
    user_id: Optional[int] = None,
    email: Optional[str] = None,
    username: Optional[str] = None,
    organization_id: Optional[str] = None,
):
    """Set user context for error tracking."""
    sentry_sdk.set_user({
        "id": user_id,
        "email": email,
        "username": username,
        "organization_id": organization_id,
    })


def set_tag(key: str, value: str):
    """Set tag for error tracking."""
    sentry_sdk.set_tag(key, value)


def set_context(name: str, context: Dict[str, Any]):
    """Set context for error tracking."""
    sentry_sdk.set_context(name, context)


def add_breadcrumb(
    message: str,
    category: str = "default",
    level: str = "info",
    data: Optional[Dict[str, Any]] = None,
):
    """Add breadcrumb for error tracking."""
    sentry_sdk.add_breadcrumb(
        message=message,
        category=category,
        level=level,
        data=data or {},
    )
