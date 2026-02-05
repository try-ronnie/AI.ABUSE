#!/usr/bin/env python3
"""
Seed script to add test users to the database
"""

import asyncio
import sys
sys.path.insert(0, '/home/ronnie-gikondi/AI.PHASE.5/backend')

from app.core.database import init_db, async_session
from app.core.security import hash_password
from sqlalchemy import select

# Import all models to avoid relationship issues
import app.models.user
import app.models.animal
import app.models.order
import app.models.cart
import app.models.payment
from app.models.user import User, Farmer


async def seed_users():
    """Create test users"""
    await init_db()
    
    async with async_session() as session:
        # Check if users exist
        stmt = select(User)
        result = await session.execute(stmt)
        existing = result.scalars().first()
        if existing:
            print("Users already exist, skipping seed")
            return
        
        # Create test farmer
        farmer = User(
            name="John Farmer",
            email="farmer@test.com",
            password_hash=hash_password("password123"),
            role="farmer"
        )
        session.add(farmer)
        await session.flush()
        
        farmer_profile = Farmer(
            user_id=farmer.id,
            farm_name="Green Valley Farm",
            phone="555-0123",
            location="Montana",
            bio="Organic cattle and sheep farm"
        )
        session.add(farmer_profile)
        
        # Create test buyer
        buyer = User(
            name="Jane Buyer",
            email="buyer@test.com",
            password_hash=hash_password("password123"),
            role="user"
        )
        session.add(buyer)
        
        await session.commit()
        print("Test users created!")
        print("  Farmer: farmer@test.com / password123")
        print("  Buyer: buyer@test.com / password123")


if __name__ == "__main__":
    asyncio.run(seed_users())
