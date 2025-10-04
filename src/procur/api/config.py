"""API configuration settings."""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class APIConfig(BaseSettings):
    """API configuration from environment variables."""
    
    model_config = SettingsConfigDict(
        env_prefix="PROCUR_API_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Server settings
    host: str = Field(default="0.0.0.0", description="API host")
    port: int = Field(default=8000, description="API port")
    reload: bool = Field(default=False, description="Auto-reload on code changes")
    workers: int = Field(default=4, description="Number of worker processes")
    
    # API metadata
    title: str = Field(default="Procur API", description="API title")
    description: str = Field(
        default="Agentic procurement automation platform API",
        description="API description"
    )
    version: str = Field(default="1.0.0", description="API version")
    
    # Security
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="JWT secret key"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30,
        description="Access token expiration in minutes"
    )
    
    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173", "http://localhost:5177", "http://localhost:8000"],
        description="Allowed CORS origins"
    )
    cors_allow_credentials: bool = Field(default=True, description="Allow credentials")
    cors_allow_methods: List[str] = Field(default=["*"], description="Allowed methods")
    cors_allow_headers: List[str] = Field(default=["*"], description="Allowed headers")
    
    # Rate limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_per_minute: int = Field(default=60, description="Requests per minute")
    rate_limit_per_hour: int = Field(default=1000, description="Requests per hour")
    
    # Pagination
    default_page_size: int = Field(default=20, description="Default page size")
    max_page_size: int = Field(default=100, description="Maximum page size")


@lru_cache
def get_api_config() -> APIConfig:
    """Get cached API configuration."""
    return APIConfig()
