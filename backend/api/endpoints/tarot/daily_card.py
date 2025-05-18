import random
import os
import traceback
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.schemas import Card
from services.auth.jwt import decode_jwt_token
from services.storage.minio import client, BUCKET_NAME
from services.database.psql import (
    get_user_by_sub,
    update_user_draw_date,
    get_card_description_by_key_and_lang,
)
from utils.formatters import format_card_name

# Load configuration from environment variables
MINIO_EXTERNAL = os.getenv("MINIO_PUBLIC_URL", "http://localhost:9000")
USE_PRESIGNED_URL = os.getenv("USE_PRESIGNED_URL", "false").lower() == "true"

# Use HTTPBearer security scheme for Swagger UI integration
bearer_scheme = HTTPBearer()

router = APIRouter(tags=["cards"])


@router.get("/daily_card", response_model=Card)
async def get_daily_card(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> Card:
    """
    Endpoint to get a daily card for the authenticated user.
    Requires a valid JWT Bearer token in the Authorization header.

    Args:
        credentials (HTTPAuthorizationCredentials): Contains the Authorization header credentials.

    Returns:
        Card: The daily card data including name, image URL, key, and description.

    Raises:
        HTTPException: For various authentication, authorization, or processing errors.
    """
    try:
        # Extract the token string from the credentials
        token = credentials.credentials

        # Decode and validate the JWT token
        payload = decode_jwt_token(token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

    # Extract user's unique identifier (sub) from the JWT payload
    user_sub = payload.get("sub")
    if not user_sub:
        raise HTTPException(status_code=400, detail="Missing user identifier in token.")

    # Fetch the user from the database by 'sub'
    user = await get_user_by_sub(user_sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Check if the user has already drawn a card today (rate limiting)
    last_draw = user.get("last_draw_date")
    today = datetime.now(timezone.utc).date()
    if last_draw == today:
        raise HTTPException(status_code=403, detail="You have already drawn a card today.")

    try:
        # List all objects in the MinIO bucket and filter PNG files
        objects = list(client.list_objects(BUCKET_NAME, recursive=True))
        png_files = [obj.object_name for obj in objects if obj.object_name.lower().endswith(".png")]

        if not png_files:
            raise HTTPException(status_code=404, detail="No PNG files found in MinIO bucket.")

        # Select a random card image from the available PNG files
        selected = random.choice(png_files)

        # Generate accessible image URL depending on config
        if USE_PRESIGNED_URL:
            image_url = client.presigned_get_object(BUCKET_NAME, selected)
        else:
            image_url = f"{MINIO_EXTERNAL}/{BUCKET_NAME}/{selected}"

        # Format card name and extract key from filename
        name = format_card_name(selected)
        key = selected.rsplit("/", 1)[-1].split(".")[0].lower()

        # Get user's preferred language or fallback to Hungarian ('hu')
        user_lang = user.get("lang", "hu")

        # Retrieve card description in user's language
        description = await get_card_description_by_key_and_lang(key, user_lang)
        if not description:
            description = "No description available."

        # Update the user's last draw date to today
        await update_user_draw_date(user_sub)

        # Return the card data as response
        return Card(name=name, image_url=image_url, key=key, description=description)

    except Exception as e:
        # Log the full traceback for debugging
        print("ERROR TRACEBACK:")
        print(traceback.format_exc())
        # Return generic internal server error to client
        raise HTTPException(status_code=500, detail=f"Unexpected error occurred: {str(e)}")
