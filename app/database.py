"""
Database configuration and session management.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Generator
import logging

from app.core.config import get_database_url, get_settings

# Get application settings
settings = get_settings()

# Create database engine with optimized settings
engine = create_engine(
    get_database_url(),
    poolclass=QueuePool,
    pool_size=settings.database.DATABASE_POOL_SIZE,
    max_overflow=settings.database.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=3600,  # 1 hour
    echo=settings.database.DATABASE_ECHO,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set SQLite PRAGMA for foreign key support (only for SQLite)."""
    if "sqlite" in get_database_url():
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Log database connection info
logger = logging.getLogger(__name__)
logger.info("Database engine initialized with connection pooling")