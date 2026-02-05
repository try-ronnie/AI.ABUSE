# app/services/payment_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.payment import Payment
from app.models.order import Order

class PaymentService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def pay_order(self, order_id: int, amount: float) -> Payment:
        order = await self.session.get(Order, order_id)
        if not order:
            raise ValueError("Order not found")
        payment = Payment(order_id=order_id, amount=amount, status="completed")
        order.is_paid = True
        self.session.add(order)
        self.session.add(payment)
        await self.session.commit()
        await self.session.refresh(payment)
        return payment
