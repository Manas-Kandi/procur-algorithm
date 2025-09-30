"""Audit repository for audit log operations."""

from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import AuditLogRecord
from .base import BaseRepository


class AuditRepository(BaseRepository[AuditLogRecord]):
    """Repository for audit log operations."""
    
    def __init__(self, session: Session) -> None:
        """Initialize audit repository."""
        super().__init__(AuditLogRecord, session)
    
    def log_action(
        self,
        action: str,
        resource_type: str,
        actor_type: str,
        resource_id: Optional[str] = None,
        user_id: Optional[int] = None,
        actor_id: Optional[str] = None,
        negotiation_session_id: Optional[int] = None,
        event_data: Optional[Dict[str, Any]] = None,
        changes: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLogRecord:
        """
        Create an audit log entry.
        
        Args:
            action: Action performed
            resource_type: Type of resource
            actor_type: Type of actor (user, system, agent)
            resource_id: Resource identifier
            user_id: User ID if applicable
            actor_id: Actor identifier
            negotiation_session_id: Negotiation session ID if applicable
            event_data: Additional event data
            changes: Changes made
            ip_address: IP address
            user_agent: User agent string
        
        Returns:
            Created audit log record
        """
        return self.create(
            action=action,
            resource_type=resource_type,
            actor_type=actor_type,
            resource_id=resource_id,
            user_id=user_id,
            actor_id=actor_id,
            negotiation_session_id=negotiation_session_id,
            event_data=event_data,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
        )
    
    def get_by_user(self, user_id: int) -> list[AuditLogRecord]:
        """
        Get all audit logs for a user.
        
        Args:
            user_id: User ID
        
        Returns:
            List of audit log records
        """
        query = select(AuditLogRecord).where(AuditLogRecord.user_id == user_id)
        result = self.session.execute(query)
        return list(result.scalars().all())
    
    def get_by_resource(self, resource_type: str, resource_id: str) -> list[AuditLogRecord]:
        """
        Get all audit logs for a specific resource.
        
        Args:
            resource_type: Resource type
            resource_id: Resource ID
        
        Returns:
            List of audit log records
        """
        query = select(AuditLogRecord).where(
            AuditLogRecord.resource_type == resource_type,
            AuditLogRecord.resource_id == resource_id,
        )
        result = self.session.execute(query)
        return list(result.scalars().all())
    
    def get_by_action(self, action: str) -> list[AuditLogRecord]:
        """
        Get all audit logs for a specific action.
        
        Args:
            action: Action name
        
        Returns:
            List of audit log records
        """
        query = select(AuditLogRecord).where(AuditLogRecord.action == action)
        result = self.session.execute(query)
        return list(result.scalars().all())
    
    def get_by_negotiation_session(self, session_id: int) -> list[AuditLogRecord]:
        """
        Get all audit logs for a negotiation session.
        
        Args:
            session_id: Negotiation session ID
        
        Returns:
            List of audit log records
        """
        query = select(AuditLogRecord).where(
            AuditLogRecord.negotiation_session_id == session_id
        )
        result = self.session.execute(query)
        return list(result.scalars().all())
