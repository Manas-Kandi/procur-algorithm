from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from ..models import Offer, Request, VendorProfile
from ..services import (
    ComplianceService,
    ExplainabilityService,
    GuardrailService,
    NegotiationEngine,
    NegotiationPlan,
    PolicyEngine,
    ScoringService,
)
from .event_bus import Event, EventBus
from ..agents import BuyerAgent


@dataclass
class ProcurementContext:
    request: Request
    vendors: List[VendorProfile]
    policy_engine: PolicyEngine
    compliance_service: ComplianceService
    guardrail_service: GuardrailService
    scoring_service: ScoringService
    negotiation_engine: NegotiationEngine
    explainability_service: ExplainabilityService
    event_bus: EventBus
    buyer_agent: BuyerAgent


class ProcurementWorkflow:
    """High-level orchestration for buyer agent workflow."""

    def __init__(self, context: ProcurementContext) -> None:
        self.ctx = context

    def start(self, plan: NegotiationPlan) -> Dict[str, Offer]:
        _ = plan  # Plan is applied through the buyer agent configuration
        request = self.ctx.request
        buyer_agent = self.ctx.buyer_agent

        self.ctx.event_bus.publish(
            Event(name="request.created", payload={"request_id": request.request_id})
        )

        shortlisted = buyer_agent.shortlist_vendors(request, self.ctx.vendors)
        for vendor in shortlisted:
            self.ctx.event_bus.publish(
                Event(
                    name="vendor.shortlisted",
                    payload={
                        "request_id": request.request_id,
                        "vendor_id": vendor.vendor_id,
                        "vendor_name": vendor.name,
                    },
                )
            )

        offers = buyer_agent.negotiate(request, shortlisted)

        for vendor_id, offer in offers.items():
            self.ctx.event_bus.publish(
                Event(
                    name="vendor.offer_generated",
                    payload={
                        "request_id": request.request_id,
                        "vendor_id": vendor_id,
                        "unit_price": offer.components.unit_price,
                        "term_months": offer.components.term_months,
                        "payment_terms": offer.components.payment_terms.value,
                    },
                )
            )

        return offers

    def finalize(self, offers: Dict[str, Offer]) -> Dict[str, Dict[str, List[str]]]:
        sensitivities = {
            name: self.ctx.scoring_service.sensitivity_analysis(offer.score)
            for name, offer in offers.items()
        }
        return self.ctx.explainability_service.bundle_summary(offers, sensitivities)
