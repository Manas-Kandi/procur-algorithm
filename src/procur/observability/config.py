"""Observability configuration."""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ObservabilityConfig(BaseSettings):
    """Observability configuration from environment variables."""
    
    model_config = SettingsConfigDict(
        env_prefix="PROCUR_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")
    log_file: Optional[str] = Field(default=None)
    
    # Tracing
    tracing_enabled: bool = Field(default=True)
    jaeger_host: str = Field(default="localhost")
    jaeger_port: int = Field(default=6831)
    
    # Metrics
    metrics_enabled: bool = Field(default=True)
    metrics_port: int = Field(default=9090)
    
    # Error tracking
    sentry_dsn: Optional[str] = Field(default=None)
    sentry_environment: str = Field(default="production")
    sentry_traces_sample_rate: float = Field(default=0.1)
    sentry_profiles_sample_rate: float = Field(default=0.1)


@lru_cache
def get_observability_config() -> ObservabilityConfig:
    """Get cached observability configuration."""
    return ObservabilityConfig()


def setup_observability(config: Optional[ObservabilityConfig] = None):
    """
    Setup complete observability stack.
    
    Args:
        config: Optional configuration (uses env vars if not provided)
    """
    from .logging import setup_logging
    from .tracing import setup_tracing
    from .metrics import setup_metrics
    from .errors import setup_error_tracking
    
    config = config or get_observability_config()
    
    # Setup logging
    setup_logging(
        level=config.log_level,
        json_format=(config.log_format == "json"),
        log_file=config.log_file,
    )
    
    # Setup tracing
    if config.tracing_enabled:
        setup_tracing(
            service_name="procur",
            jaeger_host=config.jaeger_host,
            jaeger_port=config.jaeger_port,
        )
    
    # Setup metrics
    if config.metrics_enabled:
        setup_metrics()
    
    # Setup error tracking
    if config.sentry_dsn:
        setup_error_tracking(
            dsn=config.sentry_dsn,
            environment=config.sentry_environment,
            traces_sample_rate=config.sentry_traces_sample_rate,
            profiles_sample_rate=config.sentry_profiles_sample_rate,
        )
