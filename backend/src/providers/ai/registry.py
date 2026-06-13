"""Registry of supported AI providers.

A single source of truth mapping a provider name to its (stateless) instance.
Providers hold no per-request state, so one shared instance each is fine.
"""
from __future__ import annotations

from ...core.exceptions import ValidationError
from .anthropic_provider import AnthropicProvider
from .base import IAIProvider
from .gemini_provider import GeminiProvider
from .openai_provider import OpenAIProvider
from .openrouter_provider import OpenRouterProvider

_PROVIDERS: dict[str, IAIProvider] = {
    provider.name: provider
    for provider in (
        AnthropicProvider(),
        OpenAIProvider(),
        OpenRouterProvider(),
        GeminiProvider(),
    )
}

#: Names accepted by the API (also mirrored by the schema's Literal type).
SUPPORTED_PROVIDERS: tuple[str, ...] = tuple(_PROVIDERS)


def get_provider(name: str) -> IAIProvider:
    """Return the provider for ``name`` or raise a domain ValidationError."""
    provider = _PROVIDERS.get(name)
    if provider is None:
        raise ValidationError(f"Unsupported provider '{name}'.")
    return provider
