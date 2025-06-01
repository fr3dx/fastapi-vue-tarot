from fastapi import FastAPI
from core.lifespan import lifespan
from core.middleware import setup_cors, setup_rate_limiter
from core.exceptions import setup_exception_handlers
from api.endpoints.tarot.daily_card import router as daily_card_router
from api.endpoints.tarot.card_description import router as card_description_router
from api.endpoints.tarot.all_cards import router as all_cards_router
from api.endpoints.healthcheck.health import router as healthcheck_router
from api.endpoints.auth.google import router as google_auth_router

# Initialize the FastAPI application with a custom lifespan context manager.
# The 'lifespan' handles application startup and shutdown events.
app = FastAPI(lifespan=lifespan)

# Configure middleware settings
setup_cors(app)
setup_rate_limiter(app)

# Optional: serve static files (currently disabled).
# setup_static_files(app)

# Register the API router for card-related endpoints under the '/api' prefix.
app.include_router(daily_card_router, prefix="/api")
app.include_router(card_description_router, prefix="/api")
app.include_router(all_cards_router, prefix="/api")
app.include_router(healthcheck_router, prefix="/api")
app.include_router(google_auth_router, prefix="/api/auth")

# Set up custom exception handlers for unified error responses.
setup_exception_handlers(app)
