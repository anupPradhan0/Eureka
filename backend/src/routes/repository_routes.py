"""Repository routes.

Maps HTTP endpoints to the controller. The current user and controller are
injected, so handlers hold no construction or business logic.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status

from ..controllers.repository_controller import RepositoryController
from ..dependencies.container import get_current_user_id, get_repository_controller
from ..schemas.repository_schema import RepoImportRequest, RepoSummaryResponse

router = APIRouter(prefix="/api/repository", tags=["repository"])


@router.get("", response_model=RepoSummaryResponse)
async def get_current(
    user_id: str = Depends(get_current_user_id),
    controller: RepositoryController = Depends(get_repository_controller),
) -> RepoSummaryResponse:
    return await controller.get_current(user_id)


@router.post("/import", response_model=RepoSummaryResponse)
async def import_repo(
    payload: RepoImportRequest,
    user_id: str = Depends(get_current_user_id),
    controller: RepositoryController = Depends(get_repository_controller),
) -> RepoSummaryResponse:
    return await controller.import_repo(user_id, payload)


@router.post("/refresh", response_model=RepoSummaryResponse)
async def refresh(
    user_id: str = Depends(get_current_user_id),
    controller: RepositoryController = Depends(get_repository_controller),
) -> RepoSummaryResponse:
    return await controller.refresh(user_id)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current(
    user_id: str = Depends(get_current_user_id),
    controller: RepositoryController = Depends(get_repository_controller),
) -> Response:
    await controller.delete_current(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
