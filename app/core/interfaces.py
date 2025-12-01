"""
Repository interfaces defining contracts for data access operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Generic, TypeVar, Dict, Any
from sqlalchemy.orm import Session
from app.models import User, Post, Comment, Category

# Type variables for generic repository
T = TypeVar('T')
ModelType = TypeVar('ModelType', bound=User)
CreateSchemaType = TypeVar('CreateSchemaType')
UpdateSchemaType = TypeVar('UpdateSchemaType')


class RepositoryInterface(ABC, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base repository interface with common CRUD operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[ModelType]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all entities with pagination."""
        pass
    
    @abstractmethod
    def create(self, data: CreateSchemaType) -> ModelType:
        """Create new entity."""
        pass
    
    @abstractmethod
    def update(self, id: int, data: UpdateSchemaType) -> Optional[ModelType]:
        """Update existing entity."""
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        """Delete entity by ID."""
        pass
    
    @abstractmethod
    def exists(self, id: int) -> bool:
        """Check if entity exists by ID."""
        pass


class UserRepositoryInterface(RepositoryInterface[User, Dict[str, Any], Dict[str, Any]]):
    """User repository interface."""
    
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        pass
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        pass
    
    @abstractmethod
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password."""
        pass


class PostRepositoryInterface(RepositoryInterface[Post, Dict[str, Any], Dict[str, Any]]):
    """Post repository interface."""
    
    @abstractmethod
    def get_by_author(self, author_id: int, skip: int = 0, limit: int = 100) -> List[Post]:
        """Get posts by author."""
        pass
    
    @abstractmethod
    def search(self, query: str, skip: int = 0, limit: int = 100) -> List[Post]:
        """Search posts by title or content."""
        pass
    
    @abstractmethod
    def get_with_comments(self, post_id: int) -> Optional[Post]:
        """Get post with all comments."""
        pass
    
    @abstractmethod
    def add_category(self, post_id: int, category_id: int) -> bool:
        """Add category to post."""
        pass
    
    @abstractmethod
    def remove_category(self, post_id: int, category_id: int) -> bool:
        """Remove category from post."""
        pass


class CommentRepositoryInterface(RepositoryInterface[Comment, Dict[str, Any], Dict[str, Any]]):
    """Comment repository interface."""
    
    @abstractmethod
    def get_by_post(self, post_id: int, skip: int = 0, limit: int = 100) -> List[Comment]:
        """Get comments by post."""
        pass
    
    @abstractmethod
    def get_by_author(self, author_id: int, skip: int = 0, limit: int = 100) -> List[Comment]:
        """Get comments by author."""
        pass


class CategoryRepositoryInterface(RepositoryInterface[Category, Dict[str, Any], Dict[str, Any]]):
    """Category repository interface."""
    
    @abstractmethod
    def get_by_name(self, name: str) -> Optional[Category]:
        """Get category by name."""
        pass
    
    @abstractmethod
    def get_with_post_count(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get categories with post counts."""
        pass
    
    @abstractmethod
    def get_by_post(self, post_id: int) -> List[Category]:
        """Get categories for a specific post."""
        pass
    
    @abstractmethod
    def search(self, query: str, skip: int = 0, limit: int = 100) -> List[Category]:
        """Search categories by name or description."""
        pass