# app/models/order.py

"""
SQLModel models for Orders & OrderItems

Responsibilities:
- Define the Order table (buyer orders)
- Define OrderItem table (items within an order)
- Track relationships to Animal, User, and Payment
- Keep models lean; no business logic
"""

from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, func

if TYPE_CHECKING:
    from app.models.user import User  # type: ignore
    from app.models.animal import Animal  # type: ignore
    from app.models.payment import Payment  # type: ignore


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: Optional[int] = Field(default=None, primary_key=True)
    buyer_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    status: str = Field(default="pending", index=True)  # pending, confirmed, rejected, paid
    total_price: float = Field(default=0.0)
    is_paid: bool = Field(default=False)

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    )

    # Relationships
    buyer: Optional["User"] = Relationship(back_populates="orders")
    items: Optional[List["OrderItem"]] = Relationship(back_populates="order")
    payment: Optional["Payment"] = Relationship(back_populates="order")


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id", nullable=False, index=True)
    animal_id: int = Field(foreign_key="animals.id", nullable=False, index=True)
    quantity: int = Field(default=1)
    price: float = Field(default=0.0)  # capture price at time of order

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    )

    # Relationships
    order: Optional["Order"] = Relationship(back_populates="items")
    animal: Optional["Animal"] = Relationship(back_populates="order_items")
