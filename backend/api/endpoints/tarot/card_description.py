from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from services.database.psql import get_card_data_by_key_and_lang
from models.schemas import CardDescription

router = APIRouter(tags=["cards"])


@router.get("/card_description/{key}", response_model=CardDescription)
async def get_card_description(key: str, lang: Optional[str] = Query("hu", max_length=10)) -> CardDescription:
    """
    Retrieves the description for a specific card from the database using its unique key.
    """
    card_data = await get_card_data_by_key_and_lang(key, lang)

    if not card_data or "description" not in card_data:
        raise HTTPException(status_code=404, detail=f"Card description not found for key: {key} and lang: {lang}")

    return CardDescription(description=card_data["description"])


