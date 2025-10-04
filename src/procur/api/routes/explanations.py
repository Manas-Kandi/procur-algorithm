"""API endpoints for LLM-powered negotiation explanations."""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...db import get_session
from ...db.models import UserAccount
from ...db.repositories import (
    NegotiationRepository,
    OfferRepository,
    RequestRepository,
    VendorRepository,
)
from ...models import Request, VendorProfile, Offer
from ...services import LLMExplainabilityService
from ..schemas import ExplanationResponse, ExplainNegotiationRequest
from ..security import get_current_user

router = APIRouter(prefix="/explanations", tags=["Explanations"])


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

    return VendorProfile(
        vendor_id=db_vendor.vendor_id,
        name=db_vendor.name,
        category=db_vendor.category or "",
        price_tiers=db_vendor.price_tiers or {},
        capability_tags=db_vendor.features or [],
        certifications=db_vendor.certifications or [],
        guardrails=guardrails,
    )


def _convert_db_offer_to_model(db_offer: Any) -> Offer:
    """Convert database offer record to domain model."""
    from ...models import OfferComponents, OfferScore, PaymentTerms

    components = OfferComponents(
        unit_price=db_offer.components["unit_price"],
        currency=db_offer.components.get("currency", "USD"),
        quantity=db_offer.components["quantity"],
        term_months=db_offer.components["term_months"],
        payment_terms=PaymentTerms(db_offer.components["payment_terms"]),
        one_time_fees=db_offer.components.get("one_time_fees"),
    )

    score = OfferScore(
        utility=db_offer.score.get("utility", 0.0),
        risk=db_offer.score.get("risk", 0.0),
        savings=db_offer.score.get("savings", 0.0),
    )

    return Offer(
        offer_id=db_offer.offer_id,
        vendor_id=db_offer.vendor_id,
        components=components,
        score=score,
        accepted=db_offer.status == "accepted",
        from_buyer=True,  # Assume buyer offers for now
    )


@router.post(
    "/negotiations/{session_id}",
    response_model=ExplanationResponse,
    summary="Generate explanation for negotiation",
    description="Generate LLM-powered explanation for a negotiation session",
)
async def explain_negotiation(
    session_id: str,
    request_data: ExplainNegotiationRequest,
    current_user: UserAccount = Depends(get_current_user),
    db_session: Session = Depends(get_session),
) -> ExplanationResponse:
    """
    Generate an LLM-powered explanation for a negotiation session.

    This endpoint uses the LLMExplainabilityService to:
    1. Analyze the negotiation state
    2. Generate human-readable explanations
    3. Provide actionable recommendations
    4. Create structured audit trails

    Args:
        session_id: Negotiation session ID
        request_data: Configuration for explanation generation
        current_user: Authenticated user
        db_session: Database session

    Returns:
        Complete explanation record with summary, rationale, and recommendations
    """
    # Repositories
    neg_repo = NegotiationRepository(db_session)
    request_repo = RequestRepository(db_session)
    vendor_repo = VendorRepository(db_session)
    offer_repo = OfferRepository(db_session)

    # Load negotiation session
    negotiation = neg_repo.get_by_session_id(session_id)
    if not negotiation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Negotiation session not found",
        )

    # Check authorization
    request_record = request_repo.get_by_id(negotiation.request_id)
    if request_record.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this negotiation",
        )

    # Load vendor
    vendor_record = vendor_repo.get_by_id(negotiation.vendor_id)
    if not vendor_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found",
        )

    # Get offers for this session (sorted by created_at)
    offers = offer_repo.get_by_negotiation_session(negotiation.id)
    if not offers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No offers found for this negotiation session",
        )

    # Convert to domain models
    request_model = _convert_db_request_to_model(request_record)
    vendor_model = _convert_db_vendor_to_model(vendor_record)
    offer_models = [_convert_db_offer_to_model(o) for o in offers]

    # Determine which offer to explain
    if request_data.round_number is not None:
        if request_data.round_number < 1 or request_data.round_number > len(offer_models):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid round number. Must be between 1 and {len(offer_models)}",
            )
        latest_offer = offer_models[request_data.round_number - 1]
        round_number = request_data.round_number
    else:
        latest_offer = offer_models[-1]
        round_number = len(offer_models)

    # Extract policy events from negotiation metadata
    policy_events = negotiation.metadata.get("policy_events", []) if negotiation.metadata else []

    # Get decision and acceptance probability from metadata
    decision = negotiation.metadata.get("decision", "COUNTER") if negotiation.metadata else "COUNTER"
    acceptance_probability = negotiation.metadata.get("acceptance_probability", 0.0) if negotiation.metadata else 0.0

    # Get opponent model and plan from metadata
    opponent_model = negotiation.metadata.get("opponent_model") if negotiation.metadata else None
    plan = negotiation.metadata.get("plan") if negotiation.metadata else None

    # Create explainability service
    explainability_service = LLMExplainabilityService()

    try:
        # Generate explanation
        explanation = explainability_service.explain_state(
            request=request_model,
            vendor=vendor_model,
            latest_offer=latest_offer,
            history=offer_models,
            round_number=round_number,
            decision=decision,
            acceptance_probability=acceptance_probability,
            policy_events=policy_events,
            opponent_model=opponent_model,
            plan=plan,
        )

        # Convert to response model
        return ExplanationResponse(
            explanation_version=explanation.explanation_version,
            short_summary=explanation.short_summary,
            detailed_explanation=explanation.detailed_explanation,
            rationale=[
                {"fact": r.fact, "implication": r.implication}
                for r in explanation.rationale
            ],
            policy_summary=[
                {"policy_id": p.policy_id, "outcome": p.outcome, "note": p.note}
                for p in explanation.policy_summary
            ],
            numeric_snapshots={
                "latest_unit_price": explanation.numeric_snapshots.latest_unit_price,
                "budget_per_unit": explanation.numeric_snapshots.budget_per_unit,
                "tco": explanation.numeric_snapshots.tco,
                "tco_vs_budget_pct": explanation.numeric_snapshots.tco_vs_budget_pct,
                "acceptance_probability": explanation.numeric_snapshots.acceptance_probability,
            },
            recommended_actions=[
                {"priority": a.priority, "type": a.type, "text": a.text}
                for a in explanation.recommended_actions
            ],
            confidence=explanation.confidence,
            explainability_trace=[
                {"step": t.step, "detail": t.detail}
                for t in explanation.explainability_trace
            ] if request_data.include_trace else [],
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate explanation: {str(e)}",
        )


@router.get(
    "/negotiations/{session_id}/rounds",
    summary="List available rounds for explanation",
    description="Get list of negotiation rounds available for explanation",
)
async def list_negotiation_rounds(
    session_id: str,
    current_user: UserAccount = Depends(get_current_user),
    db_session: Session = Depends(get_session),
) -> Dict[str, Any]:
    """
    List available negotiation rounds for a session.

    Args:
        session_id: Negotiation session ID
        current_user: Authenticated user
        db_session: Database session

    Returns:
        List of available rounds with basic info
    """
    # Repositories
    neg_repo = NegotiationRepository(db_session)
    request_repo = RequestRepository(db_session)
    offer_repo = OfferRepository(db_session)

    # Load negotiation session
    negotiation = neg_repo.get_by_session_id(session_id)
    if not negotiation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Negotiation session not found",
        )

    # Check authorization
    request_record = request_repo.get_by_id(negotiation.request_id)
    if request_record.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this negotiation",
        )

    # Get offers for this session
    offers = offer_repo.get_by_negotiation_session(negotiation.id)

    rounds = []
    for idx, offer in enumerate(offers, start=1):
        rounds.append({
            "round_number": idx,
            "offer_id": offer.offer_id,
            "unit_price": offer.components.get("unit_price"),
            "status": offer.status,
            "created_at": offer.created_at.isoformat() if offer.created_at else None,
        })

    return {
        "session_id": session_id,
        "total_rounds": len(rounds),
        "rounds": rounds,
    }
