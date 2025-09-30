"""Contract endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ...db import get_session
from ...db.models import UserAccount
from ...db.repositories import ContractRepository, RequestRepository
from ..schemas import ContractResponse, ContractSign
from ..security import get_current_user

router = APIRouter(prefix="/contracts", tags=["Contracts"])


@router.get(
    "",
    response_model=List[ContractResponse],
    summary="List contracts",
    description="Get all contracts for current user",
)
def list_contracts(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List contracts for current user."""
    contract_repo = ContractRepository(session)
    request_repo = RequestRepository(session)
    
    # Get user's requests
    user_requests = request_repo.get_by_user(current_user.id)
    request_ids = [r.id for r in user_requests]
    
    # Get contracts for user's requests
    all_contracts = []
    for request_id in request_ids:
        contracts = contract_repo.get_by_request(request_id)
        all_contracts.extend(contracts)
    
    # Apply status filter
    if status:
        all_contracts = [c for c in all_contracts if c.status == status]
    
    # Apply pagination
    all_contracts = all_contracts[offset : offset + limit]
    
    return all_contracts


@router.get(
    "/{contract_id}",
    response_model=ContractResponse,
    summary="Get contract",
    description="Get contract by ID",
)
def get_contract(
    contract_id: str,
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get a specific contract."""
    contract_repo = ContractRepository(session)
    request_repo = RequestRepository(session)
    
    contract = contract_repo.get_by_contract_id(contract_id)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found",
        )
    
    # Check authorization
    request = request_repo.get_by_id(contract.request_id)
    if request.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this contract",
        )
    
    return contract


@router.post(
    "/{contract_id}/sign",
    response_model=ContractResponse,
    summary="Sign contract",
    description="Sign a contract (buyer or vendor)",
)
def sign_contract(
    contract_id: str,
    sign_data: ContractSign,
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Sign a contract."""
    contract_repo = ContractRepository(session)
    request_repo = RequestRepository(session)
    
    contract = contract_repo.get_by_contract_id(contract_id)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found",
        )
    
    # Check authorization
    request = request_repo.get_by_id(contract.request_id)
    if request.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to sign this contract",
        )
    
    # Validate signature type
    if sign_data.signature_type not in ["buyer", "vendor"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature_type. Must be 'buyer' or 'vendor'",
        )
    
    # Sign contract
    if sign_data.signature_type == "buyer":
        updated_contract = contract_repo.sign_by_buyer(contract.id)
    else:
        updated_contract = contract_repo.sign_by_vendor(contract.id)
    
    # Update status if both parties signed
    if updated_contract.signed_by_buyer and updated_contract.signed_by_vendor:
        updated_contract = contract_repo.update(contract.id, status="active")
    
    return updated_contract


@router.get(
    "/{contract_id}/download",
    summary="Download contract",
    description="Download contract document",
)
def download_contract(
    contract_id: str,
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Download contract document."""
    contract_repo = ContractRepository(session)
    request_repo = RequestRepository(session)
    
    contract = contract_repo.get_by_contract_id(contract_id)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found",
        )
    
    # Check authorization
    request = request_repo.get_by_id(contract.request_id)
    if request.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to download this contract",
        )
    
    # Return document URL or generate document
    if contract.document_url:
        return {"document_url": contract.document_url}
    else:
        return {
            "message": "Contract document not yet generated",
            "contract_id": contract.contract_id,
        }
