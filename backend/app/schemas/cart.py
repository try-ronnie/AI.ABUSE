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
from pydantic import BaseModel, Field
from annotated_types import Gt, Ge


# ----------------------------
# CartItem Schemas
# ----------------------------
class CartItemCreate(BaseModel):
    """
    Payload for adding an item to the cart.
    """
    animal_id: int
    quantity: int = Field(default=1, gt=0)


class CartItemUpdate(BaseModel):
    """
    Payload for updating an existing cart item.
    All fields optional — only provided fields will be applied.
    """
    quantity: Optional[int] = Field(default=None, gt=0)


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

    model_config = {"from_attributes": True}


# ----------------------------
# Cart Schemas
# ----------------------------
class CartRead(BaseModel):
    """
    Representation of a buyer's cart.
    """
    buyer_id: int
    items: List[CartItemRead] = []

    model_config = {"from_attributes": True}
