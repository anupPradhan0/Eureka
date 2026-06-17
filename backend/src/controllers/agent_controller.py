"""Agent HTTP controller.

Thin layer: takes the authenticated user id + validated DTO, delegates to the
service, returns response DTOs. ``execute_run`` is invoked from a background task
(not a request), so it takes only the run id.
"""
from __future__ import annotations

from ..schemas.agent_schema import AgentRunRequest, AgentRunResponse
from ..services.agent_service import AgentService


class AgentController:
    def __init__(self, agent_service: AgentService) -> None:
        self._service = agent_service

    async def start_run(
        self, user_id: str, payload: AgentRunRequest
    ) -> AgentRunResponse:
        return await self._service.start_run(user_id, payload)

    async def execute_run(self, run_id: str) -> None:
        await self._service.execute_run(run_id)

    async def get_run(self, user_id: str, run_id: str) -> AgentRunResponse:
        return await self._service.get_run(user_id, run_id)

    async def list_runs(self, user_id: str) -> list[AgentRunResponse]:
        return await self._service.list_runs(user_id)
