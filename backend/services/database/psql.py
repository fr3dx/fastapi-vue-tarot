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

async def get_card_data_by_key_and_lang(key: str, lang: str = "hu") -> Optional[Dict[str, str]]:
    """
    Retrieves card name and description from the database by card key and language.

    Returns:
        Optional[Dict[str, str]]: {"name": ..., "description": ...} or None
    """
    if not pool:
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        async with pool.acquire() as connection:
            card_row = await connection.fetchrow(
                "SELECT id FROM cards WHERE key=$1",
                key
            )
            if not card_row:
                return None

            card_id = card_row['id']

            row = await connection.fetchrow(
                "SELECT name, description FROM card_translations WHERE card_id=$1 AND lang=$2",
                card_id, lang
            )
            if row:
                return {"name": row["name"], "description": row["description"]}

            # fallback magyarul
            row = await connection.fetchrow(
                "SELECT name, description FROM card_translations WHERE card_id=$1 AND lang='hu'",
                card_id
            )
            if row:
                return {"name": row["name"], "description": row["description"]}

            return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")

async def get_all_card_data(lang: Optional[str] = "hu") -> List[Dict[str, Any]]:
    """
    Fetches all card translations for the given language from the 'card_translations' table.

    Args:
        lang (str, optional): Language code to filter by (default is 'hu').

    Returns:
        List[Dict[str, Any]]: A list of card descriptions for the requested language.

    Raises:
        HTTPException: If the pool is uninitialized or the query fails.
    """
    if not pool:
        print("Database pool not initialized.")
        raise HTTPException(status_code=503, detail="Database unavailable")

    try:
        async with pool.acquire() as connection:
            query = """
                SELECT c.key, ct.lang, ct.name, ct.description
                FROM cards c
                JOIN card_translations ct ON c.id = ct.card_id
                WHERE ct.lang = $1
                ORDER BY c.id
            """
            rows = await connection.fetch(query, lang)
            return [dict(row) for row in rows]

    except asyncpg.exceptions.PostgresError as e:
        print(f"Postgres error while fetching cards for lang '{lang}': {e}")
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")
    except Exception as e:
        print(f"Unexpected error while fetching cards for lang '{lang}': {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

async def insert_or_get_user(sub: str, email: Optional[str], name: Optional[str], lang: Optional[str]) -> Dict[str, Any]:
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
    INSERT INTO users (sub, email, name, lang)
    VALUES ($1, $2, $3, $4)
    ON CONFLICT (sub) DO UPDATE SET
    email = EXCLUDED.email,
    name = EXCLUDED.name,
    lang = EXCLUDED.lang
    RETURNING id, sub, email, name, lang, created_at, last_draw_date;
    """
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, sub, email, name, lang)
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
