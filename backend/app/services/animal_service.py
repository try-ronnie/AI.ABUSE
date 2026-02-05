# app/services/animal_service.py

from typing import List, Optional, Union
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.animal import Animal
from app.schemas.animal import AnimalCreate, AnimalUpdate


class AnimalService:
    """
    Service layer for Animal CRUD operations.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    # -----------------------------
    # Fetch
    # -----------------------------
    async def get_animal(self, animal_id: int) -> Optional[Animal]:
        """
        Retrieve a single animal by ID.
        Returns None if not found.
        """
        stmt = select(Animal).where(Animal.id == animal_id)
        result = await self.session.exec(stmt)
        return result.scalar_one_or_none()

    async def list_animals(self, available_only: bool = True) -> List[Animal]:
        """
        List all animals. Optionally filter by availability.
        """
        stmt = select(Animal)
        if available_only:
            stmt = stmt.where(Animal.available == True)
        result = await self.session.exec(stmt)
        return result.scalars().all()

    # -----------------------------
    # Create
    # -----------------------------
    async def create_animal(self, animal_data: AnimalCreate) -> Animal:
        """
        Create a new animal from AnimalCreate schema.
        """
        animal = Animal(**animal_data.model_dump())  # SQLModel-friendly
        self.session.add(animal)
        await self.session.commit()
        await self.session.refresh(animal)
        return animal

    # -----------------------------
    # Update
    # -----------------------------
    async def update_animal(self, animal: Animal, updates: AnimalUpdate) -> Animal:
        """
        Update an existing animal with AnimalUpdate schema.
        Only fields provided in the schema are updated.
        """
        update_data = updates.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(animal, key, value)
        self.session.add(animal)
        await self.session.commit()
        await self.session.refresh(animal)
        return animal

    # -----------------------------
    # Delete
    # -----------------------------
    async def delete_animal(self, animal: Animal):
        """
        Delete an animal from the database.
        """
        await self.session.delete(animal)
        await self.session.commit()
