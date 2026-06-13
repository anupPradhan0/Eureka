"""Request/response DTOs for the AI-config API.

The response is deliberately key-free: it exposes only the provider, model, and a
masked hint, so the API key is never returned once saved.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from ..models.ai_config_model import AIConfigModel

# Kept in sync with providers/ai/registry.SUPPORTED_PROVIDERS. Using a Literal
# makes FastAPI reject unknown providers with a 422 at the boundary.
ProviderName = Literal["anthropic", "openai", "openrouter", "gemini"]


class AIConfigSaveRequest(BaseModel):
    provider: ProviderName
    model: str = Field(min_length=1, max_length=200)
    api_key: str = Field(min_length=1, max_length=500)


class AIConfigResponse(BaseModel):
    """Safe, public view of a user's AI config (no key material)."""

    configured: bool
    provider: ProviderName | None = None
    model: str | None = None
    key_hint: str | None = None

    @classmethod
    def not_configured(cls) -> "AIConfigResponse":
        return cls(configured=False)

    @classmethod
    def from_model(cls, config: AIConfigModel) -> "AIConfigResponse":
        return cls(
            configured=True,
            provider=config.provider,  # type: ignore[arg-type]
            model=config.model,
            key_hint=config.key_hint,
        )
