# /models/users.py

from sqlalchemy import Column, String, DateTime, Integer, Date
from services.database.psql import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sub = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    last_draw_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


