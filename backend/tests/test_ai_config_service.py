"""Unit tests for AIConfigService over an in-memory Mongo + stubbed provider HTTP.

Proves the validate-then-encrypt-then-persist contract: an invalid key is never
stored, and stored keys are encrypted and never returned to callers.
"""
from __future__ import annotations

import httpx
import pytest
from cryptography.fernet import Fernet

from src.core.crypto import decrypt_secret
from src.core.exceptions import UnauthorizedError
from src.repositories.ai_config_repository import AIConfigRepository
from src.schemas.ai_config_schema import AIConfigSaveRequest
from src.services.ai_config_service import AIConfigService


@pytest.fixture
def encryption_key() -> str:
    return Fernet.generate_key().decode()


@pytest.fixture
def ai_config_repository(mongo_db) -> AIConfigRepository:
    return AIConfigRepository(mongo_db)


def _service(repo: AIConfigRepository, key: str, status_code: int) -> AIConfigService:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json={"data": []})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return AIConfigService(repo, client, key)


async def test_status_is_unconfigured_by_default(ai_config_repository, encryption_key):
    service = _service(ai_config_repository, encryption_key, 200)
    status = await service.get_status("user1")
    assert status.configured is False
    assert status.provider is None


async def test_save_persists_encrypted_and_returns_no_key(
    ai_config_repository, encryption_key
):
    service = _service(ai_config_repository, encryption_key, 200)
    payload = AIConfigSaveRequest(
        provider="anthropic", model="claude-x", api_key="sk-secret-1234"
    )

    response = await service.save("user1", payload)

    assert response.configured is True
    assert response.provider == "anthropic"
    assert response.model == "claude-x"
    assert response.key_hint == "••••1234"
    # The plaintext key is never echoed back anywhere in the response.
    assert "sk-secret" not in response.model_dump_json()

    stored = await ai_config_repository.find_by_user_id("user1")
    assert stored is not None
    assert stored.api_key_encrypted != "sk-secret-1234"
    assert decrypt_secret(stored.api_key_encrypted, encryption_key) == "sk-secret-1234"


async def test_invalid_key_raises_and_persists_nothing(
    ai_config_repository, encryption_key
):
    service = _service(ai_config_repository, encryption_key, 401)
    payload = AIConfigSaveRequest(provider="openai", model="gpt", api_key="bad-key")

    with pytest.raises(UnauthorizedError):
        await service.save("user1", payload)

    assert await ai_config_repository.find_by_user_id("user1") is None


async def test_save_upserts_existing_config(ai_config_repository, encryption_key):
    service = _service(ai_config_repository, encryption_key, 200)
    await service.save(
        "user1", AIConfigSaveRequest(provider="anthropic", model="m1", api_key="k1aaaa")
    )
    await service.save(
        "user1", AIConfigSaveRequest(provider="openai", model="m2", api_key="k2bbbb")
    )

    stored = await ai_config_repository.find_by_user_id("user1")
    assert stored.provider == "openai"
    assert stored.model == "m2"
