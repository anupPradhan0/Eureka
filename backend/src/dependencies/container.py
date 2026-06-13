"""Dependency injection wiring.

Builds each request's object graph from the bottom up:
    database -> repository -> service -> controller

Routes depend only on get_user_controller(); they never import concrete
repositories or services. This keeps the wiring in one place and the layers
decoupled.
"""
from __future__ import annotations

import httpx
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..config.database import Database, get_database
from ..config.settings import get_settings
from ..controllers.ai_config_controller import AIConfigController
from ..controllers.repository_controller import RepositoryController
from ..controllers.user_controller import UserController
from ..core.exceptions import UnauthorizedError
from ..core.security import decode_access_token
from ..providers.github.client import GitHubClient
from ..repositories.ai_config_repository import AIConfigRepository
from ..repositories.repository_repository import RepositoryRepository
from ..repositories.user_repository import UserRepository
from ..services.ai_config_service import AIConfigService
from ..services.repository_service import RepositoryService
from ..services.user_service import UserService

_bearer_scheme = HTTPBearer(auto_error=False)

# Process-wide HTTP client for all outbound calls (AI providers, GitHub).
# Reusing one client pools connections; it is closed in the app lifespan.
_http_client: httpx.AsyncClient | None = None


def get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None:
        settings = get_settings()
        _http_client = httpx.AsyncClient(timeout=settings.ai_http_timeout_seconds)
    return _http_client


async def close_http_client() -> None:
    """Close the shared client on shutdown. Idempotent."""
    global _http_client
    if _http_client is not None:
        await _http_client.aclose()
        _http_client = None


def get_user_controller(
    database: Database = Depends(get_database),
) -> UserController:
    user_repository = UserRepository(database.db)
    user_service = UserService(user_repository)
    return UserController(user_service)


def get_ai_config_controller(
    database: Database = Depends(get_database),
) -> AIConfigController:
    settings = get_settings()
    repository = AIConfigRepository(database.db)
    service = AIConfigService(repository, get_http_client(), settings.encryption_key)
    return AIConfigController(service)


def get_repository_controller(
    database: Database = Depends(get_database),
) -> RepositoryController:
    settings = get_settings()
    repository = RepositoryRepository(database.db)
    github_client = GitHubClient(get_http_client(), settings.github_http_timeout_seconds)
    service = RepositoryService(
        repository,
        github_client,
        settings.encryption_key,
        settings.github_tree_max_entries,
    )
    return RepositoryController(service)


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> str:
    """Extract and verify the user id from the Bearer token."""
    if credentials is None:
        raise UnauthorizedError("Missing authentication token.")
    claims = decode_access_token(credentials.credentials)
    if claims is None or "sub" not in claims:
        raise UnauthorizedError("Invalid or expired token.")
    return str(claims["sub"])
