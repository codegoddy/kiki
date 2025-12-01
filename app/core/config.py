"""
Application configuration management with environment-based settings.
"""

from typing import Optional, List
from pydantic import BaseSettings, validator
from functools import lru_cache


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    DATABASE_URL: str
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    
    class Config:
        env_prefix = "DATABASE_"


class APISettings(BaseSettings):
    """API configuration settings."""
    
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "FastAPI with PostgreSQL"
    PROJECT_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS settings
    CORS_ALLOW_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    class Config:
        env_prefix = "API_"


class SecuritySettings(BaseSettings):
    """Security and authentication settings."""
    
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # Password settings
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_NUMBERS: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    
    class Config:
        env_prefix = "SECURITY_"


class LoggingSettings(BaseSettings):
    """Logging configuration settings."""
    
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = None
    
    class Config:
        env_prefix = "LOG_"


class Settings(BaseSettings):
    """Main application settings combining all configurations."""
    
    # Additional settings
    ENVIRONMENT: str = "development"
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        valid_envs = ["development", "testing", "staging", "production"]
        if v not in valid_envs:
            raise ValueError(f"Invalid environment: {v}. Must be one of: {valid_envs}")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


def get_database_url() -> str:
    """Get database URL from settings."""
    return get_settings().database.DATABASE_URL


def is_development() -> bool:
    """Check if running in development environment."""
    return get_settings().ENVIRONMENT == "development"


def is_testing() -> bool:
    """Check if running in testing environment."""
    return get_settings().ENVIRONMENT == "testing"


def is_production() -> bool:
    """Check if running in production environment."""
    return get_settings().ENVIRONMENT == "production"