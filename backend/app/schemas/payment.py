"""
Pydantic schemas for Payments

Responsibilities:
- Define request/response payloads for payment operations
- Keep schemas lean; no DB logic
- Separate Create, Update, and Read payloads
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, confloat

class PaymentCreate(BaseModel):
    order_id: int
    buyer_id: int
    amount: confloat(ge=0.0)
    provider: Optional[str] = "mpesa"


class PaymentUpdate(BaseModel):
    status: Optional[str] = Field(default=None)  # pending, completed, failed


class PaymentRead(BaseModel):
    id: int
    order_id: int
    buyer_id: int
    amount: float
    status: str
    provider: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
