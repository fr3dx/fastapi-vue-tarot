from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# CORS Configuration: This middleware enables Cross-Origin Resource Sharing.
# It allows your backend API to accept requests from frontend clients hosted on different origins.
def setup_cors(app: FastAPI):
    """
    Configures and adds CORS middleware to the FastAPI application.

    This is necessary for enabling requests from frontend clients running on a different origin,
    such as during development with tools like Vite or React.
    """
    print("Setting up CORS middleware...")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],  # Allowed origin(s), e.g., local frontend dev server
        allow_credentials=True,  # Enable cookies, authorization headers, and other credentials
        allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
        allow_headers=["*"],  # Allow all custom and standard headers
    )
    print("CORS middleware setup complete.")
