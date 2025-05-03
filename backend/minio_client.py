from minio import Minio
import os

# Csatlakozás a MinIO szerverhez
client = Minio(
    "localhost:9000",        # MinIO host és port
    access_key=os.getenv("MINIO_ACCESS_KEY", "test"),
    secret_key=os.getenv("MINIO_SECRET_KEY", "test"),
    secure=False             # HTTPS helyett HTTP (ha nincs TLS)
)

BUCKET_NAME = "tarot-cards"
