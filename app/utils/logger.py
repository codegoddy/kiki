"""
Logging utilities with centralized configuration.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional
from app.core.config import get_settings, is_development, is_production

def setup_logger(
    name: str, 
    log_file: Optional[str] = None, 
    level: Optional[int] = None
) -> logging.Logger:
    """
    Set up logger with file and console handlers using application settings.
    
    Args:
        name: Logger name (typically __name__)
        log_file: Optional log file path (uses settings if not provided)
        level: Optional log level (uses settings if not provided)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    settings = get_settings()
    
    # Use settings if not explicitly provided
    log_level = level or getattr(settings.logging, 'LOG_LEVEL', 'INFO')
    log_format = getattr(settings.logging, 'LOG_FORMAT', 
                        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_file_path = log_file or getattr(settings.logging, 'LOG_FILE', None)
    
    # Convert string level to logging constant
    if isinstance(log_level, str):
        log_level = getattr(logging, log_level.upper())
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Add console handler (always enabled)
    if not is_production():
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
        
        # File handler with rotation (10MB max, 5 backup files)
        file_handler = RotatingFileHandler(
            log_file_path, 
            maxBytes=10*1024*1024, 
            backupCount=5
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with centralized configuration.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return setup_logger(name)

# Global logger instance for the application
logger = get_logger(__name__)

# Specialized loggers for different components
auth_logger = get_logger("app.auth")
api_logger = get_logger("app.api")
db_logger = get_logger("app.database")
security_logger = get_logger("app.security")