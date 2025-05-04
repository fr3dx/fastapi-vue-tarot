from pydantic import BaseModel

# Pydantic Models: Define the structure and validation rules for API request and response bodies.

class Card(BaseModel):
    """
    Represents a Tarot card with key identifying information.
    This model is used for serializing card metadata such as name and image.
    """
    name: str  # Human-readable, formatted name of the card (e.g., "The Fool")
    image_url: str  # Relative URL to the card image (e.g., "/static/images/major-arcana/the-fool.png")
    key: str  # Unique identifier for the card, typically derived from the filename (e.g., "major-arcana_the-fool")

class CardDescription(BaseModel):
    """
    Represents the textual description of a Tarot card.
    Used in responses where only the card’s explanation is needed.
    """
    description: str  # Narrative or symbolic meaning of the card

class CardData(BaseModel):
    """
    Combines the card's key with its description.
    Suitable for API responses that return complete card data from the database.
    """
    key: str  # Unique key of the card (e.g., "major-arcana_the-fool")
    description: str  # Full textual description
