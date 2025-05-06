from pydantic import BaseModel

class TokenIn(BaseModel):
    token: str
