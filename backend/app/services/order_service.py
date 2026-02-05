from typing import List, Optional
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderItem
from app.models.cart import CartItem
from app.models.animal import Animal


class OrderService:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ----------------------------
    # Fetch single order
    # ----------------------------
    async def get_order(self, order_id: int) -> Optional[Order]:
        return await self.session.get(Order, order_id)

    # ----------------------------
    # List orders for a buyer
    # ----------------------------
    async def list_orders(self, buyer_id: int) -> List[Order]:
        stmt = select(Order).where(Order.buyer_id == buyer_id)
        result = await self.session.exec(stmt)
        return result.scalars().all()

    # ----------------------------
    # Checkout: create order from cart
    # ----------------------------
    async def checkout(self, buyer_id: int) -> Order:
        # Fetch cart items
        stmt = select(CartItem).where(CartItem.buyer_id == buyer_id)
        result = await self.session.exec(stmt)
        cart_items = result.scalars().all()

        if not cart_items:
            raise ValueError("Cart is empty")

        # Create order
        order = Order(buyer_id=buyer_id, status="pending", is_paid=False, total_price=0.0)
        self.session.add(order)
        await self.session.flush()  # get order.id without commit

        total_price = 0.0
        order_items: List[OrderItem] = []

        for item in cart_items:
            animal = await self.session.get(Animal, item.animal_id)
            if not animal or not animal.available:
                raise ValueError(f"Animal {item.animal_id} is not available")

            price = animal.price * item.quantity
            total_price += price

            order_item = OrderItem(
                order_id=order.id,
                animal_id=item.animal_id,
                quantity=item.quantity,
                price=animal.price,
            )
            order_items.append(order_item)

            # Mark animal as unavailable
            animal.available = False
            self.session.add(animal)

        order.total_price = total_price
        self.session.add_all(order_items)

        # Clear buyer's cart
        for item in cart_items:
            await self.session.delete(item)

        await self.session.commit()
        await self.session.refresh(order)
        return order

    # ----------------------------
    # Update order status / payment
    # ----------------------------
    async def update_order(
        self,
        order: Order,
        status: Optional[str] = None,
        is_paid: Optional[bool] = None,
        total_price: Optional[float] = None,
    ) -> Order:
        if status is not None:
            order.status = status
        if is_paid is not None:
            order.is_paid = is_paid
        if total_price is not None:
            order.total_price = total_price

        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order)
        return order

"""
OrderService

Responsibilities:
- Handle all business logic related to Orders & OrderItems
- Interact with the database using AsyncSession
- Operate on models: Order, OrderItem, Animal, CartItem
- Keep service layer focused on DB/business logic; no FastAPI routing here
"""
