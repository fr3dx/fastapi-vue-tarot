import httpx
from fastapi import Request
from urllib.parse import urlencode

FACEBOOK_CLIENT_ID = "your_app_id"
FACEBOOK_CLIENT_SECRET = "your_app_secret"
REDIRECT_URI = "http://localhost:8000/api/auth/facebook/callback"

def get_facebook_login_url() -> str:
    query_params = {
        "client_id": FACEBOOK_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "public_profile,email",
        "response_type": "code"
    }
    return f"https://www.facebook.com/v18.0/dialog/oauth?{urlencode(query_params)}"

async def exchange_code_for_token(code: str) -> str:
    async with httpx.AsyncClient() as client:
        token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
        params = {
            "client_id": FACEBOOK_CLIENT_ID,
            "client_secret": FACEBOOK_CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "code": code
        }
        response = await client.get(token_url, params=params)
        return response.json().get("access_token")

async def get_user_info(token: str) -> dict:
    async with httpx.AsyncClient() as client:
        user_info_url = "https://graph.facebook.com/me"
        params = {"fields": "id,name,email", "access_token": token}
        response = await client.get(user_info_url, params=params)
        return response.json()
