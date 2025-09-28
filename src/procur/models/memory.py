from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from .enums import ActorRole, NegotiationDecision
from .offer import OfferComponents


class CandidateEvaluation(BaseModel):
    """Scored candidate offer considered during a round."""

    offer: OfferComponents
    primary_lever: str
    tco: float
    buyer_utility: float
    seller_utility: Optional[float] = None
    valid: bool = True
    policy_violations: List[str] = Field(default_factory=list)
    guardrail_alerts: List[str] = Field(default_factory=list)
    rationale: List[str] = Field(default_factory=list)
    buyer_breakdown: Dict[str, float] = Field(default_factory=dict)
    seller_breakdown: Dict[str, float] = Field(default_factory=dict)
    tco_breakdown: Dict[str, float] = Field(default_factory=dict)


class RoundMemory(BaseModel):
    """Structured record of buyer/seller logic for a negotiation round."""

    request_id: str
    vendor_id: str
    round_number: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    actor: ActorRole
    strategy: str
    selected: CandidateEvaluation
    rejected: List[CandidateEvaluation] = Field(default_factory=list)
    decision: NegotiationDecision
    delta_utility: float
    delta_tco: float


class NegotiationMemory(BaseModel):
    """Full negotiation trace suitable for retrieval or training."""

    request_id: str
    vendor_id: str
    scenario_tags: List[str] = Field(default_factory=list)
    rounds: List[RoundMemory] = Field(default_factory=list)
    outcome: str = "in_progress"
    savings: Optional[float] = None
    notes: Dict[str, str] = Field(default_factory=dict)

    def add_round(self, round_memory: RoundMemory) -> None:
        self.rounds.append(round_memory)

    def finalize(self, outcome: str, savings: Optional[float] = None) -> None:
        self.outcome = outcome
        self.savings = savings
