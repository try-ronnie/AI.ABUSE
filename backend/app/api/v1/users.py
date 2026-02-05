# app/api/v1/users.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.core.database import get_session
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


# ----------------------------
# Get current user's profile
# ----------------------------
@router.get("/me", response_model=UserRead)
async def get_my_profile(user=Depends(get_current_user)):
    return user


# ----------------------------
# Update current user's profile
# ----------------------------
@router.patch("/me", response_model=UserRead)
async def update_my_profile(
    payload: UserUpdate,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    changed = False
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(user, field, value)
        changed = True

    if changed:
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user


# ----------------------------
# Optional: List all users (admin-only)
# ----------------------------
@router.get("/", response_model=List[UserRead])
async def list_users(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    if getattr(user, "role", "user") != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    stmt = select(User)
    result = await db.exec(stmt)
    users = result.scalars().all()
    return users
