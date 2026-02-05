from typing import Optional
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, Float, String, func, Boolean

from app.models.order import Order  # circular import safe if only TYPE_CHECKING used elsewhere


class Payment(SQLModel, table=True):
    __tablename__ = "payments"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id", nullable=False, index=True)
    amount: float = Field(default=0.0)
    method: str = Field(default="unknown")
    status: str = Field(default="pending", index=True)  # pending, successful, failed
    transaction_ref: Optional[str] = None  # optional reference from payment gateway

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    )

    # Relationship to Order
    order: Optional[Order] = Relationship(back_populates="payment")
