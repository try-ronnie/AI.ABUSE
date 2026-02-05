# app/models/cart.py

"""
SQLModel model for Cart Items

Responsibilities:
- Track items a buyer has added before checkout
- Link each cart item to a buyer (User) and an animal
- Keep table lean; no business logic here
"""

from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, Float, func

if TYPE_CHECKING:
    from app.models.user import User  # type: ignore
    from app.models.animal import Animal  # type: ignore


class CartItem(SQLModel, table=True):
    __tablename__ = "cart_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    buyer_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    animal_id: int = Field(foreign_key="animals.id", nullable=False, index=True)
    quantity: int = Field(default=1)
    price: float = Field(default=0.0)

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    )

    # Relationships
    buyer: Optional["User"] = Relationship(back_populates="cart_items")
    animal: Optional["Animal"] = Relationship(back_populates="cart_items")
