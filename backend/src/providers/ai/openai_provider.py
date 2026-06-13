"""OpenAI key validation via the models endpoint."""
from __future__ import annotations

import httpx

from .base import IAIProvider, validate_via_get


class OpenAIProvider(IAIProvider):
    name = "openai"
    _URL = "https://api.openai.com/v1/models"

    async def validate(self, model: str, api_key: str, client: httpx.AsyncClient) -> None:
        await validate_via_get(
            client,
            self._URL,
            provider="OpenAI",
            headers={"Authorization": f"Bearer {api_key}"},
        )
