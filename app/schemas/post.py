"""Post Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class PostBase(BaseModel):
    """Base post schema with common fields."""
    title: str
    content: str


class PostCreate(PostBase):
    """Schema for post creation."""
    author_id: int


class PostUpdate(BaseModel):
    """Schema for post updates."""
    title: Optional[str] = None
    content: Optional[str] = None


class Post(PostBase):
    """Complete post schema for responses."""
    id: int
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Pydantic v2 configuration
    model_config = ConfigDict(from_attributes=True)


class PostSummary(BaseModel):
    """Schema for post summary/list responses."""
    id: int
    title: str
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)