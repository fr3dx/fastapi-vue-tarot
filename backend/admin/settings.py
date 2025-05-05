from pydantic import BaseSettings

class Settings(BaseSettings):
    SECRET: str = "verysecret"
    DATABASE_URL: str = "sqlite://db.sqlite3"  # vagy a te Postgres URL-ed
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"

settings = Settings()
