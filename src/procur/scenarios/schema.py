from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ScenarioRequest(BaseModel):
    category: str
    quantity: int
    budget_total: float
    must_haves: List[str] = Field(default_factory=list)
    compliance_requirements: List[str] = Field(default_factory=list)
    timeline_days: Optional[int] = None


class ScenarioSeller(BaseModel):
    name: str
    list_price: float
    price_floor: float
    term_options: List[int]
    payment_options: List[str]
    non_negotiables: List[str] = Field(default_factory=list)
    behavior_profile: str = "general"


class ScenarioExchange(BaseModel):
    term_12m_to_price_drop: float = 0.03
    pay_NET15_to_price_drop: float = 0.008
    training_credit_value: float = 1500.0


class ScenarioRisk(BaseModel):
    soc2: bool = True
    data_residency: Optional[str] = None
    exceptions_allowed: bool = False


class ScenarioEvaluationTargets(BaseModel):
    close_gap_abs: float = 3000.0
    max_rounds: int = 6
    target_savings_pct: float = 7.0


class Scenario(BaseModel):
    scenario_id: str
    description: str
    request: ScenarioRequest
    seller: ScenarioSeller
    exchange_table: ScenarioExchange = Field(default_factory=ScenarioExchange)
    risk: ScenarioRisk = Field(default_factory=ScenarioRisk)
    eval_targets: ScenarioEvaluationTargets = Field(default_factory=ScenarioEvaluationTargets)
    tags: List[str] = Field(default_factory=list)

    def tag_set(self) -> set[str]:
        return set(self.tags)
