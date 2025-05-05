from fastapi import APIRouter, HTTPException
import random
from services.storage.minio import client, BUCKET_NAME
from models.schemas import Card
from utils.formatters import format_card_name

router = APIRouter(tags=["cards"])

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
