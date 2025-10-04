"""Sourcing and negotiation initiation endpoints."""

import asyncio
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...db import get_session
from ...db.models import UserAccount
from ...db.repositories import (
    RequestRepository,
    VendorRepository,
    NegotiationRepository,
)
from ..schemas import NegotiationResponse, AutoNegotiateRequest
from ..security import get_current_user

router = APIRouter(prefix="/sourcing", tags=["Sourcing"])


async def _trigger_auto_negotiations(session_ids: List[str], user_id: int):
    """Background task to trigger auto-negotiations for all sessions."""
    from ..services.auto_negotiation import run_auto_negotiation
    from ...db import SessionLocal

    print(f"[Background] Starting auto-negotiations for {len(session_ids)} sessions")

    # Create new DB session for background task
    db = SessionLocal()
    try:
        # Trigger negotiations for all sessions in parallel
        tasks = []
        for session_id in session_ids:
            print(f"[Background] Queuing negotiation for session {session_id}")
            task = run_auto_negotiation(
                session_id=session_id,
                db_session=db,
                max_rounds=8,
            )
            tasks.append(task)

        # Run all negotiations in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Log results
        for idx, result in enumerate(results):
            session_id = session_ids[idx]
            if isinstance(result, Exception):
                print(f"[Background] Session {session_id} failed: {result}")
            elif isinstance(result, dict) and "error" in result:
                print(f"[Background] Session {session_id} error: {result['error']}")
            else:
                print(f"[Background] Session {session_id} completed: {result.get('outcome', 'unknown')}")

    except Exception as e:
        print(f"[Background] Fatal error in auto-negotiations: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
        print(f"[Background] Auto-negotiations background task finished")


@router.post(
    "/start/{request_id}",
    response_model=List[NegotiationResponse],
    summary="Start negotiations for a request",
    description="Find vendors and initiate negotiation sessions for a request, then auto-negotiate with all vendors",
)
async def start_negotiations(
    request_id: str,
    background_tasks: BackgroundTasks,
    current_user: UserAccount = Depends(get_current_user),
    db_session: Session = Depends(get_session),
    auto_negotiate: bool = True,
):
    """Start negotiations for a request by creating negotiation sessions with vendors."""
    try:
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
        if request.status not in ["draft", "intake", "sourcing", "pending"]:
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
            
            session = neg_repo.create(**session_data)
            created_sessions.append(session)

        # Update request status to negotiating
        request_repo.update(request.id, status="negotiating")
        
        # Commit the transaction to persist sessions
        db_session.commit()

        # Trigger auto-negotiations in background if requested
        if auto_negotiate and created_sessions:
            session_ids = [s.session_id for s in created_sessions]
            background_tasks.add_task(
                _trigger_auto_negotiations,
                session_ids,
                current_user.id
            )

        return created_sessions
    except Exception as e:
        import traceback
        print(f"[ERROR] Failed to start negotiations: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start negotiations: {str(e)}",
        )
