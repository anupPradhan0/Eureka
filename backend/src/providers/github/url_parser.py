"""Parse a GitHub repo URL into ``(owner, repo)``.

This is the primary SSRF guard: the host is pinned to ``github.com`` and only the
owner/repo are extracted. Callers then build ``api.github.com`` paths themselves,
so a user-supplied URL can never choose the host we actually request.
"""
from __future__ import annotations

import re

from ...core.exceptions import ValidationError

# host must be exactly github.com (optionally www.); capture owner + repo,
# tolerating an optional .git suffix and any trailing /path, ?query or #frag.
_PATTERN = re.compile(
    r"^(?:https?://)?(?:www\.)?github\.com/"
    r"(?P<owner>[A-Za-z0-9][A-Za-z0-9-]*)/"
    r"(?P<repo>[A-Za-z0-9._-]+?)"
    r"(?:\.git)?(?:[/?#].*)?$"
)


def parse_repo_url(url: str) -> tuple[str, str]:
    """Return ``(owner, repo)`` or raise a domain ValidationError."""
    match = _PATTERN.match(url.strip())
    if match is None:
        raise ValidationError(
            "Enter a valid GitHub repository URL, e.g. https://github.com/owner/repo."
        )
    return match.group("owner"), match.group("repo")
