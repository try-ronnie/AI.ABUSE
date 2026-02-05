from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.security import require_buyer
from app.models.order import Order

router = APIRouter(prefix="/payments", tags=["Payments"])


# ----------------------------
# Helpers
# ----------------------------
def get_user_id(user) -> int:
    user_id = getattr(user, "id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    return user_id


# ----------------------------
# Routes
# ----------------------------
@router.post("/{order_id}", summary="Pay for an order")
async def pay_for_order(
    order_id: int,
    user=Depends(require_buyer),
    session: AsyncSession = Depends(get_session),
):
    buyer_id = get_user_id(user)

    stmt = select(Order).where(Order.id == order_id)
    result = await session.exec(stmt)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.buyer_id != buyer_id:
        raise HTTPException(status_code=403, detail="Not allowed to pay for this order")

    if order.is_paid:
        raise HTTPException(status_code=400, detail="Order already paid")

    # ---- Simulated payment success ----
    order.is_paid = True
    order.status = "paid"

    session.add(order)
    await session.commit()
    await session.refresh(order)

    return {
        "message": "Payment successful",
        "order_id": order.id,
        "amount_paid": order.total_price,
        "status": order.status,
    }
