# app/schemas/cart.py

"""
Pydantic schemas for CartItem

Responsibilities:
- Define request/response models for Cart endpoints
- Keep schemas lean, no business logic
- Align with CartItem model from SQLModel
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class CartItemBase(BaseModel):
    animal_id: int
    quantity: int = Field(default=1, ge=1)


class CartItemCreate(CartItemBase):
    """Schema for adding an item to cart"""
    pass


class CartItemUpdate(BaseModel):
    """Schema for updating quantity in cart"""
    quantity: int = Field(..., ge=1)


class CartItemRead(CartItemBase):
    id: int
    buyer_id: int
    price: float
    created_at: datetime
    updated_at: Optional[datetime]

    # Optional nested animal info (from relationship) - handy for responses
    animal_name: Optional[str]
    animal_species: Optional[str]
    animal_price: Optional[float]

    class Config:
        orm_mode = True
