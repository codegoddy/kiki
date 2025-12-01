"""
Category model - represents post categories/tags.
"""

from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class Category(Base, TimestampMixin):
    """Category model for organizing posts."""
    
    __tablename__ = "categories"

    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    color = Column(String, default="#3b82f6")  # Hex color code for UI

    # Relationships
    posts = relationship("Post", secondary="post_category_association", back_populates="categories")

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name='{self.name}')>"