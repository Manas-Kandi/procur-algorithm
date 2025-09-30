"""Negotiation repository for negotiation session operations."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import NegotiationSessionRecord
from .base import BaseRepository


class NegotiationRepository(BaseRepository[NegotiationSessionRecord]):
    """Repository for negotiation session operations."""
    
    def __init__(self, session: Session) -> None:
        """Initialize negotiation repository."""
        super().__init__(NegotiationSessionRecord, session)
    
    def get_by_session_id(self, session_id: str) -> Optional[NegotiationSessionRecord]:
        """
        Get negotiation session by session_id.
        
        Args:
            session_id: Session ID
        
        Returns:
            Negotiation session record or None
        """
        query = select(NegotiationSessionRecord).where(
            NegotiationSessionRecord.session_id == session_id
        )
        result = self.session.execute(query)
        return result.scalar_one_or_none()
    
    def get_by_request(self, request_id: int) -> list[NegotiationSessionRecord]:
        """
        Get all negotiation sessions for a request.
        
        Args:
            request_id: Request ID
        
        Returns:
            List of negotiation session records
        """
        query = select(NegotiationSessionRecord).where(
            NegotiationSessionRecord.request_id == request_id
        )
        result = self.session.execute(query)
        return list(result.scalars().all())
    
    def get_by_vendor(self, vendor_id: int) -> list[NegotiationSessionRecord]:
        """
        Get all negotiation sessions with a vendor.
        
        Args:
            vendor_id: Vendor ID
        
        Returns:
            List of negotiation session records
        """
        query = select(NegotiationSessionRecord).where(
            NegotiationSessionRecord.vendor_id == vendor_id
        )
        result = self.session.execute(query)
        return list(result.scalars().all())
    
    def get_active_sessions(self) -> list[NegotiationSessionRecord]:
        """
        Get all active negotiation sessions.
        
        Returns:
            List of active negotiation session records
        """
        query = select(NegotiationSessionRecord).where(
            NegotiationSessionRecord.status == "active"
        )
        result = self.session.execute(query)
        return list(result.scalars().all())
    
    def increment_round(self, session_id: int) -> Optional[NegotiationSessionRecord]:
        """
        Increment the current round number.
        
        Args:
            session_id: Session ID
        
        Returns:
            Updated negotiation session record or None
        """
        session = self.get_by_id(session_id)
        if session is None:
            return None
        
        return self.update(session_id, current_round=session.current_round + 1)
    
    def complete_session(
        self,
        session_id: int,
        outcome: str,
        outcome_reason: Optional[str] = None,
        final_offer_id: Optional[int] = None,
        savings_achieved: Optional[float] = None,
    ) -> Optional[NegotiationSessionRecord]:
        """
        Mark a negotiation session as completed.
        
        Args:
            session_id: Session ID
            outcome: Outcome status
            outcome_reason: Reason for outcome
            final_offer_id: Final offer ID
            savings_achieved: Savings amount
        
        Returns:
            Updated negotiation session record or None
        """
        return self.update(
            session_id,
            status="completed",
            outcome=outcome,
            outcome_reason=outcome_reason,
            final_offer_id=final_offer_id,
            savings_achieved=savings_achieved,
            completed_at=datetime.utcnow(),
        )
