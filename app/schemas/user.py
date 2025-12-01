"""User Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    """Base user schema with common fields."""
    username: str
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user creation."""
    password: str


class UserUpdate(BaseModel):
    """Schema for user updates."""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class User(UserBase):
    """Complete user schema for responses."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

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