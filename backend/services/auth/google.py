from google.oauth2 import id_token
from google.auth.transport import requests
from fastapi import HTTPException, status
import os

# Retrieve Google OAuth2 Client ID from environment variables
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

def verify_google_token(token: str):
    """
    Verifies a Google ID token and extracts user information.

    Args:
        token (str): The Google-issued ID token to validate.

    Returns:
        dict: A dictionary containing user information such as email, name, and Google user ID (sub).

    Raises:
        HTTPException: If the token is invalid, expired, or missing required claims.
    """
    try:
        # Validate the ID token against Google's public keys and the client ID
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

        # Ensure the token contains a 'sub' claim (Google user ID)
        if "sub" not in idinfo:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: 'sub' claim missing"
            )

        # Return user details extracted from the token
        return {
            "email": idinfo.get("email"),
            "name": idinfo.get("name"),
            "sub": idinfo.get("sub"),
            "email_verified": idinfo.get("email_verified"),
            "given_name": idinfo.get("given_name"),
            "family_name": idinfo.get("family_name"),
            "picture": idinfo.get("picture", "")  # Optional profile picture URL
        }

    except ValueError:
        # Token is invalid or expired
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Google token"
        )
