"""Multi-factor authentication (MFA) support."""

import io
from typing import Optional

import pyotp
import qrcode
from qrcode.image.pil import PilImage


class MFAService:
    """Service for managing multi-factor authentication."""
    
    def __init__(self, issuer_name: str = "Procur"):
        """Initialize MFA service."""
        self.issuer_name = issuer_name
    
    def generate_secret(self) -> str:
        """
        Generate a new TOTP secret.
        
        Returns:
            Base32-encoded secret
        """
        return pyotp.random_base32()
    
    def get_provisioning_uri(
        self,
        secret: str,
        account_name: str,
    ) -> str:
        """
        Get provisioning URI for QR code.
        
        Args:
            secret: TOTP secret
            account_name: User's account name (email or username)
        
        Returns:
            Provisioning URI
        """
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=account_name,
            issuer_name=self.issuer_name,
        )
    
    def generate_qr_code(
        self,
        secret: str,
        account_name: str,
    ) -> bytes:
        """
        Generate QR code image for MFA setup.
        
        Args:
            secret: TOTP secret
            account_name: User's account name
        
        Returns:
            PNG image bytes
        """
        uri = self.get_provisioning_uri(secret, account_name)
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to bytes
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def verify_token(
        self,
        secret: str,
        token: str,
        window: int = 1,
    ) -> bool:
        """
        Verify a TOTP token.
        
        Args:
            secret: TOTP secret
            token: 6-digit token from authenticator app
            window: Number of time windows to check (default: 1 = 30 seconds)
        
        Returns:
            True if token is valid
        """
        if not token or not token.isdigit() or len(token) != 6:
            return False
        
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=window)
    
    def get_current_token(self, secret: str) -> str:
        """
        Get current TOTP token (for testing).
        
        Args:
            secret: TOTP secret
        
        Returns:
            Current 6-digit token
        """
        totp = pyotp.TOTP(secret)
        return totp.now()
    
    def generate_backup_codes(self, count: int = 10) -> list[str]:
        """
        Generate backup codes for account recovery.
        
        Args:
            count: Number of backup codes to generate
        
        Returns:
            List of backup codes
        """
        import secrets
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric code
            code = ''.join(secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789') for _ in range(8))
            # Format as XXXX-XXXX
            formatted = f"{code[:4]}-{code[4:]}"
            codes.append(formatted)
        return codes
    
    def verify_backup_code(
        self,
        code: str,
        hashed_codes: list[str],
        hasher,
    ) -> Optional[str]:
        """
        Verify a backup code and return the hash if valid.
        
        Args:
            code: Backup code to verify
            hashed_codes: List of hashed backup codes
            hasher: Password hasher instance
        
        Returns:
            Hash of the used code if valid, None otherwise
        """
        # Normalize code (remove dashes, uppercase)
        normalized = code.replace('-', '').replace(' ', '').upper()
        
        for hashed_code in hashed_codes:
            if hasher.verify_password(normalized, hashed_code):
                return hashed_code
        
        return None
