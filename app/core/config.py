"""
Application configuration management with modern pydantic-settings.
"""

from typing import Optional, List, Any
from functools import lru_cache
from pydantic import field_validator, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    model_config = SettingsConfigDict(env_prefix="DATABASE_", case_sensitive=False)
    
    url: str
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10
    
    @property
    def DATABASE_URL(self) -> str:
        """Get database URL for backward compatibility."""
        return self.url


class APISettings(BaseSettings):
    """API configuration settings."""
    
    model_config = SettingsConfigDict(env_prefix="API_", case_sensitive=False)
    
    v1_str: str = "/api/v1"
    project_name: str = "FastAPI with PostgreSQL"
    project_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS settings
    cors_allow_origins: List[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    
    @property
    def API_V1_STR(self) -> str:
        """Get API v1 string for backward compatibility."""
        return self.v1_str
    
    @property
    def PROJECT_NAME(self) -> str:
        """Get project name for backward compatibility."""
        return self.project_name
    
    @property
    def PROJECT_VERSION(self) -> str:
        """Get project version for backward compatibility."""
        return self.project_version
    
    @property
    def DEBUG(self) -> bool:
        """Get debug flag for backward compatibility."""
        return self.debug
    
    @property
    def CORS_ALLOW_ORIGINS(self) -> List[str]:
        """Get CORS allow origins for backward compatibility."""
        return self.cors_allow_origins
    
    @property
    def CORS_ALLOW_CREDENTIALS(self) -> bool:
        """Get CORS allow credentials for backward compatibility."""
        return self.cors_allow_credentials
    
    @property
    def CORS_ALLOW_METHODS(self) -> List[str]:
        """Get CORS allow methods for backward compatibility."""
        return self.cors_allow_methods
    
    @property
    def CORS_ALLOW_HEADERS(self) -> List[str]:
        """Get CORS allow headers for backward compatibility."""
        return self.cors_allow_headers


class SecuritySettings(BaseSettings):
    """Security and authentication settings."""
    
    model_config = SettingsConfigDict(env_prefix="SECURITY_", case_sensitive=False)
    
    secret_key: str
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"
    
    # Password settings
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_special: bool = True
    
    @property
    def SECRET_KEY(self) -> str:
        """Get secret key for backward compatibility."""
        return self.secret_key
    
    @property
    def ACCESS_TOKEN_EXPIRE_MINUTES(self) -> int:
        """Get access token expire minutes for backward compatibility."""
        return self.access_token_expire_minutes
    
    @property
    def ALGORITHM(self) -> str:
        """Get algorithm for backward compatibility."""
        return self.algorithm


class LoggingSettings(BaseSettings):
    """Logging configuration settings."""
    
    model_config = SettingsConfigDict(env_prefix="LOG_", case_sensitive=False)
    
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = None
    
    @property
    def LOG_LEVEL(self) -> str:
        """Get log level for backward compatibility."""
        return self.level
    
    @property
    def LOG_FORMAT(self) -> str:
        """Get log format for backward compatibility."""
        return self.format
    
    @property
    def LOG_FILE(self) -> Optional[str]:
        """Get log file for backward compatibility."""
        return self.file


class Settings(BaseSettings):
    """Main application settings combining all configurations."""
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Sub-configurations
    database: DatabaseSettings = DatabaseSettings()
    api: APISettings = APISettings()
    security: SecuritySettings = SecuritySettings()
    logging: LoggingSettings = LoggingSettings()
    
    # Additional settings
    environment: str = "development"
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        valid_envs = ["development", "testing", "staging", "production"]
        if v not in valid_envs:
            raise ValueError(f"Invalid environment: {v}. Must be one of: {valid_envs}")
        return v
    
    @property
    def ENVIRONMENT(self) -> str:
        """Get environment for backward compatibility."""
        return self.environment


# Global settings instance
_settings_instance: Optional[Settings] = None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached application settings."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance


def get_database_url() -> str:
    """Get database URL from settings."""
    return get_settings().database.DATABASE_URL


def is_development() -> bool:
    """Check if running in development environment."""
    return get_settings().environment == "development"


def is_testing() -> bool:
    """Check if running in testing environment."""
    return get_settings().environment == "testing"


def is_production() -> bool:
    """Check if running in production environment."""
    return get_settings().environment == "production"


def is_staging() -> bool:
    """Check if running in staging environment."""
    return get_settings().environment == "staging"