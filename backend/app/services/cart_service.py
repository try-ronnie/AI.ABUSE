# app/services/cart_service.py

from typing import Optional, List
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.cart import CartItem
from app.models.animal import Animal

class CartService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_cart(self, buyer_id: int) -> List[CartItem]:
        stmt = select(CartItem).where(CartItem.buyer_id == buyer_id)
        result = await self.session.exec(stmt)
        return result.scalars().all()

    async def add_item(self, buyer_id: int, animal_id: int, quantity: int) -> CartItem:
        stmt = select(CartItem).where((CartItem.buyer_id == buyer_id) & (CartItem.animal_id == animal_id))
        res = await self.session.exec(stmt)
        existing = res.scalar_one_or_none()
        animal = await self.session.get(Animal, animal_id)
        if existing:
            existing.quantity += quantity
            existing.price = float(animal.price)
            self.session.add(existing)
            await self.session.commit()
            await self.session.refresh(existing)
            return existing
        cart_item = CartItem(buyer_id=buyer_id, animal_id=animal_id, quantity=quantity, price=float(animal.price))
        self.session.add(cart_item)
        await self.session.commit()
        await self.session.refresh(cart_item)
        return cart_item
