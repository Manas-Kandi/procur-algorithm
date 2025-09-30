"""Offer repository for offer operations."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import OfferRecord
from .base import BaseRepository


class OfferRepository(BaseRepository[OfferRecord]):
    """Repository for offer operations."""
    
    def __init__(self, session: Session) -> None:
        """Initialize offer repository."""
        super().__init__(OfferRecord, session)
    
    def get_by_offer_id(self, offer_id: str) -> Optional[OfferRecord]:
        """
        Get offer by offer_id.
        
        Args:
            offer_id: Offer ID
        
        Returns:
            Offer record or None
        """
        query = select(OfferRecord).where(OfferRecord.offer_id == offer_id)
        result = self.session.execute(query)
        return result.scalar_one_or_none()
    
    def get_by_request(self, request_id: int) -> list[OfferRecord]:
        """
        Get all offers for a request.
        
        Args:
            request_id: Request ID
        
        Returns:
            List of offer records
        """
        query = select(OfferRecord).where(OfferRecord.request_id == request_id)
        result = self.session.execute(query)
        return list(result.scalars().all())
    
    def get_by_vendor(self, vendor_id: int) -> list[OfferRecord]:
        """
        Get all offers from a vendor.
        
        Args:
            vendor_id: Vendor ID
        
        Returns:
            List of offer records
        """
        query = select(OfferRecord).where(OfferRecord.vendor_id == vendor_id)
        result = self.session.execute(query)
        return list(result.scalars().all())
    
    def get_by_negotiation_session(self, session_id: int) -> list[OfferRecord]:
        """
        Get all offers in a negotiation session.
        
        Args:
            session_id: Negotiation session ID
        
        Returns:
            List of offer records
        """
        query = select(OfferRecord).where(OfferRecord.negotiation_session_id == session_id)
        result = self.session.execute(query)
        return list(result.scalars().all())
    
    def get_accepted_offers(self, request_id: int) -> list[OfferRecord]:
        """
        Get all accepted offers for a request.
        
        Args:
            request_id: Request ID
        
        Returns:
            List of accepted offer records
        """
        query = select(OfferRecord).where(
            OfferRecord.request_id == request_id,
            OfferRecord.accepted == True
        )
        result = self.session.execute(query)
        return list(result.scalars().all())
    
    def accept_offer(self, offer_id: int) -> Optional[OfferRecord]:
        """
        Mark an offer as accepted.
        
        Args:
            offer_id: Offer ID
        
        Returns:
            Updated offer record or None
        """
        return self.update(offer_id, accepted=True)
    
    def reject_offer(self, offer_id: int) -> Optional[OfferRecord]:
        """
        Mark an offer as rejected.
        
        Args:
            offer_id: Offer ID
        
        Returns:
            Updated offer record or None
        """
        return self.update(offer_id, rejected=True)
