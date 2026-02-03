from typing import List
from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    """
    Farmart backend configuration.

    Loads environment variables (supports .env file).
    CORS_ORIGINS accepts:
      - a list
      - a comma-separated string
      - "*" literal
    """

    PROJECT_NAME: str = "Farmart"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000

    DATABASE_URL: str
    DB_ECHO: bool = False

    CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["*"])
    ALLOWED_HOSTS: List[str] = Field(default_factory=lambda: ["*"])
    ENABLE_GZIP: bool = Tru_
