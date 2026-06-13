"""AI-config routes.

Maps HTTP endpoints to the controller. The current user and controller are
injected, so handlers hold no construction or business logic.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends

from ..controllers.ai_config_controller import AIConfigController
from ..dependencies.container import get_ai_config_controller, get_current_user_id
from ..schemas.ai_config_schema import AIConfigResponse, AIConfigSaveRequest

router = APIRouter(prefix="/api/ai-config", tags=["ai-config"])


@router.get("", response_model=AIConfigResponse)
async def get_status(
    user_id: str = Depends(get_current_user_id),
    controller: AIConfigController = Depends(get_ai_config_controller),
) -> AIConfigResponse:
    return await controller.get_status(user_id)


@router.put("", response_model=AIConfigResponse)
async def save(
    payload: AIConfigSaveRequest,
    user_id: str = Depends(get_current_user_id),
    controller: AIConfigController = Depends(get_ai_config_controller),
) -> AIConfigResponse:
    return await controller.save(user_id, payload)
