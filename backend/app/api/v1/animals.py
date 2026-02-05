# app/api/v1/payments.py

"""
Payment endpoints
- Process payments for orders
- Track payment status
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.database import get_session
from app.core.security import require_buyer
from app.models.payment import Payment
from app.models.order import Order
from app.schemas.payment import PaymentCreate, PaymentRead

router = APIRouter(prefix="/payments", tags=["Payments"])

def get_user_id(user) -> int:
    user_id = getattr(user, "id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    return user_id

@router.post("/", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
async def make_payment(payload: PaymentCreate, user=Depends(require_buyer), db: AsyncSession = Depends(get_session)):
    buyer_id = get_user_id(user)
    order = await db.get(Order, payload.order_id)
    if not order or order.buyer_id != buyer_id:
        raise HTTPException(status_code=404, detail="Order not found or not yours")
    payment = Payment(order_id=order.id, amount=payload.amount, status="completed")
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    order.is_paid = True
    db.add(order)
    await db.commit()
    return payment
