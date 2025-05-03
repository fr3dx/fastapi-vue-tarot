from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any # Import Dict and Any for the new endpoint
import os
import random
import database # Import our new database module
from contextlib import asynccontextmanager # Lifespan setup
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from minio_client import client, BUCKET_NAME  # MinIO client import


# Lifespan event handler: Uses the functions from the database module
# to manage the database connection pool across the application's life.
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown events, specifically database connection.
    Calls connect_to_db on startup (which will raise an exception if connection fails)
    and close_db_connection on shutdown.
    """
    # --- Startup ---
    # Connect to the database pool. database.connect_to_db is designed to
    # raise an exception on failure, preventing the app from starting if the DB is down.
    await database.connect_to_db()
    print("Application startup tasks finished.")

    yield # This separates startup from shutdown. The application is now ready to handle requests.

    # --- Shutdown ---
    # Close the database connection pool when the application is shutting down.
    await database.close_db_connection()
    print("Application shutdown tasks finished.")


# Initialize the FastAPI application instance.
# Pass the lifespan context manager to the 'lifespan' argument.
# This tells FastAPI to use this context manager for startup and shutdown events.
app = FastAPI(lifespan=lifespan)

# CORS Configuration: Middleware to handle Cross-Origin Resource Sharing.
# This allows requests from specified origins (like your frontend dev server).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # List of origins allowed to make requests (e.g., frontend URL)
    allow_credentials=True,  # Allow cookies, authorization headers etc.
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers in the request
)

# Directory Paths and Static Files setup: Configuration for serving static content (like images).
BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Get the path to the project's base directory
CARDS_DIR: str = os.path.join(BASE_DIR, "cards-test") # Path to the directory containing card images
# Mount the 'CARDS_DIR' to the '/cards' URL path. Files inside CARDS_DIR will be accessible via this URL.
app.mount("/cards", StaticFiles(directory=CARDS_DIR), name="cards")

# Pydantic Models: Define the structure of data for request validation and response serialization.
class Card(BaseModel):
    """Represents a Tarot card with basic information."""
    name: str # The human-readable formatted name of the card
    image_url: str # The URL path to the card image file (relative to the API base URL)
    key: str # A unique string key identifying the card (usually derived from the filename)

class CardDescription(BaseModel):
    """Represents the description text of a Tarot card."""
    description: str # The textual description content for the card

class CardData(BaseModel):
    key: str
    description: str

# Helper function to format a card name from a filename.
# This function remains the same as it operates on filenames.
def format_card_name(filename: str) -> str:
    """
    Formats a human-readable card name from a given filename.
    Example: Input 'major-arcana_the-fool.png' -> Output 'The Fool'
    """
    name_part: str = os.path.splitext(filename)[0] # Split filename and extension, take the base name
    name: str = name_part.split("_", 1)[-1] # Split by the first underscore and take the part after it
    # Replace hyphens and underscores with spaces, apply title case, and prepend "The ".
    return "The " + name.replace("-", " ").replace("_", " ").title()

# Endpoint to get a random daily card.
# This endpoint fetches a random card image file and provides basic info.
# It does NOT include the description in this version, as the description is fetched separately.
@app.get("/api/daily_card", response_model=Card)
async def get_daily_card() -> Card:
    try:
        # Lekérjük az összes fájlt a bucketből
        objects = list(client.list_objects(BUCKET_NAME, recursive=True))
        png_files = [obj.object_name for obj in objects if obj.object_name.lower().endswith(".png")]

        # Ellenőrizzük, hogy van-e png
        if not png_files:
            raise HTTPException(status_code=404, detail="Nincs elérhető kép a MinIO-ban.")

        # Véletlenszerűen választunk egyet
        selected = random.choice(png_files)

        # Generálunk presigned URL-t
        presigned_url = client.presigned_get_object(BUCKET_NAME, selected)

        # Képnév + kulcs formázása
        name = format_card_name(selected)
        key = selected.rsplit("/", 1)[-1].split(".")[0].lower()

        return Card(
            name=name,
            image_url=presigned_url,
            key=key
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hiba a MinIO kapcsolat során: {str(e)}")

# Endpoint to retrieve a card description by its key from the database.
# This endpoint uses the dedicated DAO function to fetch the description.
# It handles cases where the description is not found or database issues occur.
@app.get("/api/card_description/{key}", response_model=CardDescription)
async def get_card_description(key: str) -> CardDescription:
    """
    Retrieves and returns the description for a specific card by its unique key from the database.
    If the description is not found for the given key, a 404 Not Found error is returned.
    If the database is unavailable or a query error occurs, appropriate HTTP exceptions are raised (503 or 500).
    """
    # Use the DAO function from the 'database' module to retrieve the description.
    # This function returns the description string or None if not found,
    # and raises HTTPException if database connection or query errors occur.
    description: Optional[str] = await database.get_card_description_by_key(key)

    # Check if the description was successfully retrieved.
    if description is None:
        # If the description is None, it means the key was not found in the database table.
        # Raise a 404 Not Found exception.
        raise HTTPException(status_code=404, detail=f"Card description not found for key: {key}")
    else:
        # If the description was found, use the retrieved text.
        description_text = description

    # Return a CardDescription model instance containing the retrieved description text.
    return CardDescription(description=description_text)

# Endpoint to get all card data from the database using the DAO function.
# This endpoint uses the dedicated DAO function to fetch all rows from the descriptions table.
@app.get("/api/all_cards", response_model=List[CardData]) # Response model explicitly defined
async def get_all_cards() -> List[Dict[str, Any]]:
     """
     Retrieves and returns all card data (all columns) from the 'card_descriptions' table in the database.
     Uses the database DAO function to perform the query.
     Raises HTTPException if the database is unavailable or a query error occurs (handled by the DAO).
     """
     print("Request received for /api/all_cards")
     # Use the DAO function from the 'database' module to fetch all data.
     # This function is designed to handle database errors by raising HTTPException.
     all_data: List[CardData] = await database.get_all_card_data()
     print(f"Retrieved {len(all_data)} rows from card_descriptions.")
     # Return the retrieved list of dictionaries. FastAPI will automatically serialize this to JSON.
     return all_data


# Root endpoint (optional): A basic endpoint to quickly verify the API is running.
@app.get("/")
async def read_root():
    """
    Basic root endpoint that returns a simple message to confirm the API service is operational.
    """
    return {"message": "Tarot API is running."}

# Note on running: To run this FastAPI application, save the code for each file
# into 'database.py' and 'main.py' respectively in the same directory.
# Ensure you have a '.env' file in that directory with your database credentials.
# Then run it from your terminal using Uvicorn:
# uvicorn main:app --reload
# Ensure you are in the correct virtual environment and directory.

# HTTP Exception handler (e.g., 404, 403)
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handles HTTP exceptions (such as 404 Not Found or 403 Forbidden).
    Returns a standardized JSON response structure with the error detail.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail
        },
    )

# Pydantic Validation Error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handles validation errors raised by Pydantic when request data is invalid.
    Returns a 422 Unprocessable Entity response with error details.
    """
    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "message": "Validation failed",
            "details": exc.errors()
        },
    )

# General Exception handler (e.g., database errors or unhandled exceptions)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catches all unhandled exceptions (such as unexpected runtime errors or database issues).
    Logs the exception (if logging is implemented) and returns a generic 500 error response.
    """
    # A logger can be integrated here, e.g., logger.error(str(exc))
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error"
        },
    )

