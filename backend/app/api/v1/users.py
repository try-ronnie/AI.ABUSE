# app/api/v1/users.py

"""
User endpoints.
- Get current user profile
- Update user profile
- Admin: List users
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_session
from app.core.security import get_current_user, hash_password
from app.models.user import User, Farmer
from app.schemas.user import UserRead, UserUpdate, FarmerCreate, FarmerRead, FarmerUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserRead)
async def get_current_user_profile(user=Depends(get_current_user)):
    """Get current authenticated user's profile"""
    return user


@router.patch("/me", response_model=UserRead)
async def update_current_user(
    payload: UserUpdate,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Update current user's profile"""
    update_data = payload.model_dump(exclude_unset=True)
    
    # Handle password update separately
    if "password" in update_data:
        update_data["password_hash"] = hash_password(update_data.pop("password"))
    
    for key, value in update_data.items():
        setattr(user, key, value)
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/me/farmer", response_model=FarmerRead)
async def get_farmer_profile(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Get current user's farmer profile"""
    if user.role != "farmer":
        raise HTTPException(status_code=400, detail="User is not a farmer")
    
    stmt = select(Farmer).where(Farmer.user_id == user.id)
    result = await db.execute(stmt)
    farmer = result.scalar_one_or_none()
    
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer profile not found")
    
    return farmer


@router.patch("/me/farmer", response_model=FarmerRead)
async def update_farmer_profile(
    payload: FarmerUpdate,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Update current user's farmer profile"""
    if user.role != "farmer":
        raise HTTPException(status_code=400, detail="User is not a farmer")
    
    stmt = select(Farmer).where(Farmer.user_id == user.id)
    result = await db.execute(stmt)
    farmer = result.scalar_one_or_none()
    
    if not farmer:
        # Create farmer profile if it doesn't exist
        farmer = Farmer(user_id=user.id)
    
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(farmer, key, value)
    
    db.add(farmer)
    await db.commit()
    await db.refresh(farmer)
    return farmer


@router.get("/", response_model=List[UserRead])
async def list_users(db: AsyncSession = Depends(get_session)):
    """List all users (admin endpoint)"""
    stmt = select(User)
    result = await db.execute(stmt)
    return result.scalars().all()
