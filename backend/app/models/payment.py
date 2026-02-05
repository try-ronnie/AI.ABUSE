"""
SQLModel model for Payments

Responsibilities:
- Track payment records for orders
- Link each payment to an order and a buyer
- Keep table lean; no business logic here
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, Float, String, Boolean, func

class Payment(SQLModel, table=True):
    __tablename__ = "payments"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id", nullable=False, index=True)
    buyer_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    amount: float = Field(default=0.0)
    status: str = Field(default="pending", index=True)  # pending, completed, failed
    provider: Optional[str] = Field(default="mpesa")  # payment gateway

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    )

    # Relationships
    order: Optional["Order"] = Relationship(back_populates="payments")
