"""Application settings loaded from environment variables / .env.

Centralizes all configuration so no other layer reads os.environ directly.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Server
    app_name: str = "Eureka"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # MongoDB
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "eureka"

    # Auth / JWT
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 60

    # Encryption — protects BYO API keys / tokens at rest (Fernet key, base64).
    # This default is for local dev only; set ENCRYPTION_KEY in production.
    # Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    encryption_key: str = "1xNwJe7yBXM4XFGiE1eNWcMDQPrqAw8lG2epy-D4JmQ="

    # Outbound HTTP (AI provider validation + GitHub API)
    ai_http_timeout_seconds: float = 15.0
    github_http_timeout_seconds: float = 20.0
    # Cap how many tree entries we keep from very large repos.
    github_tree_max_entries: int = 5000


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (read env once per process)."""
    return Settings()
