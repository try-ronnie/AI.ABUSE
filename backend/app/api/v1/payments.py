# app/api/v1/payments.py

"""
Payment endpoints
- Process payments for orders
- Track payment status
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_session
from app.core.security import require_buyer
from app.models.payment import Payment
from app.models.order import Order
from app.services.payment_service import PaymentService
from app.schemas.payment import PaymentCreate, PaymentRead, PaymentUpdate

router = APIRouter(prefix="/payments", tags=["Payments"])


def get_user_id(user) -> int:
    user_id = getattr(user, "id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    return user_id


@router.post("/", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payload: PaymentCreate,
    db: AsyncSession = Depends(get_session),
    user=Depends(require_buyer)
):
    """Create a new payment for an order"""
    buyer_id = get_user_id(user)
    
    # Verify the order belongs to the user
    order = await db.get(Order, payload.order_id)
    if not order or order.buyer_id != buyer_id:
        raise HTTPException(status_code=404, detail="Order not found or not yours")
    
    if order.is_paid:
        raise HTTPException(status_code=400, detail="Order already paid")
    
    service = PaymentService(db)
    payment = await service.create_payment(
        order_id=payload.order_id,
        amount=float(payload.amount),
        method=payload.method
    )
    return payment


@router.get("/", response_model=List[PaymentRead])
async def list_payments(
    db: AsyncSession = Depends(get_session),
    user=Depends(require_buyer)
):
    """List all payments for the current user's orders"""
    buyer_id = get_user_id(user)
    
    # Get user's orders first
    order_stmt = select(Order.id).where(Order.buyer_id == buyer_id)
    order_result = await db.execute(order_stmt)
    order_ids = [row[0] for row in order_result.fetchall()]
    
    if not order_ids:
        return []
    
    # Get payments for those orders
    stmt = select(Payment).where(Payment.order_id.in_(order_ids))
    result = await db.execute(stmt)
    payments = result.scalars().all()
    return payments


@router.get("/{payment_id}", response_model=PaymentRead)
async def get_payment(
    payment_id: int,
    db: AsyncSession = Depends(get_session),
    user=Depends(require_buyer)
):
    """Get a specific payment by ID"""
    buyer_id = get_user_id(user)
    
    payment = await db.get(Payment, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Verify the payment belongs to user's order
    order = await db.get(Order, payment.order_id)
    if not order or order.buyer_id != buyer_id:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return payment


@router.patch("/{payment_id}", response_model=PaymentRead)
async def update_payment(
    payment_id: int,
    payload: PaymentUpdate,
    db: AsyncSession = Depends(get_session),
    user=Depends(require_buyer)
):
    """Update a payment status"""
    buyer_id = get_user_id(user)
    
    payment = await db.get(Payment, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Verify the payment belongs to user's order
    order = await db.get(Order, payment.order_id)
    if not order or order.buyer_id != buyer_id:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    service = PaymentService(db)
    if payload.status:
        payment = await service.update_payment_status(payment, payload.status)
        
        # If payment completed, mark order as paid
        if payload.status == "completed":
            order.is_paid = True
            order.status = "paid"
            db.add(order)
            await db.commit()
    
    return payment


@router.post("/{payment_id}/complete", response_model=PaymentRead)
async def complete_payment(
    payment_id: int,
    db: AsyncSession = Depends(get_session),
    user=Depends(require_buyer)
):
    """Mark a payment as completed"""
    buyer_id = get_user_id(user)
    
    payment = await db.get(Payment, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Verify the payment belongs to user's order
    order = await db.get(Order, payment.order_id)
    if not order or order.buyer_id != buyer_id:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    service = PaymentService(db)
    payment = await service.complete_payment(payment)
    return payment
