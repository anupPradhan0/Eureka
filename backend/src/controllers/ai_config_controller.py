"""AI-config HTTP controller.

Thin layer: takes the authenticated user id + validated DTO, delegates to the
service, returns the response DTO. No business logic, no data access.
"""
from __future__ import annotations

from ..schemas.ai_config_schema import AIConfigResponse, AIConfigSaveRequest
from ..services.ai_config_service import AIConfigService


class AIConfigController:
    def __init__(self, ai_config_service: AIConfigService) -> None:
        self._service = ai_config_service

    async def get_status(self, user_id: str) -> AIConfigResponse:
        return await self._service.get_status(user_id)

    async def save(self, user_id: str, payload: AIConfigSaveRequest) -> AIConfigResponse:
        return await self._service.save(user_id, payload)
