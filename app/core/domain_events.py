"""
Domain events system for implementing event-driven architecture.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable, Type
from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4
from enum import Enum
import asyncio
import logging
from app.utils.logger import get_logger


class EventType(Enum):
    """Domain event types."""
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    USER_AUTHENTICATED = "user.authenticated"
    
    POST_CREATED = "post.created"
    POST_UPDATED = "post.updated"
    POST_DELETED = "post.deleted"
    POST_PUBLISHED = "post.published"
    POST_VIEWED = "post.viewed"
    
    COMMENT_CREATED = "comment.created"
    COMMENT_UPDATED = "comment.updated"
    COMMENT_DELETED = "comment.deleted"
    
    CATEGORY_CREATED = "category.created"
    CATEGORY_UPDATED = "category.updated"
    CATEGORY_DELETED = "category.deleted"


@dataclass
class DomainEvent:
    """Base domain event class."""
    
    event_id: str
    event_type: EventType
    aggregate_id: str
    event_data: Dict[str, Any]
    timestamp: datetime
    version: int = 1
    
    @classmethod
    def create(cls, event_type: EventType, aggregate_id: str, event_data: Dict[str, Any]) -> 'DomainEvent':
        """Create a new domain event."""
        return cls(
            event_id=str(uuid4()),
            event_type=event_type,
            aggregate_id=aggregate_id,
            event_data=event_data,
            timestamp=datetime.utcnow(),
            version=1
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "aggregate_id": self.aggregate_id,
            "event_data": self.event_data,
            "timestamp": self.timestamp.isoformat(),
            "version": self.version
        }


class EventHandler(ABC):
    """Base event handler interface."""
    
    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        """Handle the domain event."""
        pass
    
    @property
    @abstractmethod
    def event_types(self) -> List[EventType]:
        """Return list of event types this handler can handle."""
        pass


class EventStore(ABC):
    """Event store interface for persisting domain events."""
    
    @abstractmethod
    async def save_event(self, event: DomainEvent) -> None:
        """Save a domain event."""
        pass
    
    @abstractmethod
    async def get_events_for_aggregate(self, aggregate_id: str) -> List[DomainEvent]:
        """Get all events for a specific aggregate."""
        pass
    
    @abstractmethod
    async def get_events_by_type(self, event_type: EventType) -> List[DomainEvent]:
        """Get all events of a specific type."""
        pass


class MemoryEventStore(EventStore):
    """In-memory event store for development and testing."""
    
    def __init__(self):
        self._events: Dict[str, List[DomainEvent]] = {}
        self._logger = get_logger("event_store", structured=True)
    
    async def save_event(self, event: DomainEvent) -> None:
        """Save a domain event to memory."""
        if event.aggregate_id not in self._events:
            self._events[event.aggregate_id] = []
        
        self._events[event.aggregate_id].append(event)
        
        self._logger.info(
            "Event saved",
            extra={
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "aggregate_id": event.aggregate_id
            }
        )
    
    async def get_events_for_aggregate(self, aggregate_id: str) -> List[DomainEvent]:
        """Get all events for a specific aggregate."""
        return self._events.get(aggregate_id, [])
    
    async def get_events_by_type(self, event_type: EventType) -> List[DomainEvent]:
        """Get all events of a specific type."""
        events = []
        for aggregate_events in self._events.values():
            events.extend([e for e in aggregate_events if e.event_type == event_type])
        return events


class EventBus:
    """Event bus for publishing and subscribing to domain events."""
    
    def __init__(self, event_store: EventStore):
        self._event_store = event_store
        self._handlers: Dict[EventType, List[EventHandler]] = {}
        self._logger = get_logger("event_bus", structured=True)
    
    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Subscribe an event handler to an event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        
        self._handlers[event_type].append(handler)
        
        self._logger.info(
            "Handler subscribed",
            extra={
                "event_type": event_type.value,
                "handler": handler.__class__.__name__
            }
        )
    
    def subscribe_multiple(self, handler: EventHandler) -> None:
        """Subscribe a handler to multiple event types."""
        for event_type in handler.event_types:
            self.subscribe(event_type, handler)
    
    async def publish(self, event: DomainEvent) -> None:
        """Publish a domain event."""
        # Save event to store
        await self._event_store.save_event(event)
        
        # Get handlers for this event type
        handlers = self._handlers.get(event.event_type, [])
        
        if not handlers:
            self._logger.debug(
                "No handlers found for event",
                extra={
                    "event_id": event.event_id,
                    "event_type": event.event_type.value
                }
            )
            return
        
        # Execute handlers asynchronously
        tasks = []
        for handler in handlers:
            try:
                task = asyncio.create_task(handler.handle(event))
                tasks.append(task)
            except Exception as e:
                self._logger.error(
                    "Failed to create handler task",
                    extra={
                        "handler": handler.__class__.__name__,
                        "error": str(e)
                    }
                )
        
        if tasks:
            # Wait for all handlers to complete (or fail)
            await asyncio.gather(*tasks, return_exceptions=True)
        
        self._logger.info(
            "Event published",
            extra={
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "handler_count": len(handlers)
            }
        )


class DomainEventPublisher:
    """Domain event publisher utility."""
    
    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus
    
    async def publish_user_created(self, user_id: int, username: str, email: str) -> None:
        """Publish user created event."""
        event = DomainEvent.create(
            EventType.USER_CREATED,
            str(user_id),
            {
                "user_id": user_id,
                "username": username,
                "email": email
            }
        )
        await self._event_bus.publish(event)
    
    async def publish_user_authenticated(self, user_id: int, username: str) -> None:
        """Publish user authenticated event."""
        event = DomainEvent.create(
            EventType.USER_AUTHENTICATED,
            str(user_id),
            {
                "user_id": user_id,
                "username": username
            }
        )
        await self._event_bus.publish(event)
    
    async def publish_post_created(self, post_id: int, author_id: int, title: str) -> None:
        """Publish post created event."""
        event = DomainEvent.create(
            EventType.POST_CREATED,
            str(post_id),
            {
                "post_id": post_id,
                "author_id": author_id,
                "title": title
            }
        )
        await self._event_bus.publish(event)
    
    async def publish_post_viewed(self, post_id: int, viewer_id: Optional[int] = None) -> None:
        """Publish post viewed event."""
        event = DomainEvent.create(
            EventType.POST_VIEWED,
            str(post_id),
            {
                "post_id": post_id,
                "viewer_id": viewer_id
            }
        )
        await self._event_bus.publish(event)


# Global event instances
_event_bus: Optional[EventBus] = None
_event_publisher: Optional[DomainEventPublisher] = None


def initialize_event_system(event_store: Optional[EventStore] = None) -> None:
    """Initialize the global event system."""
    global _event_bus, _event_publisher
    
    if event_store is None:
        event_store = MemoryEventStore()
    
    _event_bus = EventBus(event_store)
    _event_publisher = DomainEventPublisher(_event_bus)
    
    # Subscribe built-in handlers
    _setup_builtin_handlers()


def get_event_bus() -> EventBus:
    """Get the global event bus."""
    if _event_bus is None:
        raise RuntimeError("Event system not initialized. Call initialize_event_system() first.")
    return _event_bus


def get_event_publisher() -> DomainEventPublisher:
    """Get the global event publisher."""
    if _event_publisher is None:
        raise RuntimeError("Event system not initialized. Call initialize_event_system() first.")
    return _event_publisher


def _setup_builtin_handlers() -> None:
    """Set up built-in event handlers."""
    from app.core.event_handlers import (
        UserActivityLogger,
        PostViewCounter,
        AnalyticsHandler
    )
    
    event_bus = get_event_bus()
    
    # Subscribe built-in handlers
    event_bus.subscribe_multiple(UserActivityLogger())
    event_bus.subscribe_multiple(PostViewCounter())
    event_bus.subscribe_multiple(AnalyticsHandler())