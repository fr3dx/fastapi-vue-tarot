from typing import Optional, List, Dict, Any
import asyncpg
import os
from dotenv import load_dotenv
from fastapi import HTTPException
from datetime import datetime

# Load environment variables from a .env file (typically used during development)
load_dotenv()

# Database configuration from environment
POSTGRES_USER: Optional[str] = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD: Optional[str] = os.getenv("POSTGRES_PASSWORD")
DATABASE_NAME: str = os.getenv("DB_NAME", "tarot_db")
DATABASE_HOST: str = os.getenv("DB_HOST", "127.0.0.1")
DATABASE_PORT: str = os.getenv("DB_PORT", "5432")

# Global connection pool variable, initialized during application startup
pool: Optional[asyncpg.Pool] = None

async def connect_to_db():
    """
    Establishes an asyncpg connection pool to the PostgreSQL database.
    This should be called once during the application's startup event.
    """
    global pool
    print("Attempting to create database connection pool...")

    if not POSTGRES_USER or not POSTGRES_PASSWORD:
        print("Error: Missing POSTGRES_USER or POSTGRES_PASSWORD environment variables.")
        raise ValueError("Missing required database credentials in environment variables.")

    try:
        db_port_int = int(DATABASE_PORT) if DATABASE_PORT else 5432
        pool = await asyncpg.create_pool(
            database=DATABASE_NAME,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=DATABASE_HOST,
            port=db_port_int
        )
        print("Database connection pool created successfully.")
    except Exception as e:
        print(f"Failed to create database connection pool: {e}")
        raise e  # Propagate the exception to fail app startup

async def close_db_connection():
    """
    Closes the database connection pool gracefully.
    Should be invoked during application shutdown.
    """
    global pool
    print("Closing database connection pool...")

    if pool:
        await pool.close()
        print("Database connection pool closed.")
    else:
        print("No active database connection pool to close.")

# ------------------- Data Access Layer (DAO) -------------------

async def get_card_description_by_key(key: str) -> Optional[str]:
    """
    Retrieves a card description from the 'card_descriptions' table by key.
    
    Args:
        key (str): The unique key identifier of the card.
    
    Returns:
        Optional[str]: The description if found, otherwise None.

    Raises:
        HTTPException: If the database pool is not initialized or the query fails.
    """
    if not pool:
        print(f"Database pool not available for key '{key}'.")
        raise HTTPException(status_code=503, detail="Database unavailable")

    try:
        async with pool.acquire() as connection:
            row = await connection.fetchrow(
                "SELECT description FROM card_descriptions WHERE key=$1", key
            )
            return row['description'] if row else None
    except asyncpg.exceptions.PostgresError as e:
        print(f"Postgres error for key '{key}': {e}")
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")
    except Exception as e:
        print(f"Unexpected error for key '{key}': {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

async def get_all_card_data() -> List[Dict[str, Any]]:
    """
    Fetches all records from the 'card_descriptions' table.

    Returns:
        List[Dict[str, Any]]: A list of all card descriptions.

    Raises:
        HTTPException: If the pool is uninitialized or the query fails.
    """
    if not pool:
        print("Database pool not initialized.")
        raise HTTPException(status_code=503, detail="Database unavailable")

    try:
        async with pool.acquire() as connection:
            rows = await connection.fetch("SELECT * FROM card_descriptions")
            return [dict(row) for row in rows]
    except asyncpg.exceptions.PostgresError as e:
        print(f"Postgres error while fetching all cards: {e}")
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")
    except Exception as e:
        print(f"Unexpected error while fetching all cards: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

async def insert_or_get_user(sub: str, email: Optional[str], name: Optional[str]) -> Dict[str, Any]:
    """
    Inserts a new user if they do not exist (based on 'sub'), then returns the user record.

    Args:
        sub (str): User's unique identifier (e.g., from JWT).
        email (Optional[str]): User's email address.
        name (Optional[str]): User's display name.

    Returns:
        Dict[str, Any]: User record.

    Raises:
        HTTPException: If the database is not available.
    """
    if not pool:
        raise HTTPException(status_code=503, detail="Database unavailable")

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
    """
    Retrieves a user record from the 'users' table by their unique subject identifier.

    Args:
        sub (str): User's unique identifier.

    Returns:
        Optional[Dict[str, Any]]: The user record if found, otherwise None.

    Raises:
        HTTPException: If the database is not available.
    """
    if not pool:
        raise HTTPException(status_code=503, detail="Database unavailable")

    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT id, sub, email, name, created_at, last_draw_date
            FROM users
            WHERE sub = $1;
        """, sub)
        return dict(row) if row else None

async def update_user_draw_date(sub: str):
    """
    Updates the user's last card draw date to the current UTC timestamp.

    Args:
        sub (str): User's unique identifier.

    Raises:
        HTTPException: If the database connection pool is not initialized.
    """
    if not pool:
        raise HTTPException(status_code=503, detail="Database unavailable")

    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE users
            SET last_draw_date = $1
            WHERE sub = $2
        """, datetime.utcnow(), sub)
