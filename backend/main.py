from fastapi import FastAPI
from starlette.exceptions import HTTPException as StarletteHTTPException
from core.lifespan import lifespan
from core.middleware import setup_cors
from services.minio_client import check_bucket_exists
from core.exceptions import setup_exception_handlers
from api.endpoints.cards import router as cards_router

# Initialize the FastAPI application with a custom lifespan context manager.
# The 'lifespan' handles application startup and shutdown events.
app = FastAPI(lifespan=lifespan)

# Configure middleware settings (e.g., CORS).
setup_cors(app)

# Optional: serve static files (currently disabled).
# setup_static_files(app)

# Register the API router for card-related endpoints under the '/api' prefix.
app.include_router(cards_router, prefix="/api")

# Set up custom exception handlers for unified error responses.
setup_exception_handlers(app)
