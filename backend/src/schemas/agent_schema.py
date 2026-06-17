"""Request/response DTOs for the agent API.

A run is started with a plain-language feature request and an optional target
page; the response is the public view the UI polls until the status is terminal.
"""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from ..models.agent_run_model import AgentRunModel

AgentRunStatus = Literal["pending", "running", "succeeded", "failed"]


class AgentRunRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=4000)
    target_page: str | None = Field(default=None, max_length=500)


class AgentRunResponse(BaseModel):
    """Public view of a run — safe to return and poll."""

    id: str
    status: AgentRunStatus
    prompt: str
    target_page: str | None = None
    diff: str | None = None
    error: str | None = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, run: AgentRunModel) -> "AgentRunResponse":
        return cls(
            id=run.id or "",
            status=run.status,  # type: ignore[arg-type]
            prompt=run.prompt,
            target_page=run.target_page,
            diff=run.diff,
            error=run.error,
            created_at=run.created_at,
            updated_at=run.updated_at,
        )
