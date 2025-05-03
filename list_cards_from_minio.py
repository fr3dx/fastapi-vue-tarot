from minio import Minio
from dotenv import load_dotenv
import os

load_dotenv()

client = Minio(
    "localhost:9000",
    access_key=os.getenv("MINIO_ACCESS_KEY", "test"),
    secret_key=os.getenv("MINIO_SECRET_KEY", "test"),
    secure=False
)

bucket_name = "tarot-cards"

# Fájlok listázása
objects = client.list_objects(bucket_name)

for obj in objects:
    file_name = obj.object_name
    url = f"http://localhost:9000/{bucket_name}/{file_name}"
    print(f"{file_name} -> {url}")
