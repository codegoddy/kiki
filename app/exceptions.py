"""
Custom exceptions and error handling for the application.
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from app.utils.logger import logger


class AppException(HTTPException):
    """Base application exception."""
    
    def __init__(
        self, 
        status_code: int, 
        detail: str, 
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        logger.error(f"Application exception: {detail}")


class ValidationException(AppException):
    """Exception for validation errors."""
    
    def __init__(self, detail: str = "Validation error"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


class NotFoundException(AppException):
    """Exception for resource not found errors."""
    
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} not found"
        )


class UnauthorizedException(AppException):
    """Exception for authentication/authorization errors."""
    
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenException(AppException):
    """Exception for authorization errors."""
    
    def __init__(self, detail: str = "Not authorized to access this resource"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class ConflictException(AppException):
    """Exception for resource conflict errors."""
    
    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )


class DatabaseException(AppException):
    """Exception for database errors."""
    
    def __init__(self, detail: str = "Database error occurred"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


class ExternalServiceException(AppException):
    """Exception for external service errors."""
    
    def __init__(self, service: str, detail: str = "External service error"):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"{service}: {detail}"
        )


def handle_exception(exc: Exception) -> AppException:
    """Convert standard exceptions to application exceptions."""
    
    if isinstance(exc, AppException):
        return exc
    
    if isinstance(exc, ValueError):
        return ValidationException(str(exc))
    
    if isinstance(exc, KeyError):
        return NotFoundException(f"Missing key: {str(exc)}")
    
    if isinstance(exc, PermissionError):
        return ForbiddenException(str(exc))
    
    # Generic internal server error
    logger.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)}")
    return AppException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Internal server error occurred"
    )


def create_error_response(
    error_type: str, 
    message: str, 
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a standardized error response."""
    
    response: Dict[str, Any] = {
        "error": {
            "type": error_type,
            "message": message
        }
    }
    
    if details:
        response["error"]["details"] = details  # type: ignore
    
    return response