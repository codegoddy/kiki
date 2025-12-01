"""
Built-in domain event handlers.
"""

from typing import List, Dict, Any
from app.core.domain_events import DomainEvent, EventType, EventHandler
from app.utils.logger import get_logger


class UserActivityLogger(EventHandler):
    """Log user activities for audit purposes."""
    
    def __init__(self):
        self.logger = get_logger("user_activity", structured=True)
    
    @property
    def event_types(self) -> List[EventType]:
        return [
            EventType.USER_CREATED,
            EventType.USER_UPDATED,
            EventType.USER_DELETED,
            EventType.USER_AUTHENTICATED
        ]
    
    async def handle(self, event: DomainEvent) -> None:
        """Log user activity events."""
        if event.event_type == EventType.USER_CREATED:
            self.logger.info(
                "User created",
                extra={
                    "user_id": event.event_data["user_id"],
                    "username": event.event_data["username"],
                    "event_id": event.event_id
                }
            )
        elif event.event_type == EventType.USER_AUTHENTICATED:
            self.logger.info(
                "User authenticated",
                extra={
                    "user_id": event.event_data["user_id"],
                    "username": event.event_data["username"],
                    "event_id": event.event_id
                }
            )
        elif event.event_type == EventType.USER_UPDATED:
            self.logger.info(
                "User updated",
                extra={
                    "user_id": event.aggregate_id,
                    "event_id": event.event_id
                }
            )
        elif event.event_type == EventType.USER_DELETED:
            self.logger.info(
                "User deleted",
                extra={
                    "user_id": event.aggregate_id,
                    "event_id": event.event_id
                }
            )


class PostViewCounter(EventHandler):
    """Count post views for analytics."""
    
    def __init__(self):
        self.logger = get_logger("post_views", structured=True)
        self._view_counts: Dict[str, int] = {}
    
    @property
    def event_types(self) -> List[EventType]:
        return [
            EventType.POST_VIEWED,
            EventType.POST_CREATED
        ]
    
    async def handle(self, event: DomainEvent) -> None:
        """Handle post view events."""
        if event.event_type == EventType.POST_VIEWED:
            post_id = event.aggregate_id
            
            # Increment view count
            self._view_counts[post_id] = self._view_counts.get(post_id, 0) + 1
            
            viewer_id = event.event_data.get("viewer_id")
            
            self.logger.info(
                "Post viewed",
                extra={
                    "post_id": post_id,
                    "viewer_id": viewer_id,
                    "total_views": self._view_counts[post_id],
                    "event_id": event.event_id
                }
            )
            
        elif event.event_type == EventType.POST_CREATED:
            self.logger.info(
                "Post created - views initialized",
                extra={
                    "post_id": event.aggregate_id,
                    "author_id": event.event_data["author_id"],
                    "title": event.event_data["title"],
                    "event_id": event.event_id
                }
            )
    
    def get_view_count(self, post_id: str) -> int:
        """Get current view count for a post."""
        return self._view_counts.get(post_id, 0)


class AnalyticsHandler(EventHandler):
    """Handle analytics and reporting events."""
    
    def __init__(self):
        self.logger = get_logger("analytics", structured=True)
        self._metrics: Dict[str, Any] = {
            "user_registrations": 0,
            "post_creations": 0,
            "post_views": 0,
            "comment_creations": 0
        }
    
    @property
    def event_types(self) -> List[EventType]:
        return [
            EventType.USER_CREATED,
            EventType.POST_CREATED,
            EventType.POST_VIEWED,
            EventType.COMMENT_CREATED
        ]
    
    async def handle(self, event: DomainEvent) -> None:
        """Handle analytics events."""
        if event.event_type == EventType.USER_CREATED:
            self._metrics["user_registrations"] += 1
            self.logger.info(
                "Analytics: User registration",
                extra={
                    "total_registrations": self._metrics["user_registrations"],
                    "event_id": event.event_id
                }
            )
            
        elif event.event_type == EventType.POST_CREATED:
            self._metrics["post_creations"] += 1
            self.logger.info(
                "Analytics: Post creation",
                extra={
                    "total_posts": self._metrics["post_creations"],
                    "author_id": event.event_data["author_id"],
                    "event_id": event.event_id
                }
            )
            
        elif event.event_type == EventType.POST_VIEWED:
            self._metrics["post_views"] += 1
            
        elif event.event_type == EventType.COMMENT_CREATED:
            self._metrics["comment_creations"] += 1
    
    def get_metrics(self) -> Dict[str, int]:
        """Get current analytics metrics."""
        return self._metrics.copy()


class NotificationHandler(EventHandler):
    """Handle notification events (placeholder for future implementation)."""
    
    def __init__(self):
        self.logger = get_logger("notifications", structured=True)
    
    @property
    def event_types(self) -> List[EventType]:
        return [
            EventType.USER_CREATED,
            EventType.COMMENT_CREATED,
            EventType.POST_PUBLISHED
        ]
    
    async def handle(self, event: DomainEvent) -> None:
        """Handle notification events."""
        # Placeholder for notification logic
        self.logger.info(
            "Notification event received",
            extra={
                "event_type": event.event_type.value,
                "aggregate_id": event.aggregate_id,
                "event_id": event.event_id
            }
        )


class CacheInvalidationHandler(EventHandler):
    """Handle cache invalidation events."""
    
    def __init__(self):
        self.logger = get_logger("cache_invalidation", structured=True)
    
    @property
    def event_types(self) -> List[EventType]:
        return [
            EventType.USER_UPDATED,
            EventType.USER_DELETED,
            EventType.POST_UPDATED,
            EventType.POST_DELETED,
            EventType.COMMENT_UPDATED,
            EventType.COMMENT_DELETED
        ]
    
    async def handle(self, event: DomainEvent) -> None:
        """Handle cache invalidation events."""
        # Placeholder for cache invalidation logic
        self.logger.info(
            "Cache invalidation event",
            extra={
                "event_type": event.event_type.value,
                "aggregate_id": event.aggregate_id,
                "event_id": event.event_id
            }
        )


class SearchIndexHandler(EventHandler):
    """Handle search index updates."""
    
    def __init__(self):
        self.logger = get_logger("search_index", structured=True)
    
    @property
    def event_types(self) -> List[EventType]:
        return [
            EventType.USER_CREATED,
            EventType.USER_UPDATED,
            EventType.USER_DELETED,
            EventType.POST_CREATED,
            EventType.POST_UPDATED,
            EventType.POST_DELETED,
            EventType.COMMENT_CREATED,
            EventType.COMMENT_UPDATED,
            EventType.COMMENT_DELETED
        ]
    
    async def handle(self, event: DomainEvent) -> None:
        """Handle search index update events."""
        # Placeholder for search indexing logic
        self.logger.info(
            "Search index update",
            extra={
                "event_type": event.event_type.value,
                "aggregate_id": event.aggregate_id,
                "event_id": event.event_id
            }
        )