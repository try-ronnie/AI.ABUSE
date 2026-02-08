# app/api/v1/animals.py

"""
Animal endpoints
- CRUD operations for farm animals
- Farmers can create/update/delete their animals
- Buyers can view available animals
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_session
from app.core.security import require_farmer, get_current_user
from app.models.animal import Animal
from app.models.user import User, Farmer
from app.schemas.animal import AnimalCreate, AnimalUpdate, AnimalRead

router = APIRouter(prefix="/animals", tags=["Animals"])


def get_user_id(user) -> int:
    user_id = getattr(user, "id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    return user_id


@router.get("/", response_model=List[AnimalRead])
async def list_animals(
    available_only: bool = Query(True, description="Filter by availability"),
    species: Optional[str] = Query(None, description="Filter by species"),
    breed: Optional[str] = Query(None, description="Filter by breed"),
    min_age: Optional[int] = Query(None, description="Minimum age in months"),
    max_age: Optional[int] = Query(None, description="Maximum age in months"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    db: AsyncSession = Depends(get_session)
):
    """List all animals with filtering options"""
    stmt = select(Animal)
    if available_only:
        stmt = stmt.where(Animal.available == True)
    if species:
        stmt = stmt.where(Animal.species == species)
    if breed:
        stmt = stmt.where(Animal.breed.ilike(f"%{breed}%"))
    if min_age is not None:
        stmt = stmt.where(Animal.age >= min_age)
    if max_age is not None:
        stmt = stmt.where(Animal.age <= max_age)
    if search:
        stmt = stmt.where(
            (Animal.name.ilike(f"%{search}%")) | 
            (Animal.description.ilike(f"%{search}%"))
        )
    result = await db.execute(stmt)
    animals = result.scalars().all()
    return animals


@router.get("/{animal_id}", response_model=AnimalRead)
async def get_animal(animal_id: int, db: AsyncSession = Depends(get_session)):
    """Get a single animal by ID (public endpoint)"""
    animal = await db.get(Animal, animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    return animal


@router.post("/", response_model=AnimalRead, status_code=status.HTTP_201_CREATED)
async def create_animal(
    payload: AnimalCreate,
    user=Depends(require_farmer),
    db: AsyncSession = Depends(get_session)
):
    """Create a new animal (farmer only)"""
    user_id = get_user_id(user)
    
    # Get farmer profile
    stmt = select(Farmer).where(Farmer.user_id == user_id)
    result = await db.execute(stmt)
    farmer = result.scalar_one_or_none()
    
    if not farmer:
        raise HTTPException(status_code=400, detail="Farmer profile not found")
    
    animal = Animal(
        name=payload.name,
        species=payload.species,
        breed=payload.breed,
        age=payload.age,
        gender=payload.gender,
        price=payload.price,
        available=payload.available if payload.available is not None else True,
        farmer_id=farmer.id
    )
    db.add(animal)
    await db.commit()
    await db.refresh(animal)
    return animal


@router.patch("/{animal_id}", response_model=AnimalRead)
async def update_animal(
    animal_id: int,
    payload: AnimalUpdate,
    user=Depends(require_farmer),
    db: AsyncSession = Depends(get_session)
):
    """Update an animal (farmer only, must own the animal)"""
    user_id = get_user_id(user)
    
    # Get farmer profile
    stmt = select(Farmer).where(Farmer.user_id == user_id)
    result = await db.execute(stmt)
    farmer = result.scalar_one_or_none()
    
    if not farmer:
        raise HTTPException(status_code=400, detail="Farmer profile not found")
    
    animal = await db.get(Animal, animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    if animal.farmer_id != farmer.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this animal")
    
    # Update only provided fields
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(animal, key, value)
    
    db.add(animal)
    await db.commit()
    await db.refresh(animal)
    return animal


@router.delete("/{animal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_animal(
    animal_id: int,
    user=Depends(require_farmer),
    db: AsyncSession = Depends(get_session)
):
    """Delete an animal (farmer only, must own the animal)"""
    user_id = get_user_id(user)
    
    # Get farmer profile
    stmt = select(Farmer).where(Farmer.user_id == user_id)
    result = await db.execute(stmt)
    farmer = result.scalar_one_or_none()
    
    if not farmer:
        raise HTTPException(status_code=400, detail="Farmer profile not found")
    
    animal = await db.get(Animal, animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    if animal.farmer_id != farmer.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this animal")
    
    await db.delete(animal)
    await db.commit()


@router.get("/farmer/my-animals", response_model=List[AnimalRead])
async def list_my_animals(
    user=Depends(require_farmer),
    db: AsyncSession = Depends(get_session)
):
    """List all animals owned by the current farmer"""
    user_id = get_user_id(user)
    
    # Get farmer profile
    stmt = select(Farmer).where(Farmer.user_id == user_id)
    result = await db.execute(stmt)
    farmer = result.scalar_one_or_none()
    
    if not farmer:
        raise HTTPException(status_code=400, detail="Farmer profile not found")
    
    stmt = select(Animal).where(Animal.farmer_id == farmer.id)
    result = await db.execute(stmt)
    animals = result.scalars().all()
    return animals
