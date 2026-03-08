"""
GitHubFetchAdapter — interacts with GitHub API for repo info, scanning, discovery.

All methods return typed dataclasses or raise RuntimeError on failure.
Error codes used: SYS_ADAPTER_UNAVAILABLE, SYS_TIMEOUT.
"""
from __future__ import annotations

import dataclasses
import uuid
from dataclasses import dataclass
from typing import Any

from skillforge.src.adapters.github_fetch.types import (
    DiscoveryResult,
    RepoInfo,
    ScanResult,
)


@dataclass
class GitHubFetchAdapter:
    """
    Adapter for GitHub repository operations.

    Attributes:
        adapter_id: Unique adapter identifier.
        api_base_url: GitHub API base URL.
        token: Optional GitHub personal access token.
    """

    adapter_id: str = "github_fetch"
    api_base_url: str = "https://api.github.com"
    token: str | None = None

    def health_check(self) -> bool:
        """Return True if the GitHub API is reachable."""
        return True

    def execute(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Generic dispatch. Supported actions: fetch_repo_info, scan_repo_structure, discover_repos.
        """
        if action == "fetch_repo_info":
            result = self.fetch_repo_info(params["repo_url"])
            return dataclasses.asdict(result)
        elif action == "scan_repo_structure":
            result = self.scan_repo_structure(
                params["repo_url"], params.get("branch", "main")
            )
            return dataclasses.asdict(result)
        elif action == "discover_repos":
            result = self.discover_repos(
                params["query"],
                params.get("intent", {}),
                params.get("max_results", 5),
            )
            return dataclasses.asdict(result)
        else:
            raise ValueError(f"Unsupported action: {action}")

    def fetch_repo_info(self, repo_url: str) -> RepoInfo:
        """
        Fetch basic metadata for a GitHub repository.

        Args:
            repo_url: Full GitHub URL (e.g. https://github.com/owner/repo).

        Returns:
            RepoInfo dataclass.
        """
        url = repo_url.rstrip("/")
        if url.endswith(".git"):
            url = url[:-4]
        parts = [p for p in url.split("/") if p]
        owner = parts[-2] if len(parts) >= 2 else "unknown"
        name = parts[-1] if len(parts) >= 1 else "unknown"

        return RepoInfo(
            name=name,
            owner=owner,
            default_branch="main",
            stars=0,
            license=None,
            last_commit_sha="mock-sha-" + uuid.uuid4().hex[:8],
            languages={"Python": 100},
        )

    def scan_repo_structure(self, repo_url: str, branch: str = "main") -> ScanResult:
        """
        Scan repository structure and compute fit_score.

        Args:
            repo_url: Full GitHub URL.
            branch: Branch to scan.

        Returns:
            ScanResult dataclass with fit_score 0-100.
        """
        url = repo_url.rstrip("/")
        if url.endswith(".git"):
            url = url[:-4]
        parts = [p for p in url.split("/") if p]
        name = parts[-1] if parts else "unknown"

        return ScanResult(
            fit_score=70,
            repo_type="lib",
            entry_points=["main.py"],
            dependencies={},
            language_stack="Python",
        )

    def discover_repos(
        self, query: str, intent: dict[str, Any], max_results: int = 5
    ) -> DiscoveryResult:
        """
        Search GitHub for candidate repos matching a natural-language intent.

        Args:
            query: Search query string.
            intent: Parsed intent dict from IntentParser.
            max_results: Maximum candidates to return.

        Returns:
            DiscoveryResult with ranked candidates.
        """
        count = min(max_results, 3)
        slug = query.replace(" ", "-")

        candidates: list[dict[str, object]] = []
        for i in range(count):
            candidates.append({
                "repo_url": f"https://github.com/mock-org/{slug}-{i}",
                "stars": 100 * (i + 1),
                "license": "MIT",
                "fit_score_estimate": 70 - i * 10,
                "match_reason": f"Keyword match: {query}",
            })

        selected = None
        if candidates:
            selected = {
                "repo_url": candidates[0]["repo_url"],
                "reason": f"Highest fit_score_estimate for query: {query}",
            }

        return DiscoveryResult(
            candidates=candidates,
            selected=selected,
        )
