"""Enhanced authentication models for database."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class UserSession(Base, TimestampMixin):
    """User session tracking."""
    
    __tablename__ = "user_sessions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_accounts.id"), nullable=False)
    
    # Session data
    refresh_token: Mapped[str | None] = mapped_column(String(200), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    device_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    
    # Session state
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user: Mapped["UserAccount"] = relationship("UserAccount", back_populates="sessions")
    
    def __repr__(self) -> str:
        return f"<UserSession(id={self.id}, session_id='{self.session_id}', user_id={self.user_id})>"


class APIKey(Base, TimestampMixin):
    """API key for programmatic access."""
    
    __tablename__ = "api_keys"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_accounts.id"), nullable=False)
    
    # Key details
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    hashed_secret: Mapped[str] = mapped_column(String(255), nullable=False)
    key_prefix: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Permissions and scopes
    scopes: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Usage tracking
    usage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Relationships
    user: Mapped["UserAccount"] = relationship("UserAccount", back_populates="api_keys")
    
    def __repr__(self) -> str:
        return f"<APIKey(id={self.id}, key_id='{self.key_id}', name='{self.name}')>"


class PasswordHistory(Base, TimestampMixin):
    """Password history for reuse prevention."""
    
    __tablename__ = "password_history"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_accounts.id"), nullable=False)
    
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["UserAccount"] = relationship("UserAccount", back_populates="password_history")
    
    def __repr__(self) -> str:
        return f"<PasswordHistory(id={self.id}, user_id={self.user_id})>"


class LoginAttempt(Base, TimestampMixin):
    """Login attempt tracking for security."""
    
    __tablename__ = "login_attempts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("user_accounts.id"), nullable=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Attempt details
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String(200), nullable=True)
    
    # MFA
    mfa_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mfa_success: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    
    def __repr__(self) -> str:
        return f"<LoginAttempt(id={self.id}, username='{self.username}', success={self.success})>"


class Organization(Base, TimestampMixin):
    """Organization for multi-tenancy."""
    
    __tablename__ = "organizations"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    organization_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    
    # Organization details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    domain: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    # Settings
    settings: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Subscription
    plan: Mapped[str | None] = mapped_column(String(50), nullable=True)
    max_users: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Relationships
    users: Mapped[list["UserAccount"]] = relationship(
        "UserAccount",
        back_populates="organization"
    )
    
    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, organization_id='{self.organization_id}', name='{self.name}')>"


class OAuthConnection(Base, TimestampMixin):
    """OAuth/SSO connection for users."""
    
    __tablename__ = "oauth_connections"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_accounts.id"), nullable=False)
    
    # Provider details
    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    provider_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Tokens
    access_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Provider data
    provider_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    # Relationships
    user: Mapped["UserAccount"] = relationship("UserAccount", back_populates="oauth_connections")
    
    def __repr__(self) -> str:
        return f"<OAuthConnection(id={self.id}, provider='{self.provider}', user_id={self.user_id})>"
