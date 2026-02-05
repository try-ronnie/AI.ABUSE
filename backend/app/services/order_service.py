# app/services/order_service.py

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.order import Order, OrderItem
from app.models.cart import CartItem
from app.models.animal import Animal

class OrderService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def checkout(self, buyer_id: int) -> Order:
        cart_items_stmt = CartItem.__table__.select().where(CartItem.buyer_id == buyer_id)
        result = await self.session.execute(cart_items_stmt)
        cart_items = result.scalars().all()
        if not cart_items:
            raise ValueError("Cart empty")
        order = Order(buyer_id=buyer_id, status="pending", is_paid=False, total_price=0.0)
        self.session.add(order)
        await self.session.flush()
        total_price = 0.0
        for item in cart_items:
            animal = await self.session.get(Animal, item.animal_id)
            order_item = OrderItem(order_id=order.id, animal_id=item.animal_id, quantity=item.quantity, price=animal.price)
            total_price += animal.price * item.quantity
            animal.available = False
            self.session.add(animal)
            self.session.add(order_item)
            await self.session.delete(item)
        order.total_price = total_price
        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order)
        return order
