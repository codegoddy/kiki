"""
Comment model - represents comments on posts.
"""

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class Comment(Base, TimestampMixin):
    """Comment model for post comments."""
    
    __tablename__ = "comments"

    content = Column(String, nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")

    def __repr__(self) -> str:
        return f"<Comment(id={self.id}, post_id={self.post_id}, author_id={self.author_id})>"