from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

class UserData(BaseModel):
    """
    Schema representing a user record.

    This model is typically used for serializing/deserializing user data 
    between the database and the API. It includes basic identity fields 
    and tracking for the last card draw.

    Attributes:
    - id (int): Unique identifier for the user (typically from the database).
    - sub (str): The subject identifier from an external auth provider (e.g., Google).
    - email (Optional[str]): User's email address, if available.
    - name (Optional[str]): Display name of the user.
    - created_at (datetime): Timestamp indicating when the user was created.
    - last_draw_date (Optional[date]): The date of the user's last tarot card draw.
    """

    id: int
    sub: str
    email: Optional[str]
    name: Optional[str]
    created_at: datetime
    last_draw_date: Optional[date]

    class Config:
        orm_mode = True  # Allows Pydantic to work seamlessly with ORM objects (e.g., SQLAlchemy)
