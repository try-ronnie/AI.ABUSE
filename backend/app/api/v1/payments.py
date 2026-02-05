"""
FastAPI routes for Payments

Responsibilities:
- Allow creation and update of payments
- Return payment info
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.security import require_buyer
from app.services.payment_service import PaymentService
from app.schemas.payment import PaymentCreate, PaymentRead, PaymentUpdate

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payload: PaymentCreate,
    db: AsyncSession = Depends(get_session),
    user=Depends(require_buyer)
):
    service = PaymentService(db)
    payment = await service.create_payment(
        order_id=payload.order_id,
        buyer_id=payload.buyer_id,
        amount=payload.amount,
        provider=payload.provider
    )
    return payment


@router.patch("/{payment_id}", response_model=PaymentRead)
async def update_payment(
    payment_id: int,
    payload: PaymentUpdate,
    db: AsyncSession = Depends(get_session),
    user=Depends(require_buyer)
):
    service = PaymentService(db)
    payment = await service.get_payment(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payload.status:
        payment = await service.update_payment_status(payment, payload.status)
    return payment


@router.get("/", response_model=List[PaymentRead])
async def list_payments(db: AsyncSession = Depends(get_session), user=Depends(require_buyer)):
    service = PaymentService(db)
    stmt = await db.exec(select(Payment))
    payments = stmt.scalars().all()
    return payments
