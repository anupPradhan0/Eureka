"""Abstraction for user data access.

Services depend on this interface, not on the concrete Mongo implementation
(Dependency Inversion + Interface Segregation). This makes the service testable
with a fake repository and lets the storage backend change without touching
business logic.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from ...models.user_model import UserModel


class IUserRepository(ABC):
    @abstractmethod
    async def create(self, user: UserModel) -> UserModel:
        """Persist a new user and return it with its generated id."""

    @abstractmethod
    async def find_by_id(self, user_id: str) -> UserModel | None:
        """Return the user with this id, or None."""

    @abstractmethod
    async def find_by_email(self, email: str) -> UserModel | None:
        """Return the user with this email, or None."""
