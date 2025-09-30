"""Request repository for procurement request operations."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import RequestRecord
from .base import BaseRepository


class RequestRepository(BaseRepository[RequestRecord]):
    """Repository for procurement request operations."""
    
    def __init__(self, session: Session) -> None:
        """Initialize request repository."""
        super().__init__(RequestRecord, session)
    
    def get_by_request_id(self, request_id: str) -> Optional[RequestRecord]:
        """
        Get request by request_id.
        
        Args:
            request_id: Request ID
        
        Returns:
            Request record or None
        """
        query = select(RequestRecord).where(RequestRecord.request_id == request_id)
        result = self.session.execute(query)
        return result.scalar_one_or_none()
    
    def get_by_user(self, user_id: int) -> list[RequestRecord]:
        """
        Get all requests for a user.
        
        Args:
            user_id: User ID
        
        Returns:
            List of request records
        """
        query = select(RequestRecord).where(RequestRecord.user_id == user_id)
        result = self.session.execute(query)
        return list(result.scalars().all())
    
    def get_by_status(self, status: str) -> list[RequestRecord]:
        """
        Get all requests with a specific status.
        
        Args:
            status: Request status
        
        Returns:
            List of request records
        """
        query = select(RequestRecord).where(RequestRecord.status == status)
        result = self.session.execute(query)
        return list(result.scalars().all())
    
    def get_by_category(self, category: str) -> list[RequestRecord]:
        """
        Get all requests in a category.
        
        Args:
            category: Request category
        
        Returns:
            List of request records
        """
        query = select(RequestRecord).where(RequestRecord.category == category)
        result = self.session.execute(query)
        return list(result.scalars().all())
    
    def approve_request(self, request_id: int, approved_by: int) -> Optional[RequestRecord]:
        """
        Approve a request.
        
        Args:
            request_id: Request ID
            approved_by: User ID who approved
        
        Returns:
            Updated request record or None
        """
        from datetime import datetime
        return self.update(
            request_id,
            status="approved",
            approved_at=datetime.utcnow(),
            approved_by=approved_by,
        )
