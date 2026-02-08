# app/services/order_service.py

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.order import Order, OrderItem
from app.models.cart import CartItem
from app.models.animal import Animal


class OrderService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def checkout(self, buyer_id: int) -> Order:
        """Create an order from cart items"""
        stmt = select(CartItem).where(CartItem.buyer_id == buyer_id)
        result = await self.session.execute(stmt)
        cart_items = result.scalars().all()
        
        if not cart_items:
            raise ValueError("Cart is empty")
        
        order = Order(buyer_id=buyer_id, status="pending", is_paid=False, total_price=0.0)
        self.session.add(order)
        await self.session.flush()
        
        total_price = 0.0
        for item in cart_items:
            animal = await self.session.get(Animal, item.animal_id)
            if not animal or not animal.available:
                raise ValueError(f"Animal {item.animal_id} not available")
            
            order_item = OrderItem(
                order_id=order.id,
                animal_id=item.animal_id,
                quantity=item.quantity,
                price=animal.price
            )
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

    async def get_order(self, order_id: int) -> Optional[Order]:
        return await self.session.get(Order, order_id)

    async def list_orders(self, buyer_id: int) -> List[Order]:
        stmt = select(Order).where(Order.buyer_id == buyer_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_order_status(self, order: Order, status: str) -> Order:
        order.status = status
        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order)
        return order

    async def mark_as_paid(self, order: Order) -> Order:
        order.is_paid = True
        order.status = "paid"
        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order)
        return order

    async def list_farmer_orders(self, farmer_id: int) -> List[Order]:
        """Get all orders containing animals owned by this farmer"""
        # Join OrderItem -> Animal to get farmer_id, then get unique orders
        stmt = select(OrderItem).join(Animal).where(Animal.farmer_id == farmer_id)
        result = await self.session.execute(stmt)
        order_items = result.scalars().all()
        
        # Get unique order IDs
        order_ids = list(set([item.order_id for item in order_items]))
        if not order_ids:
            return []
        
        stmt = select(Order).where(Order.id.in_(order_ids))
        result = await self.session.execute(stmt)
        return result.scalars().all()
