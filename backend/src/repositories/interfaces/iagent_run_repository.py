"""Abstraction for agent-run data access.

The service depends on this interface, not the concrete Mongo implementation, so
it can be unit-tested with an in-memory repository (Dependency Inversion).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ...models.agent_run_model import AgentRunModel


class IAgentRunRepository(ABC):
    @abstractmethod
    async def create(self, run: AgentRunModel) -> AgentRunModel:
        """Persist a new run and return it with its generated id."""

    @abstractmethod
    async def find_by_id(self, run_id: str) -> AgentRunModel | None:
        """Return the run with this id, or None."""

    @abstractmethod
    async def update_fields(
        self, run_id: str, changes: dict[str, Any]
    ) -> AgentRunModel | None:
        """Apply partial changes (status/diff/error) and return the updated run."""

    @abstractmethod
    async def list_by_user(self, user_id: str, limit: int) -> list[AgentRunModel]:
        """Return the user's runs, newest first, capped at ``limit``."""
