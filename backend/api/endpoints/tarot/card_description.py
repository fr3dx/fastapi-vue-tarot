from fastapi import APIRouter, HTTPException
from typing import Optional
from services.database.psql import get_card_description_by_key
from models.schemas import CardDescription

router = APIRouter(tags=["cards"])

@router.get("/card_description/{key}", response_model=CardDescription)
async def get_card_description(key: str) -> CardDescription:
    """
    Retrieves the description for a specific card from the database using its unique key.
    """
    description: Optional[str] = await get_card_description_by_key(key)

    if description is None:
        raise HTTPException(status_code=404, detail=f"Card description not found for key: {key}")

    return CardDescription(description=description)
