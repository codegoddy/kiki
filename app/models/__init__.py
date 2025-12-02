"""
Database models package.

This package contains all SQLAlchemy models organized by domain.
"""

from .base import Base, TimestampMixin
from .associations import post_category_association
from .user import User
from .post import Post
from .comment import Comment
from .category import Category
from .social import Follow, Notification, NotificationType
from .recommendation import (
    UserInteraction, UserPreference, ContentEmbedding, RecommendationFeedback,
    SimilarityScore, TrendingContent
)

# Make association table available at package level
post_category_association = post_category_association

__all__ = [
    "Base",
    "TimestampMixin",
    "post_category_association",
    "User",
    "Post", 
    "Comment",
    "Category",
    "Follow",
    "Notification",
    "NotificationType",
    "UserInteraction",
    "UserPreference", 
    "ContentEmbedding",
    "RecommendationFeedback",
    "SimilarityScore",
    "TrendingContent"
]