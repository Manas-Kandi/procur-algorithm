from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from .enums import ApprovalStatus, ContractStatus


class Contract(BaseModel):
    contract_id: str
    request_id: str
    vendor_id: str
    template_id: str
    clause_overrides: Dict[str, str] = Field(default_factory=dict)
    redlines: List[str] = Field(default_factory=list)
    approval_chain: List[str] = Field(default_factory=list)
    approval_status: ApprovalStatus = ApprovalStatus.DRAFT
    signature_status: ContractStatus = ContractStatus.DRAFT
    po_id: Optional[str] = None
    fulfillment_status: Optional[str] = None
    renewal_artifacts: Dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
