# app/services/payment_service.py
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.payment import Payment

class PaymentService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_payment(self, payment_data: Dict[str, Any]) -> Payment:
        payment = Payment(**payment_data)
        self.session.add(payment)
        await self.session.commit()
        await self.session.refresh(payment)
        return payment

    async def get_payment(self, payment_id: int) -> Payment:
        return await self.session.get(Payment, payment_id)
