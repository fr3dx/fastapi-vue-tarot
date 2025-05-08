from google.oauth2 import id_token
from google.auth.transport import requests
from fastapi import HTTPException, status
import os

# Google Client ID
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

def verify_google_token(token: str):
    try:
        # Az ID token validálása a Google API segítségével
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

        # Ha nincs 'sub' (felhasználói ID), akkor hibát dobunk
        if "sub" not in idinfo:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token érvénytelen"
            )

        # Felhasználói adatokat adjuk vissza
        return {
            "email": idinfo.get("email"),
            "name": idinfo.get("name"),
            "sub": idinfo.get("sub"),
            "email_verified": idinfo.get("email_verified"),
            "given_name": idinfo.get("given_name"),
            "family_name": idinfo.get("family_name"),
            "picture": idinfo.get("picture", "")  # Kép URL-jét is hozzáadjuk
        }

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token érvénytelen vagy lejárt"
        )
