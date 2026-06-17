"""Application settings loaded from environment variables / .env.

Centralizes all configuration so no other layer reads os.environ directly.
"""
from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Insecure defaults that are fine for local dev but must never reach production.
# Defined once so both the field defaults and the production guard agree.
_DEV_ENCRYPTION_KEY = "1xNwJe7yBXM4XFGiE1eNWcMDQPrqAw8lG2epy-D4JmQ="
_DEV_JWT_SECRET = "change-me-in-production"


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

    # CORS — comma-separated list of allowed frontend origins.
    allowed_origins: str = "http://localhost:5173"

    # MongoDB
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "eureka"

    # Auth / JWT
    jwt_secret: str = _DEV_JWT_SECRET
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 60

    # Encryption — protects BYO API keys / tokens at rest (Fernet key, base64).
    # This default is for local dev only; set ENCRYPTION_KEY in production.
    # Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    encryption_key: str = _DEV_ENCRYPTION_KEY

    # Outbound HTTP (AI provider validation + GitHub API)
    ai_http_timeout_seconds: float = 15.0
    github_http_timeout_seconds: float = 20.0
    # Cap how many tree entries we keep from very large repos.
    github_tree_max_entries: int = 5000
    # Cap README content stored/returned, so a huge file can't bloat the response.
    readme_max_chars: int = 50_000

    # Agent — max tool-use turns per run, and the cap on a single file read fed
    # back to the model (keeps one giant file from blowing the context window).
    agent_max_iterations: int = 12
    agent_read_file_max_chars: int = 20_000

    @property
    def cors_origins(self) -> list[str]:
        """allowed_origins parsed into a clean list."""
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @model_validator(mode="after")
    def _require_secrets_in_production(self) -> "Settings":
        """Refuse to run in production with the public dev secrets."""
        if self.app_env == "production":
            if self.encryption_key == _DEV_ENCRYPTION_KEY:
                raise ValueError("ENCRYPTION_KEY must be set to a unique value in production.")
            if self.jwt_secret == _DEV_JWT_SECRET:
                raise ValueError("JWT_SECRET must be set to a unique value in production.")
        return self


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (read env once per process)."""
    return Settings()
