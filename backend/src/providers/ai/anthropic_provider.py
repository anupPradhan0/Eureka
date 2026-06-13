"""Anthropic (Claude) key validation via the models endpoint."""
from __future__ import annotations

import httpx

from .base import IAIProvider, validate_via_get


class AnthropicProvider(IAIProvider):
    name = "anthropic"
    _URL = "https://api.anthropic.com/v1/models"
    _VERSION = "2023-06-01"

    async def validate(self, model: str, api_key: str, client: httpx.AsyncClient) -> None:
        await validate_via_get(
            client,
            self._URL,
            provider="Anthropic",
            headers={"x-api-key": api_key, "anthropic-version": self._VERSION},
        )
