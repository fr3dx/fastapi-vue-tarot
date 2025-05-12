import os
from minio import Minio
from dotenv import load_dotenv

# Load environment variables from a .env file (e.g., credentials, config settings)
load_dotenv()

# Initialize the MinIO client with credentials from environment variables or fallback defaults
client = Minio(
    endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000"),  # Address of the MinIO server
    access_key = os.getenv("MINIO_ACCESS_KEY", "test"),  # Access key (default: 'test' if not set)
    secret_key = os.getenv("MINIO_SECRET_KEY", "test"),  # Secret key (default: 'test' if not set)
    secure = False  # Use HTTP instead of HTTPS
)

bucket_name = os.getenv("MINIO_BUCKET_TAROT", "test")

# Check if the specified bucket exists, and create it if it does not
if not client.bucket_exists(bucket_name):
    client.make_bucket(bucket_name)

# Path to the local folder containing files to upload
folder_path = os.getenv("MINIO_FOLDER_PATH", "./test")

# Iterate through each file in the folder
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)

    # Ensure that we only attempt to upload actual files, not directories
    if os.path.isfile(file_path):
        # Determine the correct content type (MIME type) based on the file extension
        content_type = "image/png" if filename.lower().endswith(".png") else "application/octet-stream"

        # Upload the file to the specified MinIO bucket
        client.fput_object(
            bucket_name,
            filename,         # Object name in the bucket (same as the file name)
            file_path,        # Local path to the file
            content_type=content_type  # MIME type for the uploaded object
        )
        print(f"{filename} Uploaded...")  # Log the uploaded file name in Hungarian
