# Tarot Card Draw Application (Readme not ready)

A modern, containerized tarot card drawing app built with a Vue.js SPA frontend, FastAPI backend, MinIO object storage, and PostgreSQL database. Users can draw a random tarot card once per day, with card images stored in MinIO.

---

## Technology Stack

* **Frontend:** Vue.js Single Page Application (SPA) served by NGINX
* **Backend:** FastAPI (Python) REST API
* **Authentication:** Google OAuth 2.0 (JWT-based authentication)
* **Storage:** MinIO (S3-compatible object storage)
* **Database:** PostgreSQL
* **Containerization:** Docker Compose with separate containers for each service

---

## Architecture Overview

```plaintext
[Vue.js SPA + NGINX] <--> [FastAPI Backend] <--> [PostgreSQL Database]
                             |
                             +--> [MinIO Object Storage]
```

---

## Installation and Running

This application is containerized using Docker Compose. To run it, you will need Docker and Docker Compose installed on your system.

1.  **Clone the Repository:**
    ```bash
    https://github.com/fr3dx/fastapi-vue-tarot.git
    cd fastapi-vue-tarot
    ```

2.  **Create a `.env` File:**
    Create the `.env` file in the root of the project and fill in the necessary environment variables:

    ```dotenv
    # Container
    POSTGRES_USER=username
    POSTGRES_PASSWORD=password
    POSTGRES_DB=test_db

    # Backend
    DB_HOST=test-db
    DB_PORT=5432
    DB_NAME=test_db
    DB_USER=username
    DB_PASSWORD=password.

    # Minio
    MINIO_ENDPOINT=minio:9000
    MINIO_ROOT_USER=
    MINIO_ROOT_PASSWORD=
    MINIO_BUCKET_TAROT=yourbucket
    MINIO_PUBLIC_URL=http://localhost:9000
    USE_PRESIGNED_URL=false

    # Folder where datas uploaded to bucket
    MINIO_FOLDER_PATH='C:\Users\your\path'

    # Oauth Google
    GOOGLE_CLIENT_ID=google_token.apps.googleusercontent.com
    GOOGLE_CLIENT_SECRET=google_secret
    DATABASE_URL=postgresql+psycopg2://username:password@test-db:5432/test_db

    # FastAPI JWT secret key
    JWT_SECRET_KEY=your-secret-token

    # Frontend App.vue
    VITE_BACKEND_URL=http://localhost:8000
    VITE_GOOGLE_CLIENT_ID=google_token.apps.googleusercontent.com

    # Helper scripts
    DB_HOST_HELPER_SCRIPTS=localhost
    MINIO_ENDPOINT_HELPER_SCRIPTS=localhost:9000
    ```
    **Important:** Make sure to use secure and unique values for your passwords and secret keys.

3.  **Start the Containers:**
    Run the following command from the project root directory:

    ```bash
    docker-compose up -d
    ```
    This will build the necessary Docker images (if they don't exist) and start the containers in the background.

4.  **Access the Application:**
    The application should be accessible in your browser at `http://localhost` (or on a different port depending on your configuration).

5.  **Set up the DB/MINIO, reset dialy draw and examples:**
Set up DB and MINIO:
```
python set_up_db_and_all_tables_psql_prod.py && python set_up_minio_prod.py && python load_tarot_cards_to_minio.py
```
Reset dialy draw:
```
UPDATE users SET last_draw_date = NULL WHERE id = 1;
```
Example curl commands with JWT, first card draw:
```
curl -X 'GET' 'http://localhost:8000/api/daily_card' -H 'accept: application/json' -H "Authorization: Bearer token"
{"name":"The Of Cups","image_url":"http://localhost:9000/tarot-cards/king_of_cups.png","key":"king_of_cups"}
```
Second card draw within one day:
```
curl -X 'GET' 'http://localhost:8000/api/daily_card' -H 'accept: application/json' -H "Authorization: Bearer token"
{"error":true,"message":"Már húztál ma egy kártyát."}
```

---

## Development

If you wish to develop on the application, the Docker Compose configuration can be modified to mount your local code into the containers, allowing for hot-reloading or immediate changes as you edit the code. Refer to the `docker-compose.yml` file for details.

---

## Contributing

Contributions are welcome! If you find a bug or have an idea for a new feature, please open an issue or submit a pull request. Please adhere to our contributing guidelines (if any are provided).

---

## License

This project is licensed under the [MIT](https://mit-license.org/) License. 

---

<p align="center">
  Built with ❤️ and rational thought. <br />
  <em>Amore et ratione.</em>
</p>