"""Concrete Mongo implementation of IRepositoryRepository.

One repository per user, enforced by a unique index on ``user_id`` and an upsert.
"""
from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase

from ..models.repository_model import COLLECTION_NAME, RepositoryModel
from .base_repository import BaseRepository
from .interfaces.irepository_repository import IRepositoryRepository


class RepositoryRepository(BaseRepository, IRepositoryRepository):
    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        super().__init__(database, COLLECTION_NAME)

    async def find_by_user_id(self, user_id: str) -> RepositoryModel | None:
        document = await self.find_one({"user_id": user_id})
        return RepositoryModel.from_document(document) if document else None

    async def upsert(self, repository: RepositoryModel) -> RepositoryModel:
        document = await self._collection.find_one_and_update(
            {"user_id": repository.user_id},
            {
                "$set": {
                    "url": repository.url,
                    "owner": repository.owner,
                    "name": repository.name,
                    "default_branch": repository.default_branch,
                    "github_token_encrypted": repository.github_token_encrypted,
                    "summary": repository.summary,
                    "updated_at": repository.updated_at,
                },
                "$setOnInsert": {
                    "user_id": repository.user_id,
                    "created_at": repository.created_at,
                },
            },
            upsert=True,
            return_document=True,
        )
        if document is None:  # an upsert should always return a document
            raise RuntimeError("Repository upsert returned no document.")
        return RepositoryModel.from_document(document)

    async def delete_by_user_id(self, user_id: str) -> bool:
        result = await self._collection.delete_one({"user_id": user_id})
        return result.deleted_count > 0

    async def ensure_indexes(self) -> None:
        """Create the unique index on user_id. Safe to call repeatedly."""
        await self._collection.create_index("user_id", unique=True)
