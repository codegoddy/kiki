"""
Social features API endpoints - following and notifications.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import (
    FollowRequest, FollowResponse, NotificationResponse, NotificationUpdate,
    UserProfile
)
from app.services.social import SocialService
from app.services.user_service import UserService
from app.auth.auth import get_current_user
from app.models import User
from app.utils.logger import get_logger


router = APIRouter(prefix="/social", tags=["social"])
logger = get_logger("social_api", structured=True)


# Dependency to get services
def get_social_service(db: Session = Depends(get_db)) -> SocialService:
    """Get social service instance."""
    return SocialService(db)


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Get user service instance."""
    from app.core.repositories import UserRepository
    user_repo = UserRepository(db)
    return UserService(user_repo)


# Follow/Unfollow Endpoints
@router.post("/follow/{user_id}", response_model=FollowResponse)
async def follow_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    social_service: SocialService = Depends(get_social_service)
):
    """Follow a user."""
    try:
        if current_user.id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot follow yourself"
            )
        
        follow = await social_service.follow_user(current_user.id, user_id)
        return FollowResponse(**follow)
        
    except Exception as e:
        logger.error(
            "Failed to follow user",
            extra={
                "follower_id": current_user.id,
                "followee_id": user_id,
                "error": str(e)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/follow/{user_id}", response_model=FollowResponse)
async def unfollow_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    social_service: SocialService = Depends(get_social_service)
):
    """Unfollow a user."""
    try:
        follow = await social_service.unfollow_user(current_user.id, user_id)
        return FollowResponse(**follow)
        
    except Exception as e:
        logger.error(
            "Failed to unfollow user",
            extra={
                "follower_id": current_user.id,
                "followee_id": user_id,
                "error": str(e)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/followers/{user_id}", response_model=List[FollowResponse])
async def get_followers(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    social_service: SocialService = Depends(get_social_service)
):
    """Get followers of a user."""
    try:
        followers = await social_service.get_followers(user_id, skip, limit)
        return [FollowResponse(**follower) for follower in followers]
        
    except Exception as e:
        logger.error(
            "Failed to get followers",
            extra={
                "user_id": user_id,
                "error": str(e)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/following/{user_id}", response_model=List[FollowResponse])
async def get_following(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    social_service: SocialService = Depends(get_social_service)
):
    """Get users that a user is following."""
    try:
        following = await social_service.get_following(user_id, skip, limit)
        return [FollowResponse(**follow) for follow in following]
        
    except Exception as e:
        logger.error(
            "Failed to get following",
            extra={
                "user_id": user_id,
                "error": str(e)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/is-following/{user_id}")
async def check_follow_status(
    user_id: int,
    current_user: User = Depends(get_current_user),
    social_service: SocialService = Depends(get_social_service)
):
    """Check if current user is following another user."""
    try:
        is_following = await social_service.is_following(current_user.id, user_id)
        return {"is_following": is_following}
        
    except Exception as e:
        logger.error(
            "Failed to check follow status",
            extra={
                "follower_id": current_user.id,
                "followee_id": user_id,
                "error": str(e)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/follow-stats/{user_id}")
async def get_follow_stats(
    user_id: int,
    social_service: SocialService = Depends(get_social_service)
):
    """Get follower and following counts for a user."""
    try:
        stats = await social_service.get_follow_counts(user_id)
        return stats
        
    except Exception as e:
        logger.error(
            "Failed to get follow stats",
            extra={
                "user_id": user_id,
                "error": str(e)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Notification Endpoints
@router.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    unread_only: bool = Query(False),
    current_user: User = Depends(get_current_user),
    social_service: SocialService = Depends(get_social_service)
):
    """Get notifications for the current user."""
    try:
        notifications = await social_service.get_user_notifications(
            current_user.id, skip, limit, unread_only
        )
        return [NotificationResponse(**notification) for notification in notifications]
        
    except Exception as e:
        logger.error(
            "Failed to get notifications",
            extra={
                "user_id": current_user.id,
                "error": str(e)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/notifications/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    social_service: SocialService = Depends(get_social_service)
):
    """Mark a notification as read."""
    try:
        notification = await social_service.mark_notification_read(notification_id, current_user.id)
        return NotificationResponse(**notification)
        
    except Exception as e:
        logger.error(
            "Failed to mark notification as read",
            extra={
                "notification_id": notification_id,
                "user_id": current_user.id,
                "error": str(e)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/notifications/read-all")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    social_service: SocialService = Depends(get_social_service)
):
    """Mark all notifications as read for the current user."""
    try:
        updated_count = await social_service.mark_all_notifications_read(current_user.id)
        return {"updated_count": updated_count}
        
    except Exception as e:
        logger.error(
            "Failed to mark all notifications as read",
            extra={
                "user_id": current_user.id,
                "error": str(e)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# User Profile Endpoint with Social Info
@router.get("/profile/{user_id}", response_model=UserProfile)
async def get_user_profile(
    user_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    social_service: SocialService = Depends(get_social_service),
    user_service: UserService = Depends(get_user_service)
):
    """Get user profile with social information."""
    try:
        # Get basic user info
        user_data = await user_service.get(user_id)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get follow counts
        follow_counts = await social_service.get_follow_count(user_id)
        
        # Check if current user is following this user
        is_following = False
        if current_user and current_user.id != user_id:
            is_following = await social_service.is_following(current_user.id, user_id)
        
        # Create enhanced profile
        profile_data = {
            **user_data,
            **follow_counts,
            "is_following": is_following
        }
        
        return UserProfile(**profile_data)
        
    except Exception as e:
        logger.error(
            "Failed to get user profile",
            extra={
                "user_id": user_id,
                "error": str(e)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )