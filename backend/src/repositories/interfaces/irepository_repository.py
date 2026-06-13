"""Abstraction for imported-repository data access."""
from __future__ import annotations

from abc import ABC, abstractmethod

from ...models.repository_model import RepositoryModel


class IRepositoryRepository(ABC):
    @abstractmethod
    async def find_by_user_id(self, user_id: str) -> RepositoryModel | None:
        """Return the user's current repository, or None."""

    @abstractmethod
    async def upsert(self, repository: RepositoryModel) -> RepositoryModel:
        """Create or replace the user's current repository."""

    @abstractmethod
    async def delete_by_user_id(self, user_id: str) -> bool:
        """Remove the user's current repository. True if one was removed."""
