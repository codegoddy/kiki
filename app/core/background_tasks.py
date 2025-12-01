"""
Background task processing system with async task management.
"""

import asyncio
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Coroutine
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import logging
from app.utils.logger import get_logger


class TaskStatus(Enum):
    """Background task status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class BackgroundTask:
    """Background task definition."""
    
    task_id: str
    name: str
    func: Callable
    args: tuple
    kwargs: dict
    priority: TaskPriority
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    max_retries: int = 3
    retry_count: int = 0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        result = asdict(self)
        result["status"] = self.status.value
        result["priority"] = self.priority.value
        result["created_at"] = self.created_at.isoformat()
        if self.started_at:
            result["started_at"] = self.started_at.isoformat()
        if self.completed_at:
            result["completed_at"] = self.completed_at.isoformat()
        return result


class TaskHandler(ABC):
    """Abstract task handler."""
    
    @abstractmethod
    async def execute(self, task: BackgroundTask) -> Any:
        """Execute the task."""
        pass
    
    @abstractmethod
    def can_handle(self, task_name: str) -> bool:
        """Check if handler can handle the task."""
        pass


class BackgroundTaskManager:
    """Background task manager with queue and execution."""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.tasks: Dict[str, BackgroundTask] = {}
        self.task_queue: List[BackgroundTask] = []
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.logger = get_logger("background_tasks", structured=True)
        self._task_handlers: Dict[str, TaskHandler] = {}
    
    def register_handler(self, handler: TaskHandler):
        """Register a task handler."""
        # Handler registration logic would be implemented
        pass
    
    async def submit_task(
        self,
        name: str,
        func: Callable,
        *args,
        priority: TaskPriority = TaskPriority.NORMAL,
        max_retries: int = 3,
        **kwargs
    ) -> str:
        """Submit a new background task."""
        
        task_id = str(uuid.uuid4())
        task = BackgroundTask(
            task_id=task_id,
            name=name,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            status=TaskStatus.PENDING,
            created_at=datetime.utcnow(),
            max_retries=max_retries
        )
        
        # Store task
        self.tasks[task_id] = task
        
        # Add to queue (sorted by priority)
        self.task_queue.append(task)
        self.task_queue.sort(key=lambda t: t.priority.value, reverse=True)
        
        self.logger.info(
            "Task submitted",
            extra={
                "task_id": task_id,
                "task_name": name,
                "priority": priority.name
            }
        )
        
        # Start processing if not at max capacity
        await self._process_queue()
        
        return task_id
    
    async def get_task_status(self, task_id: str) -> Optional[BackgroundTask]:
        """Get task status by ID."""
        return self.tasks.get(task_id)
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running task."""
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        if task.status in [TaskStatus.PENDING]:
            task.status = TaskStatus.CANCELLED
            self.task_queue = [t for t in self.task_queue if t.task_id != task_id]
            return True
        
        elif task.status == TaskStatus.RUNNING:
            # Cancel running task
            running_task = self.running_tasks.get(task_id)
            if running_task:
                running_task.cancel()
                task.status = TaskStatus.CANCELLED
                return True
        
        return False
    
    async def _process_queue(self):
        """Process tasks in the queue."""
        # Start new tasks if capacity available
        while (
            len(self.running_tasks) < self.max_workers and 
            self.task_queue and
            self.task_queue[0].status == TaskStatus.PENDING
        ):
            
            task = self.task_queue.pop(0)
            await self._execute_task(task)
    
    async def _execute_task(self, task: BackgroundTask):
        """Execute a single task."""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        
        self.logger.info(
            "Task started",
            extra={
                "task_id": task.task_id,
                "task_name": task.name
            }
        )
        
        async def _run_task():
            try:
                # Execute the task function
                if asyncio.iscoroutinefunction(task.func):
                    result = await task.func(*task.args, **task.kwargs)
                else:
                    # Run sync function in thread pool
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        self.executor,
                        lambda: task.func(*task.args, **task.kwargs)
                    )
                
                task.result = result
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.utcnow()
                
                self.logger.info(
                    "Task completed",
                    extra={
                        "task_id": task.task_id,
                        "task_name": task.name,
                        "duration": (task.completed_at - task.started_at).total_seconds()
                    }
                )
                
            except asyncio.CancelledError:
                task.status = TaskStatus.CANCELLED
                task.completed_at = datetime.utcnow()
                self.logger.info(
                    "Task cancelled",
                    extra={
                        "task_id": task.task_id,
                        "task_name": task.name
                    }
                )
                
            except Exception as e:
                task.retry_count += 1
                task.error = str(e)
                
                # Check if we should retry
                if task.retry_count <= task.max_retries:
                    task.status = TaskStatus.PENDING
                    # Re-add to queue with delay
                    await asyncio.sleep(2 ** task.retry_count)  # Exponential backoff
                    self.task_queue.append(task)
                    self.task_queue.sort(key=lambda t: t.priority.value, reverse=True)
                    
                    self.logger.warning(
                        "Task failed, retrying",
                        extra={
                            "task_id": task.task_id,
                            "task_name": task.name,
                            "retry_count": task.retry_count,
                            "error": str(e)
                        }
                    )
                else:
                    task.status = TaskStatus.FAILED
                    task.completed_at = datetime.utcnow()
                    
                    self.logger.error(
                        "Task failed permanently",
                        extra={
                            "task_id": task.task_id,
                            "task_name": task.name,
                            "total_retries": task.retry_count,
                            "error": str(e)
                        }
                    )
            
            finally:
                # Clean up
                if task.task_id in self.running_tasks:
                    del self.running_tasks[task.task_id]
                
                # Process next task in queue
                await self._process_queue()
        
        # Run the task
        task_coroutine = asyncio.create_task(_run_task())
        self.running_tasks[task.task_id] = task_coroutine
    
    async def get_all_tasks(self) -> List[BackgroundTask]:
        """Get all tasks."""
        return list(self.tasks.values())
    
    async def get_tasks_by_status(self, status: TaskStatus) -> List[BackgroundTask]:
        """Get tasks by status."""
        return [task for task in self.tasks.values() if task.status == status]
    
    async def get_statistics(self) -> Dict[str, int]:
        """Get task statistics."""
        stats = {
            "total": len(self.tasks),
            "pending": 0,
            "running": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0
        }
        
        for task in self.tasks.values():
            stats[task.status.value] += 1
        
        return stats


# Predefined background tasks
async def send_email_task(recipient: str, subject: str, content: str):
    """Example email sending task."""
    # Placeholder for email sending logic
    await asyncio.sleep(2)  # Simulate email sending time
    return f"Email sent to {recipient}"


async def generate_report_task(report_type: str, parameters: dict):
    """Example report generation task."""
    # Placeholder for report generation logic
    await asyncio.sleep(5)  # Simulate report generation time
    return f"{report_type} report generated with parameters: {parameters}"


async def cleanup_data_task(cleanup_type: str, days_old: int):
    """Example data cleanup task."""
    # Placeholder for data cleanup logic
    await asyncio.sleep(3)  # Simulate cleanup time
    return f"Cleanup completed for {cleanup_type}, removed data older than {days_old} days"


# Global background task manager
_task_manager: Optional[BackgroundTaskManager] = None


def initialize_background_tasks(max_workers: int = 4) -> BackgroundTaskManager:
    """Initialize the global background task system."""
    global _task_manager
    _task_manager = BackgroundTaskManager(max_workers=max_workers)
    return _task_manager


def get_background_task_manager() -> BackgroundTaskManager:
    """Get the global background task manager."""
    if _task_manager is None:
        raise RuntimeError("Background task system not initialized. Call initialize_background_tasks() first.")
    return _task_manager


async def submit_background_task(
    name: str,
    func: Callable,
    *args,
    priority: TaskPriority = TaskPriority.NORMAL,
    max_retries: int = 3,
    **kwargs
) -> str:
    """Submit a background task using the global manager."""
    manager = get_background_task_manager()
    return await manager.submit_task(name, func, *args, priority=priority, max_retries=max_retries, **kwargs)


# Convenience functions for common tasks
async def submit_email_task(recipient: str, subject: str, content: str) -> str:
    """Submit an email sending task."""
    return await submit_background_task(
        "send_email",
        send_email_task,
        recipient=recipient,
        subject=subject,
        content=content,
        priority=TaskPriority.NORMAL
    )


async def submit_report_task(report_type: str, parameters: dict) -> str:
    """Submit a report generation task."""
    return await submit_background_task(
        "generate_report",
        generate_report_task,
        report_type=report_type,
        parameters=parameters,
        priority=TaskPriority.HIGH
    )


async def submit_cleanup_task(cleanup_type: str, days_old: int) -> str:
    """Submit a data cleanup task."""
    return await submit_background_task(
        "cleanup_data",
        cleanup_data_task,
        cleanup_type=cleanup_type,
        days_old=days_old,
        priority=TaskPriority.LOW
    )