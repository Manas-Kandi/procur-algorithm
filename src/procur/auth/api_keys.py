"""API key management for programmatic access."""

import secrets
from datetime import datetime, timedelta
from typing import Optional

from itsdangerous import URLSafeTimedSerializer


class APIKeyService:
    """Service for managing API keys."""
    
    def __init__(self, secret_key: str):
        """Initialize API key service."""
        self.secret_key = secret_key
        self.serializer = URLSafeTimedSerializer(secret_key)
    
    def generate_api_key(
        self,
        user_id: int,
        name: str,
        scopes: Optional[list[str]] = None,
    ) -> tuple[str, str]:
        """
        Generate a new API key.
        
        Args:
            user_id: User ID
            name: Key name/description
            scopes: Optional list of permission scopes
        
        Returns:
            Tuple of (key_id, api_key)
        """
        # Generate unique key ID
        key_id = f"pk_{secrets.token_urlsafe(16)}"
        
        # Generate secret key
        secret = secrets.token_urlsafe(32)
        
        # Create API key with embedded metadata
        api_key = f"{key_id}.{secret}"
        
        return key_id, api_key
    
    def parse_api_key(self, api_key: str) -> Optional[tuple[str, str]]:
        """
        Parse API key into key_id and secret.
        
        Args:
            api_key: API key string
        
        Returns:
            Tuple of (key_id, secret) or None if invalid
        """
        parts = api_key.split('.')
        if len(parts) != 2:
            return None
        
        key_id, secret = parts
        if not key_id.startswith('pk_'):
            return None
        
        return key_id, secret
    
    def hash_api_key_secret(self, secret: str) -> str:
        """
        Hash API key secret for storage.
        
        Args:
            secret: API key secret part
        
        Returns:
            Hashed secret
        """
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(secret)
    
    def verify_api_key_secret(self, secret: str, hashed_secret: str) -> bool:
        """
        Verify API key secret against hash.
        
        Args:
            secret: Plain secret
            hashed_secret: Hashed secret from database
        
        Returns:
            True if valid
        """
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(secret, hashed_secret)
    
    def is_api_key_expired(
        self,
        created_at: datetime,
        expires_in_days: Optional[int] = None,
    ) -> bool:
        """
        Check if API key has expired.
        
        Args:
            created_at: Key creation timestamp
            expires_in_days: Expiration period in days (None = never expires)
        
        Returns:
            True if expired
        """
        if expires_in_days is None:
            return False
        
        expiry_date = created_at + timedelta(days=expires_in_days)
        return datetime.utcnow() > expiry_date
    
    def generate_key_prefix(self) -> str:
        """Generate a short prefix for displaying keys."""
        return f"pk_{secrets.token_hex(4)}"
    
    def mask_api_key(self, api_key: str) -> str:
        """
        Mask API key for display.
        
        Args:
            api_key: Full API key
        
        Returns:
            Masked key (e.g., "pk_abc...xyz")
        """
        parts = api_key.split('.')
        if len(parts) != 2:
            return "***"
        
        key_id = parts[0]
        return f"{key_id[:8]}...{key_id[-4:]}"
