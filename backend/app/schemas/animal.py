# app/schemas/cart.py

"""
Pydantic schemas for Cart & CartItems

Responsibilities:
- Define request/response payloads for cart operations
- Keep schemas lean; no DB logic
- Separate Create, Update, and Read payloads
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, conint, confloat


# ----------------------------
# CartItem Schemas
# ----------------------------
class CartItemCreate(BaseModel):
    """
    Payload for adding an item to the cart.
    """
    animal_id: int
    quantity: conint(gt=0) = 1


class CartItemUpdate(BaseModel):
    """
    Payload for updating an existing cart item.
    All fields optional — only provided fields will be applied.
    """
    quantity: Optional[conint(gt=0)] = None
    price: Optional[confloat(ge=0.0)] = None


class CartItemRead(BaseModel):
    """
    Representation returned by the API for a cart item.
    """
    id: int
    buyer_id: int
    animal_id: int
    quantity: int
    price: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# ----------------------------
# Cart Schemas (optional wrapper)
# ----------------------------
class CartRead(BaseModel):
    """
    Representation of a buyer's cart.
    """
    buyer_id: int
    items: List[CartItemRead] = []

    class Config:
        orm_mode = True
