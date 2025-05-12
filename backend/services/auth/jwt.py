from datetime import datetime, timedelta
from typing import Optional
import jwt  # PyJWT library for encoding and decoding JWTs
import os

# Load secret key from environment or fallback to a default (use only for development)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "test")

# JWT configuration constants
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_jwt_token(sub: str) -> str:
    """
    Generates a JWT token containing a subject and expiry time.

    Args:
        sub (str): The subject of the token (typically a user ID or unique identifier).

    Returns:
        str: A signed JWT token as a string.
    """
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": sub,
        "exp": expire,
        "iat": datetime.utcnow()  # Issued at
    }
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
