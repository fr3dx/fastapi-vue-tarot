from datetime import datetime, timedelta
from typing import Optional
import jwt  # PyJWT library for encoding and decoding JWTs
import os
import secrets

# Load secret key from environment or fallback to a default (use only for development)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "test")

# JWT configuration constants
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1

# Refresh token configuration constant
REFRESH_TOKEN_EXPIRE_DAYS = 30

def create_jwt_token(sub: str, name: Optional[str] = None, email: Optional[str] = None) -> str:
    """
    Generates a JWT token containing a subject, expiry time, and optionally user's name and email.

    Args:
        sub (str): The subject of the token (typically a user ID or unique identifier).
        name (Optional[str], optional): The user's name. Defaults to None.
        email (Optional[str], optional): The user's email address. Defaults to None.

    Returns:
        str: A signed JWT token as a string.
    """
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": sub,
        "exp": expire,
        "iat": datetime.utcnow()  # Issued at
    }

    # Add name to payload if it's provided and not None
    if name is not None:
        payload["name"] = name

    # Add email to payload if it's provided and not None
    if email is not None:
        payload["email"] = email

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_jwt_token(token: str) -> Optional[dict]:
    """
    Decodes and verifies a JWT token.

    Args:
        token (str): The JWT token to decode.

    Returns:
        dict: The decoded payload if the token is valid.

    Raises:
        ValueError: If the token is expired or invalid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")

def create_refresh_token() -> str:
    """
    Generates a secure random string to be used as a refresh token.

    Returns:
        str: A URL-safe random string token.
    """
    return secrets.token_urlsafe(48)

def get_refresh_token_expiry() -> datetime:
    """
    Calculates the expiration datetime for the refresh token.

    Returns:
        datetime: The UTC datetime when the refresh token will expire.
    """
    return datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
