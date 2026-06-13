"""Google Gemini key validation via the models endpoint."""
from __future__ import annotations

import httpx

from .base import IAIProvider, validate_via_get


class GeminiProvider(IAIProvider):
    name = "gemini"
    _URL = "https://generativelanguage.googleapis.com/v1beta/models"

    async def validate(self, model: str, api_key: str, client: httpx.AsyncClient) -> None:
        # Gemini authenticates with a query-string key; never log the params.
        await validate_via_get(
            client,
            self._URL,
            provider="Gemini",
            params={"key": api_key},
        )
