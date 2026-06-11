"""Concrete Mongo implementation of IUserRepository.

Translates between UserModel entities and Mongo documents, and provides the
user-specific queries. Reuses generic CRUD from BaseRepository.
"""
from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase

from ..models.user_model import COLLECTION_NAME, UserModel
from .base_repository import BaseRepository
from .interfaces.iuser_repository import IUserRepository


class UserRepository(BaseRepository, IUserRepository):
    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        super().__init__(database, COLLECTION_NAME)

    async def create(self, user: UserModel) -> UserModel:
        document = await self.insert_one(user.to_document())
        return UserModel.from_document(document)

    async def find_by_id(self, user_id: str) -> UserModel | None:
        document = await super().find_by_id(user_id)
        return UserModel.from_document(document) if document else None

    async def find_by_email(self, email: str) -> UserModel | None:
        document = await self.find_one({"email": email})
        return UserModel.from_document(document) if document else None

    async def ensure_indexes(self) -> None:
        """Create the unique index on email. Safe to call repeatedly."""
        await self._collection.create_index("email", unique=True)
