# app/models/payment.py

"""
SQLModel model for Payments

Responsibilities:
- Define the Payment table
- Track payment status and method
- Link to orders via foreign key
"""

from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, func

if TYPE_CHECKING:
    from app.models.order import Order  # type: ignore


class Payment(SQLModel, table=True):
    __tablename__ = "payments"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id", nullable=False, index=True)
    amount: float = Field(default=0.0)
    status: str = Field(default="pending")  # pending, completed, failed
    method: str = Field(default="mpesa")    # mpesa, card, bank, etc.

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    )

    # Relationships
    order: Optional["Order"] = Relationship(back_populates="payment")
