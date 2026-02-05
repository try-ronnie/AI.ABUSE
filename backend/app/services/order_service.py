# app/services/order_service.py

from typing import List
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderItem
from app.models.cart import CartItem
from app.models.animal import Animal
from app.schemas.order import OrderCreate, OrderUpdate


class OrderService:
    """
    Service layer for handling Orders and OrderItems
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    # -----------------------------
    # Checkout cart into an order
    # -----------------------------
    async def checkout_cart(self, buyer_id: int) -> Order:
        # Fetch cart items
        stmt = select(CartItem).where(CartItem.buyer_id == buyer_id)
        result = await self.session.exec(stmt)
        cart_items = result.scalars().all()

        if not cart_items:
            raise ValueError("Cart is empty")

        order = Order(
            buyer_id=buyer_id,
            status="pending",
            is_paid=False,
            total_price=0.0,
        )
        self.session.add(order)
        await self.session.flush()  # populate order.id

        total_price = 0.0
        order_items: List[OrderItem] = []

        for item in cart_items:
            animal = await self.session.get(Animal, item.animal_id)
            if not animal or not animal.available:
                raise ValueError(f"Animal {item.animal_id} is no longer available")

            total_price += animal.price * item.quantity

            order_item = OrderItem(
                order_id=order.id,
                animal_id=item.animal_id,
                quantity=item.quantity,
                price=float(animal.price),
            )
            order_items.append(order_item)

            # Optionally mark animal unavailable
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
    # List all orders for a buyer
    # -----------------------------
    async def list_orders(self, buyer_id: int) -> List[Order]:
        stmt = select(Order).where(Order.buyer_id == buyer_id)
        result = await self.session.exec(stmt)
        return result.scalars().all()
