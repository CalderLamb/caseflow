from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://caseflow:caseflow@localhost:5432/caseflow"
    REDIS_URL: str = "redis://localhost:6379/0"

    ANTHROPIC_API_KEY: str = ""

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/callback"
    DRIVE_ROOT_FOLDER_ID: str = "1ndXrubfGj7pSY-ms6XkcJrawcEoEg8WZ"

    SECRET_KEY: str = "dev-secret-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

    APP_ENV: str = "development"
    LOG_LEVEL: str = "info"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
