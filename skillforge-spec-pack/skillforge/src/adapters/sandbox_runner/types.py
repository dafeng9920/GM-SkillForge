"""Data types for the sandbox runner adapter."""
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
