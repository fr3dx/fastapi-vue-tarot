from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
import random
from services.storage.minio import client, BUCKET_NAME
from models.schemas import Card, CardDescription, CardData
from utils.formatters import format_card_name
from services.database.psql import get_card_description_by_key, get_all_card_data

router = APIRouter(tags=["cards"])

# Endpoint to get a random daily card.
# This fetches a random card image from the MinIO bucket.
# The description is not included here and must be fetched separately.
@router.get("/daily_card", response_model=Card)
async def get_daily_card() -> Card:
    try:
        # Retrieve all objects in the MinIO bucket (recursively)
        objects = list(client.list_objects(BUCKET_NAME, recursive=True))
        png_files = [obj.object_name for obj in objects if obj.object_name.lower().endswith(".png")]

        # If no PNG files are found, return a 404 error
        if not png_files:
            raise HTTPException(status_code=404, detail="No PNG images found in the MinIO bucket.")

        # Randomly select one PNG file
        selected = random.choice(png_files)

        # Generate a presigned URL for accessing the selected image
        presigned_url = client.presigned_get_object(BUCKET_NAME, selected)

        # Format the card name and extract the key
        name = format_card_name(selected)
        key = selected.rsplit("/", 1)[-1].split(".")[0].lower()

        return Card(
            name=name,
            image_url=presigned_url,
            key=key
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MinIO error occurred: {str(e)}")

# Endpoint to retrieve a card description by its key from the database.
@router.get("/card_description/{key}", response_model=CardDescription)
async def get_card_description(key: str) -> CardDescription:
    """
    Retrieves the description for a specific card from the database using its unique key.
    """
    description: Optional[str] = await get_card_description_by_key(key)

    if description is None:
        raise HTTPException(status_code=404, detail=f"Card description not found for key: {key}")

    return CardDescription(description=description)

# Endpoint to get all card data from the database.
@router.get("/all_cards", response_model=List[CardData])
async def get_all_cards() -> List[Dict[str, Any]]:
    """
    Returns all card data from the database.
    This includes every record in the 'card_descriptions' table.
    """
    print("Request received for /api/all_cards")
    all_data: List[CardData] = await get_all_card_data()
    print(f"Retrieved {len(all_data)} records from card_descriptions.")
    return all_data
