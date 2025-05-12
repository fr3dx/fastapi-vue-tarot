import random
from fastapi import APIRouter, HTTPException, Depends
from models.schemas import Card
from services.auth.jwt import decode_jwt_token
from services.storage.minio import client, BUCKET_NAME
from utils.formatters import format_card_name
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timezone
from services.database.psql import get_user_by_sub, update_user_draw_date

# OAuth2 dependency for extracting the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Define the API router with a "cards" tag
router = APIRouter(tags=["cards"])

@router.get("/daily_card", response_model=Card)
async def get_daily_card(token: str = Depends(oauth2_scheme)) -> Card:
    """
    Endpoint to draw a daily tarot card for the authenticated user.
    Ensures one draw per day, retrieves a random card from MinIO,
    and returns its name, image URL, and key.
    """

    # Decode the JWT token and extract payload
    try:
        payload = decode_jwt_token(token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Get the user's unique identifier from the token
    user_sub = payload.get("sub")
    if not user_sub:
        raise HTTPException(status_code=400, detail="Missing user identifier in token")

    # Retrieve user data from the database
    user = await get_user_by_sub(user_sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Enforce one draw per calendar day (UTC)
    last_draw = user.get("last_draw_date")
    today = datetime.now(timezone.utc).date()
    if last_draw == today:
        raise HTTPException(status_code=403, detail="You have already drawn a card today")

    try:
        # List all PNG image files in the MinIO bucket
        objects = list(client.list_objects(BUCKET_NAME, recursive=True))
        png_files = [obj.object_name for obj in objects if obj.object_name.lower().endswith(".png")]

        if not png_files:
            raise HTTPException(status_code=404, detail="No PNG files found in MinIO")

        # Randomly select a card image
        selected = random.choice(png_files)

        # Generate a presigned URL for the selected image
        presigned_url = client.presigned_get_object(BUCKET_NAME, selected)

        # Extract the card name and key from the file name
        name = format_card_name(selected)
        key = selected.rsplit("/", 1)[-1].split(".")[0].lower()

        # Update the user's last draw timestamp in the database
        await update_user_draw_date(user_sub)

        # Return the card data to the frontend
        return Card(name=name, image_url=presigned_url, key=key)

    except Exception as e:
        # Catch-all for unexpected errors, e.g., MinIO connectivity issues
        raise HTTPException(status_code=500, detail=f"MinIO error: {str(e)}")
