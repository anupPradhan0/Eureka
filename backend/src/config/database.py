"""MongoDB connection management using Motor (async driver).

Owns the single client/database handle for the process. Other layers receive
the database from here via dependency injection — they never construct a client
themselves.
"""
from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from .settings import Settings, get_settings


class Database:
    """Holds and manages the lifecycle of the Mongo client/database."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._client: AsyncIOMotorClient | None = None
        self._db: AsyncIOMotorDatabase | None = None

    def connect(self) -> None:
        """Open the client connection. Idempotent."""
        if self._client is None:
            self._client = AsyncIOMotorClient(self._settings.mongodb_uri)
            self._db = self._client[self._settings.mongodb_db_name]

    def disconnect(self) -> None:
        """Close the client connection. Idempotent."""
        if self._client is not None:
            self._client.close()
            self._client = None
            self._db = None

    @property
    def db(self) -> AsyncIOMotorDatabase:
        if self._db is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._db


# Process-wide singleton, wired into the app lifespan in app.py.
_database = Database()


def get_database() -> Database:
    """Return the process-wide Database instance (for dependency injection)."""
    return _database
