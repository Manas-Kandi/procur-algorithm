"""Policy repository for policy configuration operations."""

from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import PolicyConfigRecord
from .base import BaseRepository


class PolicyRepository(BaseRepository[PolicyConfigRecord]):
    """Repository for policy configuration operations."""
    
    def __init__(self, session: Session) -> None:
        """Initialize policy repository."""
        super().__init__(PolicyConfigRecord, session)
    
    def get_by_name(
        self,
        policy_name: str,
        organization_id: Optional[str] = None,
    ) -> Optional[PolicyConfigRecord]:
        """
        Get active policy by name.
        
        Args:
            policy_name: Policy name
            organization_id: Organization ID
        
        Returns:
            Policy config record or None
        """
        query = select(PolicyConfigRecord).where(
            PolicyConfigRecord.policy_name == policy_name,
            PolicyConfigRecord.is_active == True,
        )
        
        if organization_id is not None:
            query = query.where(PolicyConfigRecord.organization_id == organization_id)
        
        result = self.session.execute(query)
        return result.scalar_one_or_none()
    
    def get_by_type(
        self,
        policy_type: str,
        organization_id: Optional[str] = None,
    ) -> list[PolicyConfigRecord]:
        """
        Get all active policies of a specific type.
        
        Args:
            policy_type: Policy type
            organization_id: Organization ID
        
        Returns:
            List of policy config records
        """
        query = select(PolicyConfigRecord).where(
            PolicyConfigRecord.policy_type == policy_type,
            PolicyConfigRecord.is_active == True,
        )
        
        if organization_id is not None:
            query = query.where(PolicyConfigRecord.organization_id == organization_id)
        
        result = self.session.execute(query)
        return list(result.scalars().all())
    
    def get_by_organization(self, organization_id: str) -> list[PolicyConfigRecord]:
        """
        Get all active policies for an organization.
        
        Args:
            organization_id: Organization ID
        
        Returns:
            List of policy config records
        """
        query = select(PolicyConfigRecord).where(
            PolicyConfigRecord.organization_id == organization_id,
            PolicyConfigRecord.is_active == True,
        )
        result = self.session.execute(query)
        return list(result.scalars().all())
    
    def create_policy(
        self,
        policy_name: str,
        policy_type: str,
        policy_data: Dict[str, Any],
        organization_id: Optional[str] = None,
        description: Optional[str] = None,
        created_by: Optional[int] = None,
    ) -> PolicyConfigRecord:
        """
        Create a new policy configuration.
        
        Args:
            policy_name: Policy name
            policy_type: Policy type
            policy_data: Policy data
            organization_id: Organization ID
            description: Policy description
            created_by: User ID who created the policy
        
        Returns:
            Created policy config record
        """
        return self.create(
            policy_name=policy_name,
            policy_type=policy_type,
            policy_data=policy_data,
            organization_id=organization_id,
            description=description,
            created_by=created_by,
            version=1,
            is_active=True,
        )
    
    def deactivate_policy(self, policy_id: int) -> Optional[PolicyConfigRecord]:
        """
        Deactivate a policy.
        
        Args:
            policy_id: Policy ID
        
        Returns:
            Updated policy config record or None
        """
        return self.update(policy_id, is_active=False)
