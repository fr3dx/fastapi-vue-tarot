from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from models.auth import TokenIn, TokenOut, UserData, RefreshTokenRequest
from services.auth.google import verify_google_token
from services.auth.jwt import (
    create_jwt_token,
    decode_jwt_token,
    create_refresh_token,
    get_refresh_token_expiry,
)
from services.database.psql import (
    insert_or_get_user,
    get_user_by_sub,
    upsert_refresh_token_for_user,
    get_user_by_refresh_token,
    delete_refresh_token,
)
from datetime import datetime

router = APIRouter(tags=["auth"])

# Security scheme for extracting and validating Bearer tokens
bearer_scheme = HTTPBearer()


@router.post("/google", response_model=TokenOut)
async def login_google(payload: TokenIn):
    """
    Logs in a user via Google OAuth2 token.

    - Verifies the Google token.
    - Fetches or inserts the user in the database.
    - Issues JWT access and refresh tokens.
    """
    user_info = verify_google_token(payload.token)

    db_user = await insert_or_get_user(
        sub=user_info["sub"],
        email=user_info.get("email"),
        name=user_info.get("name"),
        lang=payload.lang
    )

    token = create_jwt_token(
        sub=user_info["sub"],
        name=user_info.get("name"),
        email=user_info.get("email")
    )

    refresh_token = create_refresh_token()
    expires_at = get_refresh_token_expiry()

    await upsert_refresh_token_for_user(
        sub=user_info["sub"],
        refresh_token=refresh_token,
        expires_at=expires_at
    )

    return TokenOut(access_token=token, refresh_token=refresh_token)


@router.get("/user", response_model=UserData)
async def get_user_data(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """
    Retrieves the authenticated user's profile using a Bearer token.

    - Validates the JWT token.
    - Fetches user info from the database.
    """
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme.")

    token = credentials.credentials

    try:
        payload = decode_jwt_token(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    db_user = await get_user_by_sub(payload["sub"])
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserData(**db_user)


@router.post("/refresh", response_model=TokenOut)
async def refresh_access_token(payload: RefreshTokenRequest = Body(...)):
    """
    Refreshes the access token using a valid refresh token.

    - Verifies and validates the refresh token.
    - Issues new access and refresh tokens.
    """
    refresh_token = payload.refresh_token

    try:
        db_user = await get_user_by_refresh_token(refresh_token)
        if not db_user:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        expires_at = db_user.get("refresh_token_expires_at")
        if not expires_at or expires_at < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Refresh token expired")

        user_data_for_token = await get_user_by_sub(db_user["sub"])
        if not user_data_for_token:
            raise HTTPException(status_code=404, detail="User not found for refresh token")

        new_access_token = create_jwt_token(
            sub=db_user["sub"],
            name=user_data_for_token.get("name"),
            email=user_data_for_token.get("email")
        )

        new_refresh_token = create_refresh_token()
        new_expires_at = get_refresh_token_expiry()

        await upsert_refresh_token_for_user(
            sub=db_user["sub"],
            refresh_token=new_refresh_token,
            expires_at=new_expires_at
        )

        return TokenOut(access_token=new_access_token, refresh_token=new_refresh_token)

    except HTTPException as e:
        raise e

    except Exception as e:
        print(f"Unexpected error in refresh token endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/logout")
async def logout(refresh_token: str = Body(..., embed=True)):
    """
    Logs out the user by invalidating the provided refresh token.

    - Deletes the refresh token record from the database.
    """
    token_record = await get_user_by_refresh_token(refresh_token)
    if not token_record:
        raise HTTPException(status_code=400, detail="Invalid refresh token")

    await delete_refresh_token(refresh_token)
    return {"message": "Successfully logged out"}
