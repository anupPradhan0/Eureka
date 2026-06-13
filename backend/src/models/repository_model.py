"""Imported-repository entity — one "current repo" per user.

Holds the parsed location, an optional **encrypted** GitHub token (so a refresh
can re-fetch private repos), and the last fetched summary snapshot so the UI can
resume instantly without re-hitting GitHub.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

COLLECTION_NAME = "repositories"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RepositoryModel(BaseModel):
    id: str | None = Field(default=None, description="Mongo _id as string")
    user_id: str
    url: str
    owner: str
    name: str
    default_branch: str
    github_token_encrypted: str | None = None
    summary: dict[str, Any]
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)

    @classmethod
    def from_document(cls, document: dict[str, Any]) -> "RepositoryModel":
        return cls(
            id=str(document["_id"]),
            user_id=document["user_id"],
            url=document["url"],
            owner=document["owner"],
            name=document["name"],
            default_branch=document["default_branch"],
            github_token_encrypted=document.get("github_token_encrypted"),
            summary=document.get("summary", {}),
            created_at=document.get("created_at", _utcnow()),
            updated_at=document.get("updated_at", _utcnow()),
        )
