from pydantic import BaseModel
from typing import Optional

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None

class TokenIn(BaseModel):
    token: str
    lang: str

# Felhasználói adatokat tartalmazó modell
class UserData(BaseModel):
    sub: str
    email: str
    name: str
