"""Negotiation endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...db import get_session
from ...db.models import UserAccount
from ...db.repositories import (
    NegotiationRepository,
    OfferRepository,
    RequestRepository,
)
from ..schemas import NegotiationApprove, NegotiationResponse, OfferResponse
from ..security import get_current_user

router = APIRouter(prefix="/negotiations", tags=["Negotiations"])


@router.get(
    "/request/{request_id}",
    response_model=List[NegotiationResponse],
    summary="Get negotiations for request",
    description="Get all negotiation sessions for a request",
)
def get_negotiations_for_request(
    request_id: str,
    current_user: UserAccount = Depends(get_current_user),
    db_session: Session = Depends(get_session),
):
    """Get all negotiations for a request."""
    from ...db.repositories import VendorRepository
    
    neg_repo = NegotiationRepository(db_session)
    request_repo = RequestRepository(db_session)
    vendor_repo = VendorRepository(db_session)
    offer_repo = OfferRepository(db_session)
    
    # Check if request exists and user has access (by request_id string)
    request = request_repo.get_by_request_id(request_id)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found",
        )
    
    if request.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this request",
        )
    
    # Get all negotiations for the request using the integer ID
    negotiations = neg_repo.get_by_request(request.id)
    
    # Enrich with vendor data and messages
    enriched = []
    for neg in negotiations:
        # Get vendor name with fallback
        vendor_name = f"Vendor {neg.vendor_id}"
        try:
            vendor = vendor_repo.get_by_id(neg.vendor_id)
            if vendor:
                vendor_name = vendor.name
        except Exception as e:
            print(f"Error fetching vendor {neg.vendor_id}: {e}")
        
        # Get offers for this session (messages)
        offers = []
        try:
            offers = offer_repo.get_by_negotiation_session(neg.id)
        except Exception as e:
            print(f"Error fetching offers for session {neg.id}: {e}")
        
        # Calculate current metrics
        current_price = offers[-1].unit_price if offers else None
        total_cost = (current_price * request.quantity if current_price and request.quantity else None)
        
        # Build response using NegotiationResponse schema
        from ..schemas import NegotiationResponse
        neg_response = NegotiationResponse(
            id=neg.id,
            session_id=neg.session_id,
            request_id=neg.request_id,
            vendor_id=neg.vendor_id,
            status=neg.status,
            current_round=neg.current_round,
            max_rounds=neg.max_rounds,
            outcome=neg.outcome,
            outcome_reason=neg.outcome_reason,
            started_at=neg.started_at,
            completed_at=neg.completed_at,
            total_messages=neg.total_messages,
            savings_achieved=neg.savings_achieved,
            vendor_name=vendor_name,
            current_price=current_price,
            total_cost=total_cost,
            utility_score=offers[-1].score if offers else None,
            rounds_completed=neg.current_round,
            messages=[],  # Will be populated by WebSocket events
        )
        enriched.append(neg_response)
    
    return enriched


@router.get(
    "/{session_id}",
    response_model=NegotiationResponse,
    summary="Get negotiation",
    description="Get negotiation session details",
)
def get_negotiation(
    session_id: str,
    current_user: UserAccount = Depends(get_current_user),
    db_session: Session = Depends(get_session),
):
    """Get negotiation session details."""
    neg_repo = NegotiationRepository(db_session)
    request_repo = RequestRepository(db_session)
    
    negotiation = neg_repo.get_by_session_id(session_id)
    if not negotiation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Negotiation not found",
        )
    
    # Check if user owns the request
    request = request_repo.get_by_id(negotiation.request_id)
    if request.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this negotiation",
        )
    
    return negotiation


@router.get(
    "/{session_id}/offers",
    response_model=List[OfferResponse],
    summary="Get negotiation offers",
    description="Get all offers in a negotiation session",
)
def get_negotiation_offers(
    session_id: str,
    current_user: UserAccount = Depends(get_current_user),
    db_session: Session = Depends(get_session),
):
    """Get all offers in a negotiation session."""
    neg_repo = NegotiationRepository(db_session)
    offer_repo = OfferRepository(db_session)
    request_repo = RequestRepository(db_session)
    
    negotiation = neg_repo.get_by_session_id(session_id)
    if not negotiation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Negotiation not found",
        )
    
    # Check authorization
    request = request_repo.get_by_id(negotiation.request_id)
    if request.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this negotiation",
        )
    
    # Get offers
    offers = offer_repo.get_by_negotiation_session(negotiation.id)
    
    return offers


@router.post(
    "/{session_id}/approve",
    response_model=NegotiationResponse,
    summary="Approve negotiation offer",
    description="Approve an offer and complete negotiation",
)
def approve_negotiation(
    session_id: str,
    approval_data: NegotiationApprove,
    current_user: UserAccount = Depends(get_current_user),
    db_session: Session = Depends(get_session),
):
    """Approve an offer and complete the negotiation."""
    neg_repo = NegotiationRepository(db_session)
    offer_repo = OfferRepository(db_session)
    request_repo = RequestRepository(db_session)
    
    negotiation = neg_repo.get_by_session_id(session_id)
    if not negotiation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Negotiation not found",
        )
    
    # Check authorization
    request = request_repo.get_by_id(negotiation.request_id)
    if request.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to approve this negotiation",
        )
    
    # Check if negotiation is still active
    if negotiation.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Negotiation is {negotiation.status}, cannot approve",
        )
    
    # Get and validate offer
    offer = offer_repo.get_by_id(approval_data.offer_id)
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offer not found",
        )
    
    if offer.negotiation_session_id != negotiation.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Offer does not belong to this negotiation",
        )
    
    # Accept the offer
    offer_repo.accept_offer(offer.id)
    
    # Complete negotiation
    updated_negotiation = neg_repo.complete_session(
        negotiation.id,
        outcome="accepted",
        outcome_reason=approval_data.notes or "Offer approved by buyer",
        final_offer_id=offer.id,
    )
    
    return updated_negotiation


@router.post(
    "/{session_id}/reject",
    response_model=NegotiationResponse,
    summary="Reject negotiation",
    description="Reject negotiation and mark as failed",
)
def reject_negotiation(
    session_id: str,
    reason: str,
    current_user: UserAccount = Depends(get_current_user),
    db_session: Session = Depends(get_session),
):
    """Reject a negotiation."""
    neg_repo = NegotiationRepository(db_session)
    request_repo = RequestRepository(db_session)
    
    negotiation = neg_repo.get_by_session_id(session_id)
    if not negotiation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Negotiation not found",
        )
    
    # Check authorization
    request = request_repo.get_by_id(negotiation.request_id)
    if request.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to reject this negotiation",
        )
    
    # Complete negotiation as rejected
    updated_negotiation = neg_repo.complete_session(
        negotiation.id,
        outcome="rejected",
        outcome_reason=reason,
    )
    
    return updated_negotiation
