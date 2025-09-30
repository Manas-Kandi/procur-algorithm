"""Password policy enforcement and validation."""

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional

from passlib.context import CryptContext


@dataclass
class PasswordPolicy:
    """Password policy configuration."""
    
    min_length: int = 12
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_digit: bool = True
    require_special: bool = True
    special_chars: str = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    max_age_days: int = 90
    prevent_reuse_count: int = 5
    max_failed_attempts: int = 5
    lockout_duration_minutes: int = 30


class PasswordValidator:
    """Validates passwords against policy."""
    
    def __init__(self, policy: Optional[PasswordPolicy] = None):
        """Initialize validator with policy."""
        self.policy = policy or PasswordPolicy()
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def validate(self, password: str) -> tuple[bool, List[str]]:
        """
        Validate password against policy.
        
        Args:
            password: Password to validate
        
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        
        # Check length
        if len(password) < self.policy.min_length:
            errors.append(f"Password must be at least {self.policy.min_length} characters long")
        
        # Check uppercase
        if self.policy.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        # Check lowercase
        if self.policy.require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        # Check digit
        if self.policy.require_digit and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        # Check special character
        if self.policy.require_special:
            special_pattern = f"[{re.escape(self.policy.special_chars)}]"
            if not re.search(special_pattern, password):
                errors.append(f"Password must contain at least one special character from: {self.policy.special_chars}")
        
        # Check for common patterns
        if self._has_common_patterns(password):
            errors.append("Password contains common patterns and is too weak")
        
        return len(errors) == 0, errors
    
    def _has_common_patterns(self, password: str) -> bool:
        """Check for common weak patterns."""
        common_patterns = [
            r'(.)\1{2,}',  # Repeated characters (aaa, 111)
            r'(012|123|234|345|456|567|678|789)',  # Sequential numbers
            r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)',  # Sequential letters
            r'password|admin|user|login|welcome',  # Common words
        ]
        
        password_lower = password.lower()
        for pattern in common_patterns:
            if re.search(pattern, password_lower):
                return True
        
        return False
    
    def hash_password(self, password: str) -> str:
        """Hash a password."""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def needs_rehash(self, hashed_password: str) -> bool:
        """Check if password hash needs to be updated."""
        return self.pwd_context.needs_update(hashed_password)
    
    def is_password_expired(self, last_changed: datetime) -> bool:
        """Check if password has expired."""
        if self.policy.max_age_days <= 0:
            return False
        
        expiry_date = last_changed + timedelta(days=self.policy.max_age_days)
        return datetime.utcnow() > expiry_date
    
    def can_reuse_password(
        self,
        new_password: str,
        previous_hashes: List[str]
    ) -> bool:
        """Check if password can be reused."""
        if self.policy.prevent_reuse_count <= 0:
            return True
        
        # Check against last N passwords
        recent_hashes = previous_hashes[-self.policy.prevent_reuse_count:]
        for old_hash in recent_hashes:
            if self.verify_password(new_password, old_hash):
                return False
        
        return True


# Global validator instance
_validator = PasswordValidator()


def validate_password(password: str, policy: Optional[PasswordPolicy] = None) -> tuple[bool, List[str]]:
    """
    Validate password against policy.
    
    Args:
        password: Password to validate
        policy: Optional custom policy
    
    Returns:
        Tuple of (is_valid, list of error messages)
    """
    if policy:
        validator = PasswordValidator(policy)
    else:
        validator = _validator
    
    return validator.validate(password)
