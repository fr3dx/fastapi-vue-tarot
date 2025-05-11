from fastapi import APIRouter, HTTPException, Depends
from models.auth import TokenIn, TokenOut, UserData
from services.auth.google import verify_google_token
from services.database.psql import insert_or_get_user, get_user_by_sub
from services.auth.jwt import create_jwt_token, decode_jwt_token

router = APIRouter(tags=["auth"])

@router.post("/google", response_model=TokenOut)
async def login_google(payload: TokenIn):
    user_info = verify_google_token(payload.token)
    db_user = await insert_or_get_user(
        sub=user_info["sub"],
        email=user_info.get("email"),
        name=user_info.get("name")
    )
    token = create_jwt_token(sub=user_info["sub"])
    return TokenOut(access_token=token)

@router.get("/user", response_model=UserData)
async def get_user_data(token: str):
    try:
        payload = decode_jwt_token(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    
    db_user = await get_user_by_sub(payload["sub"])
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserData(**db_user)
