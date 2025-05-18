from fastapi import APIRouter, Query
from typing import List
from services.database.psql import get_all_card_data
from models.schemas import CardData

router = APIRouter(tags=["cards"])

@router.get("/all_cards", response_model=List[CardData])
async def get_all_cards(lang: str = Query("hu", description="Language code, e.g. 'hu' or 'en'")) -> List[CardData]:
    """
    Returns all card data for the specified language from the database.

    Args:
        lang (str): Language code to filter the card descriptions by (default is 'hu').

    Returns:
        List[CardData]: List of card descriptions for the requested language.
    """
    all_data: List[CardData] = await get_all_card_data(lang=lang)
    return all_data

