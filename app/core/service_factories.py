"""
Service factories and dependency injection for enhanced service management.
"""

from typing import Type, TypeVar, Dict, Any, Callable
from sqlalchemy.orm import Session
from app.services.user_service import UserService
from app.core.interfaces import UserRepositoryInterface, PostRepositoryInterface, CommentRepositoryInterface, CategoryRepositoryInterface
from app.core.service_interfaces import UserServiceInterface, PostServiceInterface, CommentServiceInterface, CategoryServiceInterface, AdminServiceInterface

T = TypeVar('T')


class ServiceFactory:
    """Factory for creating service instances with dependency injection."""
    
    def __init__(self):
        self._service_classes: Dict[Type, Type] = {}
        self._service_factories: Dict[Type, Callable] = {}
    
    def register_service(self, interface: Type[T], service_class: Type[T], repository_interface: Type = None):
        """Register a service class for dependency injection."""
        self._service_classes[interface] = service_class
        
        if repository_interface:
            def factory(db: Session):
                from app.core.dependency_injection import get_repository_factory
                repository_factory = get_repository_factory(repository_interface)
                repository = repository_factory(db)
                return service_class(repository)
            
            self._service_factories[interface] = factory
    
    def create_service(self, interface: Type[T], db: Session) -> T:
        """Create service instance using registered factory."""
        if interface in self._service_factories:
            return self._service_factories[interface](db)
        
        if interface in self._service_classes:
            # Create repository and service directly
            service_class = self._service_classes[interface]
            
            # For UserService
            if service_class == UserService:
                from app.core.dependency_injection import create_user_repository
                repository = create_user_repository(db)
                return service_class(repository)
            
            # Add other service types as needed
            return service_class(db)
        
        raise ValueError(f"Service interface {interface} not registered")
    
    def clear(self):
        """Clear all registered services."""
        self._service_classes.clear()
        self._service_factories.clear()


# Global service factory
_service_factory = ServiceFactory()


def setup_service_factory():
    """Set up service factory with all services."""
    
    # Register User Service
    _service_factory.register_service(
        UserServiceInterface, 
        UserService, 
        UserRepositoryInterface
    )
    
    # Register other services as they are implemented
    # _service_factory.register_service(
    #     PostServiceInterface, 
    #     PostService, 
    #     PostRepositoryInterface
    # )
    
    # _service_factory.register_service(
    #     CommentServiceInterface, 
    #     CommentService, 
    #     CommentRepositoryInterface
    # )
    
    # _service_factory.register_service(
    #     CategoryServiceInterface, 
    #     CategoryService, 
    #     CategoryRepositoryInterface
    # )


def get_service_factory() -> ServiceFactory:
    """Get global service factory."""
    return _service_factory


def create_service(interface: Type[T], db: Session) -> T:
    """Create service instance using global factory."""
    return _service_factory.create_service(interface, db)


def get_user_service(db: Session) -> UserServiceInterface:
    """Get user service instance."""
    return create_service(UserServiceInterface, db)


def get_post_service(db: Session) -> PostServiceInterface:
    """Get post service instance."""
    return create_service(PostServiceInterface, db)


def get_comment_service(db: Session) -> CommentServiceInterface:
    """Get comment service instance."""
    return create_service(CommentServiceInterface, db)


def get_category_service(db: Session) -> CategoryServiceInterface:
    """Get category service instance."""
    return create_service(CategoryServiceInterface, db)


def get_admin_service(db: Session) -> AdminServiceInterface:
    """Get admin service instance."""
    return create_service(AdminServiceInterface, db)