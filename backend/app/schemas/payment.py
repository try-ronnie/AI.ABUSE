# app/schemas/payment.py
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, condecimal

class PaymentCreate(BaseModel):
    order_id: int
    amount: condecimal(gt=0)
    method: str = "mpesa"


class PaymentRead(BaseModel):
    id: int
    order_id: int
    amount: float
    status: str
    method: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
