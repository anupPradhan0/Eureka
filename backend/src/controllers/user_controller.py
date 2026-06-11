"""User/auth HTTP controller.

Thin layer that takes validated request DTOs, delegates to the service, and
returns response DTOs. It holds no business logic and no data access — domain
errors raised by the service are translated to HTTP by the app's exception
handler.
"""
from __future__ import annotations

from ..schemas.user_schema import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from ..services.user_service import UserService


class UserController:
    def __init__(self, user_service: UserService) -> None:
        self._service = user_service

    async def register(self, payload: UserRegisterRequest) -> TokenResponse:
        return await self._service.register(payload)

    async def login(self, payload: UserLoginRequest) -> TokenResponse:
        return await self._service.login(payload)

    async def get_profile(self, user_id: str) -> UserResponse:
        return await self._service.get_profile(user_id)
