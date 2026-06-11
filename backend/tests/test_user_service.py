"""Unit tests for UserService, exercising the full service->repository slice
against an in-memory Mongo.
"""
from __future__ import annotations

import pytest

from src.core.exceptions import ConflictError, UnauthorizedError
from src.core.security import decode_access_token
from src.schemas.user_schema import UserLoginRequest, UserRegisterRequest


@pytest.fixture
def register_payload() -> UserRegisterRequest:
    return UserRegisterRequest(email="user@example.com", password="supersecret1")


async def test_register_creates_user_and_returns_token(user_service, register_payload):
    result = await user_service.register(register_payload)

    assert result.user.email == "user@example.com"
    assert result.user.id
    claims = decode_access_token(result.access_token)
    assert claims is not None
    assert claims["sub"] == result.user.id


async def test_register_duplicate_email_raises_conflict(user_service, register_payload):
    await user_service.register(register_payload)
    with pytest.raises(ConflictError):
        await user_service.register(register_payload)


async def test_password_is_not_stored_in_plaintext(user_repository, user_service, register_payload):
    await user_service.register(register_payload)
    stored = await user_repository.find_by_email("user@example.com")
    assert stored is not None
    assert stored.password_hash != "supersecret1"


async def test_login_with_correct_credentials_succeeds(user_service, register_payload):
    await user_service.register(register_payload)
    result = await user_service.login(
        UserLoginRequest(email="user@example.com", password="supersecret1")
    )
    assert result.user.email == "user@example.com"


async def test_login_with_wrong_password_raises_unauthorized(user_service, register_payload):
    await user_service.register(register_payload)
    with pytest.raises(UnauthorizedError):
        await user_service.login(
            UserLoginRequest(email="user@example.com", password="wrongpassword")
        )


async def test_login_unknown_email_raises_unauthorized(user_service):
    with pytest.raises(UnauthorizedError):
        await user_service.login(
            UserLoginRequest(email="nobody@example.com", password="whatever12")
        )


async def test_get_profile_returns_user(user_service, register_payload):
    registered = await user_service.register(register_payload)
    profile = await user_service.get_profile(registered.user.id)
    assert profile.email == "user@example.com"
