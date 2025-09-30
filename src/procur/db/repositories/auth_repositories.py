"""Repositories for authentication models."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models_auth import (
    APIKey,
    LoginAttempt,
    OAuthConnection,
    Organization,
    PasswordHistory,
    UserSession,
)
from .base import BaseRepository


class SessionRepository(BaseRepository[UserSession]):
    """Repository for user sessions."""
    
    def __init__(self, session: Session) -> None:
        super().__init__(UserSession, session)
    
    def get_by_session_id(self, session_id: str) -> Optional[UserSession]:
        query = select(UserSession).where(UserSession.session_id == session_id)
        result = self.session.execute(query)
        return result.scalar_one_or_none()
    
    def get_active_sessions(self, user_id: int) -> List[UserSession]:
        query = select(UserSession).where(
            UserSession.user_id == user_id,
            UserSession.is_active == True
        )
        result = self.session.execute(query)
        return list(result.scalars().all())
    
    def deactivate_session(self, session_id: str) -> Optional[UserSession]:
        return self.update(session_id, is_active=False)
    
    def update_activity(self, session_id: str) -> Optional[UserSession]:
        session_obj = self.get_by_session_id(session_id)
        if session_obj:
            return self.update(session_obj.id, last_activity_at=datetime.utcnow())
        return None


class APIKeyRepository(BaseRepository[APIKey]):
    """Repository for API keys."""
    
    def __init__(self, session: Session) -> None:
        super().__init__(APIKey, session)
    
    def get_by_key_id(self, key_id: str) -> Optional[APIKey]:
        query = select(APIKey).where(APIKey.key_id == key_id)
        result = self.session.execute(query)
        return result.scalar_one_or_none()
    
    def get_user_keys(self, user_id: int) -> List[APIKey]:
        query = select(APIKey).where(APIKey.user_id == user_id)
        result = self.session.execute(query)
        return list(result.scalars().all())
    
    def get_active_keys(self, user_id: int) -> List[APIKey]:
        query = select(APIKey).where(
            APIKey.user_id == user_id,
            APIKey.is_active == True
        )
        result = self.session.execute(query)
        return list(result.scalars().all())
    
    def update_last_used(self, key_id: str) -> Optional[APIKey]:
        key = self.get_by_key_id(key_id)
        if key:
            return self.update(
                key.id,
                last_used_at=datetime.utcnow(),
                usage_count=key.usage_count + 1
            )
        return None


class PasswordHistoryRepository(BaseRepository[PasswordHistory]):
    """Repository for password history."""
    
    def __init__(self, session: Session) -> None:
        super().__init__(PasswordHistory, session)
    
    def get_user_history(self, user_id: int, limit: int = 5) -> List[PasswordHistory]:
        query = (
            select(PasswordHistory)
            .where(PasswordHistory.user_id == user_id)
            .order_by(PasswordHistory.changed_at.desc())
            .limit(limit)
        )
        result = self.session.execute(query)
        return list(result.scalars().all())


class LoginAttemptRepository(BaseRepository[LoginAttempt]):
    """Repository for login attempts."""
    
    def __init__(self, session: Session) -> None:
        super().__init__(LoginAttempt, session)
    
    def get_recent_attempts(
        self,
        username: str,
        minutes: int = 30
    ) -> List[LoginAttempt]:
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        
        query = (
            select(LoginAttempt)
            .where(
                LoginAttempt.username == username,
                LoginAttempt.created_at >= cutoff
            )
            .order_by(LoginAttempt.created_at.desc())
        )
        result = self.session.execute(query)
        return list(result.scalars().all())
    
    def count_failed_attempts(self, username: str, minutes: int = 30) -> int:
        attempts = self.get_recent_attempts(username, minutes)
        return sum(1 for a in attempts if not a.success)


class OrganizationRepository(BaseRepository[Organization]):
    """Repository for organizations."""
    
    def __init__(self, session: Session) -> None:
        super().__init__(Organization, session)
    
    def get_by_organization_id(self, organization_id: str) -> Optional[Organization]:
        query = select(Organization).where(
            Organization.organization_id == organization_id
        )
        result = self.session.execute(query)
        return result.scalar_one_or_none()
    
    def get_active_organizations(self) -> List[Organization]:
        query = select(Organization).where(Organization.is_active == True)
        result = self.session.execute(query)
        return list(result.scalars().all())


class OAuthConnectionRepository(BaseRepository[OAuthConnection]):
    """Repository for OAuth connections."""
    
    def __init__(self, session: Session) -> None:
        super().__init__(OAuthConnection, session)
    
    def get_by_provider(
        self,
        user_id: int,
        provider: str
    ) -> Optional[OAuthConnection]:
        query = select(OAuthConnection).where(
            OAuthConnection.user_id == user_id,
            OAuthConnection.provider == provider
        )
        result = self.session.execute(query)
        return result.scalar_one_or_none()
    
    def get_by_provider_user_id(
        self,
        provider: str,
        provider_user_id: str
    ) -> Optional[OAuthConnection]:
        query = select(OAuthConnection).where(
            OAuthConnection.provider == provider,
            OAuthConnection.provider_user_id == provider_user_id
        )
        result = self.session.execute(query)
        return result.scalar_one_or_none()
