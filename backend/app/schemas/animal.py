# app/schemas/animal.py

"""
Pydantic schemas for Animals

Responsibilities:
- Define request/response payloads for animal operations
- Keep schemas lean; no DB logic
- Separate Create, Update, and Read payloads
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, confloat


# ----------------------------
# Animal Schemas
# ----------------------------
class AnimalCreate(BaseModel):
    """
    Payload for creating a new animal.
    """
    name: str = Field(..., min_length=1, max_length=100)
    species: str = Field(default="unknown", max_length=50)
    breed: Optional[str] = Field(default=None, max_length=50)
    age: Optional[int] = Field(default=None, ge=0)
    gender: Optional[str] = Field(default=None, max_length=20)
    price: confloat(ge=0.0) = 0.0
    available: Optional[bool] = True


class AnimalUpdate(BaseModel):
    """
    Payload for updating an existing animal.
    All fields optional — only provided fields will be applied.
    """
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    species: Optional[str] = Field(default=None, max_length=50)
    breed: Optional[str] = Field(default=None, max_length=50)
    age: Optional[int] = Field(default=None, ge=0)
    gender: Optional[str] = Field(default=None, max_length=20)
    price: Optional[confloat(ge=0.0)] = None
    available: Optional[bool] = None


class AnimalRead(BaseModel):
    """
    Representation returned by the API for an animal.
    """
    id: int
    name: str
    species: str
    breed: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    price: float
    available: bool
    farmer_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
