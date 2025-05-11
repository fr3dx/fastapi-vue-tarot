from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

class UserData(BaseModel):
    id: int
    sub: str
    email: Optional[str]
    name: Optional[str]
    created_at: datetime
    last_draw_date: Optional[date]

    class Config:
        orm_mode = True



