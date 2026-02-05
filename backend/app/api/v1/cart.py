# app/api/v1/cart.py

"""
Shopping cart endpoints
- Add / update / delete / list cart items
"""

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.database import get_session
from app.core.security import require_buyer
from app.models.cart import CartItem as CartItemModel
from app.models.animal import Animal as AnimalModel
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartItemRead

router = APIRouter(prefix="/cart", tags=["Cart"])

def _get_user_id(user: Any) -> int:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    uid = getattr(user, "id", None)
    if uid:
        return int(uid)
    if isinstance(user, dict):
        sub = user.get("sub")
        if sub is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        try:
            return int(sub)
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user id in token")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unable to determine user id")

@router.get("/", response_model=List[CartItemRead])
async def list_cart(user=Depends(require_buyer), db: AsyncSession = Depends(get_session)):
    buyer_id = _get_user_id(user)
    stmt = select(CartItemModel).where(CartItemModel.buyer_id == buyer_id)
    result = await db.exec(stmt)
    items = result.scalars().all()
    return [CartItemRead.from_orm(i) for i in items]

@router.post("/", response_model=CartItemRead, status_code=status.HTTP_201_CREATED)
async def add_to_cart(payload: CartItemCreate, user=Depends(require_buyer), db: AsyncSession = Depends(get_session)):
    buyer_id = _get_user_id(user)
    stmt = select(AnimalModel).where(AnimalModel.id == payload.animal_id)
    res = await db.exec(stmt)
    animal = res.scalar_one_or_none()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    if not animal.available:
        raise HTTPException(status_code=400, detail="Animal not available")

    stmt = select(CartItemModel).where(
        (CartItemModel.buyer_id == buyer_id) & (CartItemModel.animal_id == payload.animal_id)
    )
    res = await db.exec(stmt)
    existing = res.scalar_one_or_none()
    if existing:
        existing.quantity += payload.quantity
        existing.price = float(animal.price)
        db.add(existing)
        await db.commit()
        await db.refresh(existing)
        return CartItemRead.from_orm(existing)

    cart_item = CartItemModel(
        buyer_id=buyer_id,
        animal_id=payload.animal_id,
        quantity=payload.quantity,
        price=float(animal.price),
    )
    db.add(cart_item)
    await db.commit()
    await db.refresh(cart_item)
    return CartItemRead.from_orm(cart_item)
