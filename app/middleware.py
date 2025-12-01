"""
HTTP request/response middleware for logging and monitoring.
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from app.utils.logger import logger
from app.core.config import get_settings

settings = get_settings()

async def log_requests(request: Request, call_next: Callable) -> Response:
    """
    Middleware to log HTTP requests and responses.
    
    Args:
        request: The incoming HTTP request
        call_next: The next middleware/endpoint to call
        
    Returns:
        Response: The HTTP response from the next handler
    """
    # Generate unique request ID for tracing
    request_id = str(uuid.uuid4())
    
    # Add request ID to request state for later use
    request.state.request_id = request_id
    
    start_time = time.time()
    
    # Log request
    logger.info(
        f"Request started | ID: {request_id} | "
        f"{request.method} {request.url.path} | "
        f"Client: {request.client.host if request.client else 'Unknown'}"
    )
    
    # Process the request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log response
    logger.info(
        f"Request completed | ID: {request_id} | "
        f"Status: {response.status_code} | "
        f"Time: {process_time:.3f}s"
    )
    
    # Add request ID to response headers for client-side tracing
    response.headers["X-Request-ID"] = request_id
    
    return response

async def security_headers(request: Request, call_next: Callable) -> Response:
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
    
    return response