from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging
from services.database.psql import connect_to_db, close_db_connection

# Lifespan event handler: Handles the lifecycle of the application.
# Specifically manages the database connection pool during startup and shutdown.
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager to manage application-wide startup and shutdown tasks.

    This setup ensures that the database connection pool is established before handling any requests,
    and properly closed when the application is shutting down.
    """
    # --- Startup ---
    # Initialize the database connection pool.
    # If the connection fails, an exception is raised and the application will not start.
    await connect_to_db()
    print("Application startup tasks finished.")

    yield  # The application runs while paused here. Control is returned to FastAPI to process requests.

    # --- Shutdown ---
    # Clean up the database connection pool upon application shutdown.
    await close_db_connection()
    print("Application shutdown tasks finished.")
