"""Data types for the GitHub fetch adapter."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RepoInfo:
    """Basic metadata about a GitHub repository."""

    name: str
    owner: str
    default_branch: str
    stars: int
    license: str | None
    last_commit_sha: str
    languages: dict[str, int] = field(default_factory=dict)


@dataclass
class ScanResult:
    """Structural scan result for a repository."""

    fit_score: int  # 0-100
    repo_type: str  # workflow | cli | lib | service | template
    entry_points: list[str] = field(default_factory=list)
    dependencies: dict[str, str] = field(default_factory=dict)
    language_stack: str = ""


@dataclass
class DiscoveryResult:
    """Result of searching GitHub for candidate repos."""

    candidates: list[dict[str, object]] = field(default_factory=list)
    # Each candidate: { repo_url, stars, license, fit_score_estimate, match_reason }
    selected: dict[str, object] | None = None
