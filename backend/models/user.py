from sqlalchemy import Column, String, DateTime
from services.database.psql import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    last_draw_date = Column(DateTime, default=None)
    created_at = Column(DateTime, default=datetime.utcnow)
