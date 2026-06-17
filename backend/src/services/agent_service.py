"""Agent business logic.

Runs a plain-language feature request against the user's imported repo using the
provider they configured, and produces a **proposed unified diff** (it never
applies changes). A run is created synchronously (so the caller gets an id to
poll) and executed in the background; its lifecycle and result live in Mongo.

Depends only on abstractions: the run/repo/config repository interfaces, the
injected GitHubClient + httpx client, and the provider registry.
"""
from __future__ import annotations

from typing import Any

import httpx

from ..core.crypto import decrypt_secret
from ..core.exceptions import AppError, NotFoundError
from ..models.agent_run_model import AgentRunModel
from ..models.repository_model import RepositoryModel
from ..providers.ai.agent import AgentTool
from ..providers.ai.registry import get_provider
from ..providers.github.client import GitHubClient
from ..repositories.interfaces.iagent_run_repository import IAgentRunRepository
from ..repositories.interfaces.iai_config_repository import IAIConfigRepository
from ..repositories.interfaces.irepository_repository import IRepositoryRepository
from ..schemas.agent_schema import AgentRunRequest, AgentRunResponse

# How many files to list in the prompt; a huge tree would blow the context window.
_TREE_PROMPT_MAX_ENTRIES = 400

_READ_FILE_TOOL = AgentTool(
    name="read_file",
    description=(
        "Read a UTF-8 text file from the repository by its path (as shown in the "
        "file tree). Use this to inspect the code you need before proposing changes."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Repo-relative file path."}
        },
        "required": ["path"],
    },
)

_SYSTEM_PROMPT = """You are Eureka's coding agent. You help a self-hoster add a \
feature to an open-source project they run.

Repository: {full_name} (default branch: {branch})
{target_line}
Available files (may be truncated):
{tree}

Use the read_file tool to inspect any files you need. When you have enough \
context, respond with a SINGLE unified diff (git format, `--- a/path` / `+++ \
b/path` headers) that implements the request, followed by a short explanation. \
Do not apply anything — only propose the diff. If the request is impossible or \
unclear, say so plainly instead of inventing a diff."""


class AgentService:
    def __init__(
        self,
        agent_repository: IAgentRunRepository,
        repository_repository: IRepositoryRepository,
        ai_config_repository: IAIConfigRepository,
        github_client: GitHubClient,
        http_client: httpx.AsyncClient,
        encryption_key: str,
        max_iterations: int,
        read_file_max_chars: int,
    ) -> None:
        self._runs = agent_repository
        self._repos = repository_repository
        self._configs = ai_config_repository
        self._github = github_client
        self._http = http_client
        self._encryption_key = encryption_key
        self._max_iterations = max_iterations
        self._read_file_max_chars = read_file_max_chars

    async def start_run(
        self, user_id: str, payload: AgentRunRequest
    ) -> AgentRunResponse:
        """Validate prerequisites and create a pending run. Execution is deferred."""
        repo = await self._repos.find_by_user_id(user_id)
        if repo is None:
            raise NotFoundError("Import a repository before running the agent.")
        if await self._configs.find_by_user_id(user_id) is None:
            raise NotFoundError("Configure an AI provider before running the agent.")

        run = await self._runs.create(
            AgentRunModel(
                user_id=user_id,
                repo_owner=repo.owner,
                repo_name=repo.name,
                prompt=payload.prompt,
                target_page=payload.target_page,
                status="pending",
            )
        )
        return AgentRunResponse.from_model(run)

    async def execute_run(self, run_id: str) -> None:
        """Background worker: drive the agent and persist the result or error."""
        run = await self._runs.find_by_id(run_id)
        if run is None:
            return  # nothing to do — the run was deleted or never existed
        await self._runs.update_fields(run_id, {"status": "running"})

        try:
            diff = await self._build_diff(run)
            await self._runs.update_fields(
                run_id, {"status": "succeeded", "diff": diff, "error": None}
            )
        except AppError as exc:
            await self._runs.update_fields(
                run_id, {"status": "failed", "error": exc.message}
            )
        except Exception:  # noqa: BLE001 - never leak an internal error to a stuck run
            await self._runs.update_fields(
                run_id, {"status": "failed", "error": "The agent run failed unexpectedly."}
            )

    async def get_run(self, user_id: str, run_id: str) -> AgentRunResponse:
        run = await self._runs.find_by_id(run_id)
        if run is None or run.user_id != user_id:
            raise NotFoundError("Run not found.")
        return AgentRunResponse.from_model(run)

    async def list_runs(self, user_id: str, limit: int = 50) -> list[AgentRunResponse]:
        runs = await self._runs.list_by_user(user_id, limit)
        return [AgentRunResponse.from_model(run) for run in runs]

    async def _build_diff(self, run: AgentRunModel) -> str:
        """Load fresh config/repo for the run's user and drive the provider loop."""
        config = await self._configs.find_by_user_id(run.user_id)
        repo = await self._repos.find_by_user_id(run.user_id)
        if config is None or repo is None:
            raise NotFoundError("Repository or AI configuration is no longer available.")

        api_key = decrypt_secret(config.api_key_encrypted, self._encryption_key)
        github_token = (
            decrypt_secret(repo.github_token_encrypted, self._encryption_key)
            if repo.github_token_encrypted
            else None
        )
        provider = get_provider(config.provider)

        return await provider.run_agent(
            system=self._system_prompt(repo, run.target_page),
            prompt=run.prompt,
            tools=[_READ_FILE_TOOL],
            execute_tool=self._tool_executor(repo, github_token),
            model=config.model,
            api_key=api_key,
            client=self._http,
            max_iterations=self._max_iterations,
        )

    def _tool_executor(self, repo: RepositoryModel, token: str | None):
        """Return an async (name, input) -> str executor bound to this repo."""

        async def execute(name: str, tool_input: dict[str, Any]) -> str:
            if name != "read_file":
                return f"Unknown tool: {name}"
            path = str(tool_input.get("path", "")).strip()
            if not path:
                return "Error: a 'path' is required."
            text = await self._github.get_file_text(
                repo.owner, repo.name, path, token
            )
            if text is None:
                return f"File not found or not readable: {path}"
            if len(text) > self._read_file_max_chars:
                return text[: self._read_file_max_chars] + "\n… (truncated)"
            return text

        return execute

    @staticmethod
    def _system_prompt(repo: RepositoryModel, target_page: str | None) -> str:
        tree = repo.summary.get("tree", []) if isinstance(repo.summary, dict) else []
        paths = [
            entry["path"]
            for entry in tree
            if isinstance(entry, dict)
            and entry.get("type") == "blob"
            and "path" in entry
        ]
        listing = "\n".join(paths[:_TREE_PROMPT_MAX_ENTRIES]) or "(file tree unavailable)"
        if len(paths) > _TREE_PROMPT_MAX_ENTRIES:
            listing += "\n… (file list truncated)"
        target_line = (
            f"Target page/area: {target_page}\n" if target_page else ""
        )
        return _SYSTEM_PROMPT.format(
            full_name=f"{repo.owner}/{repo.name}",
            branch=repo.default_branch,
            target_line=target_line,
            tree=listing,
        )
