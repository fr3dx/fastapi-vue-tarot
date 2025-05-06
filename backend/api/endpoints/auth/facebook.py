from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse
from services.auth.facebook import (
    get_facebook_login_url, exchange_code_for_token, get_user_info
)
from services.database.psql import get_async_session
from models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.get("/facebook/login")
async def facebook_login():
    login_url = get_facebook_login_url()
    return RedirectResponse(login_url)

@router.get("/facebook/callback")
async def facebook_callback(code: str, request: Request):
    token = await exchange_code_for_token(code)
    user_data = await get_user_info(token)
    user_id = user_data["id"]
    name = user_data["name"]
    email = user_data.get("email")

    async with get_async_session() as session:
        existing = await session.execute(select(User).where(User.id == user_id))
        user = existing.scalars().first()

        if not user:
            user = User(id=user_id, name=name, email=email)
            session.add(user)
            await session.commit()

    return JSONResponse({"message": "Login successful", "user": user_data})
