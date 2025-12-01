"""
Core application layer containing shared business logic and interfaces.
"""

from .interfaces import (
    UserRepositoryInterface,
    PostRepositoryInterface, 
    CommentRepositoryInterface,
    CategoryRepositoryInterface,
    RepositoryInterface
)
from .base_repository import BaseRepository
from .repositories import (
    UserRepository,
    PostRepository,
    CommentRepository,
    CategoryRepository
)
from .exceptions import (
    EntityNotFoundError,
    EntityAlreadyExistsError,
    ValidationError,
    BaseAppException,
    AuthenticationError,
    AuthorizationError,
    BusinessLogicError
)
from .config import (
    Settings,
    DatabaseSettings,
    APISettings,
    SecuritySettings,
    LoggingSettings,
    get_settings,
    get_database_url,
    is_development,
    is_testing,
    is_production
)
from .dependency_injection import (
    DIContainer,
    get_container,
    get_repository,
    create_user_repository,
    create_post_repository,
    create_comment_repository,
    create_category_repository,
    setup_container
)

__all__ = [
    # Base classes
    "RepositoryInterface",
    "BaseRepository",
    
    # Interfaces
    "UserRepositoryInterface",
    "PostRepositoryInterface", 
    "CommentRepositoryInterface",
    "CategoryRepositoryInterface",
    
    # Implementations
    "UserRepository",
    "PostRepository",
    "CommentRepository",
    "CategoryRepository",
    
    # Exceptions
    "BaseAppException",
    "EntityNotFoundError",
    "EntityAlreadyExistsError",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "BusinessLogicError",
    
    # Configuration
    "Settings",
    "DatabaseSettings",
    "APISettings",
    "SecuritySettings",
    "LoggingSettings",
    "get_settings",
    "get_database_url",
    "is_development",
    "is_testing",
    "is_production",
    
    # Dependency Injection
    "DIContainer",
    "get_container",
    "get_repository",
    "create_user_repository",
    "create_post_repository",
    "create_comment_repository",
    "create_category_repository",
    "setup_container"
]