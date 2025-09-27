from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from ..models import Offer, OfferComponents, Request, VendorProfile
from ..services import GuardrailService, NegotiationEngine, PolicyEngine, ScoringService
from ..services.policy_engine import PolicyResult
from ..services.guardrail_service import GuardrailAlert
from ..services.negotiation_engine import SellerStrategy, VendorNegotiationState


@dataclass
class SellerAgentConfig:
    response_window_hours: int = 24


class SellerAgent:
    """Simulated seller counterpart that enforces guardrails and pricing policy."""

    def __init__(
        self,
        vendor: VendorProfile,
        policy_engine: PolicyEngine,
        scoring_service: ScoringService,
        guardrail_service: GuardrailService,
        negotiation_engine: NegotiationEngine,
        config: SellerAgentConfig | None = None,
    ) -> None:
        self.vendor = vendor
        self.policy_engine = policy_engine
        self.scoring_service = scoring_service
        self.guardrail_service = guardrail_service
        self.negotiation_engine = negotiation_engine
        self.config = config or SellerAgentConfig()

    def respond(
        self,
        request: Request,
        state: VendorNegotiationState,
        buyer_offer: OfferComponents,
        round_number: int,
    ) -> Tuple[Offer, SellerStrategy, List[GuardrailAlert], PolicyResult]:
        strategy = self.negotiation_engine.determine_seller_strategy(state, buyer_offer)
        counter_components = self.negotiation_engine.generate_seller_counter(strategy, buyer_offer, state)

        policy_feedback = self.policy_engine.validate_offer(
            request,
            counter_components,
            vendor=self.vendor,
            is_buyer_proposal=False,
        )
        if not policy_feedback.valid:
            floor = self.vendor.guardrails.price_floor or counter_components.unit_price
            counter_components.unit_price = max(counter_components.unit_price, floor)

        guardrail_alerts = self.guardrail_service.vet_offer(self.vendor, counter_components)
        score = self.scoring_service.score_offer(self.vendor, counter_components, request)

        offer = Offer(
            offer_id=f"{request.request_id}-{self.vendor.vendor_id}-seller-{round_number}",
            request_id=request.request_id,
            vendor_id=self.vendor.vendor_id,
            components=counter_components,
            score=score,
        )

        return offer, strategy, guardrail_alerts, policy_feedback
