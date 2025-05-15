# Tarot Card Draw Application

A modern, containerized tarot card drawing app built with a Vue.js SPA frontend, FastAPI backend, MinIO object storage, and PostgreSQL database. Users can draw a random tarot card once per day, with card images stored in MinIO.

---

## Technology Stack

*   **Frontend:** Vue.js Single Page Application (SPA) served by NGINX
*   **Backend:** FastAPI (Python) REST API
*   **Storage:** MinIO (S3-compatible object storage)
*   **Database:** PostgreSQL
*   **Containerization:** Docker Compose with separate containers for each service

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
    git clone <your repository URL>
    cd <your repository folder>
    ```

2.  **Create a `.env` File:**
    Copy the example `.env` file (if provided) or create a new one in the root of the project and fill in the necessary environment variables:

    ```dotenv
    # PostgreSQL
    POSTGRES_USER=your_postgres_user
    POSTGRES_PASSWORD=your_postgres_password
    POSTGRES_DB=your_postgres_db_name

    # MinIO
    MINIO_ACCESS_KEY=your_minio_access_key
    MINIO_SECRET_KEY=your_minio_secret_key
    MINIO_PUBLIC_URL=http://localhost:9000 # Or your reverse proxy URL

    # Backend
    DATABASE_URL=postgresql://your_postgres_user:your_postgres_password@db:5432/your_postgres_db_name
    JWT_SECRET_KEY=a_very_secret_key_for_jwt

    # Control whether to use presigned URLs for image access
    USE_PRESIGNED_URL=false  # "true" or "false"

    # Frontend (e.g. for Google OAuth)
    VITE_BACKEND_URL=http://localhost:8000 # Or your backend URL
    VITE_GOOGLE_CLIENT_ID=your_google_client_id
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

---

## Development

If you wish to develop on the application, the Docker Compose configuration can be modified to mount your local code into the containers, allowing for hot-reloading or immediate changes as you edit the code. Refer to the `docker-compose.yml` file for details.

---

## Contributing

Contributions are welcome! If you find a bug or have an idea for a new feature, please open an issue or submit a pull request. Please adhere to our contributing guidelines (if any are provided).

---

## License

This project is licensed under the [LICENSE NAME] License. See the `LICENSE` file for details.

---

Built with ❤️ and rational thought.
Amore et ratione.
