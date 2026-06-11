"""User entity — the in-application representation of a user document.

Maps to/from a MongoDB document. Stores only the password *hash*, never the
plaintext password.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, EmailStr, Field

COLLECTION_NAME = "users"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UserModel(BaseModel):
    """Domain entity for a user."""

    id: str | None = Field(default=None, description="Mongo _id as string")
    email: EmailStr
    password_hash: str
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)

    def to_document(self) -> dict[str, Any]:
        """Serialize to a Mongo document (omitting id; Mongo manages _id)."""
        return {
            "email": self.email,
            "password_hash": self.password_hash,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_document(cls, document: dict[str, Any]) -> "UserModel":
        """Build a UserModel from a raw Mongo document."""
        return cls(
            id=str(document["_id"]),
            email=document["email"],
            password_hash=document["password_hash"],
            created_at=document.get("created_at", _utcnow()),
            updated_at=document.get("updated_at", _utcnow()),
        )
