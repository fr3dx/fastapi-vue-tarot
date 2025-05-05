from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TarotCard(Base):
    __tablename__ = "tarot_cards"

    key = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    image_url = Column(String)
    description = Column(String)
