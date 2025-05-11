from pydantic import BaseModel

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenIn(BaseModel):
    token: str

# Felhasználói adatokat tartalmazó modell
class UserData(BaseModel):
    sub: str
    email: str
    name: str
