"""OpenRouter key validation via the key-info endpoint."""
from __future__ import annotations

import httpx

from .base import IAIProvider, validate_via_get


class OpenRouterProvider(IAIProvider):
    name = "openrouter"
    _URL = "https://openrouter.ai/api/v1/key"

    async def validate(self, model: str, api_key: str, client: httpx.AsyncClient) -> None:
        await validate_via_get(
            client,
            self._URL,
            provider="OpenRouter",
            headers={"Authorization": f"Bearer {api_key}"},
        )
