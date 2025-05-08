from fastapi import APIRouter, Depends
from models.auth import TokenIn, TokenOut, UserData  # Importáljuk a UserData modellt
from services.auth.google import verify_google_token

router = APIRouter(tags=["auth"])

@router.post("/google", response_model=TokenOut)
def login_google(payload: TokenIn):
    user_data = verify_google_token(payload.token)
    # Az access_token generálása, itt most csak placeholder
    access_token = "some_generated_access_token"  # Itt generálható a valós token
    return TokenOut(access_token=access_token)

@router.get("/user", response_model=UserData)
def get_user_data(token: str):
    user_data = verify_google_token(token)
    return UserData(
        email=user_data["email"],
        name=user_data["name"],
        picture=user_data["picture"],
        given_name=user_data["given_name"],
        family_name=user_data["family_name"]
    )

