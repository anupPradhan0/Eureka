"""User/auth business logic.

Depends on the IUserRepository abstraction, not a concrete database. Knows
nothing about HTTP — it raises domain errors and returns entities/DTOs.
"""
from __future__ import annotations

from ..core.exceptions import ConflictError, UnauthorizedError
from ..core.security import create_access_token, hash_password, verify_password
from ..models.user_model import UserModel
from ..repositories.interfaces.iuser_repository import IUserRepository
from ..schemas.user_schema import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)


class UserService:
    def __init__(self, user_repository: IUserRepository) -> None:
        self._users = user_repository

    async def register(self, payload: UserRegisterRequest) -> TokenResponse:
        """Create a new account and return an access token."""
        existing = await self._users.find_by_email(payload.email)
        if existing is not None:
            raise ConflictError("An account with this email already exists.")

        user = UserModel(
            email=payload.email,
            password_hash=hash_password(payload.password),
        )
        created = await self._users.create(user)
        return self._build_token_response(created)

    async def login(self, payload: UserLoginRequest) -> TokenResponse:
        """Authenticate credentials and return an access token."""
        user = await self._users.find_by_email(payload.email)
        # Use a uniform error to avoid leaking which part was wrong.
        if user is None or not verify_password(payload.password, user.password_hash):
            raise UnauthorizedError("Invalid email or password.")
        return self._build_token_response(user)

    async def get_profile(self, user_id: str) -> UserResponse:
        """Return the public profile for an authenticated user."""
        user = await self._users.find_by_id(user_id)
        if user is None:
            raise UnauthorizedError("Account no longer exists.")
        return UserResponse.from_model(user)

    @staticmethod
    def _build_token_response(user: UserModel) -> TokenResponse:
        token = create_access_token(subject=user.id or "")
        return TokenResponse(
            access_token=token,
            user=UserResponse.from_model(user),
        )
