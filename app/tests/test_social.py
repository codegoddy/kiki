"""
Tests for social features - following and notifications.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.social import Follow, Notification, NotificationType
from app.models.user import User
from app.models.base import Base
from app.services.social import SocialService
from app.core.exceptions import EntityNotFoundError, ValidationError


# Test database setup
SQLITE_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLITE_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    """Create database session for testing."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def social_service(db):
    """Create social service instance for testing."""
    return SocialService(db)


@pytest.fixture
def test_user1(db):
    """Create first test user."""
    user = User(
        username="testuser1",
        email="test1@example.com",
        hashed_password="hashed_password_1"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_user2(db):
    """Create second test user."""
    user = User(
        username="testuser2",
        email="test2@example.com",
        hashed_password="hashed_password_2"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


class TestSocialService:
    """Test social service functionality."""
    
    def test_follow_user(self, social_service, test_user1, test_user2):
        """Test following a user."""
        follow = social_service.follow_user(test_user1.id, test_user2.id)
        
        assert follow["follower_id"] == test_user1.id
        assert follow["followee_id"] == test_user2.id
        assert follow["is_active"] is True
        
        # Verify follow relationship exists in database
        follow_record = social_service.db.query(Follow).filter(
            Follow.follower_id == test_user1.id,
            Follow.followee_id == test_user2.id
        ).first()
        
        assert follow_record is not None
        assert follow_record.is_active is True
    
    def test_follow_same_user_error(self, social_service, test_user1):
        """Test that user cannot follow themselves."""
        with pytest.raises(ValidationError):
            social_service.follow_user(test_user1.id, test_user1.id)
    
    def test_follow_nonexistent_user(self, social_service, test_user1):
        """Test following non-existent user raises error."""
        with pytest.raises(EntityNotFoundError):
            social_service.follow_user(test_user1.id, 999)
    
    def test_unfollow_user(self, social_service, test_user1, test_user2):
        """Test unfollowing a user."""
        # First follow the user
        social_service.follow_user(test_user1.id, test_user2.id)
        
        # Then unfollow
        follow = social_service.unfollow_user(test_user1.id, test_user2.id)
        
        assert follow["is_active"] is False
        
        # Verify follow relationship is deactivated
        follow_record = social_service.db.query(Follow).filter(
            Follow.follower_id == test_user1.id,
            Follow.followee_id == test_user2.id
        ).first()
        
        assert follow_record.is_active is False
    
    def test_unfollow_nonexistent_relationship(self, social_service, test_user1, test_user2):
        """Test unfollowing without existing follow relationship raises error."""
        with pytest.raises(EntityNotFoundError):
            social_service.unfollow_user(test_user1.id, test_user2.id)
    
    def test_is_following(self, social_service, test_user1, test_user2):
        """Test checking follow status."""
        # Initially not following
        assert social_service.is_following(test_user1.id, test_user2.id) is False
        
        # After following
        social_service.follow_user(test_user1.id, test_user2.id)
        assert social_service.is_following(test_user1.id, test_user2.id) is True
        
        # After unfollowing
        social_service.unfollow_user(test_user1.id, test_user2.id)
        assert social_service.is_following(test_user1.id, test_user2.id) is False
    
    def test_get_follow_counts(self, social_service, test_user1, test_user2, db):
        """Test getting follower and following counts."""
        # Create additional test users
        test_user3 = User(
            username="testuser3",
            email="test3@example.com",
            hashed_password="hashed_password_3"
        )
        db.add(test_user3)
        db.commit()
        db.refresh(test_user3)
        
        # User1 follows User2
        social_service.follow_user(test_user1.id, test_user2.id)
        
        # User1 is followed by User3
        social_service.follow_user(test_user3.id, test_user1.id)
        
        # Check User1's counts
        counts = social_service.get_follow_counts(test_user1.id)
        assert counts["followers_count"] == 1  # User3 follows User1
        assert counts["following_count"] == 1  # User1 follows User2
        
        # Check User2's counts
        counts = social_service.get_follow_counts(test_user2.id)
        assert counts["followers_count"] == 1  # User1 follows User2
        assert counts["following_count"] == 0  # User2 follows no one
    
    def test_create_notification(self, social_service, test_user1, test_user2):
        """Test creating notifications."""
        notification = social_service.create_notification({
            "user_id": test_user2.id,
            "actor_id": test_user1.id,
            "notification_type": NotificationType.NEW_FOLLOWER.value,
            "title": "New Follower",
            "message": f"{test_user1.username} started following you",
            "entity_type": "user",
            "entity_id": test_user1.id
        })
        
        assert notification["user_id"] == test_user2.id
        assert notification["actor_id"] == test_user1.id
        assert notification["notification_type"] == NotificationType.NEW_FOLLOWER.value
        assert notification["title"] == "New Follower"
        assert notification["is_read"] is False
        
        # Verify notification exists in database
        notification_record = social_service.db.query(Notification).filter(
            Notification.user_id == test_user2.id
        ).first()
        
        assert notification_record is not None
        assert notification_record.is_read is False
    
    def test_get_user_notifications(self, social_service, test_user1, test_user2):
        """Test getting user notifications."""
        # Create multiple notifications
        social_service.create_notification({
            "user_id": test_user2.id,
            "actor_id": test_user1.id,
            "notification_type": NotificationType.NEW_FOLLOWER.value,
            "title": "New Follower",
            "message": "Someone followed you",
            "entity_type": "user",
            "entity_id": test_user1.id
        })
        
        social_service.create_notification({
            "user_id": test_user2.id,
            "actor_id": test_user1.id,
            "notification_type": NotificationType.NEW_POST.value,
            "title": "New Post",
            "message": "Someone posted something",
            "entity_type": "post",
            "entity_id": 123
        })
        
        # Get all notifications
        notifications = social_service.get_user_notifications(test_user2.id)
        assert len(notifications) == 2
        
        # Test pagination
        notifications_limited = social_service.get_user_notifications(test_user2.id, limit=1)
        assert len(notifications_limited) == 1
    
    def test_mark_notification_read(self, social_service, test_user1, test_user2):
        """Test marking notification as read."""
        # Create notification
        notification = social_service.create_notification({
            "user_id": test_user2.id,
            "actor_id": test_user1.id,
            "notification_type": NotificationType.NEW_FOLLOWER.value,
            "title": "New Follower",
            "message": "Someone followed you",
            "entity_type": "user",
            "entity_id": test_user1.id
        })
        
        # Mark as read
        updated_notification = social_service.mark_notification_read(notification["id"], test_user2.id)
        assert updated_notification["is_read"] is True
        
        # Verify in database
        notification_record = social_service.db.query(Notification).filter(
            Notification.id == notification["id"]
        ).first()
        assert notification_record.is_read is True
    
    def test_mark_all_notifications_read(self, social_service, test_user1, test_user2):
        """Test marking all notifications as read."""
        # Create multiple unread notifications
        for i in range(3):
            social_service.create_notification({
                "user_id": test_user2.id,
                "actor_id": test_user1.id,
                "notification_type": NotificationType.NEW_FOLLOWER.value,
                "title": f"New Follower {i}",
                "message": f"Someone followed you {i}",
                "entity_type": "user",
                "entity_id": test_user1.id
            })
        
        # Mark all as read
        updated_count = social_service.mark_all_notifications_read(test_user2.id)
        assert updated_count == 3
        
        # Verify all notifications are read
        notifications = social_service.get_user_notifications(test_user2.id, unread_only=True)
        assert len(notifications) == 0
        
        # Get all notifications to verify they're read
        all_notifications = social_service.get_user_notifications(test_user2.id)
        assert all(notification["is_read"] for notification in all_notifications)


# Integration tests for API endpoints would go here
# These would test the actual FastAPI endpoints with the social service


@pytest.mark.asyncio
async def test_follow_user_api_integration():
    """Integration test for follow user API endpoint."""
    # This would test the actual API endpoint
    # Requires setting up the FastAPI test client
    pass


@pytest.mark.asyncio 
async def test_notifications_api_integration():
    """Integration test for notifications API endpoints."""
    # This would test the actual API endpoints
    # Requires setting up the FastAPI test client
    pass