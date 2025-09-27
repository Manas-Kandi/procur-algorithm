from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ControlStatus(BaseModel):
    name: str
    compliant: bool
    notes: Optional[str] = None


class RiskCard(BaseModel):
    request_id: str
    vendor_id: str
    controls: List[ControlStatus] = Field(default_factory=list)
    exceptions: List[str] = Field(default_factory=list)
    remediation_plan: Dict[str, str] = Field(default_factory=dict)
    sla_history: Dict[str, str] = Field(default_factory=dict)
    breach_flags: List[str] = Field(default_factory=list)
    approval_status: str = "pending"
