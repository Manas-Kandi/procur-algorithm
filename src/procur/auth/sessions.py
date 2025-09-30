"""Session management for user authentication."""

import secrets
from datetime import datetime, timedelta
from typing import Optional


class SessionService:
    """Service for managing user sessions."""
    
    def __init__(
        self,
        session_timeout_minutes: int = 60,
        max_sessions_per_user: int = 5,
    ):
        """
        Initialize session service.
        
        Args:
            session_timeout_minutes: Session timeout in minutes
            max_sessions_per_user: Maximum concurrent sessions per user
        """
        self.session_timeout_minutes = session_timeout_minutes
        self.max_sessions_per_user = max_sessions_per_user
    
    def generate_session_id(self) -> str:
        """
        Generate a unique session ID.
        
        Returns:
            Session ID
        """
        return f"sess_{secrets.token_urlsafe(32)}"
    
    def generate_refresh_token(self) -> str:
        """
        Generate a refresh token.
        
        Returns:
            Refresh token
        """
        return f"rt_{secrets.token_urlsafe(48)}"
    
    def is_session_expired(
        self,
        last_activity: datetime,
        timeout_minutes: Optional[int] = None,
    ) -> bool:
        """
        Check if session has expired due to inactivity.
        
        Args:
            last_activity: Last activity timestamp
            timeout_minutes: Optional custom timeout
        
        Returns:
            True if expired
        """
        timeout = timeout_minutes or self.session_timeout_minutes
        expiry_time = last_activity + timedelta(minutes=timeout)
        return datetime.utcnow() > expiry_time
    
    def is_session_absolute_expired(
        self,
        created_at: datetime,
        max_age_hours: int = 24,
    ) -> bool:
        """
        Check if session has exceeded absolute maximum age.
        
        Args:
            created_at: Session creation timestamp
            max_age_hours: Maximum session age in hours
        
        Returns:
            True if expired
        """
        expiry_time = created_at + timedelta(hours=max_age_hours)
        return datetime.utcnow() > expiry_time
    
    def should_rotate_session(
        self,
        created_at: datetime,
        rotation_interval_hours: int = 4,
    ) -> bool:
        """
        Check if session should be rotated for security.
        
        Args:
            created_at: Session creation timestamp
            rotation_interval_hours: Rotation interval in hours
        
        Returns:
            True if should rotate
        """
        rotation_time = created_at + timedelta(hours=rotation_interval_hours)
        return datetime.utcnow() > rotation_time
    
    def extract_session_metadata(self, request_data: dict) -> dict:
        """
        Extract session metadata from request.
        
        Args:
            request_data: Request data dict with headers, etc.
        
        Returns:
            Session metadata dict
        """
        return {
            "ip_address": request_data.get("ip_address"),
            "user_agent": request_data.get("user_agent"),
            "device_type": self._detect_device_type(request_data.get("user_agent", "")),
            "location": request_data.get("location"),
        }
    
    def _detect_device_type(self, user_agent: str) -> str:
        """Detect device type from user agent."""
        user_agent_lower = user_agent.lower()
        
        if "mobile" in user_agent_lower or "android" in user_agent_lower:
            return "mobile"
        elif "tablet" in user_agent_lower or "ipad" in user_agent_lower:
            return "tablet"
        else:
            return "desktop"
    
    def is_suspicious_session(
        self,
        current_metadata: dict,
        previous_metadata: dict,
    ) -> tuple[bool, list[str]]:
        """
        Check if session shows suspicious activity.
        
        Args:
            current_metadata: Current session metadata
            previous_metadata: Previous session metadata
        
        Returns:
            Tuple of (is_suspicious, list of reasons)
        """
        reasons = []
        
        # Check for IP address change
        if current_metadata.get("ip_address") != previous_metadata.get("ip_address"):
            reasons.append("IP address changed")
        
        # Check for device type change
        if current_metadata.get("device_type") != previous_metadata.get("device_type"):
            reasons.append("Device type changed")
        
        # Check for user agent change
        if current_metadata.get("user_agent") != previous_metadata.get("user_agent"):
            reasons.append("User agent changed")
        
        return len(reasons) > 0, reasons
