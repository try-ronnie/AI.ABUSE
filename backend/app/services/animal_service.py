# app/services/animal_service.py

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.animal import Animal


class AnimalService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, animal_id: int) -> Optional[Animal]:
        return await self.session.get(Animal, animal_id)

    async def list(self, available_only: bool = True) -> List[Animal]:
        stmt = select(Animal)
        if available_only:
            stmt = stmt.where(Animal.available == True)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, data: dict) -> Animal:
        animal = Animal(**data)
        self.session.add(animal)
        await self.session.commit()
        await self.session.refresh(animal)
        return animal

    async def update(self, animal: Animal, updates: dict) -> Animal:
        for key, value in updates.items():
            setattr(animal, key, value)
        self.session.add(animal)
        await self.session.commit()
        await self.session.refresh(animal)
        return animal

    async def delete(self, animal: Animal):
        await self.session.delete(animal)
        await self.session.commit()
