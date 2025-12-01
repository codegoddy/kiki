"""
Service interfaces defining contracts for business logic operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Generic, TypeVar
from sqlalchemy.orm import Session

# Type variables
T = TypeVar('T')
CreateSchemaType = TypeVar('CreateSchemaType')
UpdateSchemaType = TypeVar('UpdateSchemaType')


class ServiceInterface(ABC, Generic[CreateSchemaType, UpdateSchemaType]):
    """Base service interface with common operations."""
    
    @abstractmethod
    async def create(self, data: CreateSchemaType) -> Dict[str, Any]:
        """Create new entity."""
        pass
    
    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[Dict[str, Any]]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all entities with pagination."""
        pass
    
    @abstractmethod
    async def update(self, id: int, data: UpdateSchemaType) -> Optional[Dict[str, Any]]:
        """Update existing entity."""
        pass
    
    @abstractmethod
    async def delete(self, id: int) -> bool:
        """Delete entity by ID."""
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """Get total count of entities."""
        pass


class UserServiceInterface(ServiceInterface[Dict[str, Any], Dict[str, Any]]):
    """User service interface with specific operations."""
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username."""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email."""
        pass
    
    @abstractmethod
    async def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with username and password."""
        pass
    
    @abstractmethod
    async def get_user_posts(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get posts created by user."""
        pass
    
    @abstractmethod
    async def get_user_comments(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get comments created by user."""
        pass


class PostServiceInterface(ServiceInterface[Dict[str, Any], Dict[str, Any]]):
    """Post service interface with specific operations."""
    
    @abstractmethod
    async def get_by_author(self, author_id: int, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get posts by author."""
        pass
    
    @abstractmethod
    async def search(self, query: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Search posts by title or content."""
        pass
    
    @abstractmethod
    async def get_with_comments(self, post_id: int) -> Optional[Dict[str, Any]]:
        """Get post with all comments."""
        pass
    
    @abstractmethod
    async def add_category(self, post_id: int, category_id: int) -> bool:
        """Add category to post."""
        pass
    
    @abstractmethod
    async def remove_category(self, post_id: int, category_id: int) -> bool:
        """Remove category from post."""
        pass
    
    @abstractmethod
    async def get_recent_posts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent posts."""
        pass
    
    @abstractmethod
    async def increment_views(self, post_id: int) -> bool:
        """Increment post view count."""
        pass


class CommentServiceInterface(ServiceInterface[Dict[str, Any], Dict[str, Any]]):
    """Comment service interface with specific operations."""
    
    @abstractmethod
    async def get_by_post(self, post_id: int, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get comments by post."""
        pass
    
    @abstractmethod
    async def get_by_author(self, author_id: int, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get comments by author."""
        pass
    
    @abstractmethod
    async def get_post_comment_count(self, post_id: int) -> int:
        """Get comment count for a post."""
        pass


class CategoryServiceInterface(ServiceInterface[Dict[str, Any], Dict[str, Any]]):
    """Category service interface with specific operations."""
    
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get category by name."""
        pass
    
    @abstractmethod
    async def get_with_post_count(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get categories with post counts."""
        pass
    
    @abstractmethod
    async def get_by_post(self, post_id: int) -> List[Dict[str, Any]]:
        """Get categories for a specific post."""
        pass
    
    @abstractmethod
    async def search(self, query: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Search categories by name or description."""
        pass


class AdminServiceInterface(ServiceInterface[Dict[str, Any], Dict[str, Any]]):
    """Admin service interface with administrative operations."""
    
    @abstractmethod
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        pass
    
    @abstractmethod
    async def get_user_statistics(self) -> Dict[str, Any]:
        """Get user statistics."""
        pass
    
    @abstractmethod
    async def get_post_statistics(self) -> Dict[str, Any]:
        """Get post statistics."""
        pass
    
    @abstractmethod
    async def get_comment_statistics(self) -> Dict[str, Any]:
        """Get comment statistics."""
        pass
    
    @abstractmethod
    async def get_activity_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent activity logs."""
        pass
    
    @abstractmethod
    async def cleanup_orphaned_data(self) -> Dict[str, int]:
        """Cleanup orphaned data."""
        pass