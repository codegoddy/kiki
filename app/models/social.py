"""
Social features models - Follow relationships and Notifications.
"""

from sqlalchemy import Column, Integer, DateTime, String, Boolean, Text, ForeignKey, Enum as SqlEnum
from sqlalchemy.orm import relationship
from enum import Enum
from .base import Base, TimestampMixin


class NotificationType(str, Enum):
    """Types of notifications users can receive."""
    NEW_FOLLOWER = "new_follower"
    NEW_COMMENT = "new_comment" 
    NEW_POST = "new_post"
    MENTION = "mention"
    LIKE = "like"
    SYSTEM = "system"


class Follow(Base, TimestampMixin):
    """Model for user follow relationships."""
    
    __tablename__ = "follows"
    
    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    followee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")
    followee = relationship("User", foreign_keys=[followee_id], back_populates="followers")
    
    # Ensure unique follow relationship
    __table_args__ = (
        {"extend_existing": True},
    )
    
    def __repr__(self) -> str:
        return f"<Follow(follower_id={self.follower_id}, followee_id={self.followee_id})>"


class Notification(Base, TimestampMixin):
    """Model for user notifications."""
    
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Who triggered the notification
    notification_type = Column(SqlEnum(NotificationType), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    entity_type = Column(String(50), nullable=True)  # post, comment, user, etc.
    entity_id = Column(Integer, nullable=True)  # ID of the related entity
    is_read = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="notifications")
    actor = relationship("User", foreign_keys=[actor_id])
    
    def __repr__(self) -> str:
        return f"<Notification(user_id={self.user_id}, type={self.notification_type})>"