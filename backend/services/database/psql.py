from typing import Optional, List, Dict, Any
import asyncpg
import os
from dotenv import load_dotenv
from fastapi import HTTPException

# Load environment variables – helpful if this module is run directly.
# In a typical FastAPI app, this is usually done in the main entry point.
load_dotenv()

# Retrieve database configuration from environment variables.
POSTGRES_USER: Optional[str] = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD: Optional[str] = os.getenv("POSTGRES_PASSWORD")
DATABASE_NAME: str = os.getenv("DATABASE_NAME", "tarot_db")
DATABASE_HOST: str = os.getenv("DATABASE_HOST", "127.0.0.1")
DATABASE_PORT: str = os.getenv("DATABASE_PORT", "5432")

# Global database connection pool – initialized during application startup.
pool: Optional[asyncpg.Pool] = None

async def connect_to_db():
    """
    Initializes the asyncpg database connection pool using environment settings.
    Should be called during the application startup lifecycle event.
    """
    global pool  # Use the global pool reference
    print("Attempting to create database connection pool...")
    
    if not POSTGRES_USER or not POSTGRES_PASSWORD:
        print("Error: POSTGRES_USER or POSTGRES_PASSWORD environment variable not set.")
        raise ValueError("Database credentials (POSTGRES_USER or POSTGRES_PASSWORD) not set in environment variables.")

    try:
        db_port_int: int = int(DATABASE_PORT) if DATABASE_PORT else 5432
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
        raise e  # Let the exception propagate to halt app startup if needed

async def close_db_connection():
    """
    Gracefully closes the database connection pool if it exists.
    Should be called during application shutdown.
    """
    global pool
    print("Closing database connection pool...")
    
    if pool:
        await pool.close()
        print("Database connection pool closed.")
    else:
        print("No database pool to close.")

# --- Data Access Object (DAO) Functions ---

async def get_card_description_by_key(key: str) -> Optional[str]:
    """
    Retrieves a single card description by key from the 'card_descriptions' table.
    Raises an HTTP 503 error if the connection pool is not initialized.
    Handles Postgres and general exceptions gracefully.
    """
    if not pool:
        print(f"Database pool not available for description lookup for key '{key}'.")
        raise HTTPException(status_code=503, detail="Database service unavailable: Connection pool not initialized.")

    try:
        async with pool.acquire() as connection:
            row: Optional[asyncpg.Record] = await connection.fetchrow(
                "SELECT description FROM card_descriptions WHERE key=$1", key
            )
            if row:
                return row['description']
            return None  # No result found for the given key
    except asyncpg.exceptions.PostgresError as e:
        print(f"Postgres error retrieving description for key '{key}': {e}")
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")
    except Exception as e:
        print(f"Unexpected error retrieving description for key '{key}': {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected database error occurred: {e}")

async def get_all_card_data() -> List[Dict[str, Any]]:
    """
    Fetches all rows from the 'card_descriptions' table.
    Returns a list of dictionaries, one per row.
    Raises an HTTP 503 error if the database connection is not available.
    """
    if not pool:
        print("Database pool not available for fetching all card data.")
        raise HTTPException(status_code=503, detail="Database service unavailable: Connection pool not initialized.")

    try:
        async with pool.acquire() as connection:
            rows: List[asyncpg.Record] = await connection.fetch("SELECT * FROM card_descriptions")
            return [dict(row) for row in rows]
    except asyncpg.exceptions.PostgresError as e:
        print(f"Postgres error fetching all card data: {e}")
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")
    except Exception as e:
        print(f"Unexpected error fetching all card data: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected database error occurred: {e}")

# Additional DAO functions can be added here (e.g., insert, update, delete operations).

async def insert_or_get_user(sub: str, email: Optional[str], name: Optional[str]) -> Dict[str, Any]:
    if not pool:
        raise HTTPException(status_code=503, detail="DB unavailable")

    query = """
    INSERT INTO users (sub, email, name)
    VALUES ($1, $2, $3)
    ON CONFLICT (sub) DO NOTHING;

    SELECT id, sub, email, name, created_at, last_draw_date
    FROM users
    WHERE sub = $1;
    """
    async with pool.acquire() as conn:
        await conn.execute(query.split(";")[0], sub, email, name)
        row = await conn.fetchrow(query.split(";")[1], sub)
        return dict(row) if row else {}

async def get_user_by_sub(sub: str) -> Optional[Dict[str, Any]]:
    if not pool:
        raise HTTPException(status_code=503, detail="DB unavailable")
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT id, sub, email, name, created_at, last_draw_date
            FROM users
            WHERE sub = $1;
        """, sub)
        return dict(row) if row else None