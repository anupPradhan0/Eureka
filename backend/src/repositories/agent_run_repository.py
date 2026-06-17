"""Concrete Mongo implementation of IAgentRunRepository.

Many runs per user, so ``user_id`` is indexed (for listing) but not unique.
``updated_at`` is stamped on every field update so the lifecycle is auditable.
"""
from __future__ import annotations

from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from ..core.utils import utcnow
from ..models.agent_run_model import COLLECTION_NAME, AgentRunModel
from .base_repository import BaseRepository
from .interfaces.iagent_run_repository import IAgentRunRepository


class AgentRunRepository(BaseRepository, IAgentRunRepository):
    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        super().__init__(database, COLLECTION_NAME)

    async def create(self, run: AgentRunModel) -> AgentRunModel:
        document = await self.insert_one(
            {
                "user_id": run.user_id,
                "repo_owner": run.repo_owner,
                "repo_name": run.repo_name,
                "prompt": run.prompt,
                "target_page": run.target_page,
                "status": run.status,
                "diff": run.diff,
                "error": run.error,
                "created_at": run.created_at,
                "updated_at": run.updated_at,
            }
        )
        return AgentRunModel.from_document(document)

    async def find_by_id(self, run_id: str) -> AgentRunModel | None:
        document = await super().find_by_id(run_id)
        return AgentRunModel.from_document(document) if document else None

    async def update_fields(
        self, run_id: str, changes: dict[str, Any]
    ) -> AgentRunModel | None:
        document = await self.update_by_id(run_id, {**changes, "updated_at": utcnow()})
        return AgentRunModel.from_document(document) if document else None

    async def list_by_user(self, user_id: str, limit: int) -> list[AgentRunModel]:
        cursor = (
            self._collection.find({"user_id": user_id})
            .sort("created_at", -1)
            .limit(limit)
        )
        return [AgentRunModel.from_document(doc) async for doc in cursor]

    async def ensure_indexes(self) -> None:
        """Index user_id for fast per-user listing. Safe to call repeatedly."""
        await self._collection.create_index("user_id")
