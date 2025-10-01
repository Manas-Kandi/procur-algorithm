"""Event bus configuration."""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EventBusConfig(BaseSettings):
    """Event bus configuration from environment variables."""
    
    model_config = SettingsConfigDict(
        env_prefix="PROCUR_EVENT_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Redis configuration
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=0, description="Redis database")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    redis_ssl: bool = Field(default=False, description="Use SSL for Redis")
    
    # Event bus settings
    event_stream_name: str = Field(default="procur:events", description="Event stream name")
    event_consumer_group: str = Field(default="procur-workers", description="Consumer group name")
    event_batch_size: int = Field(default=10, description="Events to process per batch")
    event_block_time: int = Field(default=1000, description="Block time in ms")
    
    # Dead letter queue
    dlq_enabled: bool = Field(default=True, description="Enable dead letter queue")
    dlq_stream_name: str = Field(default="procur:dlq", description="DLQ stream name")
    dlq_max_retries: int = Field(default=3, description="Max retries before DLQ")
    
    # Event sourcing
    event_sourcing_enabled: bool = Field(default=True, description="Enable event sourcing")
    event_store_retention_days: int = Field(default=90, description="Event retention in days")
    
    # Monitoring
    monitoring_enabled: bool = Field(default=True, description="Enable monitoring")
    metrics_port: int = Field(default=9090, description="Metrics port")
    
    @property
    def redis_url(self) -> str:
        """Construct Redis URL."""
        protocol = "rediss" if self.redis_ssl else "redis"
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"{protocol}://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @property
    def celery_broker_url(self) -> str:
        """Construct Celery broker URL."""
        return self.redis_url
    
    @property
    def celery_result_backend(self) -> str:
        """Construct Celery result backend URL."""
        return self.redis_url


@lru_cache
def get_event_bus_config() -> EventBusConfig:
    """Get cached event bus configuration."""
    return EventBusConfig()
