"""Shared test fixtures.

Uses an in-memory Mongo (mongomock-motor) so tests need no running database.
"""
from __future__ import annotations

import pytest
from mongomock_motor import AsyncMongoMockClient

from src.repositories.user_repository import UserRepository
from src.services.user_service import UserService


@pytest.fixture
def mongo_db():
    client = AsyncMongoMockClient()
    return client["eureka_test"]


@pytest.fixture
def user_repository(mongo_db) -> UserRepository:
    return UserRepository(mongo_db)


@pytest.fixture
def user_service(user_repository) -> UserService:
    return UserService(user_repository)
