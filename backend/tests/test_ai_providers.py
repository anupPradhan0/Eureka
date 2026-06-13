"""Unit tests for AI provider key validation.

Uses httpx.MockTransport so no network is touched, and asserts each provider
issues the correct authenticated request and maps statuses to domain errors.
"""
from __future__ import annotations

import httpx
import pytest

from src.core.exceptions import UnauthorizedError, UpstreamError
from src.providers.ai.registry import SUPPORTED_PROVIDERS, get_provider


def _client(handler) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


async def _capture(provider_name: str, status_code: int = 200):
    """Run a provider's validate against a stub returning ``status_code``."""
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["request"] = request
        return httpx.Response(status_code, json={"data": []})

    async with _client(handler) as client:
        await get_provider(provider_name).validate("a-model", "secret-key", client)
    return captured["request"]


async def test_anthropic_request_shape():
    request = await _capture("anthropic")
    assert request.method == "GET"
    assert request.url.host == "api.anthropic.com"
    assert request.url.path == "/v1/models"
    assert request.headers["x-api-key"] == "secret-key"
    assert request.headers["anthropic-version"] == "2023-06-01"


async def test_openai_request_shape():
    request = await _capture("openai")
    assert request.url.host == "api.openai.com"
    assert request.headers["Authorization"] == "Bearer secret-key"


async def test_openrouter_request_shape():
    request = await _capture("openrouter")
    assert request.url.host == "openrouter.ai"
    assert request.url.path == "/api/v1/key"
    assert request.headers["Authorization"] == "Bearer secret-key"


async def test_gemini_request_shape():
    request = await _capture("gemini")
    assert request.url.host == "generativelanguage.googleapis.com"
    assert request.url.params["key"] == "secret-key"


@pytest.mark.parametrize("name", SUPPORTED_PROVIDERS)
async def test_all_providers_accept_success(name):
    # Should not raise.
    await _capture(name, status_code=200)


@pytest.mark.parametrize("name", SUPPORTED_PROVIDERS)
async def test_unauthorized_status_maps_to_unauthorized(name):
    with pytest.raises(UnauthorizedError):
        await _capture(name, status_code=401)


@pytest.mark.parametrize("name", SUPPORTED_PROVIDERS)
async def test_server_error_maps_to_upstream(name):
    with pytest.raises(UpstreamError):
        await _capture(name, status_code=500)


async def test_network_error_maps_to_upstream():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("boom", request=request)

    async with _client(handler) as client:
        with pytest.raises(UpstreamError):
            await get_provider("openai").validate("m", "k", client)


def test_unknown_provider_rejected():
    from src.core.exceptions import ValidationError

    with pytest.raises(ValidationError):
        get_provider("not-a-provider")
