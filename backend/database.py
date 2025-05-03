from typing import Optional, List, Dict, Any
import asyncpg
import os
from dotenv import load_dotenv
from fastapi import HTTPException

# Load environment variables - good to do this here too if this module is run directly,
# but main.py will load them first when the app starts.
load_dotenv()

# Get database credentials from environment variables
POSTGRES_USER: Optional[str] = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD: Optional[str] = os.getenv("POSTGRES_PASSWORD")
DATABASE_NAME: str = os.getenv("DATABASE_NAME", "tarot_db")
DATABASE_HOST: str = os.getenv("DATABASE_HOST", "127.0.0.1")
DATABASE_PORT: str = os.getenv("DATABASE_PORT", "5432")

# Database connection pool - Will be initialized in the lifespan event handler
pool: Optional[asyncpg.Pool] = None

async def connect_to_db():
    """
    Establishes the database connection pool based on environment variables.
    Raises an exception if the connection fails.
    """
    global pool # Declare pool as global to modify the module-level variable
    print("Attempting to create database connection pool...")
    if not POSTGRES_USER or not POSTGRES_PASSWORD:
         print("Error: POSTGRES_USER or POSTGRES_PASSWORD environment variable not set.")
         # Raise a specific error here if credentials are missing
         raise ValueError("Database credentials (POSTGRES_USER or POSTGRES_PASSWORD) not set in environment variables.")

    try:
        db_port_int: int = int(DATABASE_PORT) if DATABASE_PORT else 5432
        # Use asyncpg.create_pool with explicit parameters
        pool = await asyncpg.create_pool(
            database=DATABASE_NAME,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=DATABASE_HOST,
            port=db_port_int
        )
        print("Database connection pool created successfully.")
    except Exception as e:
        print(f"Database connection pool creation failed: {e}")
        # Re-raise the exception to signal failure on startup
        raise e # IMPORTANT: This will cause the application startup to fail


async def close_db_connection():
    """
    Closes the database connection pool if it exists.
    """
    global pool # Declare pool as global to access the module-level variable
    print("Closing database connection pool...")
    if pool:
        await pool.close()
        print("Database connection pool closed.")
    else:
        print("No database pool to close.")

# --- Data Access Object (DAO) Functions ---

async def get_card_description_by_key(key: str) -> Optional[str]:
    """
    Retrieves a card description from the 'card_descriptions' table by key.
    Handles database operational errors.
    """
    if not pool:
        print(f"Database pool not available for description lookup for key '{key}'.")
        # Instead of returning None, we should raise an HTTPException if the service is unavailable
        raise HTTPException(status_code=503, detail="Database service unavailable: Connection pool not initialized.")

    try:
        async with pool.acquire() as connection:
            # Execute the query to fetch the description
            row: Optional[asyncpg.Record] = await connection.fetchrow(
                "SELECT description FROM card_descriptions WHERE key=$1", key
            )
            if row:
                return row['description']
            return None # Return None if key not found
    except asyncpg.exceptions.PostgresError as e:
        # Catch specific asyncpg database errors
        print(f"Postgres error retrieving description for key '{key}': {e}")
        # Re-raise as HTTPException to be handled by FastAPI
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")
    except Exception as e:
        # Catch any other unexpected errors during the query
        print(f"Unexpected error retrieving description for key '{key}': {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected database error occurred: {e}")

async def get_all_card_data() -> List[Dict[str, Any]]:
    """
    Retrieves all data from the 'card_descriptions' table using SELECT *.
    Handles database operational errors.
    """
    if not pool:
        print("Database pool not available for fetching all card data.")
        raise HTTPException(status_code=503, detail="Database service unavailable: Connection pool not initialized.")

    try:
        async with pool.acquire() as connection:
            # Execute the SELECT * query
            rows: List[asyncpg.Record] = await connection.fetch("SELECT * FROM card_descriptions")
            return [dict(row) for row in rows]
    except asyncpg.exceptions.PostgresError as e:
        print(f"Postgres error fetching all card data: {e}")
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")
    except Exception as e:
        print(f"Unexpected error fetching all card data: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected database error occurred: {e}")

# You could add more DAO functions here for other database operations (e.g., adding, updating cards)
