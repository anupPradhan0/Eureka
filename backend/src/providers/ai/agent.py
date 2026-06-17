"""Provider-agnostic agent primitives.

These normalize the two things every provider's agent loop needs — the tools the
model may call, and a way to execute a call — so the service describes tools and
runs business logic (reading repo files) without knowing any provider's wire
format. Each provider translates :class:`AgentTool` into its own tool schema.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable


@dataclass(frozen=True)
class AgentTool:
    """A tool the model may call, in JSON-Schema terms (provider-neutral)."""

    name: str
    description: str
    input_schema: dict[str, Any]


#: Executes a tool call (name, input) and returns the result text for the model.
ToolExecutor = Callable[[str, dict[str, Any]], Awaitable[str]]
