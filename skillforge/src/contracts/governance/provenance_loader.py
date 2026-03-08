"""
Provenance Loader - repro_env 指纹读取与注入

SEEDS-P1-9: Repro Env 指纹占位
- 落盘 provenance 模板并保证 GateDecision 引用
- 提供 provenance.repro_env 的读取与注入功能

Contract: docs/SEEDS_v0.md P1-9
Job ID: L45-D5-SEEDS-P1-20260220-005

Usage:
    from contracts.governance.provenance_loader import (
        ProvenanceLoader,
        ProvenanceData,
        load_provenance,
        inject_provenance_to_gate_decision,
        get_repro_env,
    )

    # 加载 provenance
    provenance = load_provenance()

    # 获取 repro_env
    repro_env = get_repro_env()

    # 注入到 GateDecision
    gate_decision = inject_provenance_to_gate_decision(gate_decision_dict, provenance)

Constraints:
    - GateDecision / 报告输出必须可包含 provenance.repro_env
    - 可先占位，但字段结构必须稳定
    - 读取失败必须 fail-closed
"""
from __future__ import annotations

import json
import os
import platform
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

# Default values
DEFAULT_PYTHON_VERSION = "3.11"
DEFAULT_RULESET_REVISION = "v1"
DEFAULT_TOOL_VERSION = "0.0.1"
DENY_ERROR_CODE = "PROVENANCE_LOAD_FAILED"


@dataclass
class ReproEnv:
    """
    Reproducibility Environment 指纹。

    字段结构必须稳定，值可占位。
    """
    python_version: str = DEFAULT_PYTHON_VERSION
    deps_lock_hash: str = "PLACEHOLDER"
    os: str = "PLACEHOLDER"
    tool_versions: Dict[str, str] = field(default_factory=lambda: {"gm_skillforge": DEFAULT_TOOL_VERSION})

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "python_version": self.python_version,
            "deps_lock_hash": self.deps_lock_hash,
            "os": self.os,
            "tool_versions": self.tool_versions.copy(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReproEnv":
        """Create from dictionary."""
        return cls(
            python_version=data.get("python_version", DEFAULT_PYTHON_VERSION),
            deps_lock_hash=data.get("deps_lock_hash", "PLACEHOLDER"),
            os=data.get("os", "PLACEHOLDER"),
            tool_versions=data.get("tool_versions", {"gm_skillforge": DEFAULT_TOOL_VERSION}),
        )


@dataclass
class ProvenanceSource:
    """Source information for provenance."""
    repo_url: str = "PLACEHOLDER"
    commit_sha: str = "PLACEHOLDER"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "repo_url": self.repo_url,
            "commit_sha": self.commit_sha,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProvenanceSource":
        """Create from dictionary."""
        return cls(
            repo_url=data.get("repo_url", "PLACEHOLDER"),
            commit_sha=data.get("commit_sha", "PLACEHOLDER"),
        )


@dataclass
class ProvenanceData:
    """
    完整的 Provenance 数据结构。

    符合 SEEDS_v0.md P1-9 的 templates/provenance.json 格式。
    """
    captured_at: str
    source: ProvenanceSource
    ruleset_revision: str
    repro_env: ReproEnv

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "captured_at": self.captured_at,
            "source": self.source.to_dict(),
            "ruleset_revision": self.ruleset_revision,
            "repro_env": self.repro_env.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProvenanceData":
        """Create from dictionary."""
        return cls(
            captured_at=data.get("captured_at", ""),
            source=ProvenanceSource.from_dict(data.get("source", {})),
            ruleset_revision=data.get("ruleset_revision", DEFAULT_RULESET_REVISION),
            repro_env=ReproEnv.from_dict(data.get("repro_env", {})),
        )


class ProvenanceLoadError(Exception):
    """
    Provenance 加载失败异常。

    读取失败必须 fail-closed，抛出此异常。
    """
    code: str = DENY_ERROR_CODE

    def __init__(self, message: str, cause: Optional[Exception] = None):
        self.message = message
        self.cause = cause
        super().__init__(self.message)


class ProvenanceLoader:
    """
    Provenance 加载器。

    职责：
    1. 从 templates/provenance.json 加载模板
    2. 捕获当前环境指纹
    3. 提供 repro_env 字段供 GateDecision 引用

    Fail-closed: 读取失败时抛出 ProvenanceLoadError
    """

    def __init__(self, template_path: Optional[Path] = None):
        """
        Initialize ProvenanceLoader.

        Args:
            template_path: Optional path to provenance template.
                          If not provided, searches default locations.
        """
        self.template_path = template_path or self._find_template_path()
        self._cached_provenance: Optional[ProvenanceData] = None

    def _find_template_path(self) -> Optional[Path]:
        """
        Find provenance template in standard locations.

        Search order:
        1. PROVENANCE_TEMPLATE_PATH environment variable
        2. templates/provenance.json (relative to project root)
        3. None (will use defaults)
        """
        # Try environment variable first
        env_path = os.environ.get("PROVENANCE_TEMPLATE_PATH")
        if env_path:
            path = Path(env_path)
            if path.exists():
                return path

        # Try default location (project root / templates / provenance.json)
        current = Path(__file__).resolve()
        for parent in current.parents:
            candidate = parent / "templates" / "provenance.json"
            if candidate.exists():
                return candidate

        return None

    def _capture_current_env(self) -> ReproEnv:
        """
        Capture current environment fingerprint.

        Returns:
            ReproEnv with current system information.
        """
        return ReproEnv(
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}",
            deps_lock_hash="PLACEHOLDER",  # To be filled during pack_audit
            os=f"{platform.system()} {platform.release()}",
            tool_versions={"gm_skillforge": DEFAULT_TOOL_VERSION},
        )

    def load(self, force_reload: bool = False) -> ProvenanceData:
        """
        Load provenance from template or create from current environment.

        Args:
            force_reload: Force reload even if cached.

        Returns:
            ProvenanceData instance.

        Raises:
            ProvenanceLoadError: If template exists but is invalid.
        """
        if self._cached_provenance and not force_reload:
            return self._cached_provenance

        provenance: Optional[ProvenanceData] = None

        if self.template_path and self.template_path.exists():
            # Load from template file
            try:
                with open(self.template_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                provenance = ProvenanceData.from_dict(data)
            except json.JSONDecodeError as e:
                raise ProvenanceLoadError(
                    f"Invalid JSON in provenance template: {self.template_path}",
                    cause=e,
                )
            except Exception as e:
                raise ProvenanceLoadError(
                    f"Failed to load provenance template: {self.template_path}",
                    cause=e,
                )

        if provenance is None:
            # Create from current environment
            now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            provenance = ProvenanceData(
                captured_at=now,
                source=ProvenanceSource(),
                ruleset_revision=DEFAULT_RULESET_REVISION,
                repro_env=self._capture_current_env(),
            )

        self._cached_provenance = provenance
        return provenance

    def get_repro_env(self) -> Dict[str, Any]:
        """
        Get repro_env dictionary for GateDecision.

        Returns:
            repro_env dictionary.

        Raises:
            ProvenanceLoadError: If provenance cannot be loaded.
        """
        provenance = self.load()
        return provenance.repro_env.to_dict()

    def get_full_provenance(self) -> Dict[str, Any]:
        """
        Get full provenance dictionary.

        Returns:
            Full provenance dictionary.

        Raises:
            ProvenanceLoadError: If provenance cannot be loaded.
        """
        provenance = self.load()
        return provenance.to_dict()


# Global loader instance (lazy initialized)
_loader: Optional[ProvenanceLoader] = None


def _get_loader() -> ProvenanceLoader:
    """Get or create the global loader instance."""
    global _loader
    if _loader is None:
        _loader = ProvenanceLoader()
    return _loader


def reset_loader() -> None:
    """Reset the global loader instance (useful for testing)."""
    global _loader
    _loader = None


def load_provenance(force_reload: bool = False) -> ProvenanceData:
    """
    Load provenance data.

    Convenience function using the global loader.

    Args:
        force_reload: Force reload even if cached.

    Returns:
        ProvenanceData instance.
    """
    return _get_loader().load(force_reload=force_reload)


def get_repro_env() -> Dict[str, Any]:
    """
    Get repro_env dictionary.

    Convenience function using the global loader.

    Returns:
        repro_env dictionary with fields:
        - python_version
        - deps_lock_hash
        - os
        - tool_versions
    """
    return _get_loader().get_repro_env()


def get_full_provenance() -> Dict[str, Any]:
    """
    Get full provenance dictionary.

    Convenience function using the global loader.

    Returns:
        Full provenance dictionary with fields:
        - captured_at
        - source
        - ruleset_revision
        - repro_env
    """
    return _get_loader().get_full_provenance()


def inject_provenance_to_gate_decision(
    gate_decision: Dict[str, Any],
    provenance: Optional[ProvenanceData] = None,
) -> Dict[str, Any]:
    """
    Inject provenance into GateDecision.

    Ensures GateDecision contains provenance.repro_env field.

    Args:
        gate_decision: The GateDecision dictionary to inject into.
        provenance: Optional ProvenanceData to inject.
                   If not provided, loads from default location.

    Returns:
        Updated GateDecision dictionary with provenance field.

    Example:
        gate_decision = {
            "job_id": "JOB-001",
            "gate_decision": "ALLOW",
            "ruleset_revision": "v1",
        }
        result = inject_provenance_to_gate_decision(gate_decision)
        # result now contains "provenance" field with "repro_env"
    """
    if provenance is None:
        provenance = load_provenance()

    # Create a copy to avoid mutating the original
    result = gate_decision.copy()

    # Ensure provenance field exists
    if "provenance" not in result:
        result["provenance"] = {}

    # Merge with loaded provenance (existing values take precedence)
    loaded_provenance = provenance.to_dict()
    for key, value in loaded_provenance.items():
        if key not in result["provenance"]:
            result["provenance"][key] = value

    # Ensure repro_env field exists (required by SEEDS_v0.md DoD)
    if "repro_env" not in result["provenance"]:
        result["provenance"]["repro_env"] = provenance.repro_env.to_dict()

    return result


def create_provenance_for_job(
    job_id: str,
    repo_url: str = "PLACEHOLDER",
    commit_sha: str = "PLACEHOLDER",
    ruleset_revision: str = DEFAULT_RULESET_REVISION,
) -> ProvenanceData:
    """
    Create provenance for a specific job.

    Factory function for creating job-specific provenance.

    Args:
        job_id: The job identifier.
        repo_url: Repository URL.
        commit_sha: Commit SHA.
        ruleset_revision: Ruleset revision.

    Returns:
        ProvenanceData instance.
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    loader = _get_loader()
    loader.load()  # Ensure template is loaded

    return ProvenanceData(
        captured_at=now,
        source=ProvenanceSource(repo_url=repo_url, commit_sha=commit_sha),
        ruleset_revision=ruleset_revision,
        repro_env=loader._capture_current_env(),
    )


# Export public API
__all__ = [
    "ProvenanceLoader",
    "ProvenanceData",
    "ProvenanceSource",
    "ReproEnv",
    "ProvenanceLoadError",
    "load_provenance",
    "get_repro_env",
    "get_full_provenance",
    "inject_provenance_to_gate_decision",
    "create_provenance_for_job",
    "reset_loader",
    "DENY_ERROR_CODE",
]
