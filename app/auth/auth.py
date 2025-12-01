"""Authentication utilities including password hashing and JWT token management."""

from datetime import datetime, timedelta
from typing import Optional, Any
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import get_settings

# Get settings instance
settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthenticationError(Exception):
    """Base exception for authentication errors."""
    pass


class InvalidCredentialsError(AuthenticationError):
    """Exception for invalid credentials."""
    pass


class TokenExpiredError(AuthenticationError):
    """Exception for expired tokens."""
    pass


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        raise InvalidCredentialsError(f"Password verification failed: {e}")


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        raise AuthenticationError(f"Password hashing failed: {e}")


def create_access_token(
    data: dict[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token."""
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.security.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.security.SECRET_KEY, 
            algorithm=settings.security.ALGORITHM
        )
        return encoded_jwt
    except Exception as e:
        raise AuthenticationError(f"Token creation failed: {e}")


def verify_token(token: str, credentials_exception) -> str:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(
            token, 
            settings.security.SECRET_KEY, 
            algorithms=[settings.security.ALGORITHM]
        )
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise TokenExpiredError("Token has expired")


def create_password_reset_token(email: str) -> str:
    """Create a password reset token."""
    delta = timedelta(hours=24)  # 24 hours
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    
    to_encode = {
        "sub": email,
        "exp": exp,
        "type": "password_reset"
    }
    
    return jwt.encode(
        to_encode, 
        settings.security.SECRET_KEY, 
        algorithm=settings.security.ALGORITHM
    )


def verify_password_reset_token(token: str) -> Optional[str]:
    """Verify a password reset token and return email if valid."""
    try:
        payload = jwt.decode(
            token, 
            settings.security.SECRET_KEY, 
            algorithms=[settings.security.ALGORITHM]
        )
        
        if payload.get("type") != "password_reset":
            return None
            
        email: Optional[str] = payload.get("sub")
        return email
    except JWTError:
        return None