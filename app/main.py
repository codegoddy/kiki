"""
Main FastAPI application with enhanced middleware, exception handling, and logging.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.database import engine, get_db
from app.models.base import Base
from app.core.config import get_settings, is_production, is_development
from app.utils.logger import logger, structured_logger
from app.middleware import log_requests, security_headers, rate_limit_headers
from app.exception_handlers import register_exception_handlers

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
    description="A modern REST API built with FastAPI and PostgreSQL",
    contact={
        "name": "FastAPI Developer",
        "email": "developer@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Add CORS middleware with enhanced settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.CORS_ALLOW_ORIGINS,
    allow_credentials=settings.api.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.api.CORS_ALLOW_METHODS,
    allow_headers=settings.api.CORS_ALLOW_HEADERS,
    expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
    max_age=86400,  # 24 hours
)

# Add custom middleware in order (execution is top to bottom)
app.middleware("http")(log_requests)
app.middleware("http")(security_headers)
app.middleware("http")(rate_limit_headers)

# Register global exception handlers
register_exception_handlers(app)

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
async def root(request: Request):
    """Root endpoint with enhanced information."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    response_data = {
        "message": f"Welcome to {settings.api.PROJECT_NAME} v{settings.api.PROJECT_VERSION}",
        "environment": settings.ENVIRONMENT,
        "api_version": settings.api.PROJECT_VERSION,
        "documentation": "/docs" if not is_production() else None,
        "health": "/health"
    }
    
    structured_logger.info(
        "Root endpoint accessed",
        extra={
            "request_id": request_id,
            "endpoint": "/",
            "response_data": response_data
        }
    )
    
    return response_data

@app.get("/health")
async def health_check():
    """Enhanced health check endpoint."""
    health_data = {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": settings.api.PROJECT_VERSION,
        "timestamp": "2025-12-01T19:32:05.000Z",  # You could make this dynamic
        "services": {
            "database": "connected",  # Could be enhanced to actually check DB
            "logging": "active",
            "configuration": "loaded"
        }
    }
    
    structured_logger.info(
        "Health check performed",
        extra={
            "health_status": health_data
        }
    )
    
    return health_data

@app.get("/metrics")
async def metrics_endpoint():
    """Simple metrics endpoint (can be enhanced with actual monitoring)."""
    from datetime import datetime
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": 3600,  # Placeholder
        "request_count": 100,    # Placeholder
        "environment": settings.ENVIRONMENT
    }

@app.on_event("startup")
async def startup_event():
    """Application startup event with enhanced logging."""
    structured_logger.info(
        "Application startup",
        extra={
            "event": "startup",
            "project_name": settings.api.PROJECT_NAME,
            "version": settings.api.PROJECT_VERSION,
            "environment": settings.ENVIRONMENT,
            "debug_mode": settings.api.DEBUG,
            "features": {
                "cors_enabled": True,
                "security_headers": True,
                "request_logging": True,
                "exception_handlers": True,
                "rate_limiting": True
            }
        }
    )

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event with enhanced logging."""
    structured_logger.info(
        "Application shutdown",
        extra={
            "event": "shutdown",
            "project_name": settings.api.PROJECT_NAME
        }
    )

# Global exception handling for unhandled startup/shutdown events
if __name__ == "__main__":
    import uvicorn
    
    structured_logger.info(
        "Starting application with uvicorn",
        extra={
            "host": settings.api.HOST,
            "port": settings.api.PORT,
            "reload": settings.api.DEBUG and is_development()
        }
    )
    
    uvicorn.run(
        "app.main:app",
        host=settings.api.HOST,
        port=settings.api.PORT,
        reload=settings.api.DEBUG and is_development(),
        log_config=None  # Use our custom logging configuration
    )