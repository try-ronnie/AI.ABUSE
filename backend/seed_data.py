#!/usr/bin/env python3
"""
Seed script to add test users and animals to the database
"""

import asyncio
import sys
sys.path.insert(0, '/home/ronnie-gikondi/AI.PHASE.5/backend')

from app.core.database import init_db, async_session
from app.core.security import hash_password
from sqlalchemy import text

# Import all models to avoid relationship issues
import app.models.user
import app.models.animal
import app.models.order
import app.models.cart
import app.models.payment
from app.models.user import User, Farmer
from app.models.animal import Animal


async def seed_data():
    """Create test users and animals"""
    await init_db()
    
    async with async_session() as session:
        # Check if users exist
        stmt = text("SELECT COUNT(*) FROM users")
        result = await session.execute(stmt)
        count = result.scalar()
        
        if count > 0:
            print("Data already exists, clearing and recreating...")
            # Clear existing data in reverse order of dependencies
            await session.execute(text("DELETE FROM cart_items"))
            await session.execute(text("DELETE FROM order_items"))
            await session.execute(text("DELETE FROM orders"))
            await session.execute(text("DELETE FROM payments"))
            await session.execute(text("DELETE FROM animals"))
            await session.execute(text("DELETE FROM farmers"))
            await session.execute(text("DELETE FROM users"))
            await session.commit()
        
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
        
        # Create second farmer
        farmer2 = User(
            name="Jane Farmer",
            email="farmer2@test.com",
            password_hash=hash_password("password123"),
            role="farmer"
        )
        session.add(farmer2)
        await session.flush()
        
        farmer2_profile = Farmer(
            user_id=farmer2.id,
            farm_name="Sunrise Ranch",
            phone="555-0456",
            location="Oregon",
            bio="Poultry and pig specialist"
        )
        session.add(farmer2_profile)
        
        # Create test buyer
        buyer = User(
            name="Jane Buyer",
            email="buyer@test.com",
            password_hash=hash_password("password123"),
            role="user"
        )
        session.add(buyer)
        
        # Create second buyer
        buyer2 = User(
            name="Bob Buyer",
            email="buyer2@test.com",
            password_hash=hash_password("password123"),
            role="user"
        )
        session.add(buyer2)
        
        await session.commit()
        
        # Create animals for farmer1
        animals = [
            Animal(
                name="Premium Angus Cattle",
                species="Cattle",
                breed="Angus",
                age=24,
                gender="male",
                price=2800.0,
                available=True,
                farmer_id=farmer.id,
                description="High-quality Angus cattle, grass-fed, ready for slaughter"
            ),
            Animal(
                name="Grassland Highlands Sheep",
                species="Sheep",
                breed="Highland",
                age=12,
                gender="female",
                price=550.0,
                available=True,
                farmer_id=farmer.id,
                description="Healthy Highland sheep, good for wool and meat"
            ),
            Animal(
                name="Holstein Dairy Cows",
                species="Cattle",
                breed="Holstein",
                age=36,
                gender="female",
                price=3500.0,
                available=True,
                farmer_id=farmer.id,
                description="Excellent dairy cows, proven milk production"
            ),
            Animal(
                name="Merino Wool Sheep",
                species="Sheep",
                breed="Merino",
                age=18,
                gender="female",
                price=750.0,
                available=True,
                farmer_id=farmer.id,
                description="Premium wool sheep, high-quality fleece"
            ),
            # Animals for farmer2
            Animal(
                name="British Blue Chickens",
                species="Poultry",
                breed="British Blue",
                age=2,
                gender="female",
                price=25.0,
                available=True,
                farmer_id=farmer2.id,
                description="Healthy layer birds, brown eggs"
            ),
            Animal(
                name="Rhode Island Reds",
                species="Poultry",
                breed="Rhode Island Red",
                age=3,
                gender="female",
                price=20.0,
                available=True,
                farmer_id=farmer2.id,
                description="Prolific egg layers, friendly temperament"
            ),
            Animal(
                name="Berkshire Pigs",
                species="Pigs",
                breed="Berkshire",
                age=8,
                gender="male",
                price=450.0,
                available=True,
                farmer_id=farmer2.id,
                description="Quality pork breed, excellent marbling"
            ),
            Animal(
                name="Large Black Pigs",
                species="Pigs",
                breed="Large Black",
                age=10,
                gender="female",
                price=550.0,
                available=True,
                farmer_id=farmer2.id,
                description="Docile breed, good for free-range farming"
            ),
        ]
        
        for animal in animals:
            session.add(animal)
        
        await session.commit()
        
        print("✅ Seed data created successfully!")
        print("\n📋 Test Accounts:")
        print("  👨‍🌾 Farmer: farmer@test.com / password123")
        print("  👨‍🌾 Farmer 2: farmer2@test.com / password123")
        print("  🛒 Buyer: buyer@test.com / password123")
        print("  🛒 Buyer 2: buyer2@test.com / password123")
        print(f"\n🐄 Created {len(animals)} animals across 2 farmers")


if __name__ == "__main__":
    asyncio.run(seed_data())
