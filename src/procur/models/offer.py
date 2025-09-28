from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from .enums import ActorRole, NextStepHint, PaymentTerms


class OfferComponents(BaseModel):
    unit_price: float
    currency: str
    quantity: int
    term_months: int
    delivery_window_days: Optional[list[int]] = None
    payment_terms: PaymentTerms = PaymentTerms.NET_30
    warranty_support: Dict[str, str] = Field(default_factory=dict)
    one_time_fees: Dict[str, float] = Field(default_factory=dict)
    exclusions: List[str] = Field(default_factory=list)
    notes: Optional[str] = None


class MachineRationale(BaseModel):
    score_components: Dict[str, float]
    constraints_respected: List[str] = Field(default_factory=list)
    concession_taken: str


class NegotiationMessage(BaseModel):
    actor: ActorRole
    round: int
    proposal: OfferComponents
    justification_bullets: List[str] = Field(default_factory=list)
    machine_rationale: MachineRationale
    next_step_hint: NextStepHint


class OfferScore(BaseModel):
    spec_match: float
    tco: float
    risk: float
    time: float
    utility: float
    matched_features: List[str] = Field(default_factory=list)
    missing_features: List[str] = Field(default_factory=list)


class Offer(BaseModel):
    offer_id: str
    request_id: str
    vendor_id: str
    components: OfferComponents
    score: OfferScore
    confidence: float = 0.5
    accepted: bool = False
