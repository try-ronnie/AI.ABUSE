# app/core/database.py

"""
Database connection and session
"""

from typing import AsyncGenerator
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def init_db():
    import app.models.user  # noqa
    import app.models.animal  # noqa
    import app.models.order  # noqa
    import app.models.cart  # noqa
    import app.models.payment  # noqa

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
