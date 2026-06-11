"""User/auth routes.

Maps HTTP endpoints to controller methods. Dependencies (controller, current
user) are injected, so these handlers contain no construction or business logic.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, status

from ..controllers.user_controller import UserController
from ..dependencies.container import get_current_user_id, get_user_controller
from ..schemas.user_schema import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserRegisterRequest,
    controller: UserController = Depends(get_user_controller),
) -> TokenResponse:
    return await controller.register(payload)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: UserLoginRequest,
    controller: UserController = Depends(get_user_controller),
) -> TokenResponse:
    return await controller.login(payload)


@router.get("/me", response_model=UserResponse)
async def me(
    user_id: str = Depends(get_current_user_id),
    controller: UserController = Depends(get_user_controller),
) -> UserResponse:
    return await controller.get_profile(user_id)
