# app/api/v1/orders.py

"""
Order endpoints
- Checkout cart to order
- List buyer orders
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_session
from app.core.security import require_buyer
from app.models.cart import CartItem
from app.models.order import Order, OrderItem
from app.models.animal import Animal
from app.schemas.order import OrderRead

router = APIRouter(prefix="/orders", tags=["Orders"])


def get_user_id(user) -> int:
    user_id = getattr(user, "id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    return user_id


@router.post("/checkout", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def checkout(user=Depends(require_buyer), session: AsyncSession = Depends(get_session)):
    """Create an order from cart items"""
    buyer_id = get_user_id(user)
    
    stmt = select(CartItem).where(CartItem.buyer_id == buyer_id)
    result = await session.execute(stmt)
    cart_items = result.scalars().all()
    
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    order = Order(buyer_id=buyer_id, status="pending", is_paid=False, total_price=0.0)
    session.add(order)
    await session.flush()

    total_price = 0.0
    order_items: List[OrderItem] = []
    
    for item in cart_items:
        animal = await session.get(Animal, item.animal_id)
        if not animal or not animal.available:
            raise HTTPException(status_code=400, detail=f"Animal {item.animal_id} not available")
        
        price = animal.price * item.quantity
        total_price += price
        order_item = OrderItem(
            order_id=order.id,
            animal_id=item.animal_id,
            quantity=item.quantity,
            price=animal.price
        )
        order_items.append(order_item)
        animal.available = False
        session.add(animal)

    order.total_price = total_price
    session.add_all(order_items)

    for item in cart_items:
        await session.delete(item)

    await session.commit()
    await session.refresh(order)
    return order


@router.get("/", response_model=List[OrderRead])
async def list_my_orders(user=Depends(require_buyer), session: AsyncSession = Depends(get_session)):
    """List all orders for the current user"""
    buyer_id = get_user_id(user)
    stmt = select(Order).where(Order.buyer_id == buyer_id)
    result = await session.execute(stmt)
    orders = result.scalars().all()
    return orders


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(
    order_id: int,
    user=Depends(require_buyer),
    session: AsyncSession = Depends(get_session)
):
    """Get a specific order by ID"""
    buyer_id = get_user_id(user)
    
    order = await session.get(Order, order_id)
    if not order or order.buyer_id != buyer_id:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order
