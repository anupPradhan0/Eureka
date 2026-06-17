"""Unit tests for AgentService over in-memory Mongo + a fake provider.

Covers the contract: a run needs a repo + AI config, executes the provider's
agent loop (with a working read_file tool), and records either the proposed diff
or a clear error — never leaking an internal exception into a stuck run.
"""
from __future__ import annotations

import httpx
import pytest
from cryptography.fernet import Fernet

from src.core.crypto import encrypt_secret
from src.core.exceptions import NotFoundError, UpstreamError
from src.providers.ai.agent import AgentTool, ToolExecutor
from src.repositories.agent_run_repository import AgentRunRepository
from src.repositories.ai_config_repository import AIConfigRepository
from src.repositories.repository_repository import RepositoryRepository
from src.schemas.agent_schema import AgentRunRequest
from src.services.agent_service import AgentService


@pytest.fixture
def encryption_key() -> str:
    return Fernet.generate_key().decode()


class _FakeProvider:
    """Stands in for a real provider; records what the service handed it."""

    name = "anthropic"

    def __init__(self, *, diff: str | None = None, error: Exception | None = None):
        self._diff = diff
        self._error = error
        self.seen_system: str | None = None
        self.read_result: str | None = None

    async def run_agent(
        self, *, system, prompt, tools, execute_tool: ToolExecutor, model, api_key,
        client, max_iterations,
    ) -> str:
        self.seen_system = system
        # Exercise the tool the service wired up, like a real loop would.
        self.read_result = await execute_tool("read_file", {"path": "app/main.py"})
        if self._error is not None:
            raise self._error
        return self._diff or ""


def _service(mongo_db, key, *, provider, github_handler) -> tuple[AgentService, AgentRunRepository]:
    from src.providers.github.client import GitHubClient

    github = GitHubClient(
        httpx.AsyncClient(transport=httpx.MockTransport(github_handler)), timeout=5.0
    )
    runs = AgentRunRepository(mongo_db)
    service = AgentService(
        runs,
        RepositoryRepository(mongo_db),
        AIConfigRepository(mongo_db),
        github,
        httpx.AsyncClient(transport=httpx.MockTransport(lambda r: httpx.Response(200))),
        key,
        max_iterations=5,
        read_file_max_chars=1000,
    )
    # Patch the registry lookup so the service uses our fake provider.
    import src.services.agent_service as module

    module.get_provider = lambda _name: provider  # type: ignore[assignment]
    return service, runs


async def _seed_repo_and_config(mongo_db, key, user_id="user1") -> None:
    from src.models.ai_config_model import AIConfigModel
    from src.models.repository_model import RepositoryModel

    await RepositoryRepository(mongo_db).upsert(
        RepositoryModel(
            user_id=user_id,
            url="https://github.com/acme/app",
            owner="acme",
            name="app",
            default_branch="main",
            summary={"tree": [{"path": "app/main.py", "type": "blob"}]},
        )
    )
    await AIConfigRepository(mongo_db).upsert(
        AIConfigModel(
            user_id=user_id,
            provider="anthropic",
            model="claude-x",
            api_key_encrypted=encrypt_secret("sk-key", key),
            key_hint="••••-key",
        )
    )


async def test_start_run_requires_repo(mongo_db, encryption_key):
    service, _ = _service(
        mongo_db, encryption_key, provider=_FakeProvider(),
        github_handler=lambda r: httpx.Response(404),
    )
    with pytest.raises(NotFoundError):
        await service.start_run("user1", AgentRunRequest(prompt="add a button"))


async def test_run_succeeds_and_stores_diff(mongo_db, encryption_key):
    provider = _FakeProvider(diff="--- a/app/main.py\n+++ b/app/main.py\n+# new")
    file_body = '{"content": "cHJpbnQoImhpIik=", "encoding": "base64"}'  # print("hi")
    service, runs = _service(
        mongo_db, encryption_key, provider=provider,
        github_handler=lambda r: httpx.Response(200, text=file_body),
    )
    await _seed_repo_and_config(mongo_db, encryption_key)

    started = await service.start_run("user1", AgentRunRequest(prompt="add a button"))
    assert started.status == "pending"

    await service.execute_run(started.id)

    final = await service.get_run("user1", started.id)
    assert final.status == "succeeded"
    assert final.diff == "--- a/app/main.py\n+++ b/app/main.py\n+# new"
    assert final.error is None
    # The system prompt carried the repo's file tree; read_file actually worked.
    assert "app/main.py" in (provider.seen_system or "")
    assert provider.read_result == 'print("hi")'


async def test_run_records_provider_error(mongo_db, encryption_key):
    provider = _FakeProvider(error=UpstreamError("Anthropic is down."))
    service, _ = _service(
        mongo_db, encryption_key, provider=provider,
        github_handler=lambda r: httpx.Response(404),
    )
    await _seed_repo_and_config(mongo_db, encryption_key)

    started = await service.start_run("user1", AgentRunRequest(prompt="x"))
    await service.execute_run(started.id)

    final = await service.get_run("user1", started.id)
    assert final.status == "failed"
    assert final.error == "Anthropic is down."


async def test_get_run_is_scoped_to_owner(mongo_db, encryption_key):
    service, _ = _service(
        mongo_db, encryption_key, provider=_FakeProvider(diff="d"),
        github_handler=lambda r: httpx.Response(404),
    )
    await _seed_repo_and_config(mongo_db, encryption_key)
    started = await service.start_run("user1", AgentRunRequest(prompt="x"))

    with pytest.raises(NotFoundError):
        await service.get_run("intruder", started.id)
