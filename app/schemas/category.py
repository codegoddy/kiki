from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = "#3b82f6"  # Default blue color

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None

class Category(CategoryBase):
    id: int
    created_at: datetime
    # Include post counts for efficient display
    post_count: Optional[int] = 0

    class Config:
        orm_mode = True

class CategoryWithPosts(Category):
    posts: list[dict] = []  # Simplified post data for category details