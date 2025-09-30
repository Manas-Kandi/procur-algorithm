"""Procurement request endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ...db import get_session
from ...db.models import UserAccount
from ...db.repositories import RequestRepository
from ..schemas import RequestCreate, RequestResponse, RequestUpdate
from ..security import get_current_user

router = APIRouter(prefix="/requests", tags=["Requests"])


@router.post(
    "",
    response_model=RequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create procurement request",
    description="Create a new procurement request",
)
def create_request(
    request_data: RequestCreate,
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create a new procurement request."""
    request_repo = RequestRepository(session)
    
    # Generate unique request ID
    import uuid
    request_id = f"req-{uuid.uuid4().hex[:12]}"
    
    # Create request
    request = request_repo.create(
        request_id=request_id,
        user_id=current_user.id,
        description=request_data.description,
        request_type=request_data.request_type,
        category=request_data.category,
        budget_min=request_data.budget_min,
        budget_max=request_data.budget_max,
        quantity=request_data.quantity,
        billing_cadence=request_data.billing_cadence,
        must_haves=request_data.must_haves,
        nice_to_haves=request_data.nice_to_haves,
        compliance_requirements=request_data.compliance_requirements,
        specs=request_data.specs,
        status="pending",
    )
    
    return request


@router.get(
    "",
    response_model=List[RequestResponse],
    summary="List requests",
    description="Get all procurement requests for current user",
)
def list_requests(
    status: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List procurement requests for current user."""
    request_repo = RequestRepository(session)
    
    # Get user's requests
    requests = request_repo.get_by_user(current_user.id)
    
    # Apply filters
    if status:
        requests = [r for r in requests if r.status == status]
    if category:
        requests = [r for r in requests if r.category == category]
    
    # Apply pagination
    total = len(requests)
    requests = requests[offset : offset + limit]
    
    return requests


@router.get(
    "/{request_id}",
    response_model=RequestResponse,
    summary="Get request",
    description="Get procurement request by ID",
)
def get_request(
    request_id: str,
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get a specific procurement request."""
    request_repo = RequestRepository(session)
    
    request = request_repo.get_by_request_id(request_id)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found",
        )
    
    # Check ownership
    if request.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this request",
        )
    
    return request


@router.patch(
    "/{request_id}",
    response_model=RequestResponse,
    summary="Update request",
    description="Update procurement request",
)
def update_request(
    request_id: str,
    request_data: RequestUpdate,
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update a procurement request."""
    request_repo = RequestRepository(session)
    
    request = request_repo.get_by_request_id(request_id)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found",
        )
    
    # Check ownership
    if request.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this request",
        )
    
    # Update request
    update_data = request_data.model_dump(exclude_unset=True)
    updated_request = request_repo.update(request.id, **update_data)
    
    return updated_request


@router.delete(
    "/{request_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete request",
    description="Delete (soft delete) procurement request",
)
def delete_request(
    request_id: str,
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Delete a procurement request (soft delete)."""
    request_repo = RequestRepository(session)
    
    request = request_repo.get_by_request_id(request_id)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found",
        )
    
    # Check ownership
    if request.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this request",
        )
    
    # Soft delete
    request_repo.soft_delete(request.id)
    
    return None
