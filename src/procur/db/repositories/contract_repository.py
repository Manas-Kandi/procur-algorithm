"""Contract repository for contract operations."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import ContractRecord
from .base import BaseRepository


class ContractRepository(BaseRepository[ContractRecord]):
    """Repository for contract operations."""
    
    def __init__(self, session: Session) -> None:
        """Initialize contract repository."""
        super().__init__(ContractRecord, session)
    
    def get_by_contract_id(self, contract_id: str) -> Optional[ContractRecord]:
        """
        Get contract by contract_id.
        
        Args:
            contract_id: Contract ID
        
        Returns:
            Contract record or None
        """
        query = select(ContractRecord).where(ContractRecord.contract_id == contract_id)
        result = self.session.execute(query)
        return result.scalar_one_or_none()
    
    def get_by_request(self, request_id: int) -> list[ContractRecord]:
        """
        Get all contracts for a request.
        
        Args:
            request_id: Request ID
        
        Returns:
            List of contract records
        """
        query = select(ContractRecord).where(ContractRecord.request_id == request_id)
        result = self.session.execute(query)
        return list(result.scalars().all())
    
    def get_by_vendor(self, vendor_id: int) -> list[ContractRecord]:
        """
        Get all contracts with a vendor.
        
        Args:
            vendor_id: Vendor ID
        
        Returns:
            List of contract records
        """
        query = select(ContractRecord).where(ContractRecord.vendor_id == vendor_id)
        result = self.session.execute(query)
        return list(result.scalars().all())
    
    def get_by_status(self, status: str) -> list[ContractRecord]:
        """
        Get all contracts with a specific status.
        
        Args:
            status: Contract status
        
        Returns:
            List of contract records
        """
        query = select(ContractRecord).where(ContractRecord.status == status)
        result = self.session.execute(query)
        return list(result.scalars().all())
    
    def get_expiring_soon(self, days: int = 30) -> list[ContractRecord]:
        """
        Get contracts expiring within specified days.
        
        Args:
            days: Number of days to look ahead
        
        Returns:
            List of contract records
        """
        from datetime import timedelta
        cutoff_date = datetime.utcnow() + timedelta(days=days)
        query = select(ContractRecord).where(
            ContractRecord.end_date <= cutoff_date,
            ContractRecord.status == "active"
        )
        result = self.session.execute(query)
        return list(result.scalars().all())
    
    def sign_by_buyer(self, contract_id: int) -> Optional[ContractRecord]:
        """
        Record buyer signature.
        
        Args:
            contract_id: Contract ID
        
        Returns:
            Updated contract record or None
        """
        return self.update(
            contract_id,
            signed_by_buyer=True,
            buyer_signature_date=datetime.utcnow(),
        )
    
    def sign_by_vendor(self, contract_id: int) -> Optional[ContractRecord]:
        """
        Record vendor signature.
        
        Args:
            contract_id: Contract ID
        
        Returns:
            Updated contract record or None
        """
        return self.update(
            contract_id,
            signed_by_vendor=True,
            vendor_signature_date=datetime.utcnow(),
        )
