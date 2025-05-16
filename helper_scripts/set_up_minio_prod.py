from minio import Minio
from dotenv import load_dotenv
import os
import json

# Load environment variables from a .env file
load_dotenv()

# Initialize MinIO client with connection settings from environment variables or defaults
client = Minio(
    endpoint=os.getenv("MINIO_ENDPOINT_HELPER_SCRIPTS", "localhost:9000"),
    access_key=os.getenv("MINIO_ROOT_USER", "test"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD", "test"),
    secure=False
)

bucket_name = os.getenv("MINIO_BUCKET_TAROT", "test")

# Define a read-only (anonymous download) bucket policy in JSON format
readonly_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"AWS": "*"},
            "Action": ["s3:GetObject"],
            "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
        }
    ]
}

try:
    # Create the bucket if it doesn't exist
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        print(f"Bucket '{bucket_name}' created.")
    else:
        print(f"Bucket '{bucket_name}' already exists.")

    # Set the bucket policy for public read-only access
    client.set_bucket_policy(bucket_name, json.dumps(readonly_policy))
    print(f"Read-only public access policy applied to '{bucket_name}'.")

except Exception as e:
    print(f"Error: {e}")
