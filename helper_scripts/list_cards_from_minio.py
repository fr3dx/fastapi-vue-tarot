from minio import Minio
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Store endpoint and bucket in variables to reuse later
endpoint = os.getenv("MINIO_ENDPOINT_HELPER_SCRIPTS", "localhost:9000")
bucket_name = os.getenv("MINIO_BUCKET_TAROT", "test")

# Initialize the MinIO client
client = Minio(
    endpoint=endpoint,
    access_key=os.getenv("MINIO_ACCESS_KEY", "test"),
    secret_key=os.getenv("MINIO_SECRET_KEY", "test"),
    secure=False
)

# List all objects in the bucket
objects = client.list_objects(bucket_name)

# Print filenames and their corresponding public URLs
for obj in objects:
    file_name = obj.object_name
    url = f"http://{endpoint}/{bucket_name}/{file_name}"  # Use the saved endpoint here
    print(f"{file_name} -> {url}")
