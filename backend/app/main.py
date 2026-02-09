"""
Farmart Backend - FastAPI Application Entry Point

Responsibilities:
- Create FastAPI app instance
- Load configuration
- Mount versioned routers
- Add middleware (config-driven)
- Handle startup/shutdown events
- Keep thin - NO business logic
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging

from app.core.config import settings
from app.core.database import init_db, close_db
from app.api.v1 import auth, animals, cart, orders, payments, users

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """
    Application factory for Farmart backend.

    Responsibilities:
    - Configure FastAPI metadata
    - Register middleware
    - Mount API routers
    - Register startup/shutdown hooks
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Farmart - Direct farm animal marketplace connecting farmers and buyers",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json",
    )

    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if settings.ENABLE_GZIP:
        app.add_middleware(GZipMiddleware, minimum_size=1000)

    if settings.ENVIRONMENT == "production" and settings.ALLOWED_HOSTS:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS,
        )

    # Mount routers under /api/v1 prefix
    # Note: Each router already has its own prefix (e.g., /auth, /animals)
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(users.router, prefix="/api/v1")
    app.include_router(animals.router, prefix="/api/v1")
    app.include_router(cart.router, prefix="/api/v1")
    app.include_router(orders.router, prefix="/api/v1")
    app.include_router(payments.router, prefix="/api/v1")

    # Root endpoint - API information
    @app.get("/", tags=["root"])
    async def root():
        """API root - returns service information"""
        return {
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "description": "Farmart - Direct farm animal marketplace",
            "docs": "/docs",
            "health": "/health"
        }

    # Health check
    @app.get("/health", tags=["health"])
    async def health_check():
        """Simple health check endpoint"""
        return {"status": "healthy", "service": settings.PROJECT_NAME, "version": settings.VERSION}

    # Global exception handler example
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error occurred. Please try again later."},
        )

    # Startup event
    @app.on_event("startup")
    async def on_startup():
        logger.info(f"🚀 Starting {settings.PROJECT_NAME} v{settings.VERSION}")
        await init_db()

    # Shutdown event
    @app.on_event("shutdown")
    async def on_shutdown():
        logger.info(f"👋 Shutting down {settings.PROJECT_NAME}")
        await close_db()

    return app


# Instantiate app for ASGI server
app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST or "0.0.0.0",
        port=int(settings.SERVER_PORT or 8000),
        reload=settings.DEBUG,
    )
