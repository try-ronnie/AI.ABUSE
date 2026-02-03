from typing import AsyncGenerator
import logging

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------
# Async SQLAlchemy Engine
# ---------------------------
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    future=True,
    pool_pre_ping=True,  # Helps prevent disconnect errors
)

# ---------------------------
# Async Session Maker
# ---------------------------
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    future=True,
)


# ---------------------------
# Startup: Initialize DB
# ---------------------------
async def init_db() -> None:
    """
    Called on FastAPI startup.
    - Tests DB connection
    - Can optionally create tables (SQLModel.metadata.create_all)
    """
    try:
        async with engine.begin() as conn:
            # Test connection
            await conn.run_sync(lambda sync_conn: None)
        logger.info("✅ Database connection successful")
    except SQLAlchemyError as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise

# ---------------------------
# Shutdown: Close DB
# ---------------------------
async def close_db() -> None:
    """
    Called on FastAPI shutdown.
    - Dispose engine / connection pool
    """
    await engine.dispose()
    logger.info("🛑 Database connection pool disposed")


