from pydantic import BaseSettings

class Settings(BaseSettings):
    """
    Application configuration settings.

    This class loads environment variables and provides centralized access to 
    configuration values such as third-party API credentials and database connection URLs.

    Attributes:
    - google_client_id (str): Google OAuth 2.0 client ID used for user authentication.
    - google_client_secret (str): Google OAuth 2.0 client secret.
    - database_url (str): Database connection string (e.g., PostgreSQL URI).
    """

    google_client_id: str
    google_client_secret: str
    database_url: str

    class Config:
        # Specifies the file from which to load environment variables
        env_file = ".env"

# Instantiate and expose settings globally
settings = Settings()
