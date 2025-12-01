"""
HTTP request/response middleware for logging, monitoring, and security.
"""

import time
import uuid
from typing import Callable, Awaitable
from fastapi import Request, Response, status
from starlette.middleware.base import RequestResponseEndpoint
from app.utils.logger import api_logger, structured_logger
from app.exceptions import AppException, ValidationException, NotFoundException, UnauthorizedException, ForbiddenException

# Store current request ID in context variable for logger access
request_id_context = {}


async def log_requests(
    request: Request, 
    call_next: RequestResponseEndpoint
) -> Response:
    """
    Middleware to log HTTP requests and responses with structured logging.
    
    Args:
        request: The incoming HTTP request
        call_next: The next middleware/endpoint to call
        
    Returns:
        Response: The HTTP response from the next handler
    """
    # Generate unique request ID for tracing
    request_id = str(uuid.uuid4())
    
    # Store request ID in context for access by other components
    request_id_context['current'] = request_id
    
    # Add request ID to request state for later use
    request.state.request_id = request_id
    
    start_time = time.time()
    client_host = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Log request with structured logging
    structured_logger.info(
        "Request started",
        extra={
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "client_host": client_host,
            "user_agent": user_agent,
            "query_params": dict(request.query_params)
        }
    )
    
    # Process the request
    try:
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        structured_logger.info(
            "Request completed",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "processing_time": f"{process_time:.3f}s",
                "response_size": response.headers.get("content-length", "unknown")
            }
        )
        
        # Add request ID to response headers for client-side tracing
        response.headers["X-Request-ID"] = request_id
        
        return response
        
    except Exception as e:
        # Log exception
        process_time = time.time() - start_time
        structured_logger.error(
            "Request failed",
            extra={
                "request_id": request_id,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "processing_time": f"{process_time:.3f}s"
            }
        )
        raise
    finally:
        # Clean up request ID context
        request_id_context.pop('current', None)


async def security_headers(
    request: Request, 
    call_next: RequestResponseEndpoint
) -> Response:
    """
    Middleware to add security headers to responses.
    
    Args:
        request: The incoming HTTP request
        call_next: The next middleware/endpoint to call
        
    Returns:
        Response: The HTTP response with security headers
    """
    response = await call_next(request)
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    # Add HSTS header in production
    from app.core.config import is_production
    if is_production():
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response


async def cors_middleware(
    request: Request, 
    call_next: RequestResponseEndpoint
) -> Response:
    """
    Middleware to handle CORS with additional security.
    
    Args:
        request: The incoming HTTP request
        call_next: The next middleware/endpoint to call
        
    Returns:
        Response: The HTTP response with CORS headers
    """
    response = await call_next(request)
    
    # Add CORS headers (these should be configured in main.py with CORSMiddleware)
    # This middleware can add additional security headers
    return response


async def rate_limit_headers(
    request: Request, 
    call_next: RequestResponseEndpoint
) -> Response:
    """
    Middleware to add rate limiting headers.
    
    Args:
        request: The incoming HTTP request
        call_next: The next middleware/endpoint to call
        
    Returns:
        Response: The HTTP response with rate limit headers
    """
    response = await call_next(request)
    
    # Add rate limiting headers (placeholder for actual rate limiting logic)
    # In production, these would be set by actual rate limiting middleware
    response.headers["X-RateLimit-Limit"] = "1000"  # requests per hour
    response.headers["X-RateLimit-Remaining"] = "999"  # requests remaining
    response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 3600)  # reset time
    
    return response


def get_current_request_id() -> str:
    """Get the current request ID from context."""
    return request_id_context.get('current', 'unknown')


def get_request_id_for_logging() -> str:
    """Get request ID for logging purposes."""
    current_id = get_current_request_id()
    return current_id if current_id != 'unknown' else str(uuid.uuid4())