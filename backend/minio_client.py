from minio import Minio

# Csatlakozás a MinIO szerverhez
client = Minio(
    "localhost:9000",        # MinIO host és port
    access_key="fr3dx", # Hozzáférési kulcs
    secret_key="Mocskosf3r3g...", # Titkos kulcs
    secure=False             # HTTPS helyett HTTP (ha nincs TLS)
)

BUCKET_NAME = "tarot-cards"
