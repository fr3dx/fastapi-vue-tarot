import os
from minio import Minio
from dotenv import load_dotenv

load_dotenv()

client = Minio(
    "localhost:9000",
    access_key=os.getenv("MINIO_ACCESS_KEY", "test"),
    secret_key=os.getenv("MINIO_SECRET_KEY", "test"),
    secure=False
)

bucket_name = "tarot-cards"

if not client.bucket_exists(bucket_name):
    client.make_bucket(bucket_name)

folder_path = "./cards-test"

for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)

    # Csak fájlokat töltsünk (ne mappákat)
    if os.path.isfile(file_path):
        content_type = "image/png" if filename.lower().endswith(".png") else "application/octet-stream"

        client.fput_object(
            bucket_name,
            filename,    # Ezzel a névvel kerül fel a bucketbe
            file_path,
            content_type=content_type
        )
        print(f"{filename} feltöltve.")
