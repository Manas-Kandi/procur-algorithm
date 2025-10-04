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
    
    model_config = {"from_attributes": True}


class NegotiationApprove(BaseModel):
    """Approve negotiation offer."""
    offer_id: int = Field(..., description="Offer ID to approve")
    notes: Optional[str] = Field(None, description="Approval notes")


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
