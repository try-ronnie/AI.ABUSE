# app/api/v1/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import timedelta

from app.core.database import get_session
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.models.user import User
from app.schemas.user import UserCreate
from app.schemas.auth import TokenRead

router = APIRouter(prefix="/auth", tags=["Auth"])


# ----------------------------
# Register endpoint
# ----------------------------
@router.post("/register", response_model=TokenRead, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_session)):
    # Check if user exists
    stmt = select(User).where(User.email == payload.email)
    result = await db.exec(stmt)
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    pwd_hash = hash_password(payload.password)

    # Create user
    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=pwd_hash,
        role=payload.role or "user",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Generate tokens
    access_token = create_access_token({"sub": str(user.id), "roles": [user.role]})
    refresh_token = create_refresh_token({"sub": str(user.id), "roles": [user.role]})
    return TokenRead(access_token=access_token, refresh_token=refresh_token)


# ----------------------------
# Login endpoint
# ----------------------------
@router.post("/login", response_model=TokenRead)
async def login(payload: UserCreate, db: AsyncSession = Depends(get_session)):
    stmt = select(User).where(User.email == payload.email)
    result = await db.exec(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": str(user.id), "roles": [user.role]})
    refresh_token = create_refresh_token({"sub": str(user.id), "roles": [user.role]})
    return TokenRead(access_token=access_token, refresh_token=refresh_token)
