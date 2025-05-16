from minio import Minio
import os
from dotenv import load_dotenv  # Ensure environment variables are loaded from a .env file

# Load environment variables – essential for MinIO credentials and configuration
load_dotenv()

# Create a MinIO client instance using credentials and configuration from environment variables.
# Defining it at the top-level scope makes it accessible throughout the application.
client: Minio = Minio(
    os.getenv("MINIO_ENDPOINT", "test"),  # MinIO endpoint
    access_key=os.getenv("MINIO_ROOT_USER", "test"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD", "test"),
    secure=os.getenv("MINIO_SECURE", "false").lower() == "true"  # Use HTTPS if specified
)

# Define the bucket name to be used throughout the application
BUCKET_NAME: str = os.getenv("MINIO_BUCKET_TAROT", "test")

# Optional check that can be performed at application startup to verify bucket existence.
# This can be invoked from a lifespan handler or startup event.
async def check_bucket_exists():
    """
    Verifies the existence of the configured MinIO bucket.
    Logs a warning if the bucket is not found. This function is intended
    to be called during application startup to ensure readiness.
    """
    try:
        found = client.bucket_exists(BUCKET_NAME)
        if not found:
            print(f"Warning: MinIO bucket '{BUCKET_NAME}' does not exist.")
            # Optionally: create the bucket or raise an error depending on application policy.
            # client.make_bucket(BUCKET_NAME)
            # raise Exception(f"MinIO bucket '{BUCKET_NAME}' does not exist and cannot be created automatically.")
        else:
            print(f"MinIO bucket '{BUCKET_NAME}' found.")
    except Exception as e:
        print(f"Error checking MinIO bucket '{BUCKET_NAME}': {e}")
        # Optionally re-raise the exception if the connection is critical for application startup
        # raise e

# The MinIO client handles its own connections and does not require explicit closing.
# Unlike connection pools (e.g., asyncpg), no cleanup function is needed for shutdown.
