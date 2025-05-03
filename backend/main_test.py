# Imports
from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
import asyncpg
from contextlib import asynccontextmanager
import os # Import the os module to access environment variables
from dotenv import load_dotenv # Import load_dotenv from python-dotenv

# Load environment variables from the .env file
load_dotenv()

# Get database credentials from environment variables
# Use os.getenv() to read the environment variables
# Provide a default value (None in this case) or handle potential errors if the variable is missing
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DATABASE_NAME = os.getenv("DATABASE_NAME", "tarot_db") # Provide a default name if not specified in .env
DATABASE_HOST = os.getenv("DATABASE_HOST", "127.0.0.1") # Provide a default host
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432") # Provide a default port

# Construct the database connection URL
# We need to ensure the required variables (user and password) are available
if not POSTGRES_USER or not POSTGRES_PASSWORD:
    # If essential variables are missing, print an error or raise an exception
    print("Error: POSTGRES_USER or POSTGRES_PASSWORD environment variable not set.")
    # You might want to exit the application here if database connection is crucial
    # import sys
    # sys.exit(1)
    # For this example, we'll proceed but the DB connection will likely fail

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

# Lifespan event handler: Runs on application startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the lifecycle of the database connection pool.
    Creates the pool on startup and closes it on shutdown.
    """
    print("Creating database connection pool...")
    # Before creating the pool, check if the DATABASE_URL was successfully constructed
    if not POSTGRES_USER or not POSTGRES_PASSWORD:
         print("Skipping database connection due to missing credentials.")
         app.state.pool = None # Ensure pool is None if connection is skipped
         yield
         print("No database pool to close.")
         return # Exit the lifespan context early if connection skipped

    try:
        # Create the connection pool using the database URL
        # Convert port to integer if needed, although asyncpg might handle string ports
        db_port_int = int(DATABASE_PORT) if DATABASE_PORT else 5432
        # asyncpg.create_pool requires host and port as separate arguments sometimes, or the full URL
        # Using the full URL is generally supported. Let's stick to the URL for now.
        # If issues arise, you might need to pass host, port, user, password separately.
        app.state.pool = await asyncpg.create_pool(
            database=DATABASE_NAME,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=DATABASE_HOST,
            port=db_port_int # Pass port as integer
        )
        print("Database connection pool created successfully.")
    except Exception as e:
        # Handle potential errors during pool creation
        print(f"Failed to create database connection pool: {e}")
        app.state.pool = None # Ensure pool is None on failure
        # Depending on your app's requirements, you might re-raise the exception here:
        # raise e
    yield # Application starts processing requests after this point
    # Code to run on application shutdown: Close the database connection pool
    print("Closing database connection pool...")
    if hasattr(app.state, 'pool') and app.state.pool: # Check if the pool was successfully created
        await app.state.pool.close()
        print("Database connection pool closed.")
    else:
        print("No database pool to close.")


# IMPORTANT: The 'app' variable is created here
# Initialize the FastAPI application with the lifespan event handler
app = FastAPI(lifespan=lifespan)

# Funkció az összes elem lekérésére a 'card_descriptions' táblából a 'SELECT *' paranccsal
async def get_all_card_descriptions_full() -> List[Dict[str, Any]]:
    """
    Retrieves all data from the 'card_descriptions' table using 'SELECT *'.
    Returns the rows as a list of dictionaries.
    Raises HTTPException if the database pool is not available.
    """
    # Check if the database connection pool is initialized and available
    if not hasattr(app.state, 'pool') or not app.state.pool:
        print("Database pool not available.")
        # Raise an HTTPException to indicate that the database service is unavailable
        raise HTTPException(status_code=503, detail="Database service unavailable: Database pool not initialized.")
        # Alternatively, you could return an empty list if that's acceptable in your use case:
        # return []

    try:
        # Acquire a connection from the pool using an asynchronous context manager
        async with app.state.pool.acquire() as connection:
            # Execute the 'SELECT * FROM card_descriptions' SQL query
            rows: List[asyncpg.Record] = await connection.fetch("SELECT * FROM card_descriptions")

            # Convert the list of asyncpg.Record objects into a list of Python dictionaries
            return [dict(row) for row in rows]
    except Exception as e:
         # Catch any errors during the database interaction itself (after getting a connection)
         print(f"Error during database query: {e}")
         raise HTTPException(status_code=500, detail=f"Database query failed: {e}")


# Végpont az összes kártya leírás lekérésére a 'SELECT *' paranccsal
@app.get("/all_card_data")
async def get_all_card_data():
    """
    Returns all data from the 'card_descriptions' table from the database.
    """
    print("Request received for /all_card_data")
    try:
        # Call the function to get all data from the database
        all_data: List[Dict[str, Any]] = await get_all_card_descriptions_full()
        print(f"Retrieved {len(all_data)} rows from card_descriptions.")
        # Return the retrieved data as a JSON response
        return all_data
    except HTTPException as he:
        # If get_all_card_descriptions_full raises an HTTPException, re-raise it
        raise he
    except Exception as e:
        # This catch is mostly for unexpected errors that weren't caught in get_all_card_descriptions_full
        print(f"An unexpected error occurred in /all_card_data endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred: {e}")

# Root endpoint (optional, but useful for testing if the API is running)
@app.get("/")
async def read_root():
    """
    Basic root endpoint to confirm the API is running.
    """
    return {"message": "Tarot API is running."}

# Other endpoints (if any) would go here...
