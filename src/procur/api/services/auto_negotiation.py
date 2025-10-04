"""Service for running auto-negotiations (callable from background tasks)."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from ...agents.buyer_agent import BuyerAgent, BuyerAgentConfig
from ...agents.seller_agent import SellerAgentConfig
from ...db.repositories import (
    NegotiationRepository,
    OfferRepository,
    RequestRepository,
    VendorRepository,
)
from ...llm import LLMClient
from ...models import NegotiationDecision, OfferComponents, PaymentTerms, Request, VendorProfile
from ...services import (
    AuditTrailService,
    ComplianceService,
    ExplainabilityService,
    GuardrailService,
    MemoryService,
    NegotiationEngine,
    PolicyEngine,
    ScoringService,
)
from ...services.negotiation_engine import ExchangePolicy, VendorNegotiationState
from ...services.vendor_matching import VendorMatchSummary
from ...services.evaluation import FeatureMatchResult, ComplianceScore


def _convert_db_request_to_model(db_request: Any) -> Request:
    """Convert database request record to domain model."""
    return Request(
        request_id=db_request.request_id,
        type=db_request.request_type,
        description=db_request.description,
        quantity=db_request.quantity or 1,
        budget_min=db_request.budget_min or 0.0,
        budget_max=db_request.budget_max or 0.0,
        currency="USD",
        must_haves=db_request.must_haves or [],
        nice_to_haves=db_request.nice_to_haves or [],
        compliance_requirements=db_request.compliance_requirements or [],
        specs=db_request.specs or {},
    )


def _convert_db_vendor_to_model(db_vendor: Any) -> VendorProfile:
    """Convert database vendor record to domain model."""
    from ...models import VendorGuardrails

    guardrails_data = db_vendor.guardrails or {}
    guardrails = VendorGuardrails(
        price_floor=guardrails_data.get("price_floor"),
        price_ceiling=guardrails_data.get("price_ceiling"),
        min_quantity=guardrails_data.get("min_quantity"),
        max_quantity=guardrails_data.get("max_quantity"),
        allowed_terms=guardrails_data.get("allowed_terms", [12, 24, 36]),
        payment_terms_allowed=guardrails_data.get("payment_terms_allowed", ["net_30"]),
        max_discount_pct=guardrails_data.get("max_discount_pct", 0.25),
    )

    vendor = VendorProfile(
        vendor_id=db_vendor.vendor_id,
        name=db_vendor.name,
        category=db_vendor.category or "",
        price_tiers=db_vendor.price_tiers or {},
        capability_tags=db_vendor.features or [],
        certifications=db_vendor.certifications or [],
        guardrails=guardrails,
    )

    # Attach exchange policy if exists
    if db_vendor.exchange_policy:
        exchange_data = db_vendor.exchange_policy
        payment_trade = {}
        for key, value in exchange_data.get("payment_trade", {}).items():
            try:
                payment_trade[PaymentTerms(key)] = float(value)
            except (ValueError, KeyError):
                continue

        vendor._exchange_policy = ExchangePolicy(
            term_trade={int(k): float(v) for k, v in exchange_data.get("term_trade", {}).items()},
            payment_trade=payment_trade,
            value_add_offsets=exchange_data.get("value_add_offsets", {}),
        )

    return vendor


def _create_buyer_agent() -> BuyerAgent:
    """Factory to create buyer agent with all dependencies."""
    policy_engine = PolicyEngine()
    compliance_service = ComplianceService()
    guardrail_service = GuardrailService(run_mode="simulation")
    scoring_service = ScoringService()
    negotiation_engine = NegotiationEngine(
        policy_engine=policy_engine,
        scoring_service=scoring_service,
    )
    explainability_service = ExplainabilityService()
    llm_client = LLMClient()

    return BuyerAgent(
        policy_engine=policy_engine,
        compliance_service=compliance_service,
        guardrail_service=guardrail_service,
        scoring_service=scoring_service,
        negotiation_engine=negotiation_engine,
        explainability_service=explainability_service,
        llm_client=llm_client,
        config=BuyerAgentConfig(),
        seller_config=SellerAgentConfig(),
    )


async def run_auto_negotiation(
    session_id: str,
    db_session: Session,
    max_rounds: int = 8,
) -> Dict[str, Any]:
    """
    Run auto-negotiation for a session (can be called from background tasks).

    This is a service function that doesn't depend on FastAPI request context.

    Args:
        session_id: Negotiation session ID
        db_session: Database session
        max_rounds: Maximum negotiation rounds

    Returns:
        Dictionary with negotiation results
    """
    # Repositories
    neg_repo = NegotiationRepository(db_session)
    request_repo = RequestRepository(db_session)
    vendor_repo = VendorRepository(db_session)
    offer_repo = OfferRepository(db_session)

    # Load negotiation session
    negotiation = neg_repo.get_by_session_id(session_id)
    if not negotiation:
        return {"error": "Negotiation session not found", "session_id": session_id}

    # Check if negotiation is still active
    if negotiation.status != "active":
        return {"error": f"Negotiation is {negotiation.status}, cannot auto-negotiate", "session_id": session_id}

    # Load request and vendor
    request_record = request_repo.get_by_id(negotiation.request_id)
    vendor_record = vendor_repo.get_by_id(negotiation.vendor_id)

    if not request_record or not vendor_record:
        return {"error": "Request or vendor not found", "session_id": session_id}

    # Convert to domain models
    request_model = _convert_db_request_to_model(request_record)
    vendor_model = _convert_db_vendor_to_model(vendor_record)

    # Attach match summary to vendor (if available from negotiation metadata)
    if negotiation.metadata and "match_summary" in negotiation.metadata:
        match_data = negotiation.metadata["match_summary"]
        vendor_model._match_summary = VendorMatchSummary(
            feature=FeatureMatchResult(
                score=match_data.get("feature_score", 0.5),
                matched=[],
                missing=[],
            ),
            compliance=ComplianceScore(
                score=match_data.get("compliance_score", 1.0),
                matched=[],
                missing=[],
                blocking=False,
            ),
            sla_score=match_data.get("sla_score", 1.0),
            category_match=True,
            price_fit=match_data.get("price_fit", 0.5),
        )

    # Create buyer agent
    buyer_agent = _create_buyer_agent()

    # Run negotiation
    try:
        # Import streaming wrapper
        from ..streaming_negotiation import StreamingNegotiationWrapper
        from ..websocket_manager import manager

        # Emit start event
        await manager.send_event(session_id, "negotiation_start", {
            "vendor_name": vendor_model.name,
            "vendor_id": vendor_model.vendor_id,
            "max_rounds": max_rounds,
        })

        # Wrap agent for streaming
        streaming_wrapper = StreamingNegotiationWrapper(buyer_agent, session_id)
        offers_dict = await streaming_wrapper.negotiate_with_streaming(
            request_model,
            [vendor_model]
        )

        # Get the final offer for this vendor
        final_offer = offers_dict.get(vendor_model.vendor_id)

        if not final_offer:
            # No deal reached
            neg_repo.complete_session(
                negotiation.id,
                outcome="no_agreement",
                outcome_reason="Failed to reach agreement",
            )

            return {
                "session_id": session_id,
                "status": "completed",
                "outcome": "no_agreement",
                "rounds_completed": 0,
            }

        # Save final offer to database
        offer_record = offer_repo.create(
            request_id=request_record.id,
            vendor_id=vendor_record.id,
            negotiation_session_id=negotiation.id,
            components={
                "unit_price": final_offer.components.unit_price,
                "currency": final_offer.components.currency,
                "quantity": final_offer.components.quantity,
                "term_months": final_offer.components.term_months,
                "payment_terms": final_offer.components.payment_terms.value,
            },
            score={
                "utility": final_offer.score.utility,
                "risk": final_offer.score.risk,
                "savings": final_offer.score.savings,
            },
            status="pending" if final_offer.accepted else "rejected",
        )

        # Get audit trail for round count
        audit_data = buyer_agent.export_audit()
        rounds_completed = 0
        if audit_data and vendor_model.vendor_id in audit_data:
            session_data = audit_data[vendor_model.vendor_id]
            rounds_completed = len(session_data.get("rounds", []))

        # Complete negotiation
        outcome = "accepted" if final_offer.accepted else "no_agreement"
        neg_repo.complete_session(
            negotiation.id,
            outcome=outcome,
            outcome_reason="Auto-negotiation completed",
            final_offer_id=offer_record.id if final_offer.accepted else None,
        )

        return {
            "session_id": session_id,
            "status": "completed",
            "outcome": outcome,
            "rounds_completed": rounds_completed,
            "final_offer": {
                "offer_id": offer_record.offer_id,
                "unit_price": final_offer.components.unit_price,
                "term_months": final_offer.components.term_months,
                "payment_terms": final_offer.components.payment_terms.value,
                "utility": final_offer.score.utility,
                "tco": buyer_agent.negotiation_engine.calculate_tco(final_offer.components),
            } if final_offer else None,
        }

    except Exception as e:
        # Handle negotiation errors
        neg_repo.complete_session(
            negotiation.id,
            outcome="error",
            outcome_reason=f"Negotiation error: {str(e)}",
        )

        print(f"Error in auto-negotiation for session {session_id}: {str(e)}")
        import traceback
        traceback.print_exc()

        return {
            "error": str(e),
            "session_id": session_id,
            "status": "error",
        }
