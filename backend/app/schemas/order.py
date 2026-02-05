# app/schemas/order.py

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, confloat


# ----------------------------
# OrderItem Schemas (READ ONLY)
# ----------------------------
class OrderItemRead(BaseModel):
    id: int
    order_id: int
    animal_id: int
    quantity: int
    price: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# ----------------------------
# Order Schemas
# ----------------------------
class OrderUpdate(BaseModel):
    status: Optional[str] = Field(default=None)  # pending, confirmed, paid, rejected
    is_paid: Optional[bool] = None
    total_price: Optional[confloat(ge=0.0)] = None


class OrderRead(BaseModel):
    id: int
    buyer_id: int
    status: str
    total_price: float
    is_paid: bool
    items: List[OrderItemRead] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
