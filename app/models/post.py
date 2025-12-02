"""
Post model - represents blog posts in the system.
"""

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class Post(Base, TimestampMixin):
    """Post model for blog/content management."""
    
    __tablename__ = "posts"

    title = Column(String, index=True, nullable=False)
    content = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    categories = relationship("Category", secondary="post_category_association", back_populates="posts")
    
    # Recommendation relationships
    interactions = relationship("UserInteraction", back_populates="post", cascade="all, delete-orphan")
    embeddings = relationship("ContentEmbedding", back_populates="post", cascade="all, delete-orphan")
    recommendation_feedback = relationship("RecommendationFeedback", back_populates="post", cascade="all, delete-orphan")
    source_similarities = relationship("SimilarityScore", foreign_keys="SimilarityScore.source_post_id", back_populates="source_post", cascade="all, delete-orphan")
    target_similarities = relationship("SimilarityScore", foreign_keys="SimilarityScore.target_post_id", back_populates="target_post", cascade="all, delete-orphan")
    trending_data = relationship("TrendingContent", back_populates="post", uselist=False, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Post(id={self.id}, title='{self.title}', author_id={self.author_id})>"