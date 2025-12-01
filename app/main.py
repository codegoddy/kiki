"""
Main FastAPI application with centralized configuration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, get_db
from app.models.base import Base
from app.core.config import get_settings, is_production
from app.utils.logger import logger
from app.middleware import log_requests

# Get application settings
settings = get_settings()

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app with settings
app = FastAPI(
    title=settings.api.PROJECT_NAME,
    version=settings.api.PROJECT_VERSION,
    debug=settings.api.DEBUG,
    docs_url="/docs" if not is_production() else None,
    redoc_url="/redoc" if not is_production() else None,
)

# Add CORS middleware with settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.CORS_ALLOW_ORIGINS,
    allow_credentials=settings.api.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.api.CORS_ALLOW_METHODS,
    allow_headers=settings.api.CORS_ALLOW_HEADERS,
)

# Add custom middleware
app.middleware("http")(log_requests)

# Include API routers
from app.api import auth, users, posts, comments, admin, categories

app.include_router(
    auth.router, 
    prefix=f"{settings.api.API_V1_STR}/auth", 
    tags=["authentication"]
)
app.include_router(
    users.router, 
    prefix=settings.api.API_V1_STR, 
    tags=["users"]
)
app.include_router(
    posts.router, 
    prefix=settings.api.API_V1_STR, 
    tags=["posts"]
)
app.include_router(
    comments.router, 
    prefix=settings.api.API_V1_STR, 
    tags=["comments"]
)
app.include_router(
    categories.router, 
    prefix=settings.api.API_V1_STR, 
    tags=["categories"]
)
app.include_router(
    admin.router, 
    prefix=f"{settings.api.API_V1_STR}/admin", 
    tags=["admin"]
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": f"Welcome to {settings.api.PROJECT_NAME} v{settings.api.PROJECT_VERSION}"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": settings.api.PROJECT_VERSION
    }

@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info(f"Starting {settings.api.PROJECT_NAME} v{settings.api.PROJECT_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.api.DEBUG}")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info(f"Shutting down {settings.api.PROJECT_NAME}")
    logger.info("Application shutdown complete")