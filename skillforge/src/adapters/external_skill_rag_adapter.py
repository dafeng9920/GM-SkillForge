"""
External Skill RAG Adapter - 外部 Skill 证据检索治理适配器

提供外部 Skill 的 RAG 查询接口，支持：
- at_time 固定时间查询（禁止漂移值，fail-closed）
- external_skill_ref + repo_url + commit_sha + at_time 组合查询
- replay_pointer 输出用于回放验证
- 完整的可复核证据链

Job ID: L45-D3-EXT-SKILL-GOV-20260220-003
Skill ID: l45_external_skill_governance_batch1
Task ID: T14
Executor: vs--cc2

Usage:
    from adapters.external_skill_rag_adapter import (
        get_external_skill_rag_adapter,
        set_external_skill_rag_adapter,
        ExternalSkillRAGAdapter,
        MockExternalSkillRAGAdapter,
    )

    # 使用默认适配器
    adapter = get_external_skill_rag_adapter()
    result = adapter.query(
        query="evidence for skill validation",
        at_time="2026-02-20T10:00:00Z",
        external_skill_ref="external/skill@v1.0.0",
        repo_url="https://github.com/example/repo",
        commit_sha="abc123",
    )

    # 切换到 mock 适配器
    set_external_skill_rag_adapter(MockExternalSkillRAGAdapter())
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
import hashlib
import uuid


# ============================================================================
# Constants (与全局常量一致)
# ============================================================================

JOB_ID = "L45-D3-EXT-SKILL-GOV-20260220-003"
SKILL_ID = "l45_external_skill_governance_batch1"

# Fixed inputs required for external skill governance
FIXED_INPUTS = frozenset([
    "repo_url",
    "commit_sha",
    "at_time",
    "external_skill_ref",
])

# Forbidden drift values for at_time (与 T9 策略一致)
AT_TIME_FORBIDDEN_VALUES = frozenset([
    "latest",
    "now",
    "current",
    "today",
    "yesterday",
    "tomorrow",
    "recent",
    "newest",
    "current_time",
    "utc_now",
    "sys_time",
])


# ============================================================================
# Error Definitions
# ============================================================================

class ExternalSkillRAGErrorCode(str, Enum):
    """External Skill RAG adapter error codes."""
    AT_TIME_MISSING = "EXT-RAG-AT-TIME-MISSING"
    AT_TIME_DRIFT_FORBIDDEN = "EXT-RAG-AT-TIME-DRIFT-FORBIDDEN"
    AT_TIME_INVALID_FORMAT = "EXT-RAG-AT-TIME-INVALID-FORMAT"
    EXTERNAL_SKILL_REF_MISSING = "EXT-RAG-SKILL-REF-MISSING"
    REPO_URL_MISSING = "EXT-RAG-REPO-URL-MISSING"
    COMMIT_SHA_MISSING = "EXT-RAG-COMMIT-SHA-MISSING"
    QUERY_EMPTY = "EXT-RAG-QUERY-EMPTY"
    REPLAY_POINTER_GENERATION_FAILED = "EXT-RAG-REPLAY-POINTER-FAILED"
    INTERNAL_ERROR = "EXT-RAG-INTERNAL-ERROR"


@dataclass
class ExternalSkillRAGError:
    """External Skill RAG query error."""
    error_code: ExternalSkillRAGErrorCode
    error_message: str
    timestamp: str
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "error_code": self.error_code.value,
            "error_message": self.error_message,
            "timestamp": self.timestamp,
            "details": self.details,
        }


# ============================================================================
# Result Types
# ============================================================================

@dataclass
class ExternalSkillReplayPointer:
    """
    Replay pointer for external skill queries.

    必须包含完整可复核信息：
    - at_time: 查询时间点
    - external_skill_ref: 外部 Skill 引用
    - repo_url: 仓库 URL
    - commit_sha: 提交 SHA
    - run_id: 运行追踪 ID
    - content_hash: 内容哈希（用于验证一致性）
    """
    at_time: str
    external_skill_ref: str
    repo_url: str
    commit_sha: str
    run_id: str
    content_hash: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "at_time": self.at_time,
            "external_skill_ref": self.external_skill_ref,
            "repo_url": self.repo_url,
            "commit_sha": self.commit_sha,
            "run_id": self.run_id,
            "content_hash": self.content_hash,
        }

    def verify_consistency(self, at_time: str) -> bool:
        """Verify that replay_pointer.at_time matches input at_time."""
        return self.at_time == at_time


@dataclass
class ExternalSkillRAGResult:
    """
    External Skill RAG query result.

    必须包含：
    - query: 原始查询
    - at_time: 查询时间点
    - results: 检索结果列表
    - replay_pointer: 回放指针（必须存在）
    """
    query: str
    at_time: str
    external_skill_ref: str
    repo_url: str
    commit_sha: str
    results: list[dict[str, Any]]
    replay_pointer: ExternalSkillReplayPointer
    total_hits: int = 0
    queried_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    job_id: str = JOB_ID

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "query": self.query,
            "at_time": self.at_time,
            "external_skill_ref": self.external_skill_ref,
            "repo_url": self.repo_url,
            "commit_sha": self.commit_sha,
            "results": self.results,
            "total_hits": self.total_hits,
            "queried_at": self.queried_at,
            "replay_pointer": self.replay_pointer.to_dict(),
            "job_id": self.job_id,
        }

    def verify_replay_consistency(self) -> dict[str, Any]:
        """Verify replay_pointer consistency with query inputs."""
        return {
            "at_time_consistent": self.replay_pointer.at_time == self.at_time,
            "repo_url_consistent": self.replay_pointer.repo_url == self.repo_url,
            "commit_sha_consistent": self.replay_pointer.commit_sha == self.commit_sha,
            "external_skill_ref_consistent": self.replay_pointer.external_skill_ref == self.external_skill_ref,
        }


# ============================================================================
# Abstract External Skill RAG Adapter
# ============================================================================

class ExternalSkillRAGAdapter(ABC):
    """
    Abstract External Skill RAG Adapter Interface.

    All external skill RAG implementations must implement this interface.
    Supports:
    - at_time fixed query (drift values forbidden, fail-closed)
    - external_skill_ref + repo_url + commit_sha + at_time combination
    - replay_pointer output (required for all successful responses)
    """

    @abstractmethod
    def query(
        self,
        query: str,
        at_time: str,
        external_skill_ref: str,
        repo_url: str,
        commit_sha: str,
        top_k: int = 5,
        **kwargs,
    ) -> ExternalSkillRAGResult:
        """
        Execute an external skill RAG query.

        Args:
            query: Query string
            at_time: ISO-8601 timestamp (MUST be fixed, no drift values)
            external_skill_ref: External skill reference (e.g., "external/skill@v1.0.0")
            repo_url: Repository URL (required for governance)
            commit_sha: Commit SHA (required for governance)
            top_k: Number of results to return
            **kwargs: Additional adapter-specific parameters

        Returns:
            ExternalSkillRAGResult with results and replay_pointer

        Raises:
            ExternalSkillRAGError if query fails or validation fails
        """
        pass

    def validate_at_time(self, at_time: Optional[str]) -> tuple[bool, Optional[ExternalSkillRAGError]]:
        """
        Validate at_time is a fixed timestamp, not a drift value.

        Fail-closed: at_time must be a valid ISO-8601 timestamp.
        Drift values (latest, now, today, etc.) are forbidden.

        Args:
            at_time: The at_time value to validate

        Returns:
            Tuple of (is_valid, error_if_invalid)
        """
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        # Check if at_time is missing (fail-closed)
        if at_time is None or at_time == "":
            return False, ExternalSkillRAGError(
                error_code=ExternalSkillRAGErrorCode.AT_TIME_MISSING,
                error_message="at_time is required for external skill queries. It must be a fixed ISO-8601 timestamp.",
                timestamp=timestamp,
                details={
                    "allowed_values": "ISO-8601 timestamp (e.g., 2026-02-20T10:00:00Z)",
                    "forbidden_values": list(AT_TIME_FORBIDDEN_VALUES),
                    "reason": "at_time is required for governance traceability",
                },
            )

        # Check if at_time is a forbidden drift value (fail-closed)
        if isinstance(at_time, str) and at_time.lower() in AT_TIME_FORBIDDEN_VALUES:
            return False, ExternalSkillRAGError(
                error_code=ExternalSkillRAGErrorCode.AT_TIME_DRIFT_FORBIDDEN,
                error_message=f"at_time must be a fixed ISO-8601 timestamp. '{at_time}' is a drift value and is forbidden.",
                timestamp=timestamp,
                details={
                    "provided_value": at_time,
                    "forbidden_values": list(AT_TIME_FORBIDDEN_VALUES),
                    "reason": "Drift values break replayability and governance traceability. Queries must be deterministic.",
                },
            )

        # Try to parse as ISO-8601
        try:
            if isinstance(at_time, str):
                # Handle 'Z' suffix
                at_time_normalized = at_time.replace("Z", "+00:00")
                datetime.fromisoformat(at_time_normalized)
        except (ValueError, AttributeError) as e:
            return False, ExternalSkillRAGError(
                error_code=ExternalSkillRAGErrorCode.AT_TIME_INVALID_FORMAT,
                error_message=f"at_time must be a valid ISO-8601 timestamp. Parse error: {str(e)}",
                timestamp=timestamp,
                details={
                    "provided_value": str(at_time),
                    "expected_format": "ISO-8601 (e.g., 2026-02-20T10:00:00Z)",
                },
            )

        return True, None

    def validate_required_inputs(
        self,
        external_skill_ref: Optional[str],
        repo_url: Optional[str],
        commit_sha: Optional[str],
    ) -> tuple[bool, Optional[ExternalSkillRAGError]]:
        """
        Validate all required governance inputs are present.

        Args:
            external_skill_ref: External skill reference
            repo_url: Repository URL
            commit_sha: Commit SHA

        Returns:
            Tuple of (is_valid, error_if_invalid)
        """
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        if not external_skill_ref:
            return False, ExternalSkillRAGError(
                error_code=ExternalSkillRAGErrorCode.EXTERNAL_SKILL_REF_MISSING,
                error_message="external_skill_ref is required for external skill governance queries.",
                timestamp=timestamp,
                details={"required_inputs": list(FIXED_INPUTS)},
            )

        if not repo_url:
            return False, ExternalSkillRAGError(
                error_code=ExternalSkillRAGErrorCode.REPO_URL_MISSING,
                error_message="repo_url is required for external skill governance queries.",
                timestamp=timestamp,
                details={"required_inputs": list(FIXED_INPUTS)},
            )

        if not commit_sha:
            return False, ExternalSkillRAGError(
                error_code=ExternalSkillRAGErrorCode.COMMIT_SHA_MISSING,
                error_message="commit_sha is required for external skill governance queries.",
                timestamp=timestamp,
                details={"required_inputs": list(FIXED_INPUTS)},
            )

        return True, None

    def _generate_content_hash(
        self,
        query: str,
        at_time: str,
        external_skill_ref: str,
        repo_url: str,
        commit_sha: str,
    ) -> str:
        """Generate content hash for replay verification."""
        content = f"{query}|{at_time}|{external_skill_ref}|{repo_url}|{commit_sha}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()


# ============================================================================
# Mock External Skill RAG Adapter (for testing)
# ============================================================================

class MockExternalSkillRAGAdapter(ExternalSkillRAGAdapter):
    """
    Mock External Skill RAG Adapter for testing.

    Returns predictable results without external dependencies.
    Always includes replay_pointer in successful responses.
    """

    def __init__(self, delay_ms: int = 0):
        """
        Initialize mock adapter.

        Args:
            delay_ms: Optional simulated delay in milliseconds
        """
        self.delay_ms = delay_ms
        self._call_count = 0

    def query(
        self,
        query: str,
        at_time: str,
        external_skill_ref: str,
        repo_url: str,
        commit_sha: str,
        top_k: int = 5,
        **kwargs,
    ) -> ExternalSkillRAGResult:
        """Execute mock external skill RAG query."""
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        # Validate at_time first (fail-closed)
        is_valid, error = self.validate_at_time(at_time)
        if not is_valid:
            raise ValueError(f"at_time validation failed: {error.error_message}")

        # Validate required inputs
        is_valid, error = self.validate_required_inputs(external_skill_ref, repo_url, commit_sha)
        if not is_valid:
            raise ValueError(f"Input validation failed: {error.error_message}")

        # Validate query
        if not query or not query.strip():
            raise ValueError(ExternalSkillRAGError(
                error_code=ExternalSkillRAGErrorCode.QUERY_EMPTY,
                error_message="Query string cannot be empty.",
                timestamp=timestamp,
            ).error_message)

        self._call_count += 1
        run_id = f"EXT-RAG-{uuid.uuid4().hex[:8].upper()}"

        # Generate content hash for replay verification
        content_hash = self._generate_content_hash(
            query=query,
            at_time=at_time,
            external_skill_ref=external_skill_ref,
            repo_url=repo_url,
            commit_sha=commit_sha,
        )

        # Generate mock results
        results = [
            {
                "rank": i + 1,
                "content": f"External skill evidence {i + 1} for query: '{query[:50]}{'...' if len(query) > 50 else ''}'",
                "score": round(0.95 - (i * 0.05), 2),
                "source": f"external-skill://{external_skill_ref}/evidence_{i + 1}",
                "metadata": {
                    "external_skill_ref": external_skill_ref,
                    "repo_url": repo_url,
                    "commit_sha": commit_sha,
                    "retrieved_at": at_time,
                    "evidence_type": "governance",
                },
            }
            for i in range(min(top_k, 10))
        ]

        # Build replay pointer (required)
        replay_pointer = ExternalSkillReplayPointer(
            at_time=at_time,
            external_skill_ref=external_skill_ref,
            repo_url=repo_url,
            commit_sha=commit_sha,
            run_id=run_id,
            content_hash=content_hash,
        )

        return ExternalSkillRAGResult(
            query=query,
            at_time=at_time,
            external_skill_ref=external_skill_ref,
            repo_url=repo_url,
            commit_sha=commit_sha,
            results=results,
            total_hits=len(results),
            queried_at=timestamp,
            replay_pointer=replay_pointer,
        )


# ============================================================================
# Global Adapter Registry
# ============================================================================

# Default to mock adapter
_default_external_skill_adapter: ExternalSkillRAGAdapter = MockExternalSkillRAGAdapter()


def get_external_skill_rag_adapter() -> ExternalSkillRAGAdapter:
    """Get the current external skill RAG adapter instance."""
    return _default_external_skill_adapter


def set_external_skill_rag_adapter(adapter: ExternalSkillRAGAdapter) -> None:
    """Set the global external skill RAG adapter instance."""
    global _default_external_skill_adapter
    _default_external_skill_adapter = adapter


def reset_external_skill_rag_adapter() -> None:
    """Reset to default mock adapter."""
    global _default_external_skill_adapter
    _default_external_skill_adapter = MockExternalSkillRAGAdapter()


# ============================================================================
# Convenience Query Function
# ============================================================================

def query_external_skill_evidence(
    query: str,
    at_time: str,
    external_skill_ref: str,
    repo_url: str,
    commit_sha: str,
    top_k: int = 5,
) -> dict[str, Any]:
    """
    Convenience function to query external skill evidence.

    This function wraps the adapter and returns a dict response.

    Returns:
        dict with either 'result' or 'error' key.
    """
    adapter = get_external_skill_rag_adapter()
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    try:
        # Validate at_time
        is_valid, error = adapter.validate_at_time(at_time)
        if not is_valid:
            return {
                "ok": False,
                "error": error.to_dict() if error else None,
            }

        # Validate required inputs
        is_valid, error = adapter.validate_required_inputs(external_skill_ref, repo_url, commit_sha)
        if not is_valid:
            return {
                "ok": False,
                "error": error.to_dict() if error else None,
            }

        # Execute query
        result = adapter.query(
            query=query,
            at_time=at_time,
            external_skill_ref=external_skill_ref,
            repo_url=repo_url,
            commit_sha=commit_sha,
            top_k=top_k,
        )

        # Verify replay consistency
        consistency = result.verify_replay_consistency()
        if not all(consistency.values()):
            return {
                "ok": False,
                "error": ExternalSkillRAGError(
                    error_code=ExternalSkillRAGErrorCode.REPLAY_POINTER_GENERATION_FAILED,
                    error_message="Replay pointer consistency check failed.",
                    timestamp=timestamp,
                    details={"consistency_check": consistency},
                ).to_dict(),
            }

        return {
            "ok": True,
            "result": result.to_dict(),
        }

    except Exception as e:
        return {
            "ok": False,
            "error": ExternalSkillRAGError(
                error_code=ExternalSkillRAGErrorCode.INTERNAL_ERROR,
                error_message=f"Internal error during query: {str(e)}",
                timestamp=timestamp,
                details={"exception": str(e)},
            ).to_dict(),
        }
