from fastapi import APIRouter, HTTPException, Depends, Response, Cookie
from typing import Optional
from datetime import timedelta # Added timedelta

# Removed OAuth2PasswordBearer as it was unused
# Removed pydantic.BaseModel as RefreshTokenIn is removed
from models.auth import TokenIn, TokenOut, UserData
from services.auth.google import verify_google_token
from services.database.psql import ( # Added new DB functions
    insert_or_get_user,
    get_user_by_sub,
    update_user_refresh_token,
    get_user_by_refresh_token
)
from services.auth.jwt import ( # Added REFRESH_TOKEN_EXPIRE_DAYS
    create_access_token,
    create_refresh_token,
    decode_jwt_token,
    REFRESH_TOKEN_EXPIRE_DAYS
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(tags=["auth"])

# This should match the actual login endpoint
bearer_scheme = HTTPBearer()

# Cookie settings
COOKIE_PATH = "/api/auth" # Specific path for auth cookies
COOKIE_SAMESITE = "lax" # Can be "strict" for better security if UX allows
COOKIE_SECURE = True # Should be True in production, False in http dev if needed
COOKIE_HTTPONLY = True

@router.post("/google", response_model=TokenOut)
async def login_google(payload: TokenIn, response: Response): # Added response: Response
    user_info = verify_google_token(payload.token)
    
    # Ensure user exists or is created in DB
    # db_user = await insert_or_get_user(...) # insert_or_get_user is called, but its return not explicitly used beyond ensuring user exists
    await insert_or_get_user(
        sub=user_info["sub"],
        email=user_info.get("email"),
        name=user_info.get("name"),
        lang=payload.lang
    )

    access_token = create_access_token(sub=user_info["sub"])
    refresh_token = create_refresh_token(sub=user_info["sub"])

    # Store refresh token in DB
    await update_user_refresh_token(user_info["sub"], refresh_token)

    # Set refresh token as HTTP-only cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=COOKIE_HTTPONLY,
        samesite=COOKIE_SAMESITE,
        secure=COOKIE_SECURE,
        path=COOKIE_PATH,
        expires=int(timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS).total_seconds())
    )
    
    # Return only access token and type in body
    # TokenOut model will be updated later to not require refresh_token in response body
    return TokenOut(access_token=access_token, token_type="bearer")

@router.post("/refresh", response_model=TokenOut)
async def refresh_access_token(response: Response, refresh_token_cookie: Optional[str] = Cookie(None, alias="refresh_token")): # Added response, changed payload to cookie
    if not refresh_token_cookie:
        raise HTTPException(status_code=401, detail="Refresh token cookie not found")

    try:
        decoded_refresh_token = decode_jwt_token(token=refresh_token_cookie)
    except ValueError as e: # Covers expired or invalid token
        raise HTTPException(status_code=401, detail=f"Invalid or expired refresh token: {e}")

    user_sub = decoded_refresh_token.get("sub")
    if not user_sub:
        raise HTTPException(status_code=401, detail="Invalid refresh token: subject missing")

    # Verify token against DB
    user_from_db = await get_user_by_refresh_token(refresh_token_cookie)
    if not user_from_db or user_from_db.get("refresh_token") != refresh_token_cookie:
        # Important: If token from cookie doesn't match DB, invalidate (even if JWT is valid)
        # This also covers cases where token was cleared from DB (e.g. logout)
        response.set_cookie(
            key="refresh_token", value="", httponly=COOKIE_HTTPONLY, samesite=COOKIE_SAMESITE,
            secure=COOKIE_SECURE, path=COOKIE_PATH, expires=0, max_age=0
        )
        raise HTTPException(status_code=401, detail="Refresh token not recognized or revoked")

    # Token rotation: Generate new access and refresh tokens
    new_access_token = create_access_token(sub=user_sub)
    new_refresh_token = create_refresh_token(sub=user_sub)

    # Update new refresh token in DB
    await update_user_refresh_token(user_sub, new_refresh_token)

    # Set new refresh token as HTTP-only cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=COOKIE_HTTPONLY,
        samesite=COOKIE_SAMESITE,
        secure=COOKIE_SECURE,
        path=COOKIE_PATH,
        expires=int(timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS).total_seconds())
    )
    
    return TokenOut(access_token=new_access_token, token_type="bearer")

@router.post("/logout")
async def logout(response: Response, credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)):
    user_sub = None
    if credentials:
        try:
            token_payload = decode_jwt_token(credentials.credentials)
            user_sub = token_payload.get("sub")
        except ValueError:
            # If token is invalid/expired, we can't get sub, but still proceed to clear cookie.
            # DB clearing for this sub won't happen, but client-side logout is primary.
            pass 
    
    if user_sub:
        await update_user_refresh_token(user_sub, None) # Clear refresh token in DB

    # Expire the refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value="", # Clear value
        httponly=COOKIE_HTTPONLY,
        samesite=COOKIE_SAMESITE,
        secure=COOKIE_SECURE,
        path=COOKIE_PATH,
        expires=0, # Set to epoch
        max_age=0  # Tell browser to delete immediately
    )
    return {"message": "Logged out successfully"}


@router.get("/user", response_model=UserData)
async def get_user_data(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
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
