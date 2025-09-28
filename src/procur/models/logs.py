from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from .enums import ActorRole, NegotiationDecision
from .offer import OfferComponents


class UtilitySnapshot(BaseModel):
    buyer_utility: float
    seller_utility: float
    tco: float
    buyer_components: Dict[str, float] = Field(default_factory=dict)
    seller_components: Dict[str, float] = Field(default_factory=dict)
    tco_breakdown: Dict[str, float] = Field(default_factory=dict)


class MoveLog(BaseModel):
    actor: ActorRole
    round_number: int
    offer: OfferComponents
    lever: str
    rationale: List[str] = Field(default_factory=list)
    utility: UtilitySnapshot
    decision: Optional[NegotiationDecision] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    policy_notes: List[str] = Field(default_factory=list)
    guardrail_notes: List[str] = Field(default_factory=list)
    compliance_notes: List[str] = Field(default_factory=list)


class RoundLog(BaseModel):
    request_id: str
    vendor_id: str
    moves: List[MoveLog] = Field(default_factory=list)
    outcome: str = "in_progress"
    summary: Dict[str, object] = Field(default_factory=dict)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    def add_move(self, move: MoveLog) -> None:
        self.moves.append(move)

    def mark_outcome(self, outcome: str, summary: Optional[Dict[str, float]] = None) -> None:
        self.outcome = outcome
        if summary:
            self.summary = summary
        self.completed_at = datetime.utcnow()
