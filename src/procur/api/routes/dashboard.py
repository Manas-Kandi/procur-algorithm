"""Dashboard endpoints."""

from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ...db import get_session
from ...db.models import UserAccount
from ...db.repositories import RequestRepository, ContractRepository
from ..security import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/metrics",
    summary="Get dashboard metrics",
    description="Get summary metrics for the buyer dashboard",
)
def get_dashboard_metrics(
    current_user: UserAccount = Depends(get_current_user),
    db_session: Session = Depends(get_session),
):
    """Get dashboard metrics."""
    request_repo = RequestRepository(db_session)
    
    # Get all requests for the user
    # Repository exposes get_by_user(user_id)
    requests = request_repo.get_by_user(current_user.id)
    
    # Calculate metrics
    total_requests = len(requests)
    active_negotiations = len([r for r in requests if getattr(r, "status", None) == "negotiating"])
    pending_approvals = len([r for r in requests if getattr(r, "status", None) == "approving"])
    completed_requests = len([r for r in requests if getattr(r, "status", None) in ["contracted", "completed"]])
    
    # Calculate average cycle time (mock for now)
    avg_cycle_time = 14.5
    
    # Calculate savings (mock for now)
    total_savings = sum([r.target_price or 0 for r in requests]) * 0.15
    
    return {
        "total_requests": total_requests,
        "active_negotiations": active_negotiations,
        "pending_approvals": pending_approvals,
        "completed_requests": completed_requests,
        "avg_cycle_time_days": avg_cycle_time,
        "total_savings": total_savings,
        "savings_percentage": 15.0,
    }


@router.get(
    "/renewals",
    summary="Get upcoming renewals",
    description="Get contracts up for renewal within the specified timeframe",
)
def get_upcoming_renewals(
    days_ahead: int = Query(60, ge=1, le=365),
    current_user: UserAccount = Depends(get_current_user),
    db_session: Session = Depends(get_session),
):
    """Get upcoming renewals."""
    contract_repo = ContractRepository(db_session)
    
    # Get contracts expiring soon; if schema mismatch occurs, return empty safely
    try:
        contracts = contract_repo.get_expiring_soon(days=days_ahead)
        return contracts
    except Exception:
        # TODO: remove guard once DB schema for contracts is aligned with ORM model
        return []


@router.get(
    "/approvals",
    summary="Get pending approvals",
    description="Get requests pending approval",
)
def get_pending_approvals(
    current_user: UserAccount = Depends(get_current_user),
    db_session: Session = Depends(get_session),
):
    """Get pending approvals."""
    request_repo = RequestRepository(db_session)
    
    # Get requests in approving status
    # If user is an approver, get all pending approvals
    # Otherwise, get only their own requests pending approval
    if current_user.role in ["approver", "admin"]:
        approvals = request_repo.get_by_status("approving")
    else:
        approvals = [
            r for r in request_repo.get_by_user(current_user.id)
            if r.status == "approving"
        ]
    
    return approvals
