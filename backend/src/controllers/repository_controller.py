"""Repository HTTP controller.

Thin layer: takes the authenticated user id + validated DTO, delegates to the
service, returns response DTOs. No business logic, no data access.
"""
from __future__ import annotations

from ..schemas.repository_schema import RepoImportRequest, RepoSummaryResponse
from ..services.repository_service import RepositoryService


class RepositoryController:
    def __init__(self, repository_service: RepositoryService) -> None:
        self._service = repository_service

    async def import_repo(
        self, user_id: str, payload: RepoImportRequest
    ) -> RepoSummaryResponse:
        return await self._service.import_repo(user_id, payload)

    async def get_current(self, user_id: str) -> RepoSummaryResponse:
        return await self._service.get_current(user_id)

    async def refresh(self, user_id: str) -> RepoSummaryResponse:
        return await self._service.refresh(user_id)

    async def delete_current(self, user_id: str) -> None:
        await self._service.delete_current(user_id)
