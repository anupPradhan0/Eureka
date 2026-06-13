"""Unit tests for RepositoryService over an in-memory Mongo + stubbed GitHub HTTP.

Asserts summary mapping, conditional stats, doc detection, persistence, error
mapping, and — critically — that only api.github.com is ever contacted.
"""
from __future__ import annotations

import base64

import httpx
import pytest
from cryptography.fernet import Fernet

from src.core.exceptions import NotFoundError
from src.providers.github.client import GitHubClient
from src.repositories.repository_repository import RepositoryRepository
from src.schemas.repository_schema import RepoImportRequest
from src.services.repository_service import RepositoryService

_REPO_META = {
    "full_name": "owner/repo",
    "description": "A repo",
    "html_url": "https://github.com/owner/repo",
    "default_branch": "main",
    "stargazers_count": 42,
}
_TREE = {
    "truncated": False,
    "tree": [
        {"path": "README.md", "type": "blob", "size": 10},
        {"path": "src", "type": "tree"},
        {"path": "src/app.py", "type": "blob", "size": 20},
        {"path": "LICENSE", "type": "blob", "size": 5},
        {"path": ".github/CONTRIBUTING.md", "type": "blob", "size": 7},
    ],
}


@pytest.fixture
def encryption_key() -> str:
    return Fernet.generate_key().decode()


def _full_handler(hosts: list[str]):
    def handler(request: httpx.Request) -> httpx.Response:
        hosts.append(request.url.host)
        path = request.url.path
        if path == "/repos/owner/repo":
            return httpx.Response(200, json=_REPO_META)
        if path == "/repos/owner/repo/contributors":
            link = (
                '<https://api.github.com/repositories/1/contributors'
                '?per_page=1&page=7>; rel="last"'
            )
            return httpx.Response(200, headers={"Link": link}, json=[{}])
        if path == "/repos/owner/repo/git/trees/main":
            return httpx.Response(200, json=_TREE)
        if path.startswith("/repos/owner/repo/contents/"):
            return httpx.Response(
                200, json={"content": base64.b64encode(b"# Hello").decode()}
            )
        return httpx.Response(404, json={})

    return handler


def _service(mongo_db, key: str, handler):
    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    github = GitHubClient(client, timeout=5.0)
    repo = RepositoryRepository(mongo_db)
    return RepositoryService(repo, github, key, tree_max_entries=5000), repo


async def test_import_builds_and_persists_summary(mongo_db, encryption_key):
    hosts: list[str] = []
    service, repo = _service(mongo_db, encryption_key, _full_handler(hosts))

    summary = await service.import_repo(
        "user1", RepoImportRequest(url="https://github.com/owner/repo")
    )

    assert summary.full_name == "owner/repo"
    assert summary.stars == 42
    assert summary.contributors_count == 7  # from the Link rel="last" page
    assert summary.file_count == 4  # blobs only (the 'src' tree excluded)
    assert summary.tree_truncated is False
    assert summary.readme == "# Hello"

    categories = {doc.category for doc in summary.docs}
    assert {"readme", "license", "contributing"} <= categories

    # Only the GitHub API host is ever contacted (SSRF guard).
    assert hosts and all(host == "api.github.com" for host in hosts)

    stored = await repo.find_by_user_id("user1")
    assert stored is not None
    assert stored.owner == "owner"
    assert stored.name == "repo"


async def test_get_current_after_import_returns_snapshot(mongo_db, encryption_key):
    service, _ = _service(mongo_db, encryption_key, _full_handler([]))
    await service.import_repo("user1", RepoImportRequest(url="https://github.com/owner/repo"))

    current = await service.get_current("user1")
    assert current.full_name == "owner/repo"
    assert current.stars == 42


async def test_get_current_without_import_raises(mongo_db, encryption_key):
    service, _ = _service(mongo_db, encryption_key, _full_handler([]))
    with pytest.raises(NotFoundError):
        await service.get_current("nobody")


async def test_truncated_tree_hides_file_count(mongo_db, encryption_key):
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/repos/owner/repo":
            return httpx.Response(200, json=_REPO_META)
        if path == "/repos/owner/repo/contributors":
            return httpx.Response(200, json=[{}])  # no Link header
        if path == "/repos/owner/repo/git/trees/main":
            return httpx.Response(
                200, json={"truncated": True, "tree": [{"path": "a", "type": "blob"}]}
            )
        return httpx.Response(404, json={})

    service, _ = _service(mongo_db, encryption_key, handler)
    summary = await service.import_repo(
        "u", RepoImportRequest(url="https://github.com/owner/repo")
    )

    assert summary.tree_truncated is True
    assert summary.file_count is None
    assert summary.contributors_count == 1  # array length fallback


async def test_missing_repo_maps_to_not_found(mongo_db, encryption_key):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"message": "Not Found"})

    service, _ = _service(mongo_db, encryption_key, handler)
    with pytest.raises(NotFoundError):
        await service.import_repo(
            "u", RepoImportRequest(url="https://github.com/owner/repo")
        )


async def test_delete_clears_current(mongo_db, encryption_key):
    service, repo = _service(mongo_db, encryption_key, _full_handler([]))
    await service.import_repo("user1", RepoImportRequest(url="https://github.com/owner/repo"))

    await service.delete_current("user1")

    assert await repo.find_by_user_id("user1") is None
