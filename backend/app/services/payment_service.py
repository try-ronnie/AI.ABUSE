"""
PaymentService

Responsibilities:
- Handle payment processing for orders
- Integrate with external payment APIs (e.g., Mpesa) or mock payment
- Update order payment status after successful payment
- Keep service layer separate from FastAPI endpoints
"""
from typing import Optional
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order


class PaymentService:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ----------------------------
    # Process payment for a given order
    # ----------------------------
    async def process_payment(self, order_id: int, amount: float) -> Order:
        order: Optional[Order] = await self.session.get(Order, order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")

        if order.is_paid:
            raise ValueError(f"Order {order_id} is already paid")

        # Optional: validate amount matches order.total_price
        if amount < order.total_price:
            raise ValueError("Payment amount is less than order total")

        # Mock payment processing (replace with Mpesa API or other)
        payment_successful = True  # replace with actual payment logic
        if not payment_successful:
            raise ValueError("Payment failed")

        # Mark order as paid
        order.is_paid = True
        order.status = "paid"
        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order)

        return order

    # ----------------------------
    # Refund / cancel payment (optional)
    # ----------------------------
    async def refund_payment(self, order: Order) -> Order:
        if not order.is_paid:
            raise ValueError("Order is not paid yet")

        # Mock refund logic
        order.is_paid = False
        order.status = "pending"
        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order)
        return order
