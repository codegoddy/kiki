"""
Custom exceptions for the core application layer.
"""


class BaseAppException(Exception):
    """Base exception for all application errors."""
    
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class EntityNotFoundError(BaseAppException):
    """Raised when an entity is not found in the database."""
    
    def __init__(self, entity_type: str, entity_id: int):
        super().__init__(
            f"{entity_type} with id {entity_id} not found",
            {"entity_type": entity_type, "entity_id": entity_id}
        )


class EntityAlreadyExistsError(BaseAppException):
    """Raised when trying to create an entity that already exists."""
    
    def __init__(self, entity_type: str, field: str, value: str):
        super().__init__(
            f"{entity_type} with {field} '{value}' already exists",
            {"entity_type": entity_type, "field": field, "value": value}
        )


class ValidationError(BaseAppException):
    """Raised when data validation fails."""
    
    def __init__(self, field: str, message: str):
        super().__init__(
            f"Validation error for field '{field}': {message}",
            {"field": field, "message": message}
        )


class AuthenticationError(BaseAppException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message)


class AuthorizationError(BaseAppException):
    """Raised when authorization fails."""
    
    def __init__(self, message: str = "Not authorized to perform this action"):
        super().__init__(message)


class BusinessLogicError(BaseAppException):
    """Raised when business logic constraints are violated."""
    
    def __init__(self, message: str):
        super().__init__(message)