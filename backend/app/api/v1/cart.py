# app/api/v1/cart.py

"""
Shopping cart endpoints
- Add / update / delete / list cart items
"""

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

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
    """List all items in the current user's cart"""
    buyer_id = _get_user_id(user)
    stmt = select(CartItemModel).where(CartItemModel.buyer_id == buyer_id)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return [CartItemRead.model_validate(i) for i in items]


@router.post("/", response_model=CartItemRead, status_code=status.HTTP_201_CREATED)
async def add_to_cart(payload: CartItemCreate, user=Depends(require_buyer), db: AsyncSession = Depends(get_session)):
    """Add an item to the cart"""
    buyer_id = _get_user_id(user)
    
    # Check if animal exists and is available
    stmt = select(AnimalModel).where(AnimalModel.id == payload.animal_id)
    result = await db.execute(stmt)
    animal = result.scalar_one_or_none()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    if not animal.available:
        raise HTTPException(status_code=400, detail="Animal not available")

    # Check if item already in cart
    stmt = select(CartItemModel).where(
        (CartItemModel.buyer_id == buyer_id) & (CartItemModel.animal_id == payload.animal_id)
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        existing.quantity += payload.quantity
        existing.price = float(animal.price)
        db.add(existing)
        await db.commit()
        await db.refresh(existing)
        return CartItemRead.model_validate(existing)

    cart_item = CartItemModel(
        buyer_id=buyer_id,
        animal_id=payload.animal_id,
        quantity=payload.quantity,
        price=float(animal.price),
    )
    db.add(cart_item)
    await db.commit()
    await db.refresh(cart_item)
    return CartItemRead.model_validate(cart_item)


@router.patch("/{item_id}", response_model=CartItemRead)
async def update_cart_item(
    item_id: int,
    payload: CartItemUpdate,
    user=Depends(require_buyer),
    db: AsyncSession = Depends(get_session)
):
    """Update a cart item quantity"""
    buyer_id = _get_user_id(user)
    
    cart_item = await db.get(CartItemModel, item_id)
    if not cart_item or cart_item.buyer_id != buyer_id:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    if payload.quantity is not None:
        cart_item.quantity = payload.quantity
    
    db.add(cart_item)
    await db.commit()
    await db.refresh(cart_item)
    return CartItemRead.model_validate(cart_item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_cart(
    item_id: int,
    user=Depends(require_buyer),
    db: AsyncSession = Depends(get_session)
):
    """Remove an item from the cart"""
    buyer_id = _get_user_id(user)
    
    cart_item = await db.get(CartItemModel, item_id)
    if not cart_item or cart_item.buyer_id != buyer_id:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    await db.delete(cart_item)
    await db.commit()


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(user=Depends(require_buyer), db: AsyncSession = Depends(get_session)):
    """Clear all items from the cart"""
    buyer_id = _get_user_id(user)
    
    stmt = select(CartItemModel).where(CartItemModel.buyer_id == buyer_id)
    result = await db.execute(stmt)
    items = result.scalars().all()
    
    for item in items:
        await db.delete(item)
    await db.commit()
