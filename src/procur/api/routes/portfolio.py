"""Portfolio API routes for subscription management"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta

from procur.db.session import get_session
from procur.db.repositories import ContractRepository
from procur.api.security import get_current_active_user
from procur.db.models import UserAccount

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


# Response Models
class SubscriptionResponse(BaseModel):
    contract_id: str
    vendor_name: str
    service_name: str
    cost_per_month: float
    seats_licensed: int
    seats_active: int
    utilization_percent: float
    renewal_date: str
    auto_renew: bool
    status: str  # "active" | "expiring_soon" | "underutilized"

    class Config:
        from_attributes = True


class UsageMetricsResponse(BaseModel):
    daily_active_users: List[int]
    feature_usage: dict
    cost_per_user: float
    waste_estimate: float

    class Config:
        from_attributes = True


class PortfolioActionRequest(BaseModel):
    action: str  # "flag_renegotiation" | "request_cancellation" | "adjust_seats"
    reason: Optional[str] = None
    target_seats: Optional[int] = None


@router.get("/subscriptions", response_model=List[SubscriptionResponse])
async def get_subscriptions(
    current_user: UserAccount = Depends(get_current_active_user),
    session: Session = Depends(get_session),
):
    """
    Get all active subscriptions (contracts) for the current user.

    Returns subscription details with utilization metrics.
    """
    contract_repo = ContractRepository(session)

    # Get all active contracts for user
    contracts = session.query(contract_repo.model)\
        .join(contract_repo.model.request)\
        .filter(contract_repo.model.request.has(user_id=current_user.id))\
        .filter(contract_repo.model.status == 'active')\
        .all()

    subscriptions = []
    now = datetime.utcnow()

    for contract in contracts:
        # Calculate utilization (for demo, we'll use a simulated value)
        # In production, this would come from SSO/directory integration
        seats_active = _simulate_seat_usage(contract.quantity)
        utilization_percent = (seats_active / contract.quantity * 100) if contract.quantity > 0 else 0

        # Determine status
        days_until_renewal = (contract.renewal_date - now.date()).days if contract.renewal_date else 999
        if days_until_renewal <= 30:
            status = "expiring_soon"
        elif utilization_percent < 70:
            status = "underutilized"
        else:
            status = "active"

        # Monthly cost calculation
        monthly_cost = contract.total_value / contract.term_months if contract.term_months > 0 else 0

        subscriptions.append(SubscriptionResponse(
            contract_id=contract.contract_id,
            vendor_name=contract.vendor.name if contract.vendor else "Unknown Vendor",
            service_name=contract.request.description if contract.request else "Service",
            cost_per_month=round(monthly_cost, 2),
            seats_licensed=contract.quantity,
            seats_active=seats_active,
            utilization_percent=round(utilization_percent, 1),
            renewal_date=contract.renewal_date.isoformat() if contract.renewal_date else "",
            auto_renew=contract.auto_renew or False,
            status=status,
        ))

    return subscriptions


@router.get("/subscriptions/{contract_id}/usage", response_model=UsageMetricsResponse)
async def get_subscription_usage(
    contract_id: str,
    current_user: UserAccount = Depends(get_current_active_user),
    session: Session = Depends(get_session),
):
    """
    Get detailed usage metrics for a specific subscription.

    In production, this would integrate with SSO providers or usage APIs.
    For now, returns simulated data.
    """
    contract_repo = ContractRepository(session)

    contract = contract_repo.get_by_contract_id(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    # Verify ownership
    if contract.request.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Simulate usage data (in production, fetch from actual usage APIs)
    seats_active = _simulate_seat_usage(contract.quantity)
    cost_per_user = (contract.total_value / contract.term_months) / seats_active if seats_active > 0 else 0
    waste = (contract.total_value / contract.term_months) * ((contract.quantity - seats_active) / contract.quantity)

    return UsageMetricsResponse(
        daily_active_users=_simulate_daily_usage(seats_active),
        feature_usage={
            "core_features": 95,
            "advanced_features": 45,
            "integrations": 30,
            "mobile_app": 60,
        },
        cost_per_user=round(cost_per_user, 2),
        waste_estimate=round(waste, 2),
    )


@router.post("/subscriptions/{contract_id}/actions")
async def perform_portfolio_action(
    contract_id: str,
    action_data: PortfolioActionRequest,
    current_user: UserAccount = Depends(get_current_active_user),
    session: Session = Depends(get_session),
):
    """
    Perform portfolio management actions:
    - flag_renegotiation: Mark contract for renegotiation
    - request_cancellation: Initiate cancellation workflow
    - adjust_seats: Request seat adjustment
    """
    contract_repo = ContractRepository(session)

    contract = contract_repo.get_by_contract_id(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    # Verify ownership
    if contract.request.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Handle different actions
    action_type = action_data.action

    if action_type == "flag_renegotiation":
        # In production: create task, notify procurement team
        # For now: add metadata to contract
        contract.metadata = contract.metadata or {}
        contract.metadata['flagged_for_renegotiation'] = True
        contract.metadata['flag_reason'] = action_data.reason
        contract.metadata['flagged_at'] = datetime.utcnow().isoformat()
        session.commit()
        return {"status": "flagged", "message": "Contract flagged for renegotiation"}

    elif action_type == "request_cancellation":
        # In production: initiate cancellation workflow
        contract.metadata = contract.metadata or {}
        contract.metadata['cancellation_requested'] = True
        contract.metadata['cancellation_reason'] = action_data.reason
        contract.metadata['requested_at'] = datetime.utcnow().isoformat()
        session.commit()
        return {"status": "pending_cancellation", "message": "Cancellation request submitted"}

    elif action_type == "adjust_seats":
        if not action_data.target_seats:
            raise HTTPException(status_code=400, detail="target_seats required for adjust_seats action")

        # In production: create adjustment request, trigger vendor negotiation
        contract.metadata = contract.metadata or {}
        contract.metadata['seat_adjustment_requested'] = True
        contract.metadata['current_seats'] = contract.quantity
        contract.metadata['target_seats'] = action_data.target_seats
        contract.metadata['adjustment_requested_at'] = datetime.utcnow().isoformat()
        session.commit()
        return {
            "status": "adjustment_pending",
            "message": f"Seat adjustment request submitted: {contract.quantity} → {action_data.target_seats}",
        }

    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {action_type}")


# Helper functions for simulation
def _simulate_seat_usage(total_seats: int) -> int:
    """Simulate active seat usage (60-95% of licensed seats)"""
    import random
    utilization_rate = random.uniform(0.6, 0.95)
    return int(total_seats * utilization_rate)


def _simulate_daily_usage(seats_active: int) -> List[int]:
    """Simulate daily active users for the last 30 days"""
    import random
    # Simulate weekly pattern with weekend dips
    daily_usage = []
    for day in range(30):
        day_of_week = day % 7
        # Weekends have lower usage
        if day_of_week in [5, 6]:
            usage = int(seats_active * random.uniform(0.3, 0.5))
        else:
            usage = int(seats_active * random.uniform(0.8, 1.0))
        daily_usage.append(usage)
    return daily_usage
