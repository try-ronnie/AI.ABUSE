# app/schemas/order.py

"""
Pydantic schemas for Orders & OrderItems

Responsibilities:
- Define request/response payloads for order operations
- Keep schemas lean; no DB logic
- Separate Create, Update, and Read payloads
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


# ----------------------------
# OrderItem Schemas
# ----------------------------
class OrderItemRead(BaseModel):
    """
    Representation returned by the API for an order item.
    """
    id: int
    order_id: int
    animal_id: int
    quantity: int
    price: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ----------------------------
# Order Schemas
# ----------------------------
class OrderCreate(BaseModel):
    """
    Payload for creating an order (checkout).
    Usually created from cart, so minimal input needed.
    """
    pass  # Checkout uses cart items, no explicit payload needed


class OrderUpdate(BaseModel):
    """
    Payload for updating an order status.
    """
    status: Optional[str] = None
    is_paid: Optional[bool] = None


class OrderRead(BaseModel):
    """
    Representation returned by the API for an order.
    """
    id: int
    buyer_id: int
    status: str
    total_price: float
    is_paid: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: Optional[List[OrderItemRead]] = None

    model_config = {"from_attributes": True}


class OrderSummary(BaseModel):
    """
    Lightweight order representation without items.
    """
    id: int
    buyer_id: int
    status: str
    total_price: float
    is_paid: bool
    created_at: datetime

    model_config = {"from_attributes": True}
