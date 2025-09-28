from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator

from .enums import RequestType


class RequestClarifier(BaseModel):
    field: str
    question: str
    required: bool = True
    attempts: int = 0


class RequestPolicyContext(BaseModel):
    policy_ids: List[str] = Field(default_factory=list)
    budget_cap: Optional[float] = None
    risk_threshold: Optional[float] = None
    approval_chain: List[str] = Field(default_factory=list)


class Request(BaseModel):
    request_id: str
    requester_id: str
    type: RequestType
    description: str
    specs: dict
    quantity: int
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    currency: str = "USD"
    timeline: Optional[str] = None
    must_haves: List[str] = Field(default_factory=list)
    compliance_requirements: List[str] = Field(default_factory=list)
    data_sensitivity: Optional[str] = None
    billing_cadence: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    policy_context: RequestPolicyContext = Field(default_factory=RequestPolicyContext)
    status: str = "intake"

    @validator("quantity")
    def validate_quantity(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("quantity must be positive")
        return value

    @validator("budget_max")
    def validate_budget(cls, value: Optional[float], values: dict[str, object]) -> Optional[float]:
        min_budget = values.get("budget_min")
        if value is not None and min_budget is not None and value < min_budget:
            raise ValueError("budget_max cannot be less than budget_min")
        return value


class RequestLifecycleState(BaseModel):
    stage: str
    round: int = 0
    approvals_required: List[str] = Field(default_factory=list)
    approvals_obtained: List[str] = Field(default_factory=list)
    last_event: Optional[str] = None
