# app/schemas/payment.py

"""
Pydantic schemas for Payments

Responsibilities:
- Define request/response payloads for payment operations
- Keep schemas lean; no DB logic
- Separate Create, Update, and Read payloads
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from decimal import Decimal


# ----------------------------
# Payment Schemas
# ----------------------------
class PaymentCreate(BaseModel):
    """
    Payload for creating a new payment.
    """
    order_id: int
    amount: Decimal = Field(..., gt=0, description="Payment amount must be positive")
    method: str = Field(default="mpesa", max_length=50)


class PaymentUpdate(BaseModel):
    """
    Payload for updating a payment.
    All fields optional — only provided fields will be applied.
    """
    status: Optional[str] = Field(default=None, max_length=20)
    method: Optional[str] = Field(default=None, max_length=50)


class PaymentRead(BaseModel):
    """
    Representation returned by the API for a payment.
    """
    id: int
    order_id: int
    amount: float
    status: str
    method: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PaymentSummary(BaseModel):
    """
    Lightweight payment representation.
    """
    id: int
    order_id: int
    amount: float
    status: str

    model_config = {"from_attributes": True}
