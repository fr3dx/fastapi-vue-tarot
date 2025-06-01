from pydantic import BaseModel

# Pydantic Models: Define the structure and validation logic for API request and response payloads.

class Card(BaseModel):
    """
    Represents a Tarot card with its core metadata.

    This model is typically used to serialize and return summary information 
    about a Tarot card, including its display name, image, and identifier.

    Attributes:
    - name (str): Human-readable, display-friendly name of the card (e.g., "The Fool").
    - image_url (str): Relative or absolute URL pointing to the card image.
    - key (str): Unique string identifier for the card, often derived from its filename.
    - description (str): Full, default-language description or meaning of the card.
    """
    name: str
    image_url: str
    key: str
    description: str


class CardDescription(BaseModel):
    """
    Provides only the textual explanation for a Tarot card.

    Useful in views or endpoints where the card's symbolic meaning is requested
    without needing image or full metadata.

    Attributes:
    - name (str): The name of the card.
    - description (str): The narrative, symbolism, or interpretation of the card.
    """
    name: str
    description: str


class CardData(BaseModel):
    """
    Contains localized data for a Tarot card, including its name and description.

    Intended for use in multilingual endpoints where card information needs
    to be returned in a specific language.

    Attributes:
    - key (str): The internal identifier of the card (e.g., "major-arcana_the-fool").
    - lang (str): ISO language code representing the localization (e.g., "en", "hu").
    - name (str): Localized name of the card.
    - description (str): Localized explanation or interpretation of the card.
    """
    key: str
    lang: str
    name: str
    description: str
