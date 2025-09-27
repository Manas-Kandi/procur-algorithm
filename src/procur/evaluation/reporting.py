from __future__ import annotations

from typing import Dict, Iterable

from .curriculum import CurriculumPhase
from .regression import RegressionReport


def build_dashboard(report: RegressionReport, *, include_details: bool = True) -> Dict[str, object]:
    dashboard: Dict[str, object] = {"summary": report.summary()}
    if include_details:
        dashboard["details"] = [
            {
                "scenario_id": result.scenario_id,
                "passed": result.passed,
                "outcome": result.outcome,
                "savings_pct": result.savings_pct,
                "rounds": result.rounds,
                "notes": result.notes,
            }
            for result in report.results
        ]
    return dashboard


def build_curriculum_dashboard(
    phase_reports: Dict[CurriculumPhase, RegressionReport]
) -> Dict[str, object]:
    phases_payload = []
    pass_count = 0
    for phase, report in phase_reports.items():
        summary = report.summary()
        summary.update(phase.goals)
        phases_payload.append(
            {
                "phase": phase.name,
                "description": phase.description,
                "scenarios": phase.scenario_ids,
                "goals": phase.goals,
                "results": summary,
            }
        )
        if report.passed():
            pass_count += 1
    curriculum_pass_rate = pass_count / max(len(phase_reports), 1)
    return {"curriculum_pass_rate": curriculum_pass_rate, "phases": phases_payload}


__all__ = ["build_dashboard", "build_curriculum_dashboard"]
