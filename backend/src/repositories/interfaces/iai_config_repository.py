"""Abstraction for AI-config data access.

The service depends on this interface, not the concrete Mongo implementation, so
it can be unit-tested with an in-memory repository (Dependency Inversion).
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from ...models.ai_config_model import AIConfigModel


class IAIConfigRepository(ABC):
    @abstractmethod
    async def find_by_user_id(self, user_id: str) -> AIConfigModel | None:
        """Return the user's AI config, or None."""

    @abstractmethod
    async def upsert(self, config: AIConfigModel) -> AIConfigModel:
        """Create or replace the user's AI config and return the stored entity."""
