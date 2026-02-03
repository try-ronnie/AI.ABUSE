from typing import AsyncGenerator
import logging

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------
# Async Engine
# ---------------------------
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    future=True,
    pool_pre_ping=True,  # Avoid disconnect issues
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
    - Tests DB connection.
    - Optionally create tables if SQLModel is detected.
    """
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        logger.info("✅ Database connection test succeeded.")

        # Optional: auto-create tables if SQLModel is present
        try:
            from sqlmodel import SQLModel  # type: ignore
            logger.info("SQLModel detected — attempting to create missing tables.")
            SQLModel.metadata.create_all(bind=engine.sync_engine)
            logger.info("SQLModel create_all completed.")
        except Exception as exc:
            logger.debug("Skipping SQLModel create_all: %s", exc)

    except SQLAlchemyError as exc:
        logger.exception("❌ Failed to initialize database connection: %s", exc)
        raise

# ---------------------------
# Shutdown: Close DB
# ---------------------------
async def close_db() -> None:
    """
    Called on FastAPI shutdown.
    - Dispose engine / connection pool
    """
    try:
        await engine.dispose()
        logger.info("🛑 Database engine disposed and connection pool closed.")
    except Exception as exc:
        logger.exception("Error while disposing database engine: %s", exc)

# ---------------------------
# FastAPI dependency for routes/services
# ---------------------------
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Yield an AsyncSession for request-scoped DB access.

    Example usage in a route:
        async def endpoint(db: AsyncSession = Depends(get_session)):
            await db.execute(...)
    """
    async with async_session() as session:
        yield session
