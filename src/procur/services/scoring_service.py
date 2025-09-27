from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from ..models import OfferComponents, OfferScore, Request, VendorProfile


@dataclass
class ScoreWeights:
    value: float = 0.35
    cost: float = 0.35
    risk: float = 0.2
    time: float = 0.1


class ScoringService:
    """Computes normalized scores and utilities for offers/bundles."""

    def __init__(self, weights: ScoreWeights | None = None, *, discount_rate: float = 0.12) -> None:
        self.weights = weights or ScoreWeights()
        self.discount_rate = discount_rate

    def compute_tco(self, components: OfferComponents) -> float:
        # Defensive programming against None values
        unit_price = components.unit_price or 0.0
        quantity = components.quantity or 1
        term_months = components.term_months or 12

        base = unit_price * quantity * (term_months / 12)
        fees = sum(components.one_time_fees.values())

        payment_term_days = {
            "Net15": 15,
            "Net30": 30,
            "Net45": 45,
            "Milestones": 30,
            "Deposit": 0,
        }.get(components.payment_terms.value, 30)

        r_daily = (1 + self.discount_rate) ** (1 / 365) - 1
        pv_adjustment = base * (1 - 1 / ((1 + r_daily) ** payment_term_days))

        return round(base - pv_adjustment + fees, 2)

    def normalize(self, value: float, *, reference: float) -> float:
        if reference <= 0:
            return 0.0
        return max(0.0, min(value / reference, 1.0))

    def compute_offer_score(
        self,
        components: OfferComponents,
        *,
        spec_match: float,
        risk_score: float,
        delivery_delay_days: float,
        reference_points: Dict[str, float],
    ) -> OfferScore:
        tco = self.compute_tco(components)
        normalized = {
            "spec": spec_match / 100.0,
            "tco": self.normalize(tco, reference=reference_points.get("tco", max(tco, 1.0))),
            "risk": self.normalize(risk_score, reference=reference_points.get("risk", 100.0)),
            "time": self.normalize(
                delivery_delay_days,
                reference=reference_points.get("time", max(delivery_delay_days, 1.0)),
            ),
        }
        utility = (
            self.weights.value * normalized["spec"]
            - self.weights.cost * normalized["tco"]
            - self.weights.risk * normalized["risk"]
            - self.weights.time * normalized["time"]
        )
        return OfferScore(
            spec_match=round(normalized["spec"], 4),
            tco=round(normalized["tco"], 4),
            risk=round(normalized["risk"], 4),
            time=round(normalized["time"], 4),
            utility=round(utility, 4),
        )

    def sensitivity_analysis(self, score: OfferScore) -> Dict[str, float]:
        return {
            "value": round(self.weights.value * score.spec_match, 4),
            "cost": round(self.weights.cost * score.tco, 4),
            "risk": round(self.weights.risk * score.risk, 4),
            "time": round(self.weights.time * score.time, 4),
            "utility": score.utility,
        }

    def score_offer(
        self,
        vendor: VendorProfile,
        components: OfferComponents,
        request: Request,
    ) -> OfferScore:
        spec_match = 70.0 + min(len(vendor.capability_tags) * 2.5, 30.0)
        if request.must_haves:
            coverage = sum(
                1
                for tag in request.must_haves
                if tag in vendor.certifications or tag in vendor.capability_tags
            )
            spec_match = min(100.0, spec_match + (coverage / max(len(request.must_haves), 1)) * 15)

        normalized_certs = {cert.lower() for cert in vendor.certifications}
        risk_score = 20.0 if "soc2" in normalized_certs else 60.0

        delivery_bracket = vendor.lead_time_brackets.get("default", (30, 45))
        delivery_delay = float(delivery_bracket[1])
        reference = {
            "tco": request.budget_max or self.compute_tco(components),
            "risk": 100.0,
            "time": max(delivery_delay, 30.0),
        }

        return self.compute_offer_score(
            components,
            spec_match=spec_match,
            risk_score=risk_score,
            delivery_delay_days=delivery_delay,
            reference_points=reference,
        )
