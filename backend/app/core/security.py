# app/core/security.py

"""
JWT, password hashing, and role-based dependencies
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import bcrypt
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_session

logger = logging.getLogger(__name__)

# Password hashing - using bcrypt directly to avoid passlib compatibility issues
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash with error handling"""
    try:
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


# OAuth2 bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    roles: Optional[List[str]] = []


def _create_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": now, "sub": str(data.get("sub", ""))})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    return _create_token(data, expires_delta)


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a refresh token with longer expiration (default 7 days)"""
    if expires_delta is None:
        expires_delta = timedelta(days=7)
    return _create_token(data, expires_delta)


def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_session)):
    payload = decode_token(token)
    from app.models.user import User as UserModel  # lazy import

    stmt = select(UserModel).where(UserModel.id == int(payload.get("sub", 0)))
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_farmer(user=Depends(get_current_user)):
    if getattr(user, "role", None) != "farmer":
        raise HTTPException(status_code=403, detail="Farmer only operation")
    return user


def require_buyer(user=Depends(get_current_user)):
    if getattr(user, "role", None) not in ("user", "buyer"):
        raise HTTPException(status_code=403, detail="Buyer only operation")
    return user
