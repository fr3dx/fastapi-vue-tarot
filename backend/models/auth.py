from pydantic import BaseModel

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenIn(BaseModel):
    token: str

# Felhasználói adatokat tartalmazó modell
class UserData(BaseModel):
    email: str
    name: str
    picture: str
    given_name: str
    family_name: str
