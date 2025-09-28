from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from .enums import RiskLevel


class VendorGuardrails(BaseModel):
    price_floor: Optional[float] = None
    non_negotiables: List[str] = Field(default_factory=list)
    lead_time_days: Optional[int] = None
    response_window_hours: Optional[int] = None
    payment_terms_allowed: List[str] = Field(default_factory=list)


class VendorProfile(BaseModel):
    vendor_id: str
    name: str
    capability_tags: List[str]
    certifications: List[str] = Field(default_factory=list)
    regions: List[str] = Field(default_factory=list)
    lead_time_brackets: Dict[str, tuple[int, int]] = Field(default_factory=dict)
    price_tiers: Dict[str, float] = Field(default_factory=dict)
    guardrails: VendorGuardrails = Field(default_factory=VendorGuardrails)
    reliability_stats: Dict[str, object] = Field(default_factory=dict)
    risk_level: RiskLevel = RiskLevel.MEDIUM
    contact_endpoints: Dict[str, str] = Field(default_factory=dict)
    billing_cadence: Optional[str] = None
