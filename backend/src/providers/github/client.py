"""Thin async wrapper over the GitHub REST API.

Wraps an injected ``httpx.AsyncClient`` (testable with MockTransport, no network).
The API base is a fixed constant — combined with :func:`parse_repo_url`, requests
can only ever target ``api.github.com`` (SSRF guard). An optional token is sent
as a Bearer credential for private repos / higher rate limits.
"""
from __future__ import annotations

import base64
import re
from typing import Any

import httpx

from ...core.exceptions import NotFoundError, UnauthorizedError, UpstreamError

_API_BASE = "https://api.github.com"
# In a paginated Link header, the rel="last" page number == the total count
# when per_page=1 — used to count contributors cheaply.
_LAST_PAGE = re.compile(r'[?&]page=(\d+)>;\s*rel="last"')


class GitHubClient:
    def __init__(self, client: httpx.AsyncClient, timeout: float) -> None:
        self._client = client
        self._timeout = timeout

    def _headers(self, token: str | None) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    async def _get(
        self, path: str, token: str | None, *, params: dict[str, str] | None = None
    ) -> httpx.Response:
        try:
            return await self._client.get(
                f"{_API_BASE}{path}",
                headers=self._headers(token),
                params=params,
                timeout=self._timeout,
            )
        except httpx.RequestError as exc:
            raise UpstreamError("Could not reach GitHub.") from exc

    @staticmethod
    def _raise_for_status(response: httpx.Response, *, context: str) -> None:
        status = response.status_code
        if 200 <= status < 300:
            return
        if status == 404:
            raise NotFoundError(
                f"GitHub {context} not found — check the URL, or add a token if it's private."
            )
        if status == 401:
            raise UnauthorizedError("GitHub rejected the token.")
        if status == 403:
            if response.headers.get("X-RateLimit-Remaining") == "0":
                raise UpstreamError(
                    "GitHub rate limit exceeded. Add a token or try again later."
                )
            raise UnauthorizedError(
                "GitHub denied access — the repo may be private. Add a token."
            )
        raise UpstreamError(f"GitHub request failed (HTTP {status}).")

    async def get_repo(self, owner: str, repo: str, token: str | None) -> dict[str, Any]:
        """Core repo metadata. Raises if the repo can't be accessed."""
        response = await self._get(f"/repos/{owner}/{repo}", token)
        self._raise_for_status(response, context="repository")
        return response.json()

    async def get_contributors_count(
        self, owner: str, repo: str, token: str | None
    ) -> int | None:
        """Contributor count via the Link header trick. None if unavailable."""
        response = await self._get(
            f"/repos/{owner}/{repo}/contributors",
            token,
            params={"per_page": "1", "anon": "true"},
        )
        if response.status_code != 200:
            return None  # optional stat — never fail the whole summary on it
        link = response.headers.get("Link")
        if link:
            match = _LAST_PAGE.search(link)
            if match:
                return int(match.group(1))
        # No pagination -> the returned array already holds everyone.
        data = response.json()
        return len(data) if isinstance(data, list) else None

    async def get_tree(
        self,
        owner: str,
        repo: str,
        branch: str,
        token: str | None,
        max_entries: int,
    ) -> tuple[list[dict[str, Any]], bool]:
        """Full recursive tree. Returns (entries, truncated)."""
        response = await self._get(
            f"/repos/{owner}/{repo}/git/trees/{branch}",
            token,
            params={"recursive": "1"},
        )
        if response.status_code != 200:
            return [], False
        data = response.json()
        entries = data.get("tree", []) or []
        truncated = bool(data.get("truncated", False))
        if len(entries) > max_entries:
            entries = entries[:max_entries]
            truncated = True
        return entries, truncated

    async def get_file_text(
        self, owner: str, repo: str, path: str, token: str | None
    ) -> str | None:
        """Decoded UTF-8 text of a file, or None if missing/binary/too large."""
        response = await self._get(f"/repos/{owner}/{repo}/contents/{path}", token)
        if response.status_code != 200:
            return None
        content = response.json().get("content")
        if not content:
            return None
        try:
            return base64.b64decode(content).decode("utf-8", errors="replace")
        except (ValueError, TypeError):
            return None
