# Tarot Card Draw Application

A modern, containerized tarot card drawing app built with a Vue.js SPA frontend, FastAPI backend, MinIO object storage, and PostgreSQL database. Users can draw a random tarot card once per day, with card images stored in MinIO.

---

## Technology Stack

* **Frontend:** Vue.js SPA served by NGINX with i18n (English & Hungarian)
* **Backend:** FastAPI (Python) REST API
* **Authentication:** Google OAuth 2.0 (JWT-based authentication)
* **Storage:** MinIO (S3-compatible object storage)
* **Database:** PostgreSQL
* **Containerization:** Docker Compose with separate containers for each service

---

## Multilanguage Support

This application supports **multiple languages** (currently English and Hungarian) using `vue-i18n`.

- The frontend automatically detects the user's browser language.
- Supported locales: `en` (English) and `hu` (Hungarian).
- New translations can be added easily in the `locales/` directory.
- The Google OAuth login UI tries to adapt to the browser language, but results may vary depending on Google’s behavior.

You can override the language by changing your browser’s language settings.

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

2. **Create a `.env` File:**
    Create the `.env` file in the root and the frontend of the project and fill in the necessary environment variables.

3.  **Start the Containers:**
    Run the following command from the project root directory:

    ```bash
    docker-compose up -d db minio
    ```

    ```bash
    python set_up_db_and_all_tables_multilanguage_psql_prod.py && python set_up_minio_prod.py && python load_tarot_cards_to_minio.py
    ```

    ```bash
    docker-compose up -d backend frontend
    ```
    This will build the necessary Docker images (if they don't exist) and start the containers in the background.

4.  **Access the Application:**
    The application should be accessible in your browser at `http://localhost` (or on a different port depending on your configuration).

5.  **Reset dialy draw and cURL examples:**
    Reset dialy draw:
    ```bash
    UPDATE users SET last_draw_date = NULL WHERE id = 1;
    ```

    Example curl commands with JWT, first card draw:
    ```bash
    curl -X 'GET' 'http://localhost:8000/api/daily_card' -H 'accept: application/json' -H "Authorization: Bearer token"
    {"name":"The Of Cups","image_url":"http://localhost:9000/tarot-cards/king_of_cups.png","key":"king_of_cups"}
    ```
    Second card draw within one day:
    ```bash
    curl -X 'GET' 'http://localhost:8000/api/daily_card' -H 'accept: application/json' -H "Authorization: Bearer token"
    {"error":true,"message":"Már húztál ma egy kártyát."}
    ```
    ---

    ## The frontend
    ![Frontend1](/images/1.png)
    ![Frontend2](/images/2.png)
    ![Frontend3](/images/3.png)
    ![Frontend4](/images/4.png)
    ![Frontend5](/images/5.png)
    ![Frontend6](/images/6.png)

    ---

    ## License
    This project released under the [GNU General Public License.](https://www.gnu.org/licenses/gpl-3.0-standalone.html). 

    ---

    <p align="center">
    Built with ❤️ and rational thought. <br />
    <em>Amore et ratione.</em>
    </p>
