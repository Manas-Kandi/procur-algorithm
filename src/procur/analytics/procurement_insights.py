from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean
from typing import Dict, Iterable, List, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - type checking only
    from ..orchestration.pipeline import NegotiationResult


class ProcurementAnalytics:
    """Transforms raw negotiation outputs into business-facing insights."""

    def generate_savings_report(self, negotiations: Iterable["NegotiationResult"]) -> Dict[str, object]:
        negotiations = list(negotiations)
        if not negotiations:
            return {
                "total_savings": 0.0,
                "avg_rounds": 0.0,
                "success_rate": 0.0,
                "top_strategies": [],
            }

        total_savings = sum(self._extract_savings(n.audit_log) for n in negotiations)
        rounds_completed = [self._estimate_rounds(n.audit_log) for n in negotiations]
        accepted = sum(1 for n in negotiations if getattr(n.offer, "accepted", False))

        return {
            "total_savings": round(total_savings, 2),
            "avg_rounds": round(mean(rounds_completed), 2) if rounds_completed else 0.0,
            "success_rate": accepted / len(negotiations),
            "top_strategies": self._analyze_successful_strategies(negotiations),
        }

    def compliance_coverage_analysis(self, results: Iterable["NegotiationResult"]) -> Dict[str, object]:
        totals: Counter[str] = Counter()
        compliant: Counter[str] = Counter()
        vendor_breakdown: Dict[str, List[str]] = defaultdict(list)

        for result in results:
            for status in result.compliance.statuses:
                totals[status.name] += 1
                if status.status == "compliant":
                    compliant[status.name] += 1
                else:
                    vendor_breakdown[status.name].append(result.selection.record.name)

        analysis = {
            name: {
                "covered": int(compliant[name]),
                "total": int(totals[name]),
                "coverage_pct": compliant[name] / totals[name] if totals[name] else 0.0,
                "gaps": vendor_breakdown.get(name, []),
            }
            for name in totals
        }
        return analysis

    def negotiation_performance_by_category(self, negotiations: Iterable["NegotiationResult"]) -> Dict[str, object]:
        stats: Dict[str, Dict[str, object]] = defaultdict(lambda: {
            "count": 0,
            "wins": 0,
            "savings": 0.0,
            "rounds": [],
        })

        for result in negotiations:
            category = result.selection.record.category
            bucket = stats[category]
            bucket["count"] += 1
            if getattr(result.offer, "accepted", False):
                bucket["wins"] += 1
            savings = self._extract_savings(result.audit_log)
            bucket["savings"] += savings
            bucket.setdefault("rounds", []).append(self._estimate_rounds(result.audit_log))

        formatted: Dict[str, object] = {}
        for category, payload in stats.items():
            rounds = payload.get("rounds", []) or [0]
            formatted[category] = {
                "win_rate": payload["wins"] / payload["count"] if payload["count"] else 0.0,
                "avg_savings": (payload["savings"] / payload["count"]) if payload["count"] else 0.0,
                "avg_rounds": mean(rounds) if rounds else 0.0,
                "sample_size": payload["count"],
            }
        return formatted

    # ---------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------
    def _extract_savings(self, audit_log: Dict[str, object]) -> float:
        summary = audit_log.get("summary", {}) if isinstance(audit_log, dict) else {}
        if isinstance(summary, dict):
            for key in ("savings", "buyer_savings", "total_savings"):
                value = summary.get(key)
                if value is not None:
                    try:
                        return float(value)
                    except (TypeError, ValueError):
                        continue
        savings = audit_log.get("savings") if isinstance(audit_log, dict) else 0
        try:
            return float(savings or 0)
        except (TypeError, ValueError):
            return 0.0

    def _estimate_rounds(self, audit_log: Dict[str, object]) -> int:
        if not isinstance(audit_log, dict):
            return 0
        moves = audit_log.get("moves")
        if isinstance(moves, list):
            return max((move.get("round_number", 0) for move in moves if isinstance(move, dict)), default=0)
        return int(audit_log.get("rounds_completed") or 0)

    def _analyze_successful_strategies(self, negotiations: Iterable["NegotiationResult"]) -> List[Dict[str, object]]:
        strategy_counter: Counter[str] = Counter()
        rationales: Dict[str, List[str]] = defaultdict(list)

        for result in negotiations:
            audit_log = result.audit_log if isinstance(result.audit_log, dict) else {}
            moves = audit_log.get("moves", [])
            if not isinstance(moves, list):
                continue
            for move in moves:
                if not isinstance(move, dict):
                    continue
                if move.get("actor") != "buyer":
                    continue
                lever = move.get("lever") or "unknown"
                strategy_counter[lever] += 1
                rationale = move.get("rationale")
                if isinstance(rationale, list) and rationale:
                    rationales[lever].extend(str(item) for item in rationale[:2])

        top = strategy_counter.most_common(5)
        return [
            {
                "lever": lever,
                "count": count,
                "sample_rationales": rationales.get(lever, [])[:3],
            }
            for lever, count in top
        ]


__all__ = ["ProcurementAnalytics"]
