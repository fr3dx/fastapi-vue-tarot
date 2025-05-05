from fastapi import APIRouter
from typing import List, Dict, Any
from services.database.psql import get_all_card_data
from models.schemas import CardData

router = APIRouter(tags=["cards"])

@router.get("/all_cards", response_model=List[CardData])
async def get_all_cards() -> List[Dict[str, Any]]:
    """
    Returns all card data from the database.
    This includes every record in the 'card_descriptions' table.
    """
    all_data: List[CardData] = await get_all_card_data()
    return all_data
