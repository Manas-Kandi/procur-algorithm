from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from ..scenarios import list_scenarios


@dataclass
class CurriculumPhase:
    name: str
    description: str
    scenario_ids: List[str]
    goals: Dict[str, float] = field(default_factory=dict)


def default_curriculum() -> List[CurriculumPhase]:
    available = set(list_scenarios())
    phases: List[CurriculumPhase] = []

    if {"S-12", "S-24"}.issubset(available):
        phases.append(
            CurriculumPhase(
                name="Phase 1 - Trade Mechanics",
                description="Validate term/payment give-get enforcement on tight ZOPA and compliance scenarios.",
                scenario_ids=["S-12", "S-24"],
                goals={"pass_rate": 1.0, "avg_savings_pct": 6.0},
            )
        )
    else:
        phases.append(
            CurriculumPhase(
                name="Phase 1",
                description="Run all available scenarios as baseline regression.",
                scenario_ids=list(available),
            )
        )
    return phases


__all__ = ["CurriculumPhase", "default_curriculum"]
