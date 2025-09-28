from __future__ import annotations

from pathlib import Path

import pytest

from procur.models import (
    Offer,
    OfferComponents,
    PaymentTerms,
    Request,
    RequestType,
    VendorGuardrails,
    VendorProfile,
)
from procur.models.enums import NegotiationDecision
from procur.services import (
    PolicyEngine,
    ScoringService,
    ComplianceService,
    GuardrailService,
    ExplainabilityService,
    AuditTrailService,
    MemoryService,
    RetrievalService,
)
from procur.services.negotiation_engine import (
    NegotiationEngine,
    NegotiationPlan,
    VendorNegotiationState,
    OpponentModel,
    SellerStrategy,
)
from procur.services.scoring_service import ScoreWeights
from procur.data import load_seed_catalog
from procur.agents import BuyerAgent, BuyerAgentConfig


def make_request(budget_per_seat: float, quantity: int = 200) -> Request:
    return Request(
        request_id="req-test",
        requester_id="user-test",
        type=RequestType.SAAS,
        description="CRM software",
        specs={"seats": quantity, "features": ["crm"]},
        quantity=quantity,
        budget_max=budget_per_seat * quantity,
        must_haves=["crm"],
        compliance_requirements=["SOC2"],
    )


def make_vendor(list_price: float, floor_price: float) -> VendorProfile:
    return VendorProfile(
        vendor_id="vendor-test",
        name="TestVendor",
        capability_tags=["crm", "lead_management", "contact_management", "pipeline_tracking", "email_integration"],
        certifications=["SOC2"],
        regions=["us-east"],
        lead_time_brackets={"default": (30, 45)},
        price_tiers={"200": list_price},
        guardrails=VendorGuardrails(price_floor=floor_price, payment_terms_allowed=[PaymentTerms.NET_30.value]),
        reliability_stats={},
    )


def make_engine() -> NegotiationEngine:
    scoring = ScoringService(weights=ScoreWeights())
    return NegotiationEngine(PolicyEngine(), scoring)


def test_tco_calculation_matches_expected_values():
    scoring = ScoringService()
    orbit_offer = OfferComponents(
        unit_price=180.0,
        currency="USD",
        quantity=200,
        term_months=12,
        payment_terms=PaymentTerms.NET_30,
    )
    celerity_offer = OfferComponents(
        unit_price=294.0,
        currency="USD",
        quantity=200,
        term_months=12,
        payment_terms=PaymentTerms.NET_30,
    )

    assert scoring.compute_tco(orbit_offer) == pytest.approx(36000.0)
    assert scoring.compute_tco(celerity_offer) == pytest.approx(58800.0)


def test_buyer_utility_scaling_with_cost_and_compliance():
    engine = make_engine()
    request = make_request(budget_per_seat=900.0)
    vendor = make_vendor(list_price=1200.0, floor_price=980.0)
    offer = OfferComponents(
        unit_price=1200.0,
        currency="USD",
        quantity=200,
        term_months=12,
        payment_terms=PaymentTerms.NET_30,
    )

    utility = engine.calculate_utility(offer, request, vendor=vendor, is_buyer=True)
    expected_cost_fit = min((request.budget_max or 0) / engine.calculate_tco(offer), 1.0)
    expected = 0.4 * expected_cost_fit + 0.2 * 1.0 + 0.2 * 1.0 + 0.1 * 1.0 + 0.1 * 1.0
    assert utility == pytest.approx(round(expected, 4))


def test_seller_strategy_closes_at_floor():
    engine = make_engine()
    vendor = make_vendor(list_price=240.0, floor_price=180.0)
    opponent = OpponentModel(price_floor_estimate=180.0, price_ceiling_estimate=240.0)
    state = VendorNegotiationState(vendor=vendor, opponent_model=opponent, plan=NegotiationPlan({}, [], {}, []))
    state.round = 2
    buyer_offer = OfferComponents(
        unit_price=180.0,
        currency="USD",
        quantity=200,
        term_months=12,
        payment_terms=PaymentTerms.NET_30,
    )

    strategy = engine.determine_seller_strategy(state, buyer_offer)
    assert strategy.name == "CLOSE_DEAL"


def test_drop_outcome_state_flagged_correctly(monkeypatch):
    engine = make_engine()
    policy_engine = engine.policy_engine
    scoring_service = engine.scoring_service
    compliance_service = ComplianceService(mandatory_certifications=["soc2"])
    guardrail_service = GuardrailService(run_mode="simulation")
    explainability_service = ExplainabilityService()
    audit_service = AuditTrailService()
    memory_service = MemoryService()
    retrieval_service = RetrievalService()

    class DummyLLM:
        def complete(self, *_, **__):
            raise RuntimeError("LLM should not be invoked in unit tests")

    buyer_agent = BuyerAgent(
        policy_engine=policy_engine,
        compliance_service=compliance_service,
        guardrail_service=guardrail_service,
        scoring_service=scoring_service,
        negotiation_engine=engine,
        explainability_service=explainability_service,
        llm_client=DummyLLM(),
        config=BuyerAgentConfig(),
        audit_service=audit_service,
        memory_service=memory_service,
        retrieval_service=retrieval_service,
    )

    request = make_request(budget_per_seat=900.0)
    vendor = make_vendor(list_price=240.0, floor_price=180.0)
    state = buyer_agent._build_state(request, vendor)
    previous_offer = buyer_agent._baseline_offer(request, vendor)

    class StubSellerAgent:
        def __init__(self, vendor: VendorProfile):
            self.vendor = vendor

        def respond(self, *, request: Request, state: VendorNegotiationState, buyer_offer: OfferComponents, round_number: int):
            components = buyer_offer.model_copy(deep=True)
            offer = Offer(
                offer_id=f"{request.request_id}-{self.vendor.vendor_id}-seller-{round_number}",
                request_id=request.request_id,
                vendor_id=self.vendor.vendor_id,
                components=components,
                score=scoring_service.score_offer(self.vendor, components, request),
            )
            policy_feedback = policy_engine.validate_offer(
                request,
                components,
                vendor=self.vendor,
                is_buyer_proposal=False,
            )
            guardrails = guardrail_service.vet_offer(self.vendor, components)
            return offer, SellerStrategy.REJECT_BELOW_FLOOR, guardrails, policy_feedback

    stub_seller = StubSellerAgent(vendor)

    monkeypatch.setattr(
        engine,
        "decide_next_move",
        lambda plan, state, offer: NegotiationDecision.DROP,
    )
    monkeypatch.setattr(buyer_agent, "_generate_buyer_message", lambda *_, **__: None)

    round_result = buyer_agent._run_round(
        request=request,
        state=state,
        seller_agent=stub_seller,
        previous_offer=previous_offer,
        round_number=1,
        compliance_notes=[],
    )

    assert round_result["decision"] is NegotiationDecision.DROP
    assert round_result["should_close"] is True
    assert state.outcome_state == "dropped"
    assert state.outcome_reason == "buyer_drop"


def test_no_zopa_gate_blocks_vendor():
    engine = make_engine()
    request = make_request(budget_per_seat=900.0)
    records = load_seed_catalog(Path("assets/seeds.json"))
    apollo = next(record for record in records if record.seed_id == "apollo-crm")
    vendor = apollo.to_vendor_profile()
    feasible = engine.feasible_with_trades(request, vendor, apollo.exchange_policy)
    assert feasible is False
