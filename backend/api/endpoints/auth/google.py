from fastapi import APIRouter, Depends
from pydantic import BaseModel
from services.auth.google import verify_google_token
from models.auth import TokenIn

router = APIRouter(tags=["auth"])

@router.post("/google")
def login_google(payload: TokenIn):
    user_data = verify_google_token(payload.token)
    return {"user": user_data}
