"""
Dependency injection container and service factories.
"""

from typing import Optional, Dict, Any, Type, TypeVar, Union, Callable
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.repositories import (
    UserRepository,
    PostRepository,
    CommentRepository,
    CategoryRepository
)

T = TypeVar('T')


class DIContainer:
    """Simple dependency injection container."""
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable] = {}
    
    def register(self, interface: Type[T], implementation: Optional[Type[T]] = None, factory: Optional[Callable] = None):
        """Register a service or factory."""
        if factory:
            self._factories[interface] = factory
        else:
            self._services[interface] = implementation or interface
    
    def get(self, interface: Type[T]) -> T:
        """Get service from container."""
        if interface in self._factories:
            return self._factories[interface]()
        
        if interface in self._services:
            return self._services[interface]
        
        raise ValueError(f"Service {interface} not registered in container")
    
    def clear(self):
        """Clear all registered services."""
        self._services.clear()
        self._factories.clear()


# Global container instance
_container = DIContainer()


def setup_container():
    """Set up dependency injection container with all services."""
    settings = get_settings()
    
    # Database repositories - using lambda to avoid circular imports
    def create_user_repository():
        from app.database import get_db
        db = next(get_db())
        return UserRepository(db)
    
    def create_post_repository():
        from app.database import get_db
        db = next(get_db())
        return PostRepository(db)
    
    def create_comment_repository():
        from app.database import get_db
        db = next(get_db())
        return CommentRepository(db)
    
    def create_category_repository():
        from app.database import get_db
        db = next(get_db())
        return CategoryRepository(db)
    
    # Register repositories
    _container.register(UserRepository, factory=create_user_repository)
    _container.register(PostRepository, factory=create_post_repository)
    _container.register(CommentRepository, factory=create_comment_repository)
    _container.register(CategoryRepository, factory=create_category_repository)


def get_container() -> DIContainer:
    """Get global dependency injection container."""
    return _container


def get_repository(repository_type: Type[T]) -> T:
    """Get repository from container."""
    return _container.get(repository_type)


# Factory functions for direct use
def create_user_repository(db: Session) -> UserRepository:
    """Create user repository instance."""
    return UserRepository(db)


def create_post_repository(db: Session) -> PostRepository:
    """Create post repository instance."""
    return PostRepository(db)


def create_comment_repository(db: Session) -> CommentRepository:
    """Create comment repository instance."""
    return CommentRepository(db)


def create_category_repository(db: Session) -> CategoryRepository:
    """Create category repository instance."""
    return CategoryRepository(db)


# Factory mapping
def get_repository_factory(repository_type: Type[T]) -> Callable[[Session], T]:
    """Factory function for creating repository instances."""
    factories = {
        UserRepository: create_user_repository,
        PostRepository: create_post_repository,
        CommentRepository: create_comment_repository,
        CategoryRepository: create_category_repository,
    }
    
    return factories.get(repository_type, lambda db: None)