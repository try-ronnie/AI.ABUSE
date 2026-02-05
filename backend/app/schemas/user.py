# app/schemas/user.py

"""
Pydantic schemas for User and Farmer

Responsibilities:
- Payloads for creating, updating, and reading users
- Separate schemas for Farmer profile
- Clean, lightweight, no DB logic
- Compatible with auth.py and users.py
"""
# app/schemas/user.py

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, constr


# ----------------------------
# User Schemas
# ----------------------------
class UserCreate(BaseModel):
    """
    Payload for registering a new user.
    """
    name: Optional[constr(strip_whitespace=True, min_length=1)]
    email: EmailStr
    password: constr(min_length=6)
    role: Optional[str] = "user"  # 'user' or 'farmer'


class UserUpdate(BaseModel):
    """
    Payload to update a user's profile.
    """
    name: Optional[constr(strip_whitespace=True, min_length=1)] = None
    email: Optional[EmailStr] = None
    password: Optional[constr(min_length=6)] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserRead(BaseModel):
    """
    Response schema for returning a user.
    """
    id: int
    name: Optional[str]
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# ----------------------------
# Farmer Schemas
# ----------------------------
class FarmerCreate(BaseModel):
    """
    Payload for creating a farmer profile.
    """
    user_id: int
    farm_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None


class FarmerRead(BaseModel):
    """
    Response schema for a farmer profile.
    """
    id: int
    user_id: int
    farm_name: Optional[str]
    phone: Optional[str]
    location: Optional[str]
    bio: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
