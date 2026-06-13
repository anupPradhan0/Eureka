"""Repository business logic.

Fetches a GitHub repo's summary (metadata, stats, file tree, docs) and persists
a snapshot so the UI can resume without re-hitting GitHub. Depends on the
repository interface and the injected GitHubClient — no HTTP or DB detail leaks
into this layer.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone

from ..core.crypto import decrypt_secret, encrypt_secret
from ..core.exceptions import NotFoundError
from ..models.repository_model import RepositoryModel
from ..providers.github.client import GitHubClient
from ..providers.github.url_parser import parse_repo_url
from ..repositories.interfaces.irepository_repository import IRepositoryRepository
from ..schemas.repository_schema import (
    DocCategory,
    DocFile,
    RepoImportRequest,
    RepoSummaryResponse,
    TreeEntry,
)

# Community/documentation files, by category. Matched case-insensitively against
# the file's base name. README is matched first so it also drives content fetch.
_DOC_RULES: list[tuple[DocCategory, re.Pattern[str]]] = [
    ("readme", re.compile(r"^readme(\.[\w.+-]+)?$", re.IGNORECASE)),
    ("code_of_conduct", re.compile(r"^code[_-]?of[_-]?conduct(\.[\w.+-]+)?$", re.IGNORECASE)),
    ("contributing", re.compile(r"^contributing(\.[\w.+-]+)?$", re.IGNORECASE)),
    ("license", re.compile(r"^licen[sc]e(\.[\w.+-]+)?$", re.IGNORECASE)),
    ("security", re.compile(r"^security(\.[\w.+-]+)?$", re.IGNORECASE)),
]
# Community files conventionally live at the root, in .github/, or in docs/.
_DOC_DIRS = {"", ".github", "docs"}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RepositoryService:
    def __init__(
        self,
        repository: IRepositoryRepository,
        github_client: GitHubClient,
        encryption_key: str,
        tree_max_entries: int,
    ) -> None:
        self._repo = repository
        self._github = github_client
        self._encryption_key = encryption_key
        self._tree_max_entries = tree_max_entries

    async def import_repo(
        self, user_id: str, payload: RepoImportRequest
    ) -> RepoSummaryResponse:
        owner, repo = parse_repo_url(payload.url)
        summary = await self._build_summary(owner, repo, payload.github_token)

        now = _utcnow()
        token_encrypted = (
            encrypt_secret(payload.github_token, self._encryption_key)
            if payload.github_token
            else None
        )
        await self._repo.upsert(
            RepositoryModel(
                user_id=user_id,
                url=payload.url,
                owner=owner,
                name=repo,
                default_branch=summary.default_branch,
                github_token_encrypted=token_encrypted,
                summary=summary.model_dump(mode="json"),
                created_at=now,
                updated_at=now,
            )
        )
        return summary

    async def get_current(self, user_id: str) -> RepoSummaryResponse:
        model = await self._require_current(user_id)
        return RepoSummaryResponse.model_validate(model.summary)

    async def refresh(self, user_id: str) -> RepoSummaryResponse:
        model = await self._require_current(user_id)
        token = (
            decrypt_secret(model.github_token_encrypted, self._encryption_key)
            if model.github_token_encrypted
            else None
        )
        summary = await self._build_summary(model.owner, model.name, token)
        model.summary = summary.model_dump(mode="json")
        model.updated_at = _utcnow()
        await self._repo.upsert(model)
        return summary

    async def delete_current(self, user_id: str) -> None:
        await self._repo.delete_by_user_id(user_id)

    async def _require_current(self, user_id: str) -> RepositoryModel:
        model = await self._repo.find_by_user_id(user_id)
        if model is None:
            raise NotFoundError("No repository imported yet.")
        return model

    async def _build_summary(
        self, owner: str, repo: str, token: str | None
    ) -> RepoSummaryResponse:
        # Metadata first — this is what raises NotFound/Unauthorized for a bad repo.
        meta = await self._github.get_repo(owner, repo, token)
        default_branch = meta.get("default_branch") or "main"

        contributors = await self._github.get_contributors_count(owner, repo, token)
        entries, truncated = await self._github.get_tree(
            owner, repo, default_branch, token, self._tree_max_entries
        )

        tree = [
            TreeEntry(path=e["path"], type=e["type"], size=e.get("size"))
            for e in entries
            if e.get("type") in ("blob", "tree") and "path" in e
        ]
        # A truncated tree means the true total is unknown -> hide the count.
        file_count = (
            None if truncated else sum(1 for entry in tree if entry.type == "blob")
        )

        docs, readme_path = self._detect_docs(tree)
        readme = (
            await self._github.get_file_text(owner, repo, readme_path, token)
            if readme_path
            else None
        )

        return RepoSummaryResponse(
            owner=owner,
            name=repo,
            full_name=meta.get("full_name", f"{owner}/{repo}"),
            description=meta.get("description"),
            html_url=meta.get("html_url", f"https://github.com/{owner}/{repo}"),
            default_branch=default_branch,
            stars=meta.get("stargazers_count"),
            contributors_count=contributors,
            file_count=file_count,
            tree_truncated=truncated,
            tree=tree,
            docs=docs,
            readme=readme,
        )

    @staticmethod
    def _detect_docs(tree: list[TreeEntry]) -> tuple[list[DocFile], str | None]:
        """Find documentation files in the tree and the README path to fetch."""
        docs: list[DocFile] = []
        readme_path: str | None = None

        for entry in tree:
            if entry.type != "blob":
                continue
            parts = entry.path.split("/")
            directory = "/".join(parts[:-1])
            if directory not in _DOC_DIRS:
                continue

            name = parts[-1]
            category: DocCategory | None = None
            for rule_category, pattern in _DOC_RULES:
                if pattern.match(name):
                    category = rule_category
                    break

            # Surface other root-level markdown as generic docs too.
            if category is None and directory == "" and name.lower().endswith(".md"):
                category = "other"
            if category is None:
                continue

            docs.append(DocFile(category=category, name=name, path=entry.path))
            if category == "readme" and readme_path is None:
                readme_path = entry.path

        return docs, readme_path
