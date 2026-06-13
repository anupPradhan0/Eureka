"""AI configuration entity — one per user.

Stores the chosen provider/model and the user's API key **encrypted** (never the
plaintext), plus a non-reversible display hint.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

COLLECTION_NAME = "ai_configs"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AIConfigModel(BaseModel):
    """Domain entity for a user's AI configuration."""

    id: str | None = Field(default=None, description="Mongo _id as string")
    user_id: str
    provider: str
    model: str
    api_key_encrypted: str
    key_hint: str
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)

    @classmethod
    def from_document(cls, document: dict[str, Any]) -> "AIConfigModel":
        return cls(
            id=str(document["_id"]),
            user_id=document["user_id"],
            provider=document["provider"],
            model=document["model"],
            api_key_encrypted=document["api_key_encrypted"],
            key_hint=document["key_hint"],
            created_at=document.get("created_at", _utcnow()),
            updated_at=document.get("updated_at", _utcnow()),
        )
