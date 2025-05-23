from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer # OAuth2PasswordBearer seems unused, can be removed later if confirmed
from pydantic import BaseModel
from models.auth import TokenIn, TokenOut, UserData
from services.auth.google import verify_google_token
from services.database.psql import insert_or_get_user, get_user_by_sub
from services.auth.jwt import create_access_token, create_refresh_token, decode_jwt_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(tags=["auth"])

# Pydantic model for the refresh token request
class RefreshTokenIn(BaseModel):
    refresh_token: str

# This should match the actual login endpoint
bearer_scheme = HTTPBearer()

@router.post("/google", response_model=TokenOut)
async def login_google(payload: TokenIn):
    user_info = verify_google_token(payload.token)
    # TODO: Consider if user active check is needed here
    db_user = await insert_or_get_user(
        sub=user_info["sub"],
        email=user_info.get("email"),
        name=user_info.get("name"),
        lang=payload.lang
    )
    access_token = create_access_token(sub=user_info["sub"])
    refresh_token = create_refresh_token(sub=user_info["sub"])
    return TokenOut(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

@router.post("/refresh", response_model=TokenOut)
async def refresh_access_token(payload: RefreshTokenIn):
    try:
        decoded_refresh_token = decode_jwt_token(token=payload.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Invalid refresh token: {e}")

    user_sub = decoded_refresh_token.get("sub")
    if not user_sub:
        raise HTTPException(status_code=401, detail="Invalid refresh token: subject missing")

    # Optional: Check if user exists and is active in DB before issuing new token
    # db_user = await get_user_by_sub(user_sub)
    # if not db_user:
    #     raise HTTPException(status_code=404, detail="User not found for refresh token")
    # if not db_user.get("is_active"): # Assuming an is_active field
    #     raise HTTPException(status_code=403, detail="User is inactive")

    new_access_token = create_access_token(sub=user_sub)
    # For the refresh endpoint, we typically only return a new access token.
    # The refresh token itself is not re-issued here.
    # Assuming TokenOut will be updated to make refresh_token optional or
    # we might need a different response model like AccessTokenOut.
    # For now, returning TokenOut with only access_token and token_type.
    return TokenOut(access_token=new_access_token, token_type="bearer", refresh_token=None)


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
