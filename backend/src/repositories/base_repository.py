"""Generic CRUD repository over a single Mongo collection.

Holds the document-level operations shared by every concrete repository so they
are written once (DRY). Concrete repositories add only entity-specific queries
and the document<->model mapping.
"""
from __future__ import annotations

from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorDatabase


class BaseRepository:
    def __init__(self, database: AsyncIOMotorDatabase, collection_name: str) -> None:
        self._collection = database[collection_name]

    @staticmethod
    def _to_object_id(value: str) -> ObjectId | None:
        """Safely convert a string to ObjectId, or None if malformed."""
        try:
            return ObjectId(value)
        except (InvalidId, TypeError):
            return None

    async def insert_one(self, document: dict[str, Any]) -> dict[str, Any]:
        """Insert a document and return it with its generated _id."""
        result = await self._collection.insert_one(document)
        return {**document, "_id": result.inserted_id}

    async def find_one(self, query: dict[str, Any]) -> dict[str, Any] | None:
        return await self._collection.find_one(query)

    async def find_by_id(self, entity_id: str) -> dict[str, Any] | None:
        object_id = self._to_object_id(entity_id)
        if object_id is None:
            return None
        return await self._collection.find_one({"_id": object_id})

    async def update_by_id(
        self, entity_id: str, changes: dict[str, Any]
    ) -> dict[str, Any] | None:
        object_id = self._to_object_id(entity_id)
        if object_id is None:
            return None
        return await self._collection.find_one_and_update(
            {"_id": object_id},
            {"$set": changes},
            return_document=True,
        )

    async def delete_by_id(self, entity_id: str) -> bool:
        object_id = self._to_object_id(entity_id)
        if object_id is None:
            return False
        result = await self._collection.delete_one({"_id": object_id})
        return result.deleted_count > 0
