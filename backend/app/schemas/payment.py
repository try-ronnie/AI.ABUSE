from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field, confloat


# ----------------------------
# Payment Schemas
# ----------------------------
class PaymentCreate(BaseModel):
    """
    Payload to initiate a payment for an order.
    """
    order_id: int
    amount: confloat(gt=0.0)
    method: str = Field(..., description="e.g. mpesa, card, cash")


class PaymentRead(BaseModel):
    """
    Representation returned by the API for a payment.
    """
    id: int
    order_id: int
    amount: float
    method: str
    status: str  # pending, successful, failed
    transaction_ref: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
