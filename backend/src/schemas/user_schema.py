"""Request/response DTOs for the user/auth API.

These are the public contract of the HTTP layer. They are deliberately separate
from the UserModel entity so internal fields (e.g. password_hash) are never
exposed, and validation rules live at the boundary.
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from ..models.user_model import UserModel


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    """Safe, public view of a user (no password material)."""

    id: str
    email: EmailStr
    created_at: datetime

    @classmethod
    def from_model(cls, user: UserModel) -> "UserResponse":
        return cls(
            id=user.id or "",
            email=user.email,
            created_at=user.created_at,
        )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
