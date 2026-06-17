"""Agent routes.

Starting a run returns immediately (202) with a pending run; the work is handed
to a FastAPI background task and the client polls GET /runs/{id} until the status
is terminal (succeeded/failed).
"""
from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, status

from ..controllers.agent_controller import AgentController
from ..dependencies.container import get_agent_controller, get_current_user_id
from ..schemas.agent_schema import AgentRunRequest, AgentRunResponse

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.post(
    "/runs",
    response_model=AgentRunResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def start_run(
    payload: AgentRunRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user_id),
    controller: AgentController = Depends(get_agent_controller),
) -> AgentRunResponse:
    run = await controller.start_run(user_id, payload)
    background_tasks.add_task(controller.execute_run, run.id)
    return run


@router.get("/runs", response_model=list[AgentRunResponse])
async def list_runs(
    user_id: str = Depends(get_current_user_id),
    controller: AgentController = Depends(get_agent_controller),
) -> list[AgentRunResponse]:
    return await controller.list_runs(user_id)


@router.get("/runs/{run_id}", response_model=AgentRunResponse)
async def get_run(
    run_id: str,
    user_id: str = Depends(get_current_user_id),
    controller: AgentController = Depends(get_agent_controller),
) -> AgentRunResponse:
    return await controller.get_run(user_id, run_id)
