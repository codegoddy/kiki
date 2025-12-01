"""
Enhanced User service with repository pattern and dependency injection.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models import User
from app.schemas.user import UserCreate, UserUpdate, UserInDB
from app.core.interfaces import UserRepositoryInterface
from app.core.base_service import BaseService
from app.core.service_interfaces import UserServiceInterface
from app.core.exceptions import ValidationError, BusinessLogicError
from app.utils.logger import get_logger


class UserService(BaseService[User, Dict[str, Any], Dict[str, Any]], UserServiceInterface):
    """Enhanced user service with repository pattern and business logic."""
    
    def __init__(self, user_repository: UserRepositoryInterface):
        super().__init__(user_repository)
        self.user_repo = user_repository
        self.logger = get_logger("user_service", structured=True)
    
    async def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username with validation."""
        try:
            if not username or not username.strip():
                raise ValidationError("username", "Username cannot be empty")
            
            user = self.user_repo.get_by_username(username.strip())
            if user:
                return self._serialize_user(user)
            
            return None
            
        except ValidationError:
            raise
        except Exception as e:
            self.logger.error(
                "Failed to get user by username",
                extra={
                    "username": username,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            raise BusinessLogicError(f"Failed to retrieve user by username: {str(e)}")
    
    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email with validation."""
        try:
            if not email or not email.strip():
                raise ValidationError("email", "Email cannot be empty")
            
            user = self.user_repo.get_by_email(email.strip())
            if user:
                return self._serialize_user(user)
            
            return None
            
        except ValidationError:
            raise
        except Exception as e:
            self.logger.error(
                "Failed to get user by email",
                extra={
                    "email": email,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            raise BusinessLogicError(f"Failed to retrieve user by email: {str(e)}")
    
    async def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with username and password."""
        try:
            if not username or not password:
                raise ValidationError("credentials", "Username and password are required")
            
            user = self.user_repo.authenticate(username.strip(), password)
            if user:
                self.logger.info(
                    "User authenticated successfully",
                    extra={
                        "username": username,
                        "user_id": user.id
                    }
                )
                return self._serialize_user(user)
            
            self.logger.warning(
                "Failed authentication attempt",
                extra={
                    "username": username,
                    "reason": "invalid_credentials"
                }
            )
            return None
            
        except ValidationError:
            raise
        except Exception as e:
            self.logger.error(
                "Authentication error",
                extra={
                    "username": username,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            raise BusinessLogicError(f"Authentication failed: {str(e)}")
    
    async def get_user_posts(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get posts created by user."""
        try:
            if not self.user_repo.exists(user_id):
                from app.core.exceptions import EntityNotFoundError
                raise EntityNotFoundError("User", user_id)
            
            # This would typically call a post repository
            # For now, implementing basic functionality
            posts = []  # Will be implemented when we enhance the service
            
            self.logger.info(
                "Retrieved user posts",
                extra={
                    "user_id": user_id,
                    "post_count": len(posts),
                    "skip": skip,
                    "limit": limit
                }
            )
            
            return posts
            
        except Exception as e:
            self.logger.error(
                "Failed to get user posts",
                extra={
                    "user_id": user_id,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            raise BusinessLogicError(f"Failed to retrieve user posts: {str(e)}")
    
    async def get_user_comments(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get comments created by user."""
        try:
            if not self.user_repo.exists(user_id):
                from app.core.exceptions import EntityNotFoundError
                raise EntityNotFoundError("User", user_id)
            
            # This would typically call a comment repository
            # For now, implementing basic functionality
            comments = []  # Will be implemented when we enhance the service
            
            self.logger.info(
                "Retrieved user comments",
                extra={
                    "user_id": user_id,
                    "comment_count": len(comments),
                    "skip": skip,
                    "limit": limit
                }
            )
            
            return comments
            
        except Exception as e:
            self.logger.error(
                "Failed to get user comments",
                extra={
                    "user_id": user_id,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            raise BusinessLogicError(f"Failed to retrieve user comments: {str(e)}")
    
    async def _validate_create_data(self, data: Dict[str, Any]) -> None:
        """Validate user data before creation."""
        # Check for required fields
        required_fields = ["username", "email", "password"]
        for field in required_fields:
            if field not in data or not data.get(field):
                raise ValidationError(field, f"Field '{field}' is required")
        
        # Validate username
        username = data["username"]
        if len(username) < 3:
            raise ValidationError("username", "Username must be at least 3 characters long")
        if len(username) > 50:
            raise ValidationError("username", "Username must not exceed 50 characters")
        
        # Validate email format (basic validation)
        email = data["email"]
        if "@" not in email or "." not in email:
            raise ValidationError("email", "Invalid email format")
        
        # Validate password strength
        password = data["password"]
        if len(password) < 8:
            raise ValidationError("password", "Password must be at least 8 characters long")
    
    async def _after_create(self, user: User) -> None:
        """Post-creation business logic."""
        self.logger.info(
            "User created successfully",
            extra={
                "user_id": user.id,
                "username": user.username,
                "email": user.email
            }
        )
    
    async def _before_delete(self, user_id: int) -> None:
        """Pre-deletion business logic."""
        # Check if user has dependent data (posts, comments)
        # This would typically involve checking related entities
        pass
    
    async def _after_delete(self, user_id: int) -> None:
        """Post-deletion business logic."""
        self.logger.info(
            "User deleted successfully",
            extra={
                "user_id": user_id
            }
        )
    
    def _serialize_user(self, user: User) -> Dict[str, Any]:
        """Serialize user model to dictionary."""
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }
    
    def _get_entity_name(self) -> str:
        """Get entity name for error messages."""
        return "User"