# app/schemas/cart.py

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, conint, confloat


# ----------------------------
# CartItem Schemas
# ----------------------------
class CartItemCreate(BaseModel):
    animal_id: int
    quantity: conint(gt=0) = 1


class CartItemUpdate(BaseModel):
    quantity: Optional[conint(gt=0)] = None


class CartItemRead(BaseModel):
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
# Cart Schemas
# ----------------------------
class CartRead(BaseModel):
    buyer_id: int
    items: List[CartItemRead] = []

    class Config:
        orm_mode = True
