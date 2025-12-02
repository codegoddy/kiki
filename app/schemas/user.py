"""User Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    """Base user schema with common fields."""
    username: str
    email: EmailStr
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user creation."""
    password: str


class UserUpdate(BaseModel):
    """Schema for user updates."""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None


class User(UserBase):
    """Complete user schema for responses."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True
    is_superuser: bool = False

    # Pydantic v2 configuration
    model_config = ConfigDict(from_attributes=True)


class UserProfile(UserBase):
    """User profile schema with additional social information."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True
    followers_count: int = 0
    following_count: int = 0
    posts_count: int = 0
    is_following: bool = False

    # Pydantic v2 configuration
    model_config = ConfigDict(from_attributes=True)


class UserInDB(User):
    """User schema including hashed password."""
    hashed_password: str


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str
    password: str


class Token(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None


class TokenData(BaseModel):
    """Schema for token payload data."""
    username: Optional[str] = None


# Social Features Schemas
class FollowRequest(BaseModel):
    """Schema for follow requests."""
    user_id: int


class FollowResponse(BaseModel):
    """Schema for follow responses."""
    follower_id: int
    followee_id: int
    is_active: bool = True
    created_at: datetime

    # Pydantic v2 configuration
    model_config = ConfigDict(from_attributes=True)


class NotificationCreate(BaseModel):
    """Schema for creating notifications."""
    user_id: int
    actor_id: Optional[int] = None
    notification_type: str
    title: str
    message: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None


class NotificationResponse(BaseModel):
    """Schema for notification responses."""
    id: int
    user_id: int
    actor_id: Optional[int] = None
    notification_type: str
    title: str
    message: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    is_read: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Optional actor information
    actor_username: Optional[str] = None
    actor_avatar_url: Optional[str] = None

    # Pydantic v2 configuration
    model_config = ConfigDict(from_attributes=True)


class NotificationUpdate(BaseModel):
    """Schema for updating notifications."""
    is_read: bool