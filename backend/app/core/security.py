# app/core/security.py
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List, AsyncGenerator

from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_session

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme (reads Authorization: Bearer <token>)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ---------- Password Utilities ----------
def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Verify a plain-text password against a hash."""
    return pwd_context.verify(password, hashed)


# ---------- JWT Utilities ----------
class TokenPayload:
    """Expected payload structure for JWT tokens."""
    sub: Optional[str] = None
    exp: Optional[int] = None
    roles: Optional[List[str]] = []


def _create_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Internal JWT creation."""
    to_encode = data.copy()
    now = datetime.utcnow()
    expire = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": now, "sub": str(data.get("sub", ""))})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    return _create_token(data, expires_delta)


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT refresh token (longer expiry)."""
    expires = expires_delta or timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    return _create_token(data, expires)


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and verify JWT, raise 401 if invalid."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


# ---------- Current User / Role Dependencies ----------
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_session)):
    """
    Resolve current user from JWT token.
    - Returns DB User object if found.
    - Falls back to token payload dict if User model not yet available.
    """
    payload = decode_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token missing subject (user id)")

    # Attempt to load DB user if model exists
    try:
        from app.models.user import User as UserModel
        stmt = select(UserModel).where(UserModel.id == int(user_id))
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except Exception:
        # Return payload dict during initial scaffolding
        return payload


def _extract_role(user_or_payload: Any) -> Optional[str]:
    """Extract 'role' from user object or token payload."""
    if hasattr(user_or_payload, "role"):
        return getattr(user_or_payload, "role")
    if isinstance(user_or_payload, dict):
        roles = user_or_payload.get("roles")
        if roles:  # assume first role
            return str(roles[0])
        return user_or_payload.get("role")
    return None


def require_farmer(user=Depends(get_current_user)):
    """Dependency: ensure user has 'farmer' role."""
    role = _extract_role(user)
    if role != "farmer":
        raise HTTPException(status_code=403, detail="Operation allowed for farmers only")
    return user


def require_buyer(user=Depends(get_current_user)):
    """Dependency: ensure user has 'user' (buyer) role."""
    role = _extract_role(user)
    if role not in ("user", "buyer"):
        raise HTTPException(status_code=403, detail="Operation allowed for buyers only")
    return user
