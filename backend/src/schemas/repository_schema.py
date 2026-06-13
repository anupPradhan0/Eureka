"""Request/response DTOs for the repository API."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

DocCategory = Literal[
    "readme", "code_of_conduct", "contributing", "license", "security", "other"
]


class TreeEntry(BaseModel):
    path: str
    type: Literal["blob", "tree"]
    size: int | None = None


class DocFile(BaseModel):
    category: DocCategory
    name: str
    path: str


class RepoSummaryResponse(BaseModel):
    owner: str
    name: str
    full_name: str
    description: str | None = None
    html_url: str
    default_branch: str
    # Null when GitHub doesn't expose the stat — the UI hides it.
    stars: int | None = None
    contributors_count: int | None = None
    file_count: int | None = None
    tree_truncated: bool = False
    tree: list[TreeEntry] = Field(default_factory=list)
    docs: list[DocFile] = Field(default_factory=list)
    readme: str | None = None


class RepoImportRequest(BaseModel):
    url: str = Field(min_length=1, max_length=500)
    github_token: str | None = Field(default=None, max_length=500)
