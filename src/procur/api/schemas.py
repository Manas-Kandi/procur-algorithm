"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# ============================================================================
# Authentication Schemas
# ============================================================================

class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """JWT token payload data."""
    user_id: Optional[int] = None


class UserLogin(BaseModel):
    """User login request."""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., min_length=8, description="Password")


class UserRegister(BaseModel):
    """User registration request."""
    email: EmailStr = Field(..., description="Email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=8, description="Password")
    full_name: Optional[str] = Field(None, description="Full name")
    organization_id: Optional[str] = Field(None, description="Organization ID")
    role: str = Field(default="buyer", description="User role")


class UserResponse(BaseModel):
    """User response."""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    role: str
    is_active: bool
    organization_id: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ============================================================================
# Request Schemas
# ============================================================================

class RequestCreate(BaseModel):
    """Create procurement request."""
    description: str = Field(..., min_length=10, description="Request description")
    request_type: str = Field(default="saas", description="Request type")
    category: Optional[str] = Field(None, description="Category")
    budget_min: Optional[float] = Field(None, gt=0, description="Minimum budget")
    budget_max: Optional[float] = Field(None, gt=0, description="Maximum budget")
    quantity: Optional[int] = Field(None, gt=0, description="Quantity")
    billing_cadence: Optional[str] = Field(None, description="Billing cadence")
    must_haves: Optional[List[str]] = Field(default=[], description="Required features")
    nice_to_haves: Optional[List[str]] = Field(default=[], description="Optional features")
    compliance_requirements: Optional[List[str]] = Field(default=[], description="Compliance requirements")
    specs: Optional[Dict[str, Any]] = Field(default={}, description="Additional specifications")
    
    @field_validator("budget_max")
    @classmethod
    def validate_budget_max(cls, v, info):
        """Ensure budget_max >= budget_min."""
        if v is not None and info.data.get("budget_min") is not None:
            if v < info.data["budget_min"]:
                raise ValueError("budget_max must be >= budget_min")
        return v


class RequestUpdate(BaseModel):
    """Update procurement request."""
    description: Optional[str] = Field(None, min_length=10)
    category: Optional[str] = None
    budget_min: Optional[float] = Field(None, gt=0)
    budget_max: Optional[float] = Field(None, gt=0)
    quantity: Optional[int] = Field(None, gt=0)
    must_haves: Optional[List[str]] = None
    nice_to_haves: Optional[List[str]] = None
    compliance_requirements: Optional[List[str]] = None
    specs: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class RequestResponse(BaseModel):
    """Procurement request response."""
    id: int
    request_id: str
    user_id: int
    description: str
    request_type: str
    category: Optional[str]
    budget_min: Optional[float]
    budget_max: Optional[float]
    quantity: Optional[int]
    billing_cadence: Optional[str]
    must_haves: Optional[List[str]]
    nice_to_haves: Optional[List[str]]
    compliance_requirements: Optional[List[str]]
    specs: Optional[Dict[str, Any]]
    status: str
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


# ============================================================================
# Vendor Schemas
# ============================================================================

class VendorCreate(BaseModel):
    """Create vendor profile."""
    vendor_id: str = Field(..., description="Vendor ID")
    name: str = Field(..., min_length=1, description="Vendor name")
    website: Optional[str] = Field(None, description="Website URL")
    description: Optional[str] = Field(None, description="Description")
    category: Optional[str] = Field(None, description="Category")
    list_price: Optional[float] = Field(None, gt=0, description="List price")
    features: Optional[List[str]] = Field(default=[], description="Features")
    certifications: Optional[List[str]] = Field(default=[], description="Certifications")


class VendorResponse(BaseModel):
    """Vendor profile response."""
    id: int
    vendor_id: str
    name: str
    website: Optional[str]
    description: Optional[str]
    category: Optional[str]
    list_price: Optional[float]
    features: Optional[List[str]]
    certifications: Optional[List[str]]
    rating: Optional[float]
    review_count: Optional[int]
    created_at: datetime
    
    model_config = {"from_attributes": True}


# ============================================================================
# Offer Schemas
# ============================================================================

class OfferResponse(BaseModel):
    """Offer response."""
    id: int
    offer_id: str
    request_id: int
    vendor_id: int
    unit_price: float
    quantity: int
    term_months: int
    payment_terms: str
    currency: str
    discount_percent: Optional[float]
    value_adds: Optional[List[str]]
    score: Optional[float]
    accepted: bool
    rejected: bool
    round_number: Optional[int]
    actor: Optional[str]
    strategy: Optional[str]
    created_at: datetime
    
    model_config = {"from_attributes": True}


# ============================================================================
# Negotiation Schemas
# ============================================================================

class NegotiationResponse(BaseModel):
    """Negotiation session response."""
    id: int
    session_id: str
    request_id: int
    vendor_id: int
    status: str
    current_round: int
    max_rounds: int
    outcome: Optional[str]
    outcome_reason: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
    total_messages: int
    savings_achieved: Optional[float]
    
    # Additional fields for frontend
    vendor_name: Optional[str] = None
    current_price: Optional[float] = None
    total_cost: Optional[float] = None
    utility_score: Optional[float] = None
    rounds_completed: Optional[int] = None
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    
    model_config = {"from_attributes": True}


class NegotiationApprove(BaseModel):
    """Approve negotiation offer."""
    offer_id: int = Field(..., description="Offer ID to approve")
    notes: Optional[str] = Field(None, description="Approval notes")


class AutoNegotiateRequest(BaseModel):
    """Request to start auto-negotiation."""
    max_rounds: int = Field(default=8, ge=1, le=15, description="Maximum negotiation rounds")
    stream_updates: bool = Field(default=True, description="Stream real-time updates via WebSocket")


class NegotiationEventResponse(BaseModel):
    """Real-time negotiation event."""
    type: str = Field(..., description="Event type")
    timestamp: str = Field(..., description="Event timestamp")
    round_number: Optional[int] = Field(None, description="Current round number")
    actor: Optional[str] = Field(None, description="Actor (buyer/seller)")
    offer: Optional[Dict[str, Any]] = Field(None, description="Offer details")
    strategy: Optional[str] = Field(None, description="Negotiation strategy used")
    rationale: Optional[List[str]] = Field(None, description="Reasoning for the move")
    utility: Optional[float] = Field(None, description="Utility score")
    tco: Optional[float] = Field(None, description="Total cost of ownership")


class NegotiationProgressResponse(BaseModel):
    """Negotiation progress and final outcome."""
    session_id: str
    status: str = Field(..., description="Negotiation status")
    outcome: str = Field(..., description="Final outcome")
    rounds_completed: int = Field(..., description="Number of rounds completed")
    final_offer: Optional[Dict[str, Any]] = Field(None, description="Final offer details")


# ============================================================================
# Contract Schemas
# ============================================================================

class ContractResponse(BaseModel):
    """Contract response."""
    id: int
    contract_id: str
    request_id: int
    vendor_id: int
    unit_price: float
    quantity: int
    term_months: int
    payment_terms: str
    total_value: float
    currency: str
    status: str
    signed_by_buyer: bool
    signed_by_vendor: bool
    buyer_signature_date: Optional[datetime]
    vendor_signature_date: Optional[datetime]
    created_at: datetime
    
    model_config = {"from_attributes": True}


class ContractSign(BaseModel):
    """Sign contract request."""
    signature_type: str = Field(..., description="Signature type: buyer or vendor")
    signature_data: Optional[str] = Field(None, description="Signature data")


# ============================================================================
# Pagination Schemas
# ============================================================================

class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Page size")


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# Error Schemas
# ============================================================================

class ErrorResponse(BaseModel):
    """Error response."""
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ValidationErrorResponse(BaseModel):
    """Validation error response."""
    detail: List[Dict[str, Any]]
    error_code: str = "validation_error"


# ============================================================================
# Health Check Schemas
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    version: str
    database: str


# ============================================================================
# Explainability Schemas
# ============================================================================

class RationaleFactResponse(BaseModel):
    """A single fact-to-implication pair."""
    fact: str
    implication: str


class PolicyEventResponse(BaseModel):
    """A policy or guardrail enforcement event."""
    policy_id: str
    outcome: str
    note: str


class NumericSnapshotResponse(BaseModel):
    """Canonical numeric facts for audits and charts."""
    latest_unit_price: float
    budget_per_unit: float
    tco: float
    tco_vs_budget_pct: float
    acceptance_probability: float


class RecommendedActionResponse(BaseModel):
    """A suggested next action with priority and type."""
    priority: int
    type: str
    text: str


class ExplainabilityTraceResponse(BaseModel):
    """Internal trace for debugging."""
    step: str
    detail: str


class ExplanationResponse(BaseModel):
    """Complete explanation record for a negotiation state."""
    explanation_version: str
    short_summary: str
    detailed_explanation: str
    rationale: List[RationaleFactResponse]
    policy_summary: List[PolicyEventResponse]
    numeric_snapshots: NumericSnapshotResponse
    recommended_actions: List[RecommendedActionResponse]
    confidence: float
    explainability_trace: List[ExplainabilityTraceResponse]


class ExplainNegotiationRequest(BaseModel):
    """Request to generate explanation for a negotiation round."""
    round_number: Optional[int] = None  # If not provided, explain latest round
    include_trace: bool = Field(default=False, description="Include debugging trace")
