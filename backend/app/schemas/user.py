# app/schemas/user.py

"""
Pydantic schemas for User and Farmer

Responsibilities:
- Payloads for creating, updating, and reading users
- Separate schemas for Farmer profile
- Clean, lightweight, no DB logic
- Compatible with auth.py and users.py
"""

from typing import Optional, Annotated
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, StringConstraints


# ----------------------------
# User Schemas
# ----------------------------
class UserCreate(BaseModel):
    """
    Payload for registering a new user.
    """
    name: Optional[Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]] = None
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=6)]
    role: Optional[str] = "user"  # 'user' or 'farmer'


class UserUpdate(BaseModel):
    """
    Payload to update a user's profile.
    """
    name: Optional[Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]] = None
    email: Optional[EmailStr] = None
    password: Optional[Annotated[str, StringConstraints(min_length=6)]] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserRead(BaseModel):
    """
    Response schema for returning a user.
    """
    id: int
    name: Optional[str] = None
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ----------------------------
# Farmer Schemas
# ----------------------------
class FarmerCreate(BaseModel):
    """
    Payload for creating a farmer profile.
    """
    farm_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None


class FarmerUpdate(BaseModel):
    """
    Payload for updating a farmer profile.
    """
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
    farm_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
