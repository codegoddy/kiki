"""
Logging utilities with centralized configuration and structured logging support.
"""

import json
import logging
import logging.config
import os
import sys
import uuid
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from typing import Any, Dict, Optional
from app.core.config import get_settings, is_development, is_production


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ["name", "msg", "args", "levelname", "levelno", "pathname",
                          "filename", "module", "lineno", "funcName", "created", 
                          "msecs", "relativeCreated", "thread", "threadName",
                          "processName", "process", "getMessage", "exc_info",
                          "exc_text", "stack_info"]:
                log_entry[key] = value
        
        return json.dumps(log_entry)


class StructuredLogger:
    """Structured logger with context and correlation tracking."""
    
    def __init__(self, name: str, base_logger: logging.Logger):
        self.name = name
        self.logger = base_logger
    
    def _log_with_context(
        self, 
        level: int, 
        message: str, 
        extra: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Log with additional context."""
        context = kwargs.copy()
        if extra:
            context.update(extra)
        
        self.logger.log(level, message, extra=context)
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log info message with context."""
        self._log_with_context(logging.INFO, message, extra, **kwargs)
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log warning message with context."""
        self._log_with_context(logging.WARNING, message, extra, **kwargs)
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log error message with context."""
        self._log_with_context(logging.ERROR, message, extra, **kwargs)
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log debug message with context."""
        self._log_with_context(logging.DEBUG, message, extra, **kwargs)
    
    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log critical message with context."""
        self._log_with_context(logging.CRITICAL, message, extra, **kwargs)
    
    def exception(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log exception with context."""
        kwargs['exc_info'] = True
        self._log_with_context(logging.ERROR, message, extra, **kwargs)


def setup_logger(
    name: str, 
    log_file: Optional[str] = None, 
    level: Optional[int] = None,
    structured: bool = False
) -> logging.Logger:
    """
    Set up logger with file and console handlers using application settings.
    
    Args:
        name: Logger name (typically __name__)
        log_file: Optional log file path (uses settings if not provided)
        level: Optional log level (uses settings if not provided)
        structured: Whether to use JSON formatting for structured logging
        
    Returns:
        logging.Logger: Configured logger instance
    """
    settings = get_settings()
    
    # Use settings if not explicitly provided
    log_level = level or getattr(settings.logging, 'LOG_LEVEL', 'INFO')
    log_file_path = log_file or getattr(settings.logging, 'LOG_FILE', None)
    
    # Convert string level to logging constant
    if isinstance(log_level, str):
        log_level = getattr(logging, log_level.upper())
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Choose formatter
    if structured:
        formatter = JSONFormatter()
    else:
        log_format = getattr(settings.logging, 'LOG_FORMAT', 
                           '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = logging.Formatter(log_format)
    
    # Add console handler (always enabled)
    if not is_production() or not structured:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Add file handler if log file is specified
    if log_file_path:
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # File handler with rotation (daily for better log management)
        file_handler = TimedRotatingFileHandler(
            log_file_path, 
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str, structured: bool = False) -> StructuredLogger:
    """
    Get a structured logger instance with centralized configuration.
    
    Args:
        name: Logger name (typically __name__)
        structured: Whether to use JSON formatting for structured logging
        
    Returns:
        StructuredLogger: Configured structured logger instance
    """
    base_logger = setup_logger(name, structured=structured)
    return StructuredLogger(name, base_logger)

# Global logger instances
logger = get_logger(__name__)
structured_logger = get_logger(__name__, structured=True)

# Specialized loggers for different components
auth_logger = get_logger("app.auth", structured=True)
api_logger = get_logger("app.api", structured=True)
db_logger = get_logger("app.database", structured=True)
security_logger = get_logger("app.security", structured=True)

# Context manager for request tracking
class RequestContext:
    """Context manager for tracking request context in logs."""
    
    def __init__(self, request_id: Optional[str] = None):
        self.request_id = request_id or str(uuid.uuid4())
    
    def __enter__(self):
        # Set request ID in thread-local storage
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Clear request ID
        pass