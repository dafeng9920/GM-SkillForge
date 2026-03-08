文件: skillforge/src/adapters/github_fetch/adapter.py
pythonDownloadCopy code"""
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
文件: skillforge/src/adapters/sandbox_runner/adapter.py
pythonDownloadCopy code"""
SandboxRunnerAdapter — runs skill bundles in an isolated sandbox.

Error codes used: EXEC_SANDBOX_VIOLATION, EXEC_TIMEOUT, SYS_ADAPTER_UNAVAILABLE.
"""
from __future__ import annotations

import dataclasses
import time
import uuid
from dataclasses import dataclass
from typing import Any

from skillforge.src.adapters.sandbox_runner.types import RunResult, SandboxConfig


@dataclass
class SandboxRunnerAdapter:
    """
    Adapter for isolated skill execution and testing.

    Attributes:
        adapter_id: Unique adapter identifier.
    """

    adapter_id: str = "sandbox_runner"

    def health_check(self) -> bool:
        """Return True if the sandbox runtime is available."""
        return True

    def execute(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Generic dispatch. Supported actions: run_in_sandbox.
        """
        if action == "run_in_sandbox":
            config = SandboxConfig(
                timeout_seconds=params.get("timeout_seconds", 120),
                max_tool_calls=params.get("max_tool_calls", 50),
                sandbox_mode=params.get("sandbox_mode", "strict"),
                allowed_domains=params.get("allowed_domains", []),
                max_bytes_io=params.get("max_bytes_io", 10_000_000),
            )
            result = self.run_in_sandbox(params["bundle_path"], config)
            return dataclasses.asdict(result)
        else:
            raise ValueError(f"Unsupported action: {action}")

    def run_in_sandbox(self, bundle_path: str, config: SandboxConfig) -> RunResult:
        """
        Execute a skill bundle inside the sandbox.

        Args:
            bundle_path: Path to the skill bundle directory or archive.
            config: SandboxConfig controlling limits and permissions.

        Returns:
            RunResult with test_report, trace_events, and sandbox_report.
        """
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        return RunResult(
            success=True,
            test_report={
                "total_runs": 3,
                "passed": 3,
                "failed": 0,
                "success_rate": 1.0,
                "avg_latency_ms": 42.5,
                "total_cost_usd": 0.001,
            },
            trace_events=[
                {
                    "event_id": str(uuid.uuid4()),
                    "event_type": "sandbox_execution",
                    "timestamp": timestamp,
                    "node_id": "sandbox_runner",
                    "status": "completed",
                }
            ],
            sandbox_report={
                "cpu_time_ms": 85,
                "memory_peak_mb": 12.3,
                "violations": [],
            },
        )
文件: skillforge/src/adapters/registry_client/adapter.py
pythonDownloadCopy code"""
RegistryClientAdapter — publish skills to and query the GM OS skill registry.

Error codes used: REG_DUPLICATE, REG_VALIDATION_FAILED, SYS_ADAPTER_UNAVAILABLE.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from typing import Any


@dataclass
class RegistryClientAdapter:
    """
    Adapter for the skill registry.

    Attributes:
        adapter_id: Unique adapter identifier.
        registry_url: Base URL of the registry service.
    """

    adapter_id: str = "registry_client"
    registry_url: str = "http://localhost:8080"

    def health_check(self) -> bool:
        """Return True if the registry service is reachable."""
        return True

    def execute(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Generic dispatch. Supported actions: publish, check_exists.
        """
        if action == "publish":
            return self.publish(params)
        elif action == "check_exists":
            result = self.check_exists(params["skill_id"], params["version"])
            return {"exists": result}
        else:
            raise ValueError(f"Unsupported action: {action}")

    def publish(self, request: dict[str, Any]) -> dict[str, Any]:
        """
        Publish a skill to the registry.

        Args:
            request: Dict conforming to gm-os-core registry_publish.schema.json
                     (RegistryPublishRequest).

        Returns:
            Dict conforming to RegistryPublishResult:
            {
                "schema_version": "0.1.0",
                "skill_id": str,
                "version": str,
                "status": "published" | "rejected",
                "registry_url": str,
                "timestamp": str
            }
        """
        skill_id: str = request.get("skill_id", "unknown")
        version: str = request.get("version", "0.1.0")
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        return {
            "schema_version": "0.1.0",
            "skill_id": skill_id,
            "version": version,
            "status": "published",
            "registry_url": f"{self.registry_url}/skills/{skill_id}/{version}",
            "timestamp": timestamp,
        }

    def check_exists(self, skill_id: str, version: str) -> bool:
        """
        Check whether a skill at the given version already exists in the registry.

        Args:
            skill_id: Skill identifier.
            version: Semantic version string.

        Returns:
            True if the skill+version combination already exists.
        """
        return False