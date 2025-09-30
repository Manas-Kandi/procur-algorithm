"""Vendor endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ...db import get_session
from ...db.models import UserAccount
from ...db.repositories import VendorRepository
from ..schemas import VendorCreate, VendorResponse
from ..security import get_current_user, require_role

router = APIRouter(prefix="/vendors", tags=["Vendors"])


@router.get(
    "",
    response_model=List[VendorResponse],
    summary="List vendors",
    description="Search and list vendor profiles",
)
def list_vendors(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search by name"),
    certification: Optional[str] = Query(None, description="Filter by certification"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    session: Session = Depends(get_session),
    current_user: UserAccount = Depends(get_current_user),
):
    """List and search vendor profiles."""
    vendor_repo = VendorRepository(session)
    
    # Get vendors based on filters
    if category:
        vendors = vendor_repo.get_by_category(category)
    elif search:
        vendors = vendor_repo.search_by_name(search)
    elif certification:
        vendors = vendor_repo.get_by_certification(certification)
    else:
        vendors = vendor_repo.get_all(limit=limit, offset=offset)
    
    # Apply pagination if not already limited
    if not (category or search or certification):
        vendors = vendors[offset : offset + limit]
    
    return vendors


@router.get(
    "/{vendor_id}",
    response_model=VendorResponse,
    summary="Get vendor",
    description="Get vendor profile by ID",
)
def get_vendor(
    vendor_id: str,
    session: Session = Depends(get_session),
    current_user: UserAccount = Depends(get_current_user),
):
    """Get a specific vendor profile."""
    vendor_repo = VendorRepository(session)
    
    vendor = vendor_repo.get_by_vendor_id(vendor_id)
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found",
        )
    
    return vendor


@router.post(
    "",
    response_model=VendorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create vendor",
    description="Create a new vendor profile (admin only)",
)
def create_vendor(
    vendor_data: VendorCreate,
    session: Session = Depends(get_session),
    current_user: UserAccount = Depends(require_role("admin")),
):
    """Create a new vendor profile (admin only)."""
    vendor_repo = VendorRepository(session)
    
    # Check if vendor already exists
    if vendor_repo.get_by_vendor_id(vendor_data.vendor_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vendor ID already exists",
        )
    
    # Create vendor
    vendor = vendor_repo.create(
        vendor_id=vendor_data.vendor_id,
        name=vendor_data.name,
        website=vendor_data.website,
        description=vendor_data.description,
        category=vendor_data.category,
        list_price=vendor_data.list_price,
        features=vendor_data.features,
        certifications=vendor_data.certifications,
    )
    
    return vendor
