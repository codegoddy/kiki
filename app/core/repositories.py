"""
Concrete repository implementations.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models import User, Post, Comment, Category, post_category_association
from app.core.interfaces import (
    UserRepositoryInterface,
    PostRepositoryInterface, 
    CommentRepositoryInterface,
    CategoryRepositoryInterface
)
from app.core.base_repository import BaseRepository
from app.core.exceptions import EntityNotFoundError, EntityAlreadyExistsError
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRepository(BaseRepository[User, Dict[str, Any], Dict[str, Any]], UserRepositoryInterface):
    """User repository implementation."""
    
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password."""
        user = self.get_by_username(username)
        if user and self._verify_password(password, user.hashed_password):
            return user
        return None
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def _get_password_hash(self, password: str) -> str:
        """Hash password."""
        return pwd_context.hash(password)
    
    def create(self, data: Dict[str, Any]) -> User:
        """Create new user with hashed password."""
        if "password" in data:
            data["hashed_password"] = self._get_password_hash(data.pop("password"))
        
        # Check for existing user
        if "username" in data and self.get_by_username(data["username"]):
            raise EntityAlreadyExistsError("User", "username", data["username"])
        
        if "email" in data and self.get_by_email(data["email"]):
            raise EntityAlreadyExistsError("User", "email", data["email"])
        
        return super().create(data)


class PostRepository(BaseRepository[Post, Dict[str, Any], Dict[str, Any]], PostRepositoryInterface):
    """Post repository implementation."""
    
    def __init__(self, db: Session):
        super().__init__(Post, db)
    
    def get_by_author(self, author_id: int, skip: int = 0, limit: int = 100) -> List[Post]:
        """Get posts by author."""
        return self.db.query(Post).filter(Post.author_id == author_id).offset(skip).limit(limit).all()
    
    def search(self, query: str, skip: int = 0, limit: int = 100) -> List[Post]:
        """Search posts by title or content."""
        return self.db.query(Post).filter(
            (Post.title.ilike(f"%{query}%")) | (Post.content.ilike(f"%{query}%"))
        ).offset(skip).limit(limit).all()
    
    def get_with_comments(self, post_id: int) -> Optional[Post]:
        """Get post with all comments."""
        return self.db.query(Post).filter(Post.id == post_id).first()
    
    def add_category(self, post_id: int, category_id: int) -> bool:
        """Add category to post."""
        post = self.get_by_id(post_id)
        category = self.db.query(Category).filter(Category.id == category_id).first()
        
        if post and category and category not in post.categories:
            post.categories.append(category)
            self.db.commit()
            return True
        return False
    
    def remove_category(self, post_id: int, category_id: int) -> bool:
        """Remove category from post."""
        post = self.get_by_id(post_id)
        category = self.db.query(Category).filter(Category.id == category_id).first()
        
        if post and category and category in post.categories:
            post.categories.remove(category)
            self.db.commit()
            return True
        return False


class CommentRepository(BaseRepository[Comment, Dict[str, Any], Dict[str, Any]], CommentRepositoryInterface):
    """Comment repository implementation."""
    
    def __init__(self, db: Session):
        super().__init__(Comment, db)
    
    def get_by_post(self, post_id: int, skip: int = 0, limit: int = 100) -> List[Comment]:
        """Get comments by post."""
        return self.db.query(Comment).filter(Comment.post_id == post_id).offset(skip).limit(limit).all()
    
    def get_by_author(self, author_id: int, skip: int = 0, limit: int = 100) -> List[Comment]:
        """Get comments by author."""
        return self.db.query(Comment).filter(Comment.author_id == author_id).offset(skip).limit(limit).all()


class CategoryRepository(BaseRepository[Category, Dict[str, Any], Dict[str, Any]], CategoryRepositoryInterface):
    """Category repository implementation."""
    
    def __init__(self, db: Session):
        super().__init__(Category, db)
    
    def get_by_name(self, name: str) -> Optional[Category]:
        """Get category by name."""
        return self.db.query(Category).filter(Category.name == name).first()
    
    def get_with_post_count(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get categories with post counts."""
        categories = (
            self.db.query(
                Category,
                func.count(Post.id).label('post_count')
            )
            .outerjoin(post_category_association, Category.id == post_category_association.c.category_id)
            .outerjoin(Post, post_category_association.c.post_id == Post.id)
            .group_by(Category.id)
            .order_by(desc('post_count'), Category.name)
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        result = []
        for category, post_count in categories:
            result.append({
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "color": category.color,
                "created_at": category.created_at,
                "updated_at": category.updated_at,
                "post_count": post_count
            })
        
        return result
    
    def get_by_post(self, post_id: int) -> List[Category]:
        """Get categories for a specific post."""
        post = self.db.query(Post).filter(Post.id == post_id).first()
        return post.categories if post else []
    
    def search(self, query: str, skip: int = 0, limit: int = 100) -> List[Category]:
        """Search categories by name or description."""
        return self.db.query(Category).filter(
            (Category.name.ilike(f"%{query}%")) | 
            (Category.description.ilike(f"%{query}%"))
        ).offset(skip).limit(limit).all()