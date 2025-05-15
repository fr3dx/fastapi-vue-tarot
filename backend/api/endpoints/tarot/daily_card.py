import random
import os
import traceback
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from models.schemas import Card
from services.auth.jwt import decode_jwt_token
from services.storage.minio import client, BUCKET_NAME
from services.database.psql import get_user_by_sub, update_user_draw_date
from utils.formatters import format_card_name

# Load config from environment variables
MINIO_EXTERNAL = os.getenv("MINIO_PUBLIC_URL", "http://localhost:9000")
USE_PRESIGNED_URL = os.getenv("USE_PRESIGNED_URL", "false").lower() == "true"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter(tags=["cards"])

@router.get("/daily_card", response_model=Card)
async def get_daily_card(token: str = Depends(oauth2_scheme)) -> Card:
    """
    Returns a daily tarot card for the authenticated user.
    Ensures one draw per day, selects a random PNG card from MinIO,
    and returns the card info with either a presigned or static URL.
    """

    try:
        payload = decode_jwt_token(token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Érvénytelen token.")

    user_sub = payload.get("sub")
    if not user_sub:
        raise HTTPException(status_code=400, detail="Hiányzó felhasználói azonosító a tokenben.")

    user = await get_user_by_sub(user_sub)
    if not user:
        raise HTTPException(status_code=404, detail="A felhasználó nem található.")

    last_draw = user.get("last_draw_date")
    today = datetime.now(timezone.utc).date()
    if last_draw == today:
        raise HTTPException(status_code=403, detail="Már húztál ma egy kártyát.")

    try:
        objects = list(client.list_objects(BUCKET_NAME, recursive=True))
        png_files = [obj.object_name for obj in objects if obj.object_name.lower().endswith(".png")]

        if not png_files:
            raise HTTPException(status_code=404, detail="Nem találhatók PNG fájlok a MinIO-ban.")

        selected = random.choice(png_files)

        if USE_PRESIGNED_URL:
            # Generate a presigned URL for temporary authenticated access
            image_url = client.presigned_get_object(BUCKET_NAME, selected)
        else:
            # Use static public URL from environment (reverse proxy or direct)
            image_url = f"{MINIO_EXTERNAL}/{BUCKET_NAME}/{selected}"

        name = format_card_name(selected)
        key = selected.rsplit("/", 1)[-1].split(".")[0].lower()

        await update_user_draw_date(user_sub)

        return Card(name=name, image_url=image_url, key=key)

    except Exception as e:
        print("HIBA TRACEBACK:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Váratlan hiba történt: {str(e)}")
