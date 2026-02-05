# app/models/user.py

"""
User and Farmer models
"""

from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, Boolean, DateTime, func

if TYPE_CHECKING:
    from app.models.animal import Animal  # type: ignore
    from app.models.order import Order  # type: ignore
    from app.models.cart import CartItem  # type: ignore


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str] = None
    email: str = Field(sa_column=Column(String, unique=True, index=True, nullable=False))
    password_hash: str = Field(sa_column=Column(String, nullable=False))
    role: str = Field(default="user", index=True)
    is_active: bool = Field(default=True, sa_column=Column(Boolean, default=True))

    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), onupdate=func.now(), nullable=True))

    # Relationships
    farmer_profile: Optional["Farmer"] = Relationship(back_populates="user")
    orders: Optional[List["Order"]] = Relationship(back_populates="buyer")
    cart_items: Optional[List["CartItem"]] = Relationship(back_populates="buyer")


class Farmer(SQLModel, table=True):
    __tablename__ = "farmers"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    farm_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), onupdate=func.now(), nullable=True))

    # Relationships
    user: Optional[User] = Relationship(back_populates="farmer_profile")
    animals: Optional[List["Animal"]] = Relationship(back_populates="farmer")
