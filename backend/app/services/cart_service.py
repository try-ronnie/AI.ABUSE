# app/services/cart_service.py

from typing import List, Optional
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cart import CartItem
from app.models.animal import Animal
from app.schemas.cart import CartItemCreate, CartItemUpdate


class CartService:
    """
    Service layer for handling buyer carts.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    # -----------------------------
    # List items
    # -----------------------------
    async def list_cart_items(self, buyer_id: int) -> List[CartItem]:
        stmt = select(CartItem).where(CartItem.buyer_id == buyer_id)
        result = await self.session.exec(stmt)
        return result.scalars().all()

    # -----------------------------
    # Add item
    # -----------------------------
    async def add_to_cart(self, buyer_id: int, payload: CartItemCreate) -> CartItem:
        # Fetch animal
        animal = await self.session.get(Animal, payload.animal_id)
        if not animal or not animal.available:
            raise ValueError("Animal not available")

        # Check existing cart
        stmt = select(CartItem).where(
            (CartItem.buyer_id == buyer_id) & (CartItem.animal_id == payload.animal_id)
        )
        result = await self.session.exec(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            existing.quantity += payload.quantity
            existing.price = float(animal.price)
            self.session.add(existing)
            await self.session.commit()
            await self.session.refresh(existing)
            return existing

        # New cart item
        cart_item = CartItem(
            buyer_id=buyer_id,
            animal_id=payload.animal_id,
            quantity=payload.quantity,
            price=float(animal.price),
        )
        self.session.add(cart_item)
        await self.session.commit()
        await self.session.refresh(cart_item)
        return cart_item

    # -----------------------------
    # Update item
    # -----------------------------
    async def update_cart_item(self, item: CartItem, payload: CartItemUpdate) -> CartItem:
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(item, key, value)
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    # -----------------------------
    # Remove item
    # -----------------------------
    async def remove_cart_item(self, item: CartItem):
        await self.session.delete(item)
        await self.session.commit()
