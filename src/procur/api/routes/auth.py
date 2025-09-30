"""Authentication endpoints."""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...db import get_session
from ...db.repositories import UserRepository
from ..config import get_api_config
from ..schemas import Token, UserLogin, UserRegister, UserResponse
from ..security import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account",
)
def register(
    user_data: UserRegister,
    session: Session = Depends(get_session),
):
    """Register a new user account."""
    user_repo = UserRepository(session)
    
    # Check if user already exists
    if user_repo.get_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    if user_repo.get_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = user_repo.create(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role="buyer",  # Default role
        organization_id=user_data.organization_id,
        is_active=True,
    )
    
    return user


@router.post(
    "/login",
    response_model=Token,
    summary="Login",
    description="Authenticate and get access token",
)
def login(
    credentials: UserLogin,
    session: Session = Depends(get_session),
):
    """Authenticate user and return JWT token."""
    config = get_api_config()
    
    user = authenticate_user(session, credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    user_repo = UserRepository(session)
    user_repo.update_last_login(user.id)
    
    # Create access token
    access_token_expires = timedelta(minutes=config.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role},
        expires_delta=access_token_expires,
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get current authenticated user information",
)
def get_me(current_user=Depends(get_current_user)):
    """Get current user information."""
    return current_user
