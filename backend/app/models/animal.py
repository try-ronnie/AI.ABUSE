# app/models/animal.py

"""
SQLModel model for farm animals

Responsibilities:
- Define the Animal table
- Track ownership (farmer) and status
- Support relationships with orders, cart, etc.
- Keep table lean and focused; no business logic here
"""

from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, Float, DateTime, Boolean, func

if TYPE_CHECKING:
    from app.models.user import Farmer  # type: ignore
    from app.models.order import OrderItem  # type: ignore


class Animal(SQLModel, table=True):
    __tablename__ = "animals"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    species: str = Field(default="unknown", index=True)
    breed: Optional[str] = None
    age: Optional[int] = None  # in months or years
    gender: Optional[str] = None  # 'male' / 'female'
    price: float = Field(default=0.0)
    available: bool = Field(default=True)

    # Foreign key to farmer who owns the animal
    farmer_id: int = Field(foreign_key="farmers.id", nullable=False, index=True)

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    )

    # Relationships
    farmer: Optional["Farmer"] = Relationship(back_populates="animals")
    order_items: Optional[List["OrderItem"]] = Relationship(back_populates="animal")
