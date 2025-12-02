"""
User model - represents user accounts in the system.
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """User model for authentication and user management."""
    
    __tablename__ = "users"

    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Profile fields
    bio = Column(Text, nullable=True)
    avatar_url = Column(String, nullable=True)
    website = Column(String, nullable=True)
    location = Column(String, nullable=True)
    
    # Account settings
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # Relationships
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    
    # Social relationships
    following = relationship("Follow", 
                           foreign_keys="Follow.follower_id",
                           back_populates="follower", 
                           cascade="all, delete-orphan")
    followers = relationship("Follow", 
                           foreign_keys="Follow.followee_id",
                           back_populates="followee", 
                           cascade="all, delete-orphan")
    notifications = relationship("Notification", 
                               back_populates="user", 
                               cascade="all, delete-orphan")
    
    # Recommendation relationships
    interactions = relationship("UserInteraction", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreference", back_populates="user", cascade="all, delete-orphan")
    recommendation_feedback = relationship("RecommendationFeedback", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"