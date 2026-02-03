from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.cart import CartItem
from app.models.animal import Animal
from app.models.user import User
from app.core.dependencies import require_buyer, get_session
from app.schemas.cart import CartItemCreate, CartItemRead, CartItemUpdate

router = APIRouter(prefix="/cart", tags=["cart"])


def _get_user_id(user: User | dict) -> int:
    """Extract buyer ID from DB User or token payload dict"""
    if hasattr(user, "id"):
        return user.id
    if isinstance(user, dict) and "sub" in user:
        return int(user["sub"])
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")


@router.get("/", response_model=List[CartItemRead])
async def list_cart_items(user=Depends(require_buyer), db: AsyncSession = Depends(get_session)):
    """List all items in the buyer's cart"""
    buyer_id = _get_user_id(user)
    result = await db.execute(select(CartItem).where(CartItem.buyer_id == buyer_id))
    items = result.scalars().all()
    return items


@router.post("/", response_model=CartItemRead, status_code=status.HTTP_201_CREATED)
async def add_cart_item(payload: CartItemCreate, user=Depends(require_buyer), db: AsyncSession = Depends(get_session)):
    """Add an item to the buyer's cart"""
    buyer_id = _get_user_id(user)

    # Verify animal exists and is available
    result = await db.execute(select(Animal).where(Animal.id == payload.animal_id))
    animal = result.scalar_one_or_none()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    if not animal.available:
        raise HTTPException(status_code=400, detail="Animal is not available")

    # Merge if already in cart
    result = await db.execute(
        select(CartItem).where(CartItem.buyer_id == buyer_id, CartItem.animal_id == payload.animal_id)
    )
    existing = result.scalar_one_or_none()
    if existing:
        existing.quantity += payload.quantity
        existing.price = float(animal.price)
        db.add(existing)
        await db.commit()
        await db.refresh(existing)
        return existing

    # Create new cart item
    item = CartItem(buyer_id=buyer_id, animal_id=payload.animal_id, quantity=payload.quantity, price=float(animal.price))
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.patch("/{item_id}", response_model=CartItemRead)
async def update_cart_item(item_id: int, payload: CartItemUpdate, user=Depends(require_buyer), db: AsyncSession = Depends(get_session)):
    """Update quantity or price of a cart item"""
    buyer_id = _get_user_id(user)
    result = await db.execute(select(CartItem).where(CartItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    if item.buyer_id != buyer_id:
        raise HTTPException(status_code=403, detail="Not allowed")

    if payload.quantity is not None:
        item.quantity = payload.quantity
    if payload.price is not None:
        item.price = payload.price

    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cart_item(item_id: int, user=Depends(require_buyer), db: AsyncSession = Depends(get_session)):
    """Remove a cart item"""
    buyer_id = _get_user_id(user)
    result = await db.execute(select(CartItem).where(CartItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    if item.buyer_id != buyer_id:
        raise HTTPException(status_code=403, detail="Not allowed")

    await db.delete(item)
    await db.commit()
