"""
Business logic for Payments

Responsibilities:
- Create, update, and retrieve payment records
- Handle payment status changes
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.payment import Payment

class PaymentService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_payment(self, order_id: int, buyer_id: int, amount: float, provider: str = "mpesa") -> Payment:
        payment = Payment(
            order_id=order_id,
            buyer_id=buyer_id,
            amount=amount,
            provider=provider,
            status="pending"
        )
        self.session.add(payment)
        await self.session.commit()
        await self.session.refresh(payment)
        return payment

    async def get_payment(self, payment_id: int) -> Optional[Payment]:
        stmt = select(Payment).where(Payment.id == payment_id)
        result = await self.session.exec(stmt)
        return result.scalar_one_or_none()

    async def update_payment_status(self, payment: Payment, status: str) -> Payment:
        payment.status = status
        self.session.add(payment)
        await self.session.commit()
        await self.session.refresh(payment)
        return payment
