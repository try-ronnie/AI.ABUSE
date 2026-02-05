# app/services/payment_service.py

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.payment import Payment
from app.models.order import Order


class PaymentService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_payment(
        self,
        order_id: int,
        amount: float,
        method: str = "mpesa"
    ) -> Payment:
        """Create a new payment for an order"""
        order = await self.session.get(Order, order_id)
        if not order:
            raise ValueError("Order not found")
        
        payment = Payment(
            order_id=order_id,
            amount=amount,
            status="pending",
            method=method
        )
        self.session.add(payment)
        await self.session.commit()
        await self.session.refresh(payment)
        return payment

    async def get_payment(self, payment_id: int) -> Optional[Payment]:
        """Get a payment by ID"""
        return await self.session.get(Payment, payment_id)

    async def get_payment_by_order(self, order_id: int) -> Optional[Payment]:
        """Get payment for a specific order"""
        stmt = select(Payment).where(Payment.order_id == order_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_payments(self) -> List[Payment]:
        """List all payments"""
        stmt = select(Payment)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_payment_status(self, payment: Payment, status: str) -> Payment:
        """Update payment status"""
        payment.status = status
        self.session.add(payment)
        await self.session.commit()
        await self.session.refresh(payment)
        return payment

    async def complete_payment(self, payment: Payment) -> Payment:
        """Mark payment as completed and update order"""
        payment.status = "completed"
        self.session.add(payment)
        
        # Also mark the order as paid
        order = await self.session.get(Order, payment.order_id)
        if order:
            order.is_paid = True
            order.status = "paid"
            self.session.add(order)
        
        await self.session.commit()
        await self.session.refresh(payment)
        return payment

    async def pay_order(self, order_id: int, amount: float) -> Payment:
        """Create and complete a payment for an order (legacy method)"""
        order = await self.session.get(Order, order_id)
        if not order:
            raise ValueError("Order not found")
        
        payment = Payment(
            order_id=order_id,
            amount=amount,
            status="completed",
            method="mpesa"
        )
        order.is_paid = True
        order.status = "paid"
        
        self.session.add(order)
        self.session.add(payment)
        await self.session.commit()
        await self.session.refresh(payment)
        return payment
