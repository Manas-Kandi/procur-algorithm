"""Sourcing and negotiation initiation endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...db import get_session
from ...db.models import UserAccount
from ...db.repositories import (
    RequestRepository,
    VendorRepository,
    NegotiationRepository,
)
from ..schemas import NegotiationResponse
from ..security import get_current_user

router = APIRouter(prefix="/sourcing", tags=["Sourcing"])


@router.post(
    "/start/{request_id}",
    response_model=List[NegotiationResponse],
    summary="Start negotiations for a request",
    description="Find vendors and initiate negotiation sessions for a request",
)
def start_negotiations(
    request_id: str,
    current_user: UserAccount = Depends(get_current_user),
    db_session: Session = Depends(get_session),
):
    """Start negotiations for a request by creating negotiation sessions with vendors."""
    request_repo = RequestRepository(db_session)
    vendor_repo = VendorRepository(db_session)
    neg_repo = NegotiationRepository(db_session)
    
    # Get the request
    request = request_repo.get_by_request_id(request_id)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found",
        )
    
    # Check authorization
    if request.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to start negotiations for this request",
        )
    
    # Check if request is in correct status
    if request.status not in ["draft", "intake", "sourcing"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot start negotiations for request with status: {request.status}",
        )
    
    # Get vendors (for now, get all active vendors - in production, this would filter by category, etc.)
    vendors = vendor_repo.get_all_active()
    
    if not vendors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active vendors found to negotiate with",
        )
    
    # Limit to top 5 vendors for demo purposes
    vendors = vendors[:5]
    
    # Create negotiation sessions
    created_sessions = []
    for vendor in vendors:
        # Check if session already exists
        existing = neg_repo.get_by_request(request.id)
        vendor_ids = [s.vendor_id for s in existing]
        
        if vendor.id in vendor_ids:
            continue  # Skip if session already exists
        
        # Create new negotiation session
        import uuid
        session_id = f"neg-{uuid.uuid4().hex[:12]}"
        
        session_data = {
            "session_id": session_id,
            "request_id": request.id,
            "vendor_id": vendor.id,
            "status": "active",
            "current_round": 1,
            "max_rounds": 8,
            "total_messages": 0,
        }
        
        session = neg_repo.create(session_data)
        created_sessions.append(session)
    
    # Update request status to negotiating
    request_repo.update(request.id, status="negotiating")
    
    return created_sessions
