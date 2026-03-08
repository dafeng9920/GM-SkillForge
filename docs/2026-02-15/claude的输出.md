文件: skillforge/src/init.py
pythonDownloadCopy code"""SkillForge — Skill production pipeline for GM OS."""
__version__ = "0.1.0"
文件: skillforge/src/orchestration/init.py
pythonDownloadCopy code"""Orchestration layer: engine, node runner, gate engine."""
from skillforge.src.orchestration.engine import PipelineEngine
from skillforge.src.orchestration.node_runner import NodeRunner
from skillforge.src.orchestration.gate_engine import GateEngine

__all__ = ["PipelineEngine", "NodeRunner", "GateEngine"]
文件: skillforge/src/adapters/init.py
pythonDownloadCopy code"""External adapters for SkillForge pipeline."""
文件: skillforge/src/adapters/github_fetch/init.py
pythonDownloadCopy code"""GitHub fetch adapter — repo info, scanning, discovery."""
from skillforge.src.adapters.github_fetch.adapter import GitHubFetchAdapter
from skillforge.src.adapters.github_fetch.types import RepoInfo, ScanResult, DiscoveryResult

__all__ = ["GitHubFetchAdapter", "RepoInfo", "ScanResult", "DiscoveryResult"]
文件: skillforge/src/adapters/sandbox_runner/init.py
pythonDownloadCopy code"""Sandbox runner adapter — isolated skill execution and testing."""
from skillforge.src.adapters.sandbox_runner.adapter import SandboxRunnerAdapter
from skillforge.src.adapters.sandbox_runner.types import SandboxConfig, RunResult

__all__ = ["SandboxRunnerAdapter", "SandboxConfig", "RunResult"]
文件: skillforge/src/adapters/registry_client/init.py
pythonDownloadCopy code"""Registry client adapter — publish and query skill registry."""
from skillforge.src.adapters.registry_client.adapter import RegistryClientAdapter

__all__ = ["RegistryClientAdapter"]
文件: skillforge/src/nodes/init.py
pythonDownloadCopy code"""Pipeline node handlers — one class per pipeline stage."""
from skillforge.src.nodes.intent_parser import IntentParser
from skillforge.src.nodes.source_strategy import SourceStrategy
from skillforge.src.nodes.github_discover import GitHubDiscovery
from skillforge.src.nodes.skill_composer import SkillComposer
from skillforge.src.nodes.intake_repo import IntakeRepo
from skillforge.src.nodes.license_gate import LicenseGate
from skillforge.src.nodes.repo_scan import RepoScan
from skillforge.src.nodes.draft_spec import DraftSpec
from skillforge.src.nodes.constitution_gate import ConstitutionGate
from skillforge.src.nodes.scaffold_impl import ScaffoldImpl
from skillforge.src.nodes.sandbox_test import SandboxTest
from skillforge.src.nodes.pack_publish import PackPublish

__all__ = [
    "IntentParser",
    "SourceStrategy",
    "GitHubDiscovery",
    "SkillComposer",
    "IntakeRepo",
    "LicenseGate",
    "RepoScan",
    "DraftSpec",
    "ConstitutionGate",
    "ScaffoldImpl",
    "SandboxTest",
    "PackPublish",
]
文件: skillforge/src/protocols.py
pythonDownloadCopy code"""
Core protocols for SkillForge implementation layer.

All modules MUST program against these protocols, never concrete classes.
Protocols follow gm-os-core schema conventions; every data structure
that leaves the process boundary carries schema_version = "0.1.0".
"""
from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class NodeHandler(Protocol):
    """
    A single pipeline node.

    Every node:
    - validates its input against the corresponding gm-os-core schema,
    - executes domain logic,
    - validates its output,
    - emits at least one trace_event.

    Attributes:
        node_id: Unique identifier matching pipeline_v0.yml node names.
        stage: Numeric stage index (pre-0 stages use -1).
    """

    node_id: str
    stage: int

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Return a list of validation error strings. Empty list = valid."""
        ...

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Run the node logic.

        Args:
            input_data: Validated input payload.

        Returns:
            Output payload conforming to this node's output schema.

        Raises:
            RuntimeError: On unrecoverable execution failure.
        """
        ...

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Return a list of validation error strings. Empty list = valid."""
        ...


@runtime_checkable
class GateEvaluator(Protocol):
    """
    Evaluates a gate decision for a given pipeline node.

    Returns a dict conforming to gm-os-core gate_decision.schema.json:
    {
        "schema_version": "0.1.0",
        "gate_id": str,
        "node_id": str,
        "decision": "ALLOW" | "DENY" | "REQUIRES_CHANGES",
        "reason": str,
        "details": dict,
        "timestamp": str (ISO-8601)
    }
    """

    def evaluate(self, node_id: str, artifacts: dict[str, Any]) -> dict[str, Any]:
        """Evaluate gate and return a GateDecision dict."""
        ...


@runtime_checkable
class Adapter(Protocol):
    """
    External service adapter.

    Adapters wrap third-party APIs (GitHub, sandbox runtime, registry)
    behind a stable interface so pipeline nodes never talk to the outside
    world directly.

    Attributes:
        adapter_id: Unique adapter identifier.
    """

    adapter_id: str

    def health_check(self) -> bool:
        """Return True if the backing service is reachable."""
        ...

    def execute(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Generic action dispatch.

        Args:
            action: The adapter-specific action name.
            params: Action parameters.

        Returns:
            Action result payload.
        """
        ...
文件: skillforge/src/orchestration/engine.py
pythonDownloadCopy code"""
PipelineEngine — dual-path orchestration engine for SkillForge.

Input Contract
--------------
{
    "mode": "nl" | "github" | "auto",
    "natural_language": str | None,
    "repo_url": str | None,
    "branch": str  (default "main"),
    "options": {
        "target_environment": "python" | "node" | "docker",
        "intended_use": "automation" | "data" | "web" | "ops",
        "visibility": "public" | "private" | "team",
        "sandbox_mode": "strict" | "moderate" | "permissive"
    }
}

Output Contract
---------------
{
    "job_id": "UUID",
    "status": "completed" | "failed" | "gate_denied",
    "path_taken": "A" | "B" | "AB",
    "stages_completed": int,
    "gate_decisions": [GateDecision...],
    "audit_pack_path": str | None,
    "publish_result": dict | None,
    "trace_events": [TraceEvent...],
    "duration_ms": int,
    "error": { "code": str, "message": str } | None
}

Path routing
------------
- mode "nl"     → Path A:  intent_parse → source_strategy → skill_compose
                            → constitution_risk_gate → scaffold → sandbox → publish
- mode "github" → Path B:  intake_repo → license_gate → repo_scan → draft_spec
                            → constitution_risk_gate → scaffold → sandbox → publish
- mode "auto"   → Path AB: intent_parse → source_strategy → github_discover
                            → intake_repo → … → publish
"""
from __future__ import annotations

import uuid
import time
from dataclasses import dataclass, field
from typing import Any

from skillforge.src.protocols import NodeHandler, GateEvaluator


# -- Path definitions ---------------------------------------------------------

PATH_A: list[str] = [
    "intent_parse",
    "source_strategy",
    "skill_compose",
    "constitution_risk_gate",
    "scaffold_skill_impl",
    "sandbox_test_and_trace",
    "pack_audit_and_publish",
]

PATH_B: list[str] = [
    "intake_repo",
    "license_gate",
    "repo_scan_fit_score",
    "draft_skill_spec",
    "constitution_risk_gate",
    "scaffold_skill_impl",
    "sandbox_test_and_trace",
    "pack_audit_and_publish",
]

PATH_AB: list[str] = [
    "intent_parse",
    "source_strategy",
    "github_discover",
    "intake_repo",
    "license_gate",
    "repo_scan_fit_score",
    "draft_skill_spec",
    "constitution_risk_gate",
    "scaffold_skill_impl",
    "sandbox_test_and_trace",
    "pack_audit_and_publish",
]

GATE_NODES: set[str] = {"license_gate", "constitution_risk_gate"}


@dataclass
class PipelineEngine:
    """
    Dual-path orchestration engine.

    Attributes:
        node_registry: Mapping of node_id → NodeHandler instance.
        gate_evaluator: GateEvaluator used for gate nodes.
        schema_version: Output schema version tag.
    """

    node_registry: dict[str, NodeHandler] = field(default_factory=dict)
    gate_evaluator: GateEvaluator | None = None
    schema_version: str = "0.1.0"

    # -- public API -----------------------------------------------------------

    def register_node(self, handler: NodeHandler) -> None:
        """Register a NodeHandler by its node_id."""
        self.node_registry[handler.node_id] = handler

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the full pipeline for the given input.

        Args:
            input_data: A dict conforming to pipeline_input.schema.json.

        Returns:
            A dict conforming to pipeline_output.schema.json.
        """
        raise NotImplementedError("TODO: implement")

    # -- internal helpers -----------------------------------------------------

    def _resolve_path(self, mode: str) -> tuple[str, list[str]]:
        """Return (path_label, ordered list of node_ids) for the given mode."""
        if mode == "nl":
            return ("A", PATH_A)
        elif mode == "github":
            return ("B", PATH_B)
        elif mode == "auto":
            return ("AB", PATH_AB)
        else:
            raise ValueError(f"Unknown mode: {mode}")

    def _build_output(
        self,
        *,
        job_id: str,
        status: str,
        path_taken: str,
        stages_completed: int,
        gate_decisions: list[dict[str, Any]],
        audit_pack_path: str | None,
        publish_result: dict[str, Any] | None,
        trace_events: list[dict[str, Any]],
        duration_ms: int,
        error: dict[str, str] | None,
    ) -> dict[str, Any]:
        """Construct a pipeline_output conforming dict."""
        return {
            "schema_version": self.schema_version,
            "job_id": job_id,
            "status": status,
            "path_taken": path_taken,
            "stages_completed": stages_completed,
            "gate_decisions": gate_decisions,
            "audit_pack_path": audit_pack_path,
            "publish_result": publish_result,
            "trace_events": trace_events,
            "duration_ms": duration_ms,
            "error": error,
        }
文件: skillforge/src/orchestration/node_runner.py
pythonDownloadCopy code"""
NodeRunner — single-node executor with trace, timeout, and retry.

Execution sequence
------------------
1. Load node schema → validate input via handler.validate_input()
2. Call handler.execute(input_data)
3. Validate output via handler.validate_output()
4. Emit trace_event(s): node_start, node_complete or node_error
5. Timeout governed by pipeline_v0.yml settings
6. Retry governed by error_policy.yml settings
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from skillforge.src.protocols import NodeHandler


@dataclass
class NodeRunner:
    """
    Single-node execution wrapper.

    Attributes:
        default_timeout_seconds: Fallback timeout if pipeline_v0.yml has no entry.
        max_retries: Fallback max retries if error_policy.yml has no entry.
        retry_delay_seconds: Base delay between retries (exponential back-off).
    """

    default_timeout_seconds: int = 300
    max_retries: int = 2
    retry_delay_seconds: float = 1.0

    def run(
        self,
        handler: NodeHandler,
        input_data: dict[str, Any],
        *,
        timeout_seconds: int | None = None,
        max_retries: int | None = None,
    ) -> dict[str, Any]:
        """
        Execute a single node with validation, tracing, timeout and retry.

        Args:
            handler: The NodeHandler to run.
            input_data: Pre-validated input payload.
            timeout_seconds: Override timeout.
            max_retries: Override max retries.

        Returns:
            Dict with keys:
            {
                "node_id": str,
                "output": dict,          # handler output
                "trace_events": [dict],   # list of TraceEvent dicts
                "duration_ms": int,
                "retries_used": int
            }

        Raises:
            ValueError: If input validation fails.
            RuntimeError: If output validation fails or execution errors exhaust retries.
        """
        raise NotImplementedError("TODO: implement")

    def _make_trace_event(
        self,
        *,
        node_id: str,
        event_type: str,
        detail: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Build a trace_event dict conforming to gm-os-core trace_event.schema.json.

        Args:
            node_id: Originating node.
            event_type: One of node_start, node_complete, node_error.
            detail: Optional extra payload.

        Returns:
            TraceEvent dict with schema_version = "0.1.0".
        """
        return {
            "schema_version": "0.1.0",
            "trace_id": str(uuid.uuid4()),
            "node_id": node_id,
            "event_type": event_type,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "detail": detail or {},
        }
文件: skillforge/src/orchestration/gate_engine.py
pythonDownloadCopy code"""
GateEngine — gate decision evaluator.

Produces a GateDecision dict conforming to gm-os-core gate_decision.schema.json:
{
    "schema_version": "0.1.0",
    "gate_id": str,
    "node_id": str,
    "decision": "ALLOW" | "DENY" | "REQUIRES_CHANGES",
    "reason": str,
    "details": dict,
    "timestamp": str (ISO-8601)
}
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from typing import Any


@dataclass
class GateEngine:
    """
    Gate decision evaluation engine.

    The GateEngine delegates to node-specific evaluator logic and wraps
    results in the standard GateDecision schema.

    Attributes:
        schema_version: Schema version for emitted GateDecision dicts.
    """

    schema_version: str = "0.1.0"

    def evaluate(self, node_id: str, artifacts: dict[str, Any]) -> dict[str, Any]:
        """
        Evaluate a gate for the specified node.

        Args:
            node_id: The gate node identifier (e.g. "license_gate").
            artifacts: Accumulated pipeline artifacts up to this stage.

        Returns:
            GateDecision dict.
        """
        raise NotImplementedError("TODO: implement")

    def _build_decision(
        self,
        *,
        gate_id: str,
        node_id: str,
        decision: str,
        reason: str,
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Helper to build a well-formed GateDecision."""
        return {
            "schema_version": self.schema_version,
            "gate_id": gate_id,
            "node_id": node_id,
            "decision": decision,
            "reason": reason,
            "details": details or {},
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
文件: skillforge/src/adapters/github_fetch/types.py
pythonDownloadCopy code"""Data types for the GitHub fetch adapter."""
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
文件: skillforge/src/adapters/github_fetch/adapter.py
pythonDownloadCopy code"""
GitHubFetchAdapter — interacts with GitHub API for repo info, scanning, discovery.

All methods return typed dataclasses or raise RuntimeError on failure.
Error codes used: SYS_ADAPTER_UNAVAILABLE, SYS_TIMEOUT.
"""
from __future__ import annotations

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
        raise NotImplementedError("TODO: implement")

    def execute(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Generic dispatch. Supported actions: fetch_repo_info, scan_repo_structure, discover_repos.
        """
        raise NotImplementedError("TODO: implement")

    def fetch_repo_info(self, repo_url: str) -> RepoInfo:
        """
        Fetch basic metadata for a GitHub repository.

        Args:
            repo_url: Full GitHub URL (e.g. https://github.com/owner/repo).

        Returns:
            RepoInfo dataclass.
        """
        raise NotImplementedError("TODO: implement")

    def scan_repo_structure(self, repo_url: str, branch: str = "main") -> ScanResult:
        """
        Scan repository structure and compute fit_score.

        Args:
            repo_url: Full GitHub URL.
            branch: Branch to scan.

        Returns:
            ScanResult dataclass with fit_score 0-100.
        """
        raise NotImplementedError("TODO: implement")

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
        raise NotImplementedError("TODO: implement")
文件: skillforge/src/adapters/sandbox_runner/types.py
pythonDownloadCopy code"""Data types for the sandbox runner adapter."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SandboxConfig:
    """Configuration for a sandboxed skill execution."""

    timeout_seconds: int = 120
    max_tool_calls: int = 50
    sandbox_mode: str = "strict"  # strict | moderate | permissive
    allowed_domains: list[str] = field(default_factory=list)
    max_bytes_io: int = 10_000_000


@dataclass
class RunResult:
    """Result of running a skill bundle in the sandbox."""

    success: bool = False
    test_report: dict[str, object] = field(default_factory=dict)
    # test_report keys: total_runs, passed, failed, success_rate, avg_latency_ms, total_cost_usd
    trace_events: list[dict[str, object]] = field(default_factory=list)
    sandbox_report: dict[str, object] = field(default_factory=dict)
    # sandbox_report keys: cpu_time_ms, memory_peak_mb, violations
文件: skillforge/src/adapters/sandbox_runner/adapter.py
pythonDownloadCopy code"""
SandboxRunnerAdapter — runs skill bundles in an isolated sandbox.

Error codes used: EXEC_SANDBOX_VIOLATION, EXEC_TIMEOUT, SYS_ADAPTER_UNAVAILABLE.
"""
from __future__ import annotations

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
        raise NotImplementedError("TODO: implement")

    def execute(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Generic dispatch. Supported actions: run_in_sandbox.
        """
        raise NotImplementedError("TODO: implement")

    def run_in_sandbox(self, bundle_path: str, config: SandboxConfig) -> RunResult:
        """
        Execute a skill bundle inside the sandbox.

        Args:
            bundle_path: Path to the skill bundle directory or archive.
            config: SandboxConfig controlling limits and permissions.

        Returns:
            RunResult with test_report, trace_events, and sandbox_report.
        """
        raise NotImplementedError("TODO: implement")
文件: skillforge/src/adapters/registry_client/adapter.py
pythonDownloadCopy code"""
RegistryClientAdapter — publish skills to and query the GM OS skill registry.

Error codes used: REG_DUPLICATE, REG_VALIDATION_FAILED, SYS_ADAPTER_UNAVAILABLE.
"""
from __future__ import annotations

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
        raise NotImplementedError("TODO: implement")

    def execute(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Generic dispatch. Supported actions: publish, check_exists.
        """
        raise NotImplementedError("TODO: implement")

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
        raise NotImplementedError("TODO: implement")

    def check_exists(self, skill_id: str, version: str) -> bool:
        """
        Check whether a skill at the given version already exists in the registry.

        Args:
            skill_id: Skill identifier.
            version: Semantic version string.

        Returns:
            True if the skill+version combination already exists.
        """
        raise NotImplementedError("TODO: implement")
文件: skillforge/src/nodes/intent_parser.py
pythonDownloadCopy code"""
IntentParser node — parses natural language into structured intent.

Path: A, A+B
Stage: pre-0 (-1)

Input Contract
--------------
{
    "natural_language": str,
    "options": { ... }   # pipeline options
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "intent": {
        "goal": str,
        "domain": str,
        "actions": list[str],
        "constraints": list[str],
        "target_environment": str,
        "intended_use": str
    },
    "confidence": float,   # 0.0 - 1.0
    "raw_input": str
}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class IntentParser:
    """Parse natural-language skill descriptions into structured intent."""

    node_id: str = "intent_parse"
    stage: int = -1

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate that natural_language is present and non-empty."""
        raise NotImplementedError("TODO: implement")

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Parse the natural language description into a structured intent dict.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        raise NotImplementedError("TODO: implement")

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate output against intent schema."""
        raise NotImplementedError("TODO: implement")
文件: skillforge/src/nodes/source_strategy.py
pythonDownloadCopy code"""
SourceStrategy node — decides whether to generate from scratch or search GitHub.

Path: A, A+B
Stage: pre-0 (-1)

Input Contract
--------------
{
    "intent": { ... },       # from IntentParser
    "mode": "nl" | "auto",
    "confidence": float
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "strategy": "generate" | "search_github" | "hybrid",
    "search_query": str | None,      # set when strategy includes github search
    "generation_hints": dict | None,  # set when strategy includes generation
    "reason": str
}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class SourceStrategy:
    """Decide source strategy based on parsed intent and mode."""

    node_id: str = "source_strategy"
    stage: int = -1

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate that intent and mode are present."""
        raise NotImplementedError("TODO: implement")

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Determine source strategy.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        raise NotImplementedError("TODO: implement")

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate strategy output."""
        raise NotImplementedError("TODO: implement")
文件: skillforge/src/nodes/github_discover.py
pythonDownloadCopy code"""
GitHubDiscovery node — search GitHub for candidate repos matching intent.

Path: A+B only
Stage: pre-0 (-1)

Input Contract
--------------
{
    "search_query": str,
    "intent": { ... },
    "max_results": int       # default 5
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "candidates": [
        {
            "repo_url": str,
            "stars": int,
            "license": str | None,
            "fit_score_estimate": int,
            "match_reason": str
        }
    ],
    "selected": {
        "repo_url": str,
        "reason": str
    } | None,
    "fallback_to_generate": bool
}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class GitHubDiscovery:
    """Search GitHub for repos that match the parsed intent."""

    node_id: str = "github_discover"
    stage: int = -1

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate search_query and intent are present."""
        raise NotImplementedError("TODO: implement")

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Search GitHub and rank candidate repos.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        raise NotImplementedError("TODO: implement")

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate discovery output."""
        raise NotImplementedError("TODO: implement")
文件: skillforge/src/nodes/skill_composer.py
pythonDownloadCopy code"""
SkillComposer node — generate a skill spec from intent (no repo source).

Path: A only
Stage: A-only (stage index 1 within path A context)

Input Contract
--------------
{
    "intent": { ... },
    "generation_hints": dict | None,
    "options": { ... }
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "skill_spec": {
        "name": str,
        "version": str,
        "description": str,
        "inputs": list[dict],
        "outputs": list[dict],
        "tools_required": list[str],
        "steps": list[dict],
        "constraints": list[str]
    },
    "source": "generated",
    "confidence": float
}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class SkillComposer:
    """Compose a skill specification directly from parsed intent."""

    node_id: str = "skill_compose"
    stage: int = -1  # A-only pre-shared stage

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate intent presence."""
        raise NotImplementedError("TODO: implement")

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Generate a skill specification from intent.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        raise NotImplementedError("TODO: implement")

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate generated skill spec."""
        raise NotImplementedError("TODO: implement")
文件: skillforge/src/nodes/intake_repo.py
pythonDownloadCopy code"""
IntakeRepo node — fetch and validate a GitHub repository.

Path: B, A+B
Stage: 0

Input Contract (conforms to gm-os-core intake_repo.schema.json)
--------------
{
    "repo_url": str,
    "branch": str,
    "options": { ... }
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "repo_info": {
        "name": str,
        "owner": str,
        "default_branch": str,
        "stars": int,
        "license": str | None,
        "last_commit_sha": str,
        "languages": dict
    },
    "fetch_status": "ok" | "error",
    "local_path": str | None
}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class IntakeRepo:
    """Fetch and intake a GitHub repository."""

    node_id: str = "intake_repo"
    stage: int = 0

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate repo_url is present and well-formed."""
        raise NotImplementedError("TODO: implement")

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Fetch repository information and clone/download.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        raise NotImplementedError("TODO: implement")

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate intake output."""
        raise NotImplementedError("TODO: implement")
文件: skillforge/src/nodes/license_gate.py
pythonDownloadCopy code"""
LicenseGate node — gate that checks repository license compatibility.

Path: B, A+B
Stage: 1

Input Contract (conforms to gm-os-core license_gate.schema.json)
--------------
{
    "repo_info": { ... },    # from IntakeRepo
    "options": { ... }
}

Output Contract (GateDecision)
---------------
{
    "schema_version": "0.1.0",
    "gate_id": "license_gate",
    "node_id": "license_gate",
    "decision": "ALLOW" | "DENY" | "REQUIRES_CHANGES",
    "reason": str,
    "details": {
        "license_detected": str | None,
        "compatible": bool,
        "allowed_licenses": list[str]
    },
    "timestamp": str
}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class LicenseGate:
    """Evaluate license compatibility for an ingested repo."""

    node_id: str = "license_gate"
    stage: int = 1

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate repo_info is present."""
        raise NotImplementedError("TODO: implement")

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Check repository license and produce GateDecision.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract (GateDecision).
        """
        raise NotImplementedError("TODO: implement")

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate GateDecision structure."""
        raise NotImplementedError("TODO: implement")
文件: skillforge/src/nodes/repo_scan.py
pythonDownloadCopy code"""
RepoScan node — scan repository structure and compute fit score.

Path: B, A+B
Stage: 2

Input Contract (conforms to gm-os-core repo_scan_fit_score.schema.json)
--------------
{
    "repo_info": { ... },
    "local_path": str,
    "options": { ... }
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "fit_score": int,          # 0-100
    "repo_type": str,          # workflow | cli | lib | service | template
    "entry_points": list[str],
    "dependencies": dict[str, str],
    "language_stack": str,
    "complexity_metrics": {
        "total_files": int,
        "total_loc": int,
        "avg_function_length": float
    }
}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RepoScan:
    """Scan repo structure and produce a fit score."""

    node_id: str = "repo_scan_fit_score"
    stage: int = 2

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate repo_info and local_path are present."""
        raise NotImplementedError("TODO: implement")

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Scan repo structure and compute fit score.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        raise NotImplementedError("TODO: implement")

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate scan result."""
        raise NotImplementedError("TODO: implement")
文件: skillforge/src/nodes/draft_spec.py
pythonDownloadCopy code"""
DraftSpec node — draft a skill specification from scan results.

Path: B, A+B
Stage: 3

Input Contract (conforms to gm-os-core draft_skill_spec.schema.json)
--------------
{
    "repo_info": { ... },
    "scan_result": { ... },     # from RepoScan
    "options": { ... }
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "skill_spec": {
        "name": str,
        "version": str,
        "description": str,
        "inputs": list[dict],
        "outputs": list[dict],
        "tools_required": list[str],
        "steps": list[dict],
        "constraints": list[str]
    },
    "source": "repo",
    "derived_from": {
        "repo_url": str,
        "commit_sha": str
    }
}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class DraftSpec:
    """Draft a skill specification from repository scan results."""

    node_id: str = "draft_skill_spec"
    stage: int = 3

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate scan_result and repo_info are present."""
        raise NotImplementedError("TODO: implement")

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Draft skill specification from scan.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        raise NotImplementedError("TODO: implement")

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate drafted spec."""
        raise NotImplementedError("TODO: implement")
文件: skillforge/src/nodes/constitution_gate.py
pythonDownloadCopy code"""
ConstitutionGate node — risk assessment gate for skill safety and alignment.

Path: ALL
Stage: 4

Input Contract (conforms to gm-os-core constitution_risk_gate.schema.json)
--------------
{
    "skill_spec": { ... },      # from SkillComposer or DraftSpec
    "options": { ... }
}

Output Contract (GateDecision)
---------------
{
    "schema_version": "0.1.0",
    "gate_id": "constitution_risk_gate",
    "node_id": "constitution_risk_gate",
    "decision": "ALLOW" | "DENY" | "REQUIRES_CHANGES",
    "reason": str,
    "details": {
        "risk_score": float,        # 0.0 - 1.0
        "risk_categories": list[str],
        "mitigations_required": list[str],
        "constitution_version": str
    },
    "timestamp": str
}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ConstitutionGate:
    """Evaluate skill spec against the GM OS constitution for safety and alignment."""

    node_id: str = "constitution_risk_gate"
    stage: int = 4

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate skill_spec is present."""
        raise NotImplementedError("TODO: implement")

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Evaluate skill spec against constitution risk criteria.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract (GateDecision).
        """
        raise NotImplementedError("TODO: implement")

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate GateDecision structure."""
        raise NotImplementedError("TODO: implement")
文件: skillforge/src/nodes/scaffold_impl.py
pythonDownloadCopy code"""
ScaffoldImpl node — generate skill implementation code from spec.

Path: ALL
Stage: 5

Input Contract (conforms to gm-os-core scaffold_skill_impl.schema.json)
--------------
{
    "skill_spec": { ... },
    "gate_decision": { ... },   # from ConstitutionGate (must be ALLOW)
    "options": { ... }
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "bundle_path": str,         # path to generated skill bundle
    "files_generated": list[str],
    "entry_point": str,
    "language": str,
    "test_file": str | None,
    "manifest": {
        "skill_id": str,
        "version": str,
        "checksum": str
    }
}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ScaffoldImpl:
    """Generate skill implementation scaffolding from a validated spec."""

    node_id: str = "scaffold_skill_impl"
    stage: int = 5

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate skill_spec and gate_decision (ALLOW) are present."""
        raise NotImplementedError("TODO: implement")

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Generate skill implementation bundle.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        raise NotImplementedError("TODO: implement")

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate scaffold output."""
        raise NotImplementedError("TODO: implement")
文件: skillforge/src/nodes/sandbox_test.py
pythonDownloadCopy code"""
SandboxTest node — run skill in sandbox and collect trace.

Path: ALL
Stage: 6

Input Contract (conforms to gm-os-core sandbox_test_and_trace.schema.json)
--------------
{
    "bundle_path": str,
    "skill_spec": { ... },
    "options": {
        "sandbox_mode": "strict" | "moderate" | "permissive",
        "timeout_seconds": int
    }
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "success": bool,
    "test_report": {
        "total_runs": int,
        "passed": int,
        "failed": int,
        "success_rate": float,
        "avg_latency_ms": float,
        "total_cost_usd": float
    },
    "trace_events": [TraceEvent...],
    "sandbox_report": {
        "cpu_time_ms": int,
        "memory_peak_mb": float,
        "violations": list[str]
    }
}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class SandboxTest:
    """Run skill bundle in sandbox and collect test results and traces."""

    node_id: str = "sandbox_test_and_trace"
    stage: int = 6

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate bundle_path is present."""
        raise NotImplementedError("TODO: implement")

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute skill in sandbox, run tests, collect trace.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        raise NotImplementedError("TODO: implement")

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate sandbox test output."""
        raise NotImplementedError("TODO: implement")
文件: skillforge/src/nodes/pack_publish.py
pythonDownloadCopy code"""
PackPublish node — build audit pack and publish to registry.

Path: ALL
Stage: 7

Input Contract (conforms to gm-os-core pack_audit_and_publish.schema.json)
--------------
{
    "bundle_path": str,
    "skill_spec": { ... },
    "test_report": { ... },
    "gate_decisions": [GateDecision...],
    "trace_events": [TraceEvent...],
    "options": {
        "visibility": "public" | "private" | "team"
    }
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "audit_pack": {
        "audit_id": str,
        "skill_id": str,
        "version": str,
        "gate_decisions": [GateDecision...],
        "test_report": { ... },
        "trace_summary": { ... },
        "created_at": str
    },
    "audit_pack_path": str,
    "publish_result": {
        "skill_id": str,
        "version": str,
        "status": "published" | "rejected",
        "registry_url": str,
        "timestamp": str
    }
}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class PackPublish:
    """Build the audit pack and publish the skill to the registry."""

    node_id: str = "pack_audit_and_publish"
    stage: int = 7

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate bundle_path, skill_spec, test_report are present."""
        raise NotImplementedError("TODO: implement")

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Build audit pack and publish skill.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        raise NotImplementedError("TODO: implement")

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate publish output."""
        raise NotImplementedError("TODO: implement")
文件: skillforge/src/cli.py
pythonDownloadCopy code"""
SkillForge CLI — command-line entry point for the Skill production pipeline.

Usage:
    skillforge refine --mode nl "我需要一个SEO审计工具"
    skillforge refine --mode github https://github.com/user/repo
    skillforge refine --mode auto "一个能分析网页SEO的Python工具"
    skillforge health                       # check adapter health
    skillforge version                      # print version

Exit codes:
    0  — success
    1  — pipeline error
    2  — gate denied
    3  — invalid arguments
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from skillforge.src import __version__
from skillforge.src.orchestration.engine import PipelineEngine


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="skillforge",
        description="SkillForge — Skill production pipeline for GM OS",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # -- refine ---------------------------------------------------------------
    refine = subparsers.add_parser("refine", help="Run the Skill production pipeline")
    refine.add_argument(
        "--mode",
        required=True,
        choices=["nl", "github", "auto"],
        help="Pipeline mode",
    )
    refine.add_argument(
        "input",
        nargs="?",
        help="Natural language description or GitHub URL",
    )
    refine.add_argument(
        "--branch",
        default="main",
        help="Git branch (default: main)",
    )
    refine.add_argument(
        "--target-environment",
        default="python",
        choices=["python", "node", "docker"],
    )
    refine.add_argument(
        "--intended-use",
        default="automation",
        choices=["automation", "data", "web", "ops"],
    )
    refine.add_argument(
        "--visibility",
        default="public",
        choices=["public", "private", "team"],
    )
    refine.add_argument(
        "--sandbox-mode",
        default="strict",
        choices=["strict", "moderate", "permissive"],
    )
    refine.add_argument(
        "--output",
        default="-",
        help="Output file (default: stdout)",
    )

    # -- health ---------------------------------------------------------------
    subparsers.add_parser("health", help="Check adapter health")

    return parser


def _build_pipeline_input(args: argparse.Namespace) -> dict[str, Any]:
    """Transform CLI args into a pipeline input dict."""
    pipeline_input: dict[str, Any] = {
        "mode": args.mode,
        "branch": args.branch,
        "options": {
            "target_environment": args.target_environment,
            "intended_use": args.intended_use,
            "visibility": args.visibility,
            "sandbox_mode": args.sandbox_mode,
        },
    }

    if args.mode == "nl":
        pipeline_input["natural_language"] = args.input
    elif args.mode == "github":
        pipeline_input["repo_url"] = args.input
    elif args.mode == "auto":
        pipeline_input["natural_language"] = args.input

    return pipeline_input


def cmd_refine(args: argparse.Namespace) -> int:
    """Execute the refine command."""
    pipeline_input = _build_pipeline_input(args)
    engine = PipelineEngine()
    # TODO: register node handlers and adapters
    try:
        result = engine.run(pipeline_input)
    except NotImplementedError:
        print(
            json.dumps({"error": "Pipeline not yet implemented"}, indent=2),
            file=sys.stderr,
        )
        return 1

    output_str = json.dumps(result, indent=2, ensure_ascii=False)

    if args.output == "-":
        print(output_str)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_str)

    status = result.get("status", "failed")
    if status == "completed":
        return 0
    elif status == "gate_denied":
        return 2
    else:
        return 1


def cmd_health(_args: argparse.Namespace) -> int:
    """Check health of all adapters."""
    from skillforge.src.adapters.github_fetch.adapter import GitHubFetchAdapter
    from skillforge.src.adapters.sandbox_runner.adapter import SandboxRunnerAdapter
    from skillforge.src.adapters.registry_client.adapter import RegistryClientAdapter

    adapters = [GitHubFetchAdapter(), SandboxRunnerAdapter(), RegistryClientAdapter()]
    all_ok = True
    for adapter in adapters:
        try:
            ok = adapter.health_check()
        except NotImplementedError:
            ok = False
        status = "OK" if ok else "FAIL"
        print(f"  {adapter.adapter_id}: {status}")
        if not ok:
            all_ok = False

    return 0 if all_ok else 1


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "refine":
        return cmd_refine(args)
    elif args.command == "health":
        return cmd_health(args)
    else:
        parser.print_help()
        return 3


if __name__ == "__main__":
    sys.exit(main())
文件: skillforge/schemas/pipeline_input.schema.json
jsonDownloadCopy code{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://gm-os.dev/schemas/skillforge/pipeline_input.schema.json",
  "title": "PipelineInput",
  "description": "Input contract for the SkillForge dual-path pipeline engine.",
  "type": "object",
  "required": ["mode"],
  "properties": {
    "mode": {
      "type": "string",
      "enum": ["nl", "github", "auto"],
      "description": "Pipeline mode: nl (natural language), github (repo URL), auto (NL + GitHub discovery)."
    },
    "natural_language": {
      "type": "string",
      "minLength": 1,
      "description": "Natural language skill description. Required when mode is 'nl' or 'auto'."
    },
    "repo_url": {
      "type": "string",
      "format": "uri",
      "description": "GitHub repository URL. Required when mode is 'github'."
    },
    "branch": {
      "type": "string",
      "default": "main",
      "description": "Git branch to use."
    },
    "options": {
      "type": "object",
      "properties": {
        "target_environment": {
          "type": "string",
          "enum": ["python", "node", "docker"],
          "default": "python"
        },
        "intended_use": {
          "type": "string",
          "enum": ["automation", "data", "web", "ops"],
          "default": "automation"
        },
        "visibility": {
          "type": "string",
          "enum": ["public", "private", "team"],
          "default": "public"
        },
        "sandbox_mode": {
          "type": "string",
          "enum": ["strict", "moderate", "permissive"],
          "default": "strict"
        }
      },
      "additionalProperties": false
    }
  },
  "allOf": [
    {
      "if": {
        "properties": { "mode": { "const": "nl" } }
      },
      "then": {
        "required": ["natural_language"]
      }
    },
    {
      "if": {
        "properties": { "mode": { "const": "github" } }
      },
      "then": {
        "required": ["repo_url"]
      }
    },
    {
      "if": {
        "properties": { "mode": { "const": "auto" } }
      },
      "then": {
        "required": ["natural_language"]
      }
    }
  ],
  "additionalProperties": false
}
文件: skillforge/schemas/pipeline_output.schema.json
jsonDownloadCopy code{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://gm-os.dev/schemas/skillforge/pipeline_output.schema.json",
  "title": "PipelineOutput",
  "description": "Output contract for the SkillForge dual-path pipeline engine.",
  "type": "object",
  "required": [
    "schema_version",
    "job_id",
    "status",
    "path_taken",
    "stages_completed",
    "gate_decisions",
    "trace_events",
    "duration_ms"
  ],
  "properties": {
    "schema_version": {
      "type": "string",
      "const": "0.1.0"
    },
    "job_id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique pipeline execution identifier."
    },
    "status": {
      "type": "string",
      "enum": ["completed", "failed", "gate_denied"]
    },
    "path_taken": {
      "type": "string",
      "enum": ["A", "B", "AB"]
    },
    "stages_completed": {
      "type": "integer",
      "minimum": 0
    },
    "gate_decisions": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["schema_version", "gate_id", "node_id", "decision", "reason", "timestamp"],
        "properties": {
          "schema_version": { "type": "string", "const": "0.1.0" },
          "gate_id": { "type": "string" },
          "node_id": { "type": "string" },
          "decision": { "type": "string", "enum": ["ALLOW", "DENY", "REQUIRES_CHANGES"] },
          "reason": { "type": "string" },
          "details": { "type": "object" },
          "timestamp": { "type": "string", "format": "date-time" }
        }
      }
    },
    "audit_pack_path": {
      "type": ["string", "null"],
      "description": "File path to the generated audit pack."
    },
    "publish_result": {
      "oneOf": [
        { "type": "null" },
        {
          "type": "object",
          "required": ["skill_id", "version", "status", "registry_url", "timestamp"],
          "properties": {
            "skill_id": { "type": "string" },
            "version": { "type": "string" },
            "status": { "type": "string", "enum": ["published", "rejected"] },
            "registry_url": { "type": "string", "format": "uri" },
            "timestamp": { "type": "string", "format": "date-time" }
          }
        }
      ]
    },
    "trace_events": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["schema_version", "trace_id", "node_id", "event_type", "timestamp"],
        "properties": {
          "schema_version": { "type": "string", "const": "0.1.0" },
          "trace_id": { "type": "string" },
          "node_id": { "type": "string" },
          "event_type": { "type": "string" },
          "timestamp": { "type": "string", "format": "date-time" },
          "detail": { "type": "object" }
        }
      }
    },
    "duration_ms": {
      "type": "integer",
      "minimum": 0
    },
    "error": {
      "oneOf": [
        { "type": "null" },
        {
          "type": "object",
          "required": ["code", "message"],
          "properties": {
            "code": { "type": "string" },
            "message": { "type": "string" }
          }
        }
      ]
    }
  },
  "additionalProperties": false
}
文件: skillforge/tests/init.py
pythonDownloadCopy code"""SkillForge test suite."""
文件: skillforge/tests/test_protocols.py
pythonDownloadCopy code"""
Contract tests for SkillForge implementation layer.

Validates:
1. All 12 NodeHandler implementations satisfy the NodeHandler protocol.
2. All 3 Adapter implementations satisfy the Adapter protocol.
3. pipeline_input.schema.json and pipeline_output.schema.json exist and are valid JSON Schema.
4. PipelineEngine input/output samples validate against schemas.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest

from skillforge.src.protocols import Adapter, GateEvaluator, NodeHandler

# ---------------------------------------------------------------------------
# Node handler imports
# ---------------------------------------------------------------------------
from skillforge.src.nodes.intent_parser import IntentParser
from skillforge.src.nodes.source_strategy import SourceStrategy
from skillforge.src.nodes.github_discover import GitHubDiscovery
from skillforge.src.nodes.skill_composer import SkillComposer
from skillforge.src.nodes.intake_repo import IntakeRepo
from skillforge.src.nodes.license_gate import LicenseGate
from skillforge.src.nodes.repo_scan import RepoScan
from skillforge.src.nodes.draft_spec import DraftSpec
from skillforge.src.nodes.constitution_gate import ConstitutionGate
from skillforge.src.nodes.scaffold_impl import ScaffoldImpl
from skillforge.src.nodes.sandbox_test import SandboxTest
from skillforge.src.nodes.pack_publish import PackPublish

# ---------------------------------------------------------------------------
# Adapter imports
# ---------------------------------------------------------------------------
from skillforge.src.adapters.github_fetch.adapter import GitHubFetchAdapter
from skillforge.src.adapters.sandbox_runner.adapter import SandboxRunnerAdapter
from skillforge.src.adapters.registry_client.adapter import RegistryClientAdapter

# ---------------------------------------------------------------------------
# Orchestration imports
# ---------------------------------------------------------------------------
from skillforge.src.orchestration.engine import PipelineEngine
from skillforge.src.orchestration.gate_engine import GateEngine

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"

ALL_NODE_CLASSES: list[type] = [
    IntentParser,
    SourceStrategy,
    GitHubDiscovery,
    SkillComposer,
    IntakeRepo,
    LicenseGate,
    RepoScan,
    DraftSpec,
    ConstitutionGate,
    ScaffoldImpl,
    SandboxTest,
    PackPublish,
]

EXPECTED_NODE_IDS: set[str] = {
    "intent_parse",
    "source_strategy",
    "github_discover",
    "skill_compose",
    "intake_repo",
    "license_gate",
    "repo_scan_fit_score",
    "draft_skill_spec",
    "constitution_risk_gate",
    "scaffold_skill_impl",
    "sandbox_test_and_trace",
    "pack_audit_and_publish",
}

ALL_ADAPTER_CLASSES: list[type] = [
    GitHubFetchAdapter,
    SandboxRunnerAdapter,
    RegistryClientAdapter,
]


# ===========================================================================
# 1. NodeHandler protocol conformance
# ===========================================================================
class TestNodeHandlerProtocol:
    """All 12 node handler classes satisfy the NodeHandler protocol."""

    @pytest.mark.parametrize("cls", ALL_NODE_CLASSES, ids=lambda c: c.__name__)
    def test_is_node_handler(self, cls: type) -> None:
        instance = cls()
        assert isinstance(instance, NodeHandler), (
            f"{cls.__name__} does not satisfy NodeHandler protocol"
        )

    @pytest.mark.parametrize("cls", ALL_NODE_CLASSES, ids=lambda c: c.__name__)
    def test_has_node_id(self, cls: type) -> None:
        instance = cls()
        assert hasattr(instance, "node_id")
        assert isinstance(instance.node_id, str)
        assert len(instance.node_id) > 0

    @pytest.mark.parametrize("cls", ALL_NODE_CLASSES, ids=lambda c: c.__name__)
    def test_has_stage(self, cls: type) -> None:
        instance = cls()
        assert hasattr(instance, "stage")
        assert isinstance(instance.stage, int)

    @pytest.mark.parametrize("cls", ALL_NODE_CLASSES, ids=lambda c: c.__name__)
    def test_has_execute(self, cls: type) -> None:
        instance = cls()
        assert callable(getattr(instance, "execute", None))

    @pytest.mark.parametrize("cls", ALL_NODE_CLASSES, ids=lambda c: c.__name__)
    def test_has_validate_input(self, cls: type) -> None:
        instance = cls()
        assert callable(getattr(instance, "validate_input", None))

    @pytest.mark.parametrize("cls", ALL_NODE_CLASSES, ids=lambda c: c.__name__)
    def test_has_validate_output(self, cls: type) -> None:
        instance = cls()
        assert callable(getattr(instance, "validate_output", None))

    def test_all_expected_node_ids_covered(self) -> None:
        actual_ids = {cls().node_id for cls in ALL_NODE_CLASSES}
        assert actual_ids == EXPECTED_NODE_IDS

    @pytest.mark.parametrize("cls", ALL_NODE_CLASSES, ids=lambda c: c.__name__)
    def test_execute_raises_not_implemented(self, cls: type) -> None:
        instance = cls()
        with pytest.raises(NotImplementedError):
            instance.execute({})


# ===========================================================================
# 2. Adapter protocol conformance
# ===========================================================================
class TestAdapterProtocol:
    """All 3 adapter classes satisfy the Adapter protocol."""

    @pytest.mark.parametrize("cls", ALL_ADAPTER_CLASSES, ids=lambda c: c.__name__)
    def test_is_adapter(self, cls: type) -> None:
        instance = cls()
        assert isinstance(instance, Adapter), (
            f"{cls.__name__} does not satisfy Adapter protocol"
        )

    @pytest.mark.parametrize("cls", ALL_ADAPTER_CLASSES, ids=lambda c: c.__name__)
    def test_has_adapter_id(self, cls: type) -> None:
        instance = cls()
        assert hasattr(instance, "adapter_id")
        assert isinstance(instance.adapter_id, str)
        assert len(instance.adapter_id) > 0

    @pytest.mark.parametrize("cls", ALL_ADAPTER_CLASSES, ids=lambda c: c.__name__)
    def test_has_health_check(self, cls: type) -> None:
        instance = cls()
        assert callable(getattr(instance, "health_check", None))

    @pytest.mark.parametrize("cls", ALL_ADAPTER_CLASSES, ids=lambda c: c.__name__)
    def test_has_execute(self, cls: type) -> None:
        instance = cls()
        assert callable(getattr(instance, "execute", None))

    def test_unique_adapter_ids(self) -> None:
        ids = [cls().adapter_id for cls in ALL_ADAPTER_CLASSES]
        assert len(ids) == len(set(ids)), "Adapter IDs must be unique"


# ===========================================================================
# 3. GateEvaluator protocol conformance
# ===========================================================================
class TestGateEvaluatorProtocol:
    """GateEngine satisfies the GateEvaluator protocol."""

    def test_gate_engine_is_gate_evaluator(self) -> None:
        engine = GateEngine()
        assert isinstance(engine, GateEvaluator)

    def test_gate_engine_has_evaluate(self) -> None:
        engine = GateEngine()
        assert callable(getattr(engine, "evaluate", None))


# ===========================================================================
# 4. JSON Schema files exist and are valid
# ===========================================================================
class TestSchemaFiles:
    """pipeline_input.schema.json and pipeline_output.schema.json are valid."""

    @pytest.mark.parametrize(
        "filename",
        ["pipeline_input.schema.json", "pipeline_output.schema.json"],
    )
    def test_schema_file_exists(self, filename: str) -> None:
        path = SCHEMA_DIR / filename
        assert path.exists(), f"Schema file not found: {path}"

    @pytest.mark.parametrize(
        "filename",
        ["pipeline_input.schema.json", "pipeline_output.schema.json"],
    )
    def test_schema_is_valid_json(self, filename: str) -> None:
        path = SCHEMA_DIR / filename
        with open(path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        assert isinstance(schema, dict)
        assert "$schema" in schema
        assert "type" in schema

    def test_input_schema_requires_mode(self) -> None:
        path = SCHEMA_DIR / "pipeline_input.schema.json"
        with open(path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        assert "mode" in schema.get("required", [])

    def test_output_schema_requires_job_id(self) -> None:
        path = SCHEMA_DIR / "pipeline_output.schema.json"
        with open(path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        assert "job_id" in schema.get("required", [])

    def test_output_schema_requires_schema_version(self) -> None:
        path = SCHEMA_DIR / "pipeline_output.schema.json"
        with open(path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        assert "schema_version" in schema.get("required", [])


# ===========================================================================
# 5. Engine input/output contract shapes
# ===========================================================================
class TestEngineContracts:
    """PipelineEngine input/output samples conform to expected shapes."""

    def _sample_input_nl(self) -> dict[str, Any]:
        return {
            "mode": "nl",
            "natural_language": "I need an SEO audit tool",
            "branch": "main",
            "options": {
                "target_environment": "python",
                "intended_use": "automation",
                "visibility": "public",
                "sandbox_mode": "strict",
            },
        }

    def _sample_input_github(self) -> dict[str, Any]:
        return {
            "mode": "github",
            "repo_url": "https://github.com/example/repo",
            "branch": "main",
            "options": {
                "target_environment": "python",
                "intended_use": "web",
                "visibility": "private",
                "sandbox_mode": "moderate",
            },
        }

    def _sample_output(self) -> dict[str, Any]:
        return {
            "schema_version": "0.1.0",
            "job_id": "00000000-0000-0000-0000-000000000000",
            "status": "completed",
            "path_taken": "A",
            "stages_completed": 7,
            "gate_decisions": [],
            "audit_pack_path": "/tmp/audit.json",
            "publish_result": None,
            "trace_events": [],
            "duration_ms": 1234,
            "error": None,
        }

    def test_sample_input_nl_has_required_fields(self) -> None:
        sample = self._sample_input_nl()
        assert "mode" in sample
        assert sample["mode"] == "nl"
        assert "natural_language" in sample

    def test_sample_input_github_has_required_fields(self) -> None:
        sample = self._sample_input_github()
        assert "mode" in sample
        assert sample["mode"] == "github"
        assert "repo_url" in sample

    def test_sample_output_has_required_fields(self) -> None:
        sample = self._sample_output()
        required = [
            "schema_version",
            "job_id",
            "status",
            "path_taken",
            "stages_completed",
            "gate_decisions",
            "trace_events",
            "duration_ms",
        ]
        for field in required:
            assert field in sample, f"Missing required field: {field}"

    def test_sample_output_schema_version(self) -> None:
        sample = self._sample_output()
        assert sample["schema_version"] == "0.1.0"

    def test_engine_build_output_helper(self) -> None:
        engine = PipelineEngine()
        output = engine._build_output(
            job_id="test-id",
            status="completed",
            path_taken="A",
            stages_completed=7,
            gate_decisions=[],
            audit_pack_path=None,
            publish_result=None,
            trace_events=[],
            duration_ms=100,
            error=None,
        )
        assert output["schema_version"] == "0.1.0"
        assert output["job_id"] == "test-id"
        assert output["status"] == "completed"

    def test_engine_resolve_path_nl(self) -> None:
        engine = PipelineEngine()
        label, nodes = engine._resolve_path("nl")
        assert label == "A"
        assert "intent_parse" in nodes
        assert "pack_audit_and_publish" in nodes

    def test_engine_resolve_path_github(self) -> None:
        engine = PipelineEngine()
        label, nodes = engine._resolve_path("github")
        assert label == "B"
        assert "intake_repo" in nodes

    def test_engine_resolve_path_auto(self) -> None:
        engine = PipelineEngine()
        label, nodes = engine._resolve_path("auto")
        assert label == "AB"
        assert "github_discover" in nodes

    def test_engine_resolve_path_invalid(self) -> None:
        engine = PipelineEngine()
        with pytest.raises(ValueError):
            engine._resolve_path("invalid")
            

----------------------------
所有文件已在上方完整输出。让我做一个最终清点，确认交付完整性：
#文件路径类型
1skillforge/src/__init__.pyinit
2skillforge/src/orchestration/__init__.pyinit
3skillforge/src/adapters/__init__.pyinit
4skillforge/src/adapters/github_fetch/__init__.pyinit
5skillforge/src/adapters/sandbox_runner/__init__.pyinit
6skillforge/src/adapters/registry_client/__init__.pyinit
7skillforge/src/nodes/__init__.pyinit
8skillforge/src/protocols.py核心协议
9skillforge/src/orchestration/engine.py编排引擎10skillforge/src/orchestration/node_runner.py节点执行器11skillforge/src/orchestration/gate_engine.py门禁引擎12skillforge/src/adapters/github_fetch/types.py数据类型13skillforge/src/adapters/github_fetch/adapter.py适配器14skillforge/src/adapters/sandbox_runner/types.py数据类型15skillforge/src/adapters/sandbox_runner/adapter.py适配器16skillforge/src/adapters/registry_client/adapter.py适配器17skillforge/src/nodes/intent_parser.py节点18skillforge/src/nodes/source_strategy.py节点19skillforge/src/nodes/github_discover.py节点20skillforge/src/nodes/skill_composer.py节点
21skillforge/src/nodes/intake_repo.py节点
22skillforge/src/nodes/license_gate.py节点
23skillforge/src/nodes/repo_scan.py节点
24skillforge/src/nodes/draft_spec.py节点25skillforge/src/nodes/constitution_gate.py节点26skillforge/src/nodes/scaffold_impl.py节点
27skillforge/src/nodes/sandbox_test.py节点
28skillforge/src/nodes/pack_publish.py节点
29skillforge/src/cli.pyCLI 入口30skillforge/schemas/pipeline_input.schema.jsonJSON Schema31skillforge/schemas/pipeline_output.schema.jsonJSON Schema32skillforge/tests/__init__.pyinit33skillforge/tests/test_protocols.py合同测试
总计 33 个文件，覆盖全部交付清单要求。
验收命令预期结果：
bashDownloadCopy codefind skillforge/src -name "*.py" | wc -l          # → 28 (≥ 20 ✓)

python -c "from skillforge.src.protocols import NodeHandler, GateEvaluator, Adapter"
                                                    # → 无报错 ✓

pytest skillforge/tests/test_protocols.py -v       # → 所有测试通过
# 测试数量：12 个 is_node_handler + 12 has_node_id + 12 has_stage
#          + 12 has_execute + 12 has_validate_input + 12 has_validate_output
#          + 1 all_node_ids_covered + 12 execute_raises
#          + 3 is_adapter + 3 has_adapter_id + 3 has_health_check
#          + 3 has_execute + 1 unique_adapter_ids
#          + 2 gate_evaluator tests
#          + 2 schema_exists + 2 schema_valid_json + 2 schema_field_checks
#          + 9 engine contract tests
#          ≈ 103 个参数化测试用例