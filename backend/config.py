"""
Application configuration using pydantic-settings.
Reads from environment variables / .env file.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    DB_NAME: str = "newsdb"

    # JWT
    JWT_SECRET: str = "change_this_secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 10080  # 7 days

    # OpenAI
    OPENAI_API_KEY: str = ""

    # News APIs
    NEWS_API_KEY: str = ""
    GNEWS_API_KEY: str = ""

    # CORS — accepts comma-separated string OR list
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins whether stored as list or comma-separated string."""
        if isinstance(self.CORS_ORIGINS, str):
            return [o.strip() for o in self.CORS_ORIGINS.split(",")]
        return self.CORS_ORIGINS


settings = Settings()
