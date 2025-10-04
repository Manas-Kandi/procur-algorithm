"""Auto-negotiation endpoints with WebSocket streaming support."""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from ...agents.buyer_agent import BuyerAgent, BuyerAgentConfig
from ...agents.seller_agent import SellerAgentConfig
from ...db import get_session
from ...db.models import UserAccount
from ...db.repositories import (
    NegotiationRepository,
    OfferRepository,
    RequestRepository,
    VendorRepository,
)
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
from ...services.negotiation_engine import (
    ExchangePolicy,
    VendorNegotiationState,
)
from ...services.vendor_matching import VendorMatchSummary
from ...services.evaluation import FeatureMatchResult, ComplianceScore
from ...llm import LLMClient
from ..schemas import (
    AutoNegotiateRequest,
    NegotiationEventResponse,
    NegotiationProgressResponse,
)
from ..security import get_current_user

router = APIRouter(prefix="/negotiations", tags=["Auto-Negotiation"])


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


async def _stream_negotiation_event(
    websocket: WebSocket,
    event_type: str,
    data: Dict[str, Any],
) -> None:
    """Send a negotiation event to WebSocket client."""
    event = {
        "type": event_type,
        "timestamp": data.get("timestamp", ""),
        "data": data,
    }
    await websocket.send_json(event)


@router.websocket("/ws/{session_id}")
async def negotiation_websocket(
    websocket: WebSocket,
    session_id: str,
):
    """WebSocket endpoint for real-time negotiation streaming."""
    from ..websocket_manager import manager

    await manager.connect(websocket, session_id)

    try:
        # Send initial connection confirmation
        await manager.send_event(
            session_id,
            "connected",
            {"session_id": session_id, "message": "Connected to negotiation stream"},
        )

        # Keep connection alive and handle client messages
        while True:
            try:
                # Wait for client ping or disconnect
                message = await asyncio.wait_for(websocket.receive_text(), timeout=60.0)

                # Echo back any client messages (for keepalive)
                if message == "ping":
                    await websocket.send_text("pong")

            except asyncio.TimeoutError:
                # Send keepalive ping
                await websocket.send_text("ping")

    except WebSocketDisconnect:
        await manager.disconnect(websocket, session_id)
        print(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        await manager.disconnect(websocket, session_id)
        print(f"WebSocket error for session {session_id}: {e}")


@router.post(
    "/{session_id}/auto-negotiate",
    response_model=NegotiationProgressResponse,
    summary="Auto-negotiate with vendor",
    description="Run automated AI negotiation for a session with real-time streaming",
)
async def auto_negotiate(
    session_id: str,
    request_data: AutoNegotiateRequest,
    current_user: UserAccount = Depends(get_current_user),
    db_session: Session = Depends(get_session),
) -> NegotiationProgressResponse:
    """
    Execute automated negotiation for a vendor.

    This endpoint triggers the AI negotiation engine to automatically
    negotiate with a vendor on behalf of the buyer. It will:

    1. Load the request and vendor details
    2. Initialize the buyer and seller agents
    3. Run negotiation rounds until completion
    4. Save all offers and final outcome to database
    5. Stream progress via WebSocket if client is connected

    Args:
        session_id: Negotiation session ID
        request_data: Configuration for auto-negotiation
        current_user: Authenticated user
        db_session: Database session

    Returns:
        Negotiation progress with final outcome
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
            detail="Not authorized to negotiate this request",
        )

    # Check if negotiation is still active
    if negotiation.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Negotiation is {negotiation.status}, cannot auto-negotiate",
        )

    # Load vendor
    vendor_record = vendor_repo.get_by_id(negotiation.vendor_id)
    if not vendor_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found",
        )

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

    # Run negotiation with streaming
    try:
        # Import streaming wrapper
        from ..streaming_negotiation import StreamingNegotiationWrapper
        from ..websocket_manager import manager

        # Emit start event
        await manager.send_event(session_id, "negotiation_start", {
            "vendor_name": vendor_model.name,
            "vendor_id": vendor_model.vendor_id,
            "max_rounds": request_data.max_rounds,
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

            return NegotiationProgressResponse(
                session_id=session_id,
                status="completed",
                outcome="no_agreement",
                rounds_completed=0,
                final_offer=None,
            )

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

        return NegotiationProgressResponse(
            session_id=session_id,
            status="completed",
            outcome=outcome,
            rounds_completed=rounds_completed,
            final_offer={
                "offer_id": offer_record.offer_id,
                "unit_price": final_offer.components.unit_price,
                "term_months": final_offer.components.term_months,
                "payment_terms": final_offer.components.payment_terms.value,
                "utility": final_offer.score.utility,
                "tco": buyer_agent.negotiation_engine.calculate_tco(final_offer.components),
            } if final_offer else None,
        )

    except Exception as e:
        # Handle negotiation errors
        neg_repo.complete_session(
            negotiation.id,
            outcome="error",
            outcome_reason=f"Negotiation error: {str(e)}",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Auto-negotiation failed: {str(e)}",
        )


@router.post(
    "/{session_id}/run-round",
    summary="Execute single negotiation round",
    description="Run one round of negotiation with the vendor",
)
async def run_negotiation_round(
    session_id: str,
    current_user: UserAccount = Depends(get_current_user),
    db_session: Session = Depends(get_session),
):
    """Execute a single round of negotiation."""
    # This is a simpler endpoint for manual step-by-step negotiation
    # For MVP, we'll focus on the full auto-negotiate endpoint
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Single round execution coming soon. Use auto-negotiate for now.",
    )
