import os
from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Initialize the MinIO client with credentials from environment variables or fallback defaults
client = Minio(
    endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000"),  # Address of the MinIO server
    access_key = os.getenv("MINIO_ACCESS_KEY", "test"),        # Access key (default: 'test' if not set)
    secret_key = os.getenv("MINIO_SECRET_KEY", "test"),        # Secret key (default: 'test' if not set)
    secure = False                                              # Use HTTP instead of HTTPS
)

# Get the bucket name from environment variables or use a fallback
bucket_name = os.getenv("MINIO_BUCKET_TAROT", "test")

# List of objects to delete from the bucket
objects_to_delete = [
    "card-back.pngxx",
    "empress.png",
    "fool.png",
    "magician.png"
]

print(f"Starting deletion from bucket '{bucket_name}'...")

try:
    # Delete objects listed in 'objects_to_delete'
    # The remove_objects() method returns an iterator containing any deletion errors
    errors = client.remove_objects(bucket_name, objects_to_delete)

    # Print any errors that occurred during deletion
    for error in errors:
        print(f"Error while deleting '{error.object_name}': {error.message}")

    print("Deletion process completed.")

except S3Error as exc:
    print(f"S3 error during deletion: {exc}")
except Exception as e:
    print(f"Unexpected error occurred: {e}")
