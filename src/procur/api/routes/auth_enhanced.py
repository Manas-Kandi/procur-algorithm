"""Enhanced authentication endpoints with MFA, API keys, and OAuth."""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ...auth import MFAService, APIKeyService, PasswordValidator, validate_password
from ...auth.permissions import Permission, PermissionChecker
from ...db import get_session
from ...db.models import UserAccount
from ...db.models_auth import APIKey, Organization, UserSession
from ...db.repositories import UserRepository
from ...db.repositories.auth_repositories import (
    APIKeyRepository,
    LoginAttemptRepository,
    OrganizationRepository,
    PasswordHistoryRepository,
    SessionRepository,
)
from ..config import get_api_config
from ..schemas import UserResponse
from ..security import create_access_token, get_current_user, get_password_hash

router = APIRouter(prefix="/auth", tags=["Authentication Enhanced"])


# ============================================================================
# MFA Endpoints
# ============================================================================

@router.post(
    "/mfa/setup",
    summary="Setup MFA",
    description="Generate MFA secret and QR code for user",
)
def setup_mfa(
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Setup MFA for current user."""
    if current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is already enabled",
        )
    
    mfa_service = MFAService()
    secret = mfa_service.generate_secret()
    
    # Store secret temporarily (not enabled until verified)
    user_repo = UserRepository(session)
    user_repo.update(current_user.id, mfa_secret=secret)
    
    # Generate QR code
    qr_code = mfa_service.generate_qr_code(secret, current_user.email)
    
    # Generate backup codes
    backup_codes = mfa_service.generate_backup_codes()
    
    return {
        "secret": secret,
        "qr_code_url": f"data:image/png;base64,{qr_code.hex()}",
        "backup_codes": backup_codes,
        "provisioning_uri": mfa_service.get_provisioning_uri(secret, current_user.email),
    }


@router.post(
    "/mfa/enable",
    summary="Enable MFA",
    description="Verify MFA token and enable MFA",
)
def enable_mfa(
    token: str,
    backup_codes: list[str],
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Enable MFA after verifying token."""
    if not current_user.mfa_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA setup not initiated. Call /mfa/setup first",
        )
    
    # Verify token
    mfa_service = MFAService()
    if not mfa_service.verify_token(current_user.mfa_secret, token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid MFA token",
        )
    
    # Hash backup codes
    validator = PasswordValidator()
    hashed_codes = [validator.hash_password(code.replace('-', '').upper()) for code in backup_codes]
    
    # Enable MFA
    user_repo = UserRepository(session)
    user_repo.update(
        current_user.id,
        mfa_enabled=True,
        mfa_backup_codes=hashed_codes,
    )
    
    return {"message": "MFA enabled successfully"}


@router.post(
    "/mfa/disable",
    summary="Disable MFA",
    description="Disable MFA for user",
)
def disable_mfa(
    password: str,
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Disable MFA (requires password confirmation)."""
    validator = PasswordValidator()
    if not validator.verify_password(password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
        )
    
    user_repo = UserRepository(session)
    user_repo.update(
        current_user.id,
        mfa_enabled=False,
        mfa_secret=None,
        mfa_backup_codes=None,
    )
    
    return {"message": "MFA disabled successfully"}


@router.post(
    "/mfa/verify",
    summary="Verify MFA token",
    description="Verify MFA token during login",
)
def verify_mfa_token(
    token: str,
    session_id: str,
    session: Session = Depends(get_session),
):
    """Verify MFA token and complete login."""
    # Get pending session
    session_repo = SessionRepository(session)
    user_session = session_repo.get_by_session_id(session_id)
    
    if not user_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    
    # Get user
    user_repo = UserRepository(session)
    user = user_repo.get_by_id(user_session.user_id)
    
    if not user or not user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA not enabled for this user",
        )
    
    # Verify token
    mfa_service = MFAService()
    if not mfa_service.verify_token(user.mfa_secret, token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA token",
        )
    
    # Activate session
    session_repo.update(user_session.id, is_active=True)
    
    # Generate access token
    config = get_api_config()
    access_token_expires = timedelta(minutes=config.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role},
        expires_delta=access_token_expires,
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


# ============================================================================
# API Key Endpoints
# ============================================================================

@router.post(
    "/api-keys",
    summary="Create API key",
    description="Generate a new API key for programmatic access",
)
def create_api_key(
    name: str,
    scopes: Optional[list[str]] = None,
    expires_in_days: Optional[int] = None,
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create a new API key."""
    # Check permission
    perm_checker = PermissionChecker()
    if not perm_checker.has_permission(
        current_user.role,
        Permission.API_KEY_CREATE,
        current_user.is_superuser,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create API keys",
        )
    
    config = get_api_config()
    api_key_service = APIKeyService(config.secret_key)
    
    # Generate API key
    key_id, api_key = api_key_service.generate_api_key(current_user.id, name, scopes)
    
    # Parse and hash secret
    parsed = api_key_service.parse_api_key(api_key)
    if not parsed:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate API key",
        )
    
    _, secret = parsed
    hashed_secret = api_key_service.hash_api_key_secret(secret)
    
    # Calculate expiration
    expires_at = None
    if expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
    
    # Store in database
    api_key_repo = APIKeyRepository(session)
    key_record = api_key_repo.create(
        key_id=key_id,
        user_id=current_user.id,
        name=name,
        hashed_secret=hashed_secret,
        key_prefix=api_key_service.mask_api_key(api_key),
        scopes=scopes,
        expires_at=expires_at,
    )
    
    return {
        "api_key": api_key,  # Only shown once!
        "key_id": key_id,
        "name": name,
        "created_at": key_record.created_at,
        "expires_at": expires_at,
        "warning": "Save this API key securely. It will not be shown again.",
    }


@router.get(
    "/api-keys",
    summary="List API keys",
    description="List all API keys for current user",
)
def list_api_keys(
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List user's API keys."""
    api_key_repo = APIKeyRepository(session)
    keys = api_key_repo.get_user_keys(current_user.id)
    
    return [
        {
            "id": key.id,
            "key_id": key.key_id,
            "name": key.name,
            "key_prefix": key.key_prefix,
            "is_active": key.is_active,
            "created_at": key.created_at,
            "last_used_at": key.last_used_at,
            "expires_at": key.expires_at,
            "usage_count": key.usage_count,
        }
        for key in keys
    ]


@router.delete(
    "/api-keys/{key_id}",
    summary="Delete API key",
    description="Revoke an API key",
)
def delete_api_key(
    key_id: str,
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Delete an API key."""
    api_key_repo = APIKeyRepository(session)
    key = api_key_repo.get_by_key_id(key_id)
    
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
    
    if key.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this API key",
        )
    
    api_key_repo.delete(key.id)
    
    return {"message": "API key deleted successfully"}


# ============================================================================
# Session Management Endpoints
# ============================================================================

@router.get(
    "/sessions",
    summary="List sessions",
    description="List all active sessions for current user",
)
def list_sessions(
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List user's active sessions."""
    session_repo = SessionRepository(session)
    sessions = session_repo.get_active_sessions(current_user.id)
    
    return [
        {
            "session_id": s.session_id,
            "ip_address": s.ip_address,
            "device_type": s.device_type,
            "location": s.location,
            "last_activity_at": s.last_activity_at,
            "created_at": s.created_at,
        }
        for s in sessions
    ]


@router.delete(
    "/sessions/{session_id}",
    summary="Revoke session",
    description="Revoke a specific session",
)
def revoke_session(
    session_id: str,
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Revoke a session."""
    session_repo = SessionRepository(session)
    user_session = session_repo.get_by_session_id(session_id)
    
    if not user_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    
    if user_session.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to revoke this session",
        )
    
    session_repo.deactivate_session(session_id)
    
    return {"message": "Session revoked successfully"}


@router.post(
    "/sessions/revoke-all",
    summary="Revoke all sessions",
    description="Revoke all sessions except current",
)
def revoke_all_sessions(
    except_current: bool = True,
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Revoke all user sessions."""
    session_repo = SessionRepository(session)
    sessions = session_repo.get_active_sessions(current_user.id)
    
    revoked_count = 0
    for user_session in sessions:
        # Skip current session if requested
        if except_current:
            # TODO: Get current session ID from request
            pass
        
        session_repo.deactivate_session(user_session.session_id)
        revoked_count += 1
    
    return {"message": f"Revoked {revoked_count} session(s)"}


# ============================================================================
# Password Management Endpoints
# ============================================================================

@router.post(
    "/password/change",
    summary="Change password",
    description="Change user password",
)
def change_password(
    current_password: str,
    new_password: str,
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Change user password."""
    validator = PasswordValidator()
    
    # Verify current password
    if not validator.verify_password(current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )
    
    # Validate new password
    is_valid, errors = validate_password(new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Password does not meet requirements", "errors": errors},
        )
    
    # Check password history
    password_history_repo = PasswordHistoryRepository(session)
    history = password_history_repo.get_user_history(current_user.id, limit=5)
    
    for old_password in history:
        if validator.verify_password(new_password, old_password.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot reuse recent passwords",
            )
    
    # Update password
    new_hash = validator.hash_password(new_password)
    user_repo = UserRepository(session)
    user_repo.update(
        current_user.id,
        hashed_password=new_hash,
        password_changed_at=datetime.utcnow(),
        must_change_password=False,
    )
    
    # Add to password history
    password_history_repo.create(
        user_id=current_user.id,
        hashed_password=new_hash,
    )
    
    return {"message": "Password changed successfully"}


# ============================================================================
# Organization Management Endpoints
# ============================================================================

@router.post(
    "/organizations",
    summary="Create organization",
    description="Create a new organization (admin only)",
)
def create_organization(
    name: str,
    organization_id: str,
    domain: Optional[str] = None,
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create a new organization."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can create organizations",
        )
    
    org_repo = OrganizationRepository(session)
    
    # Check if organization ID already exists
    if org_repo.get_by_organization_id(organization_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization ID already exists",
        )
    
    org = org_repo.create(
        organization_id=organization_id,
        name=name,
        domain=domain,
        is_active=True,
    )
    
    return {
        "id": org.id,
        "organization_id": org.organization_id,
        "name": org.name,
        "domain": org.domain,
        "created_at": org.created_at,
    }


@router.get(
    "/organizations",
    summary="List organizations",
    description="List all organizations",
)
def list_organizations(
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List organizations."""
    org_repo = OrganizationRepository(session)
    
    if current_user.is_superuser:
        orgs = org_repo.get_all()
    else:
        # Users can only see their own organization
        if not current_user.organization_id:
            return []
        org = org_repo.get_by_organization_id(current_user.organization_id)
        orgs = [org] if org else []
    
    return [
        {
            "id": org.id,
            "organization_id": org.organization_id,
            "name": org.name,
            "domain": org.domain,
            "is_active": org.is_active,
        }
        for org in orgs
    ]
