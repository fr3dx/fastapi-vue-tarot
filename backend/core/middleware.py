from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

def setup_cors(app: FastAPI):
    """
    Adds CORS (Cross-Origin Resource Sharing) middleware to the FastAPI application.

    This allows the backend API to accept requests from frontend applications
    hosted on different origins (e.g., local development environments like Vite or React).

    Parameters:
    - app (FastAPI): The FastAPI application instance.
    """
    print("Setting up CORS middleware...")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost"],  # Define allowed origins (adjust for production)
        allow_credentials=True,              # Allow sending cookies and authorization headers
        allow_methods=["*"],                 # Allow all standard HTTP methods
        allow_headers=["*"],                 # Allow all custom and standard headers
    )
    print("CORS middleware setup complete.")

def setup_rate_limiter(app: FastAPI):
    """
    Configures and adds rate limiting to the FastAPI application using SlowAPI.

    This helps prevent abuse by limiting the number of requests per IP address.
    By default, limits are set to 2 requests per minute.

    Parameters:
    - app (FastAPI): The FastAPI application instance.
    """
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["2/minute"],  # Define global rate limits
    )
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)  # Attach the rate limiter middleware
    print("Rate limiter middleware setup complete.")
