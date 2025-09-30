"""Database configuration and settings."""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseSettings):
    """Database configuration from environment variables."""
    
    model_config = SettingsConfigDict(
        env_prefix="PROCUR_DB_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # PostgreSQL connection settings
    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, description="Database port")
    database: str = Field(default="procur", description="Database name")
    username: str = Field(default="procur_user", description="Database user")
    password: str = Field(default="procur_password", description="Database password")
    
    # Connection pool settings
    pool_size: int = Field(default=5, description="Connection pool size")
    max_overflow: int = Field(default=10, description="Max overflow connections")
    pool_timeout: int = Field(default=30, description="Pool timeout in seconds")
    pool_recycle: int = Field(default=3600, description="Connection recycle time in seconds")
    
    # SQLAlchemy settings
    echo: bool = Field(default=False, description="Echo SQL statements")
    echo_pool: bool = Field(default=False, description="Echo pool events")
    
    # Migration settings
    alembic_ini_path: str = Field(default="alembic.ini", description="Path to alembic.ini")
    
    @field_validator("port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        """Validate port is in valid range."""
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v
    
    @property
    def database_url(self) -> str:
        """Construct PostgreSQL database URL."""
        return (
            f"postgresql://{self.username}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )
    
    @property
    def async_database_url(self) -> str:
        """Construct async PostgreSQL database URL."""
        return (
            f"postgresql+asyncpg://{self.username}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )
    
    def get_engine_kwargs(self) -> dict:
        """Get SQLAlchemy engine configuration."""
        return {
            "pool_size": self.pool_size,
            "max_overflow": self.max_overflow,
            "pool_timeout": self.pool_timeout,
            "pool_recycle": self.pool_recycle,
            "echo": self.echo,
            "echo_pool": self.echo_pool,
        }


@lru_cache
def get_database_config() -> DatabaseConfig:
    """Get cached database configuration."""
    return DatabaseConfig()
