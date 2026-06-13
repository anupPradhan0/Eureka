"""Unit tests for GitHub URL parsing (the SSRF guard)."""
from __future__ import annotations

import pytest

from src.core.exceptions import ValidationError
from src.providers.github.url_parser import parse_repo_url


@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://github.com/owner/repo", ("owner", "repo")),
        ("http://github.com/owner/repo", ("owner", "repo")),
        ("github.com/owner/repo", ("owner", "repo")),
        ("https://www.github.com/owner/repo", ("owner", "repo")),
        ("https://github.com/owner/repo.git", ("owner", "repo")),
        ("https://github.com/owner/repo/", ("owner", "repo")),
        ("https://github.com/owner/repo/tree/main", ("owner", "repo")),
        ("  https://github.com/owner/repo  ", ("owner", "repo")),
        ("https://github.com/owner/my.repo", ("owner", "my.repo")),
        ("https://github.com/org-name/repo_name", ("org-name", "repo_name")),
    ],
)
def test_parses_valid_urls(url, expected):
    assert parse_repo_url(url) == expected


@pytest.mark.parametrize(
    "url",
    [
        "https://gitlab.com/owner/repo",
        "https://github.com.evil.com/owner/repo",
        "https://evil.com/github.com/owner/repo",
        "https://github.com/owner",
        "https://github.com/",
        "not a url at all",
        "ftp://github.com/owner/repo",
    ],
)
def test_rejects_invalid_or_unsafe_urls(url):
    with pytest.raises(ValidationError):
        parse_repo_url(url)
