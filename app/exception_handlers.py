"""
Global exception handlers for FastAPI application.
"""

from typing import Any, Dict
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exceptions import AppException, ValidationException, NotFoundException, UnauthorizedException, ForbiddenException
from app.utils.logger import api_logger, structured_logger
from app.core.config import is_production


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle custom application exceptions."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    # Log the error
    structured_logger.error(
        "Application exception occurred",
        extra={
            "request_id": request_id,
            "status_code": exc.status_code,
            "error_type": "AppException",
            "error_message": exc.detail,
            "url": str(request.url),
            "method": request.method
        }
    )
    
    # Create error response
    error_response = {
        "error": {
            "type": "application_error",
            "message": exc.detail,
            "status_code": exc.status_code
        },
        "request_id": request_id
    }
    
    # Add debug information in development
    if not is_production():
        error_response["error"]["debug"] = {
            "exception_type": type(exc).__name__,
            "detail": exc.detail
        }
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response,
        headers=exc.headers
    )


async def validation_exception_handler(request: Request, exc: ValidationException) -> JSONResponse:
    """Handle validation exceptions."""
    return await app_exception_handler(request, exc)


async def not_found_exception_handler(request: Request, exc: NotFoundException) -> JSONResponse:
    """Handle not found exceptions."""
    return await app_exception_handler(request, exc)


async def unauthorized_exception_handler(request: Request, exc: UnauthorizedException) -> JSONResponse:
    """Handle unauthorized exceptions."""
    return await app_exception_handler(request, exc)


async def forbidden_exception_handler(request: Request, exc: ForbiddenException) -> JSONResponse:
    """Handle forbidden exceptions."""
    return await app_exception_handler(request, exc)


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    # Log the HTTP exception
    structured_logger.warning(
        "HTTP exception occurred",
        extra={
            "request_id": request_id,
            "status_code": exc.status_code,
            "error_type": "HTTPException",
            "error_message": exc.detail,
            "url": str(request.url),
            "method": request.method
        }
    )
    
    error_response = {
        "error": {
            "type": "http_error",
            "message": exc.detail,
            "status_code": exc.status_code
        },
        "request_id": request_id
    }
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    # Log the validation error
    structured_logger.warning(
        "Request validation failed",
        extra={
            "request_id": request_id,
            "status_code": 422,
            "error_type": "ValidationError",
            "validation_errors": exc.errors(),
            "url": str(request.url),
            "method": request.method
        }
    )
    
    error_response = {
        "error": {
            "type": "validation_error",
            "message": "Request validation failed",
            "status_code": 422,
            "details": exc.errors()
        },
        "request_id": request_id
    }
    
    return JSONResponse(
        status_code=422,
        content=error_response
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general unhandled exceptions."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    # Log the unexpected error
    structured_logger.error(
        "Unexpected exception occurred",
        extra={
            "request_id": request_id,
            "status_code": 500,
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "url": str(request.url),
            "method": request.method
        },
        exc_info=True
    )
    
    error_response = {
        "error": {
            "type": "internal_error",
            "message": "An unexpected error occurred",
            "status_code": 500
        },
        "request_id": request_id
    }
    
    # Add more detailed error information in development
    if not is_production():
        error_response["error"]["debug"] = {
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "traceback": str(exc.__traceback__)
        }
    
    return JSONResponse(
        status_code=500,
        content=error_response
    )


def register_exception_handlers(app):
    """Register all exception handlers with the FastAPI app."""
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(ValidationException, validation_exception_handler)
    app.add_exception_handler(NotFoundException, not_found_exception_handler)
    app.add_exception_handler(UnauthorizedException, unauthorized_exception_handler)
    app.add_exception_handler(ForbiddenException, forbidden_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, general_exception_handler)