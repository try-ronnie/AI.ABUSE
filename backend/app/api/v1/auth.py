# app/api/v1/auth.py

"""
Authentication endpoints.
- User registration
- JWT login
- Generates access & refresh tokens
"""

import logging
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_session
from app.core.config import settings
from app.core.security import verify_password, hash_password, create_access_token, create_refresh_token, decode_token
from app.models.user import User, Farmer
from app.schemas.user import UserCreate, UserRead
from app.schemas.auth import Token, RefreshTokenRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_session)):
    """Register a new user"""
    logger.info(f"Registration attempt for email: {payload.email}")
    
    # Check if email already exists
    stmt = select(User).where(User.email == payload.email)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing:
        logger.warning(f"Registration failed - email already exists: {payload.email}")
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role or "user"
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    logger.info(f"User registered successfully: {user.id} - {user.email}")
    
    # If registering as farmer, create farmer profile
    if payload.role == "farmer":
        farmer = Farmer(user_id=user.id)
        db.add(farmer)
        await db.commit()
    
    return user


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session)):
    """Login and get access/refresh tokens"""
    logger.info(f"Login attempt for username: {form_data.username}")
    
    stmt = select(User).where(User.email == form_data.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        logger.warning(f"Login failed - user not found: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verify password
    password_valid = verify_password(form_data.password, user.password_hash)
    logger.info(f"Password verification result for {form_data.username}: {password_valid}")
    
    if not password_valid or not user:
        logger.warning(f"Login failed - invalid password for: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not user.is_active:
        logger.warning(f"Login failed - inactive user: {form_data.username}")
        raise HTTPException(status_code=400, detail="User account is disabled")
    
    access_token = create_access_token(
        {"sub": str(user.id), "roles": [user.role]},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(
        {"sub": str(user.id), "roles": [user.role]}
    )
    
    logger.info(f"Login successful for user: {user.id} - {user.email}")

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_session)
):
    """Refresh access token using refresh token"""
    try:
        token_data = decode_token(payload.refresh_token)
        user_id = int(token_data.get("sub", 0))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        {"sub": str(user.id), "roles": [user.role]},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
