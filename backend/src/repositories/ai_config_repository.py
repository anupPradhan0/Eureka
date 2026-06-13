"""Concrete Mongo implementation of IAIConfigRepository.

One config per user, enforced by a unique index on ``user_id`` and an upsert.
Reuses generic helpers from BaseRepository.
"""
from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase

from ..models.ai_config_model import COLLECTION_NAME, AIConfigModel
from .base_repository import BaseRepository
from .interfaces.iai_config_repository import IAIConfigRepository


class AIConfigRepository(BaseRepository, IAIConfigRepository):
    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        super().__init__(database, COLLECTION_NAME)

    async def find_by_user_id(self, user_id: str) -> AIConfigModel | None:
        document = await self.find_one({"user_id": user_id})
        return AIConfigModel.from_document(document) if document else None

    async def upsert(self, config: AIConfigModel) -> AIConfigModel:
        document = await self._collection.find_one_and_update(
            {"user_id": config.user_id},
            {
                "$set": {
                    "provider": config.provider,
                    "model": config.model,
                    "api_key_encrypted": config.api_key_encrypted,
                    "key_hint": config.key_hint,
                    "updated_at": config.updated_at,
                },
                "$setOnInsert": {
                    "user_id": config.user_id,
                    "created_at": config.created_at,
                },
            },
            upsert=True,
            return_document=True,
        )
        if document is None:  # an upsert should always return a document
            raise RuntimeError("AI config upsert returned no document.")
        return AIConfigModel.from_document(document)

    async def ensure_indexes(self) -> None:
        """Create the unique index on user_id. Safe to call repeatedly."""
        await self._collection.create_index("user_id", unique=True)
