# app/models/payment.py
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime, Float, String, Boolean, func

class Payment(SQLModel, table=True):
    __tablename__ = "payments"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(nullable=False, index=True)
    amount: float = Field(default=0.0)
    status: str = Field(default="pending")  # pending, completed, failed
    method: str = Field(default="mpesa")   # or other payment method

    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), onupdate=func.now(), nullable=True))
