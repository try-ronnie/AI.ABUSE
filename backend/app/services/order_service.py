# app/services/order_service.py

from typing import List, Optional
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderItem
from app.models.cart import CartItem
from app.models.animal import Animal
from app.schemas.order import OrderCreate, OrderUpdate


class OrderService:
    """
    Service layer for handling orders, checkout, and order items.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    # -----------------------------
    # Create / Checkout
    # -----------------------------
    async def checkout(self, buyer_id: int) -> Optional[Order]:
        """
        Converts a buyer's cart into an order with order items.
        Marks animals as unavailable if one-off sale.
        Clears cart items after checkout.
        """
        # Fetch cart items
        stmt = select(CartItem).where(CartItem.buyer_id == buyer_id)
        result = await self.session.exec(stmt)
        cart_items = result.scalars().all()

        if not cart_items:
            return None

        # Create Order
        order = Order(buyer_id=buyer_id, status="pending", is_paid=False, total_price=0.0)
        self.session.add(order)
        await self.session.flush()  # assign order.id

        total_price = 0.0
        order_items: List[OrderItem] = []

        for item in cart_items:
            animal = await self.session.get(Animal, item.animal_id)
            if not animal or not animal.available:
                continue  # skip unavailable items

            price = animal.price * item.quantity
            total_price += price

            order_item = OrderItem(
                order_id=order.id,
                animal_id=item.animal_id,
                quantity=item.quantity,
                price=animal.price,
            )
            order_items.append(order_item)

            # Mark animal unavailable for one-off sale
            animal.available = False
            self.session.add(animal)

        order.total_price = total_price
        self.session.add_all(order_items)

        # Clear cart
        for item in cart_items:
            await self.session.delete(item)

        await self.session.commit()
        await self.session.refresh(order)
        return order

    # -----------------------------
    # Fetch
    # -----------------------------
    async def get_order(self, order_id: int) -> Optional[Order]:
        stmt = select(Order).where(Order.id == order_id)
        result = await self.session.exec(stmt)
        return result.scalar_one_or_none()

    async def list_orders_for_buyer(self, buyer_id: int) -> List[Order]:
        stmt = select(Order).where(Order.buyer_id == buyer_id)
        result = await self.session.exec(stmt)
        return result.scalars().all()

    # -----------------------------
    # Update
    # -----------------------------
    async def update_order(self, order: Order, updates: OrderUpdate) -> Order:
        update_data = updates.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(order, key, value)
        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order)
        return order
