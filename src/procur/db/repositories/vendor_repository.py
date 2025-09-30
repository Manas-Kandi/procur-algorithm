"""Vendor repository for vendor profile operations."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import VendorProfileRecord
from .base import BaseRepository


class VendorRepository(BaseRepository[VendorProfileRecord]):
    """Repository for vendor profile operations."""
    
    def __init__(self, session: Session) -> None:
        """Initialize vendor repository."""
        super().__init__(VendorProfileRecord, session)
    
    def get_by_vendor_id(self, vendor_id: str) -> Optional[VendorProfileRecord]:
        """
        Get vendor by vendor_id.
        
        Args:
            vendor_id: Vendor ID
        
        Returns:
            Vendor profile record or None
        """
        query = select(VendorProfileRecord).where(VendorProfileRecord.vendor_id == vendor_id)
        result = self.session.execute(query)
        return result.scalar_one_or_none()
    
    def get_by_category(self, category: str) -> list[VendorProfileRecord]:
        """
        Get all vendors in a category.
        
        Args:
            category: Vendor category
        
        Returns:
            List of vendor profile records
        """
        query = select(VendorProfileRecord).where(VendorProfileRecord.category == category)
        result = self.session.execute(query)
        return list(result.scalars().all())
    
    def search_by_name(self, name_query: str) -> list[VendorProfileRecord]:
        """
        Search vendors by name (case-insensitive partial match).
        
        Args:
            name_query: Name search query
        
        Returns:
            List of matching vendor profile records
        """
        query = select(VendorProfileRecord).where(
            VendorProfileRecord.name.ilike(f"%{name_query}%")
        )
        result = self.session.execute(query)
        return list(result.scalars().all())
    
    def get_by_certification(self, certification: str) -> list[VendorProfileRecord]:
        """
        Get vendors with a specific certification.
        
        Args:
            certification: Certification name
        
        Returns:
            List of vendor profile records
        """
        query = select(VendorProfileRecord).where(
            VendorProfileRecord.certifications.contains([certification])
        )
        result = self.session.execute(query)
        return list(result.scalars().all())
