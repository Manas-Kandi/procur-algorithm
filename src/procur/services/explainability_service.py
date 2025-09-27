from __future__ import annotations

from typing import Dict, List

from ..models import Offer, OfferScore


class ExplainabilityService:
    """Produces structured summaries for approvals and audit."""

    def build_why_this_pick(self, offer: Offer, sensitivity: Dict[str, float]) -> Dict[str, List[str]]:
        components = offer.score
        bullets = [
            f"Spec alignment contributes {components.spec_match:.0%} of target coverage",
            f"Total cost impact normalized at {components.tco:.0%} with weight {sensitivity['cost']:.2f}",
            f"Risk exposure normalized at {components.risk:.0%}; remaining headroom {max(0.0, 1 - components.risk):.0%}",
        ]
        return {
            "offer_id": offer.offer_id,
            "vendor_id": offer.vendor_id,
            "bullets": bullets,
        }

    def bundle_summary(self, bundles: Dict[str, Offer], sensitivities: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, List[str]]]:
        return {
            bundle_name: self.build_why_this_pick(offer, sensitivities[bundle_name])
            for bundle_name, offer in bundles.items()
        }

    def trace_score_components(self, score: OfferScore, weights: Dict[str, float]) -> Dict[str, float]:
        return {
            "spec": round(weights["value"] * score.spec_match, 4),
            "cost": round(weights["cost"] * score.tco, 4),
            "risk": round(weights["risk"] * score.risk, 4),
            "time": round(weights["time"] * score.time, 4),
            "utility": score.utility,
        }
