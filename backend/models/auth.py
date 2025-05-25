from pydantic import BaseModel

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str

class TokenIn(BaseModel):
    token: str
    lang: str

class UserData(BaseModel):
    sub: str
    email: str
    name: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str
