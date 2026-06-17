"""Agent-run entity — one record per "build a feature" request.

Unlike the AI config and imported repo (one per user), a user has *many* runs, so
this collection is indexed on ``user_id`` for listing but not uniquely. Each run
captures the request, its lifecycle status, and the proposed unified diff (or the
error that stopped it) so the UI can poll it to completion.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from ..core.utils import utcnow

COLLECTION_NAME = "agent_runs"

# Lifecycle: created -> running -> (succeeded | failed). Mirrored by the schema.
AGENT_RUN_STATUSES = ("pending", "running", "succeeded", "failed")


class AgentRunModel(BaseModel):
    id: str | None = Field(default=None, description="Mongo _id as string")
    user_id: str
    repo_owner: str
    repo_name: str
    prompt: str
    target_page: str | None = None
    status: str = "pending"
    diff: str | None = None
    error: str | None = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    @classmethod
    def from_document(cls, document: dict[str, Any]) -> "AgentRunModel":
        return cls(
            id=str(document["_id"]),
            user_id=document["user_id"],
            repo_owner=document["repo_owner"],
            repo_name=document["repo_name"],
            prompt=document["prompt"],
            target_page=document.get("target_page"),
            status=document.get("status", "pending"),
            diff=document.get("diff"),
            error=document.get("error"),
            created_at=document.get("created_at", utcnow()),
            updated_at=document.get("updated_at", utcnow()),
        )
