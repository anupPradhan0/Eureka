"""Anthropic (Claude) provider — key validation and the agent tool-use loop."""
from __future__ import annotations

from typing import Any

import httpx

from ...core.exceptions import UpstreamError
from .agent import AgentTool, ToolExecutor
from .base import IAIProvider, _raise_for_status, validate_via_get

# Per-turn output cap. Generous enough for a sizable unified diff.
_MAX_TOKENS = 4096


class AnthropicProvider(IAIProvider):
    name = "anthropic"
    _MODELS_URL = "https://api.anthropic.com/v1/models"
    _MESSAGES_URL = "https://api.anthropic.com/v1/messages"
    _VERSION = "2023-06-01"

    async def validate(self, model: str, api_key: str, client: httpx.AsyncClient) -> None:
        await validate_via_get(
            client,
            self._MODELS_URL,
            provider="Anthropic",
            headers={"x-api-key": api_key, "anthropic-version": self._VERSION},
        )

    async def run_agent(
        self,
        *,
        system: str,
        prompt: str,
        tools: list[AgentTool],
        execute_tool: ToolExecutor,
        model: str,
        api_key: str,
        client: httpx.AsyncClient,
        max_iterations: int,
    ) -> str:
        headers = {
            "x-api-key": api_key,
            "anthropic-version": self._VERSION,
            "content-type": "application/json",
        }
        tool_specs = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
            }
            for tool in tools
        ]
        messages: list[dict[str, Any]] = [{"role": "user", "content": prompt}]

        for _ in range(max_iterations):
            content = await self._send(
                client,
                headers,
                {
                    "model": model,
                    "max_tokens": _MAX_TOKENS,
                    "system": system,
                    "messages": messages,
                    "tools": tool_specs,
                },
            )
            tool_uses = [block for block in content if block.get("type") == "tool_use"]
            if not tool_uses:
                # No more tool calls -> the model has produced its final answer.
                return "".join(
                    block.get("text", "")
                    for block in content
                    if block.get("type") == "text"
                )

            # Echo the assistant turn, then answer every tool call it requested.
            messages.append({"role": "assistant", "content": content})
            results = []
            for call in tool_uses:
                output = await execute_tool(call["name"], call.get("input", {}))
                results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": call["id"],
                        "content": output,
                    }
                )
            messages.append({"role": "user", "content": results})

        raise UpstreamError("Agent stopped: exceeded the maximum number of steps.")

    @staticmethod
    async def _send(
        client: httpx.AsyncClient,
        headers: dict[str, str],
        body: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """POST one turn to the Messages API and return its content blocks."""
        try:
            response = await client.post(
                AnthropicProvider._MESSAGES_URL, headers=headers, json=body
            )
        except httpx.RequestError as exc:
            raise UpstreamError("Could not reach Anthropic.") from exc
        _raise_for_status(response, "Anthropic")
        return response.json().get("content", []) or []
