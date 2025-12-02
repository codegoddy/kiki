"""
Social features service - handling follow relationships and notifications.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import User, Follow, Notification, NotificationType
from app.schemas.user import FollowRequest, NotificationCreate, NotificationResponse, NotificationUpdate
from app.core.base_service import BaseService
from app.core.exceptions import ValidationError, BusinessLogicError, EntityNotFoundError
from app.utils.logger import get_logger


class SocialService(BaseService[Follow, Dict[str, Any], Dict[str, Any]]):
    """Service for managing social features like following and notifications."""
    
    def __init__(self, db: Session):
        super().__init__(None)  # We'll handle repositories manually for now
        self.db = db
        self.logger = get_logger("social_service", structured=True)
    
    async def follow_user(self, follower_id: int, followee_id: int) -> Dict[str, Any]:
        """Follow a user."""
        try:
            # Validate users exist
            follower = self.db.query(User).filter(User.id == follower_id).first()
            if not follower:
                raise EntityNotFoundError("Follower user", follower_id)
            
            followee = self.db.query(User).filter(User.id == followee_id).first()
            if not followee:
                raise EntityNotFoundError("Followee user", followee_id)
            
            # Check if already following
            existing_follow = self.db.query(Follow).filter(
                and_(Follow.follower_id == follower_id, Follow.followee_id == followee_id)
            ).first()
            
            if existing_follow:
                if existing_follow.is_active:
                    raise ValidationError("follow", "Already following this user")
                else:
                    # Reactivate the follow relationship
                    existing_follow.is_active = True
                    self.db.commit()
                    self.db.refresh(existing_follow)
                    return self._serialize_follow(existing_follow)
            
            # Create new follow relationship
            follow = Follow(follower_id=follower_id, followee_id=followee_id)
            self.db.add(follow)
            self.db.commit()
            self.db.refresh(follow)
            
            # Create notification for the followed user
            await self._create_notification(
                user_id=followee_id,
                actor_id=follower_id,
                notification_type=NotificationType.NEW_FOLLOWER,
                title="New Follower",
                message=f"{follower.username} started following you",
                entity_type="user",
                entity_id=follower_id
            )
            
            self.logger.info(
                "User followed successfully",
                extra={
                    "follower_id": follower_id,
                    "followee_id": followee_id,
                    "follow_id": follow.id
                }
            )
            
            return self._serialize_follow(follow)
            
        except (ValidationError, EntityNotFoundError):
            raise
        except Exception as e:
            self.db.rollback()
            self.logger.error(
                "Failed to follow user",
                extra={
                    "follower_id": follower_id,
                    "followee_id": followee_id,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            raise BusinessLogicError(f"Failed to follow user: {str(e)}")
    
    async def unfollow_user(self, follower_id: int, followee_id: int) -> Dict[str, Any]:
        """Unfollow a user."""
        try:
            follow = self.db.query(Follow).filter(
                and_(Follow.follower_id == follower_id, Follow.followee_id == followee_id, Follow.is_active == True)
            ).first()
            
            if not follow:
                raise EntityNotFoundError("Follow relationship", f"{follower_id} -> {followee_id}")
            
            follow.is_active = False
            self.db.commit()
            self.db.refresh(follow)
            
            self.logger.info(
                "User unfollowed successfully",
                extra={
                    "follower_id": follower_id,
                    "followee_id": followee_id,
                    "follow_id": follow.id
                }
            )
            
            return self._serialize_follow(follow)
            
        except EntityNotFoundError:
            raise
        except Exception as e:
            self.db.rollback()
            self.logger.error(
                "Failed to unfollow user",
                extra={
                    "follower_id": follower_id,
                    "followee_id": followee_id,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            raise BusinessLogicError(f"Failed to unfollow user: {str(e)}")
    
    async def get_followers(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get followers of a user."""
        try:
            followers = self.db.query(Follow).filter(
                and_(Follow.followee_id == user_id, Follow.is_active == True)
            ).offset(skip).limit(limit).all()
            
            return [self._serialize_follow(follow) for follow in followers]
            
        except Exception as e:
            self.logger.error(
                "Failed to get followers",
                extra={
                    "user_id": user_id,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            raise BusinessLogicError(f"Failed to get followers: {str(e)}")
    
    async def get_following(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get users that a user is following."""
        try:
            following = self.db.query(Follow).filter(
                and_(Follow.follower_id == user_id, Follow.is_active == True)
            ).offset(skip).limit(limit).all()
            
            return [self._serialize_follow(follow) for follow in following]
            
        except Exception as e:
            self.logger.error(
                "Failed to get following",
                extra={
                    "user_id": user_id,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            raise BusinessLogicError(f"Failed to get following: {str(e)}")
    
    async def is_following(self, follower_id: int, followee_id: int) -> bool:
        """Check if one user is following another."""
        try:
            follow = self.db.query(Follow).filter(
                and_(Follow.follower_id == follower_id, Follow.followee_id == followee_id, Follow.is_active == True)
            ).first()
            
            return follow is not None
            
        except Exception as e:
            self.logger.error(
                "Failed to check follow status",
                extra={
                    "follower_id": follower_id,
                    "followee_id": followee_id,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            raise BusinessLogicError(f"Failed to check follow status: {str(e)}")
    
    async def get_follow_counts(self, user_id: int) -> Dict[str, int]:
        """Get follower and following counts for a user."""
        try:
            followers_count = self.db.query(Follow).filter(
                and_(Follow.followee_id == user_id, Follow.is_active == True)
            ).count()
            
            following_count = self.db.query(Follow).filter(
                and_(Follow.follower_id == user_id, Follow.is_active == True)
            ).count()
            
            return {
                "followers_count": followers_count,
                "following_count": following_count
            }
            
        except Exception as e:
            self.logger.error(
                "Failed to get follow counts",
                extra={
                    "user_id": user_id,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            raise BusinessLogicError(f"Failed to get follow counts: {str(e)}")
    
    async def create_notification(self, notification_data: NotificationCreate) -> Dict[str, Any]:
        """Create a notification."""
        try:
            notification = Notification(
                user_id=notification_data.user_id,
                actor_id=notification_data.actor_id,
                notification_type=notification_data.notification_type,
                title=notification_data.title,
                message=notification_data.message,
                entity_type=notification_data.entity_type,
                entity_id=notification_data.entity_id
            )
            
            self.db.add(notification)
            self.db.commit()
            self.db.refresh(notification)
            
            self.logger.info(
                "Notification created",
                extra={
                    "notification_id": notification.id,
                    "user_id": notification_data.user_id,
                    "type": notification_data.notification_type
                }
            )
            
            return self._serialize_notification(notification)
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(
                "Failed to create notification",
                extra={
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            raise BusinessLogicError(f"Failed to create notification: {str(e)}")
    
    async def get_user_notifications(self, user_id: int, skip: int = 0, limit: int = 100, unread_only: bool = False) -> List[Dict[str, Any]]:
        """Get notifications for a user."""
        try:
            query = self.db.query(Notification).filter(Notification.user_id == user_id)
            
            if unread_only:
                query = query.filter(Notification.is_read == False)
            
            notifications = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
            
            return [self._serialize_notification(notification) for notification in notifications]
            
        except Exception as e:
            self.logger.error(
                "Failed to get user notifications",
                extra={
                    "user_id": user_id,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            raise BusinessLogicError(f"Failed to get user notifications: {str(e)}")
    
    async def mark_notification_read(self, notification_id: int, user_id: int) -> Dict[str, Any]:
        """Mark a notification as read."""
        try:
            notification = self.db.query(Notification).filter(
                and_(Notification.id == notification_id, Notification.user_id == user_id)
            ).first()
            
            if not notification:
                raise EntityNotFoundError("Notification", notification_id)
            
            notification.is_read = True
            self.db.commit()
            self.db.refresh(notification)
            
            return self._serialize_notification(notification)
            
        except EntityNotFoundError:
            raise
        except Exception as e:
            self.db.rollback()
            self.logger.error(
                "Failed to mark notification as read",
                extra={
                    "notification_id": notification_id,
                    "user_id": user_id,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            raise BusinessLogicError(f"Failed to mark notification as read: {str(e)}")
    
    async def mark_all_notifications_read(self, user_id: int) -> int:
        """Mark all notifications as read for a user."""
        try:
            updated_count = self.db.query(Notification).filter(
                and_(Notification.user_id == user_id, Notification.is_read == False)
            ).update({"is_read": True})
            
            self.db.commit()
            
            self.logger.info(
                "All notifications marked as read",
                extra={
                    "user_id": user_id,
                    "updated_count": updated_count
                }
            )
            
            return updated_count
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(
                "Failed to mark all notifications as read",
                extra={
                    "user_id": user_id,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            raise BusinessLogicError(f"Failed to mark all notifications as read: {str(e)}")
    
    async def _create_notification(self, user_id: int, actor_id: Optional[int], notification_type: NotificationType, 
                                 title: str, message: str, entity_type: Optional[str] = None, entity_id: Optional[int] = None) -> Dict[str, Any]:
        """Helper method to create notifications."""
        notification_data = NotificationCreate(
            user_id=user_id,
            actor_id=actor_id,
            notification_type=notification_type.value,
            title=title,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id
        )
        
        return await self.create_notification(notification_data)
    
    def _serialize_follow(self, follow: Follow) -> Dict[str, Any]:
        """Serialize follow relationship to dictionary."""
        return {
            "id": follow.id,
            "follower_id": follow.follower_id,
            "followee_id": follow.followee_id,
            "is_active": follow.is_active,
            "created_at": follow.created_at.isoformat() if follow.created_at else None,
            "follower": {
                "id": follow.follower.id,
                "username": follow.follower.username,
                "avatar_url": follow.follower.avatar_url
            } if follow.follower else None,
            "followee": {
                "id": follow.followee.id,
                "username": follow.followee.username,
                "avatar_url": follow.followee.avatar_url
            } if follow.followee else None
        }
    
    def _serialize_notification(self, notification: Notification) -> Dict[str, Any]:
        """Serialize notification to dictionary."""
        return {
            "id": notification.id,
            "user_id": notification.user_id,
            "actor_id": notification.actor_id,
            "notification_type": notification.notification_type.value,
            "title": notification.title,
            "message": notification.message,
            "entity_type": notification.entity_type,
            "entity_id": notification.entity_id,
            "is_read": notification.is_read,
            "created_at": notification.created_at.isoformat() if notification.created_at else None,
            "updated_at": notification.updated_at.isoformat() if notification.updated_at else None,
            "actor_username": notification.actor.username if notification.actor else None,
            "actor_avatar_url": notification.actor.avatar_url if notification.actor else None
        }