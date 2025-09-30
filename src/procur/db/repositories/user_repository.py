"""User repository for user account operations."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import UserAccount
from .base import BaseRepository


class UserRepository(BaseRepository[UserAccount]):
    """Repository for user account operations."""
    
    def __init__(self, session: Session) -> None:
        """Initialize user repository."""
        super().__init__(UserAccount, session)
    
    def get_by_email(self, email: str) -> Optional[UserAccount]:
        """
        Get user by email address.
        
        Args:
            email: User email
        
        Returns:
            User account or None
        """
        query = select(UserAccount).where(UserAccount.email == email)
        result = self.session.execute(query)
        return result.scalar_one_or_none()
    
    def get_by_username(self, username: str) -> Optional[UserAccount]:
        """
        Get user by username.
        
        Args:
            username: Username
        
        Returns:
            User account or None
        """
        query = select(UserAccount).where(UserAccount.username == username)
        result = self.session.execute(query)
        return result.scalar_one_or_none()
    
    def get_by_organization(self, organization_id: str) -> list[UserAccount]:
        """
        Get all users in an organization.
        
        Args:
            organization_id: Organization ID
        
        Returns:
            List of user accounts
        """
        query = select(UserAccount).where(UserAccount.organization_id == organization_id)
        result = self.session.execute(query)
        return list(result.scalars().all())
    
    def update_last_login(self, user_id: int) -> Optional[UserAccount]:
        """
        Update user's last login timestamp.
        
        Args:
            user_id: User ID
        
        Returns:
            Updated user account or None
        """
        return self.update(user_id, last_login_at=datetime.utcnow())
    
    def activate_user(self, user_id: int) -> Optional[UserAccount]:
        """
        Activate a user account.
        
        Args:
            user_id: User ID
        
        Returns:
            Updated user account or None
        """
        return self.update(user_id, is_active=True)
    
    def deactivate_user(self, user_id: int) -> Optional[UserAccount]:
        """
        Deactivate a user account.
        
        Args:
            user_id: User ID
        
        Returns:
            Updated user account or None
        """
        return self.update(user_id, is_active=False)
