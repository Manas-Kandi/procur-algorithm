"""SQLAlchemy ORM models for Procur platform."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SoftDeleteMixin, TimestampMixin
from .models_auth import (
    APIKey,
    LoginAttempt,
    OAuthConnection,
    Organization,
    PasswordHistory,
    UserSession,
)


class UserAccount(Base, TimestampMixin, SoftDeleteMixin):
    """User account for authentication and authorization."""
    
    __tablename__ = "user_accounts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    # Role and permissions
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="buyer")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Organization and team
    organization_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=True, index=True)
    team: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # Password policy
    password_changed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    password_expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    must_change_password: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Account security
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    email_verification_token: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # MFA
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mfa_secret: Mapped[str | None] = mapped_column(String(100), nullable=True)
    mfa_backup_codes: Mapped[List[str] | None] = mapped_column(JSON, nullable=True)
    
    # Metadata
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_password_change_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    preferences: Mapped[Dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    
    # Relationships
    requests: Mapped[List["RequestRecord"]] = relationship(
        "RequestRecord", back_populates="user", cascade="all, delete-orphan", foreign_keys="RequestRecord.user_id"
    )
    audit_logs: Mapped[List["AuditLogRecord"]] = relationship(
        "AuditLogRecord", back_populates="user", cascade="all, delete-orphan"
    )
    sessions: Mapped[List["UserSession"]] = relationship(
        "UserSession", back_populates="user", cascade="all, delete-orphan"
    )
    api_keys: Mapped[List["APIKey"]] = relationship(
        "APIKey", back_populates="user", cascade="all, delete-orphan"
    )
    password_history: Mapped[List["PasswordHistory"]] = relationship(
        "PasswordHistory", back_populates="user", cascade="all, delete-orphan"
    )
    oauth_connections: Mapped[List["OAuthConnection"]] = relationship(
        "OAuthConnection", back_populates="user", cascade="all, delete-orphan"
    )
    organization: Mapped["Organization | None"] = relationship(
        "Organization", back_populates="users"
    )
    
    def __repr__(self) -> str:
        return f"<UserAccount(id={self.id}, email='{self.email}', role='{self.role}')>"


class RequestRecord(Base, TimestampMixin, SoftDeleteMixin):
    """Procurement request record."""
    
    __tablename__ = "requests"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    
    # User relationship
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_accounts.id"), nullable=False)
    
    # Request details
    description: Mapped[str] = mapped_column(Text, nullable=False)
    request_type: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    
    # Budget and quantity
    budget_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    budget_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    billing_cadence: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    # Requirements
    must_haves: Mapped[List[str] | None] = mapped_column(JSON, nullable=True)
    nice_to_haves: Mapped[List[str] | None] = mapped_column(JSON, nullable=True)
    compliance_requirements: Mapped[List[str] | None] = mapped_column(JSON, nullable=True)
    
    # Additional specifications
    specs: Mapped[Dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    
    # Status tracking
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending", index=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    approved_by: Mapped[int | None] = mapped_column(Integer, ForeignKey("user_accounts.id"), nullable=True)
    
    # Relationships
    user: Mapped["UserAccount"] = relationship("UserAccount", back_populates="requests", foreign_keys=[user_id])
    offers: Mapped[List["OfferRecord"]] = relationship(
        "OfferRecord", back_populates="request", cascade="all, delete-orphan"
    )
    contracts: Mapped[List["ContractRecord"]] = relationship(
        "ContractRecord", back_populates="request", cascade="all, delete-orphan"
    )
    negotiation_sessions: Mapped[List["NegotiationSessionRecord"]] = relationship(
        "NegotiationSessionRecord", back_populates="request", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<RequestRecord(id={self.id}, request_id='{self.request_id}', status='{self.status}')>"


class VendorProfileRecord(Base, TimestampMixin, SoftDeleteMixin):
    """Vendor profile record."""
    
    __tablename__ = "vendor_profiles"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vendor_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    
    # Basic information
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    
    # Pricing
    list_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    price_tiers: Mapped[Dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="USD")
    
    # Capabilities
    features: Mapped[List[str] | None] = mapped_column(JSON, nullable=True)
    integrations: Mapped[List[str] | None] = mapped_column(JSON, nullable=True)
    
    # Compliance
    certifications: Mapped[List[str] | None] = mapped_column(JSON, nullable=True)
    compliance_frameworks: Mapped[List[str] | None] = mapped_column(JSON, nullable=True)
    
    # Guardrails and policies
    guardrails: Mapped[Dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    exchange_policy: Mapped[Dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    
    # Ratings and metadata
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    review_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vendor_metadata: Mapped[Dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    
    # Data quality
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    data_source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_enriched_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    offers: Mapped[List["OfferRecord"]] = relationship(
        "OfferRecord", back_populates="vendor", cascade="all, delete-orphan"
    )
    contracts: Mapped[List["ContractRecord"]] = relationship(
        "ContractRecord", back_populates="vendor", cascade="all, delete-orphan"
    )
    negotiation_sessions: Mapped[List["NegotiationSessionRecord"]] = relationship(
        "NegotiationSessionRecord", back_populates="vendor", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<VendorProfileRecord(id={self.id}, vendor_id='{self.vendor_id}', name='{self.name}')>"


class OfferRecord(Base, TimestampMixin, SoftDeleteMixin):
    """Offer record for negotiations."""
    
    __tablename__ = "offers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    offer_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    
    # Foreign keys
    request_id: Mapped[int] = mapped_column(Integer, ForeignKey("requests.id"), nullable=False)
    vendor_id: Mapped[int] = mapped_column(Integer, ForeignKey("vendor_profiles.id"), nullable=False)
    negotiation_session_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("negotiation_sessions.id"), nullable=True
    )
    
    # Offer components
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    term_months: Mapped[int] = mapped_column(Integer, nullable=False)
    payment_terms: Mapped[str] = mapped_column(String(50), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="USD")
    
    # Additional terms
    discount_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    value_adds: Mapped[List[str] | None] = mapped_column(JSON, nullable=True)
    conditions: Mapped[List[str] | None] = mapped_column(JSON, nullable=True)
    
    # Scoring and evaluation
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    utility_buyer: Mapped[float | None] = mapped_column(Float, nullable=True)
    utility_seller: Mapped[float | None] = mapped_column(Float, nullable=True)
    tco: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # Status
    accepted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    rejected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    round_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    actor: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    # Rationale
    rationale: Mapped[List[str] | None] = mapped_column(JSON, nullable=True)
    strategy: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    # Relationships
    request: Mapped["RequestRecord"] = relationship("RequestRecord", back_populates="offers")
    vendor: Mapped["VendorProfileRecord"] = relationship("VendorProfileRecord", back_populates="offers")
    negotiation_session: Mapped["NegotiationSessionRecord | None"] = relationship(
        "NegotiationSessionRecord", back_populates="offers", foreign_keys=[negotiation_session_id]
    )
    
    def __repr__(self) -> str:
        return f"<OfferRecord(id={self.id}, offer_id='{self.offer_id}', unit_price={self.unit_price})>"


class ContractRecord(Base, TimestampMixin, SoftDeleteMixin):
    """Contract record for finalized agreements."""
    
    __tablename__ = "contracts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    contract_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    
    # Foreign keys
    request_id: Mapped[int] = mapped_column(Integer, ForeignKey("requests.id"), nullable=False)
    vendor_id: Mapped[int] = mapped_column(Integer, ForeignKey("vendor_profiles.id"), nullable=False)
    final_offer_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("offers.id"), nullable=True)
    
    # Contract terms (denormalized from final offer)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    term_months: Mapped[int] = mapped_column(Integer, nullable=False)
    payment_terms: Mapped[str] = mapped_column(String(50), nullable=False)
    total_value: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="USD")
    
    # Contract details
    start_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    renewal_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Document management
    document_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    document_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    template_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    # Signature tracking
    signed_by_buyer: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    signed_by_vendor: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    buyer_signature_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    vendor_signature_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    docusign_envelope_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft", index=True)
    
    # ERP integration
    purchase_order_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    erp_sync_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    erp_synced_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Additional terms
    value_adds: Mapped[List[str] | None] = mapped_column(JSON, nullable=True)
    special_terms: Mapped[Dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    
    # Relationships
    request: Mapped["RequestRecord"] = relationship("RequestRecord", back_populates="contracts")
    vendor: Mapped["VendorProfileRecord"] = relationship("VendorProfileRecord", back_populates="contracts")
    
    def __repr__(self) -> str:
        return f"<ContractRecord(id={self.id}, contract_id='{self.contract_id}', status='{self.status}')>"


class NegotiationSessionRecord(Base, TimestampMixin, SoftDeleteMixin):
    """Negotiation session tracking."""
    
    __tablename__ = "negotiation_sessions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    
    # Foreign keys
    request_id: Mapped[int] = mapped_column(Integer, ForeignKey("requests.id"), nullable=False)
    vendor_id: Mapped[int] = mapped_column(Integer, ForeignKey("vendor_profiles.id"), nullable=False)
    
    # Session state
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active", index=True)
    current_round: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    max_rounds: Mapped[int] = mapped_column(Integer, nullable=False, default=8)
    
    # Outcome
    outcome: Mapped[str | None] = mapped_column(String(50), nullable=True)
    outcome_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    final_offer_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("offers.id"), nullable=True)
    
    # Negotiation state
    buyer_state: Mapped[Dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    seller_state: Mapped[Dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    opponent_model: Mapped[Dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    
    # Timing
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Summary metrics
    total_messages: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    savings_achieved: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # Relationships
    request: Mapped["RequestRecord"] = relationship("RequestRecord", back_populates="negotiation_sessions")
    vendor: Mapped["VendorProfileRecord"] = relationship(
        "VendorProfileRecord", back_populates="negotiation_sessions"
    )
    offers: Mapped[List["OfferRecord"]] = relationship(
        "OfferRecord", back_populates="negotiation_session", cascade="all, delete-orphan", foreign_keys="OfferRecord.negotiation_session_id"
    )
    audit_logs: Mapped[List["AuditLogRecord"]] = relationship(
        "AuditLogRecord", back_populates="negotiation_session", cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        UniqueConstraint("request_id", "vendor_id", name="uq_negotiation_request_vendor"),
    )
    
    def __repr__(self) -> str:
        return f"<NegotiationSessionRecord(id={self.id}, session_id='{self.session_id}', status='{self.status}')>"


class AuditLogRecord(Base, TimestampMixin):
    """Audit log for all system actions."""
    
    __tablename__ = "audit_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Actor information
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("user_accounts.id"), nullable=True)
    actor_type: Mapped[str] = mapped_column(String(50), nullable=False)  # user, system, agent
    actor_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # Action details
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    resource_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    
    # Context
    negotiation_session_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("negotiation_sessions.id"), nullable=True
    )
    
    # Event data
    event_data: Mapped[Dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    changes: Mapped[Dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    
    # Metadata
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # Relationships
    user: Mapped["UserAccount | None"] = relationship("UserAccount", back_populates="audit_logs")
    negotiation_session: Mapped["NegotiationSessionRecord | None"] = relationship(
        "NegotiationSessionRecord", back_populates="audit_logs"
    )
    
    def __repr__(self) -> str:
        return f"<AuditLogRecord(id={self.id}, action='{self.action}', resource_type='{self.resource_type}')>"


class PolicyConfigRecord(Base, TimestampMixin, SoftDeleteMixin):
    """Policy configuration storage."""
    
    __tablename__ = "policy_configs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Policy identification
    policy_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    policy_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    organization_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    
    # Policy content
    policy_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    
    # Versioning
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Metadata
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey("user_accounts.id"), nullable=True)
    
    __table_args__ = (
        UniqueConstraint("policy_name", "organization_id", "version", name="uq_policy_org_version"),
    )
    
    def __repr__(self) -> str:
        return f"<PolicyConfigRecord(id={self.id}, policy_name='{self.policy_name}', version={self.version})>"
