# app/services/cart_service.py

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.cart import CartItem
from app.models.animal import Animal


class CartService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_cart(self, buyer_id: int) -> List[CartItem]:
        stmt = select(CartItem).where(CartItem.buyer_id == buyer_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add_item(self, buyer_id: int, animal_id: int, quantity: int) -> CartItem:
        stmt = select(CartItem).where(
            (CartItem.buyer_id == buyer_id) & (CartItem.animal_id == animal_id)
        )
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()
        
        animal = await self.session.get(Animal, animal_id)
        if not animal:
            raise ValueError("Animal not found")
        
        if existing:
            existing.quantity += quantity
            existing.price = float(animal.price)
            self.session.add(existing)
            await self.session.commit()
            await self.session.refresh(existing)
            return existing
        
        cart_item = CartItem(
            buyer_id=buyer_id,
            animal_id=animal_id,
            quantity=quantity,
            price=float(animal.price)
        )
        self.session.add(cart_item)
        await self.session.commit()
        await self.session.refresh(cart_item)
        return cart_item

    async def update_item(self, cart_item: CartItem, quantity: int) -> CartItem:
        cart_item.quantity = quantity
        self.session.add(cart_item)
        await self.session.commit()
        await self.session.refresh(cart_item)
        return cart_item

    async def remove_item(self, cart_item: CartItem):
        await self.session.delete(cart_item)
        await self.session.commit()

    async def clear_cart(self, buyer_id: int):
        stmt = select(CartItem).where(CartItem.buyer_id == buyer_id)
        result = await self.session.execute(stmt)
        items = result.scalars().all()
        for item in items:
            await self.session.delete(item)
        await self.session.commit()

    async def get_item(self, item_id: int) -> Optional[CartItem]:
        return await self.session.get(CartItem, item_id)
