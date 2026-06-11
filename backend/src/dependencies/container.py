"""Dependency injection wiring.

Builds each request's object graph from the bottom up:
    database -> repository -> service -> controller

Routes depend only on get_user_controller(); they never import concrete
repositories or services. This keeps the wiring in one place and the layers
decoupled.
"""
from __future__ import annotations

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..config.database import Database, get_database
from ..controllers.user_controller import UserController
from ..core.exceptions import UnauthorizedError
from ..core.security import decode_access_token
from ..repositories.user_repository import UserRepository
from ..services.user_service import UserService

_bearer_scheme = HTTPBearer(auto_error=False)


def get_user_controller(
    database: Database = Depends(get_database),
) -> UserController:
    user_repository = UserRepository(database.db)
    user_service = UserService(user_repository)
    return UserController(user_service)


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
