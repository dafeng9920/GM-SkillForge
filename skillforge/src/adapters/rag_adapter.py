"""
RAG Adapter Interface - 可替换 RAG 适配器接口

提供统一的 RAG 查询接口，支持：
- at_time 固定时间查询（禁止漂移值）
- repo_url + commit_sha + at_time 组合查询
- replay_pointer 输出用于回放
- 可替换实现（mock 与真实实现可切换）

Job ID: L45-D2-ORCH-MINCAP-20260220-002
Skill ID: l45_orchestration_min_capabilities

Usage:
    from adapters.rag_adapter import get_rag_adapter, set_rag_adapter, MockRAGAdapter

    # 使用默认适配器
    adapter = get_rag_adapter()
    result = adapter.query(query="test", at_time="2026-02-20T10:00:00Z")

    # 切换到 mock 适配器
    set_rag_adapter(MockRAGAdapter())
    adapter = get_rag_adapter()
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
import uuid


# ============================================================================
# Constants
# ============================================================================

# Forbidden drift values for at_time
AT_TIME_FORBIDDEN_VALUES = frozenset([
    "latest",
    "now",
    "current",
    "today",
    "yesterday",
    "tomorrow",
    "recent",
    "newest",
])


# ============================================================================
# Error Definitions
# ============================================================================

class RAGErrorCode(str, Enum):
    """RAG adapter error codes."""
    AT_TIME_DRIFT_FORBIDDEN = "RAG-AT-TIME-DRIFT-FORBIDDEN"
    AT_TIME_MISSING = "RAG-AT-TIME-MISSING"
    AT_TIME_INVALID_FORMAT = "RAG-AT-TIME-INVALID-FORMAT"
    QUERY_EMPTY = "RAG-QUERY-EMPTY"
    INTERNAL_ERROR = "RAG-INTERNAL-ERROR"


@dataclass
class RAGQueryError:
    """RAG query error."""
    error_code: RAGErrorCode
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
class RAGQueryResult:
    """RAG query result."""
    query: str
    at_time: str
    results: list[dict[str, Any]]
    replay_pointer: dict[str, Any]
    repo_url: Optional[str] = None
    commit_sha: Optional[str] = None
    total_hits: int = 0
    queried_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "query": self.query,
            "at_time": self.at_time,
            "repo_url": self.repo_url,
            "commit_sha": self.commit_sha,
            "results": self.results,
            "total_hits": self.total_hits,
            "queried_at": self.queried_at,
            "replay_pointer": self.replay_pointer,
        }


@dataclass
class ReplayPointer:
    """Replay pointer for at_time queries."""
    at_time: str
    repo_url: Optional[str] = None
    commit_sha: Optional[str] = None
    run_id: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result = {"at_time": self.at_time}
        if self.repo_url:
            result["repo_url"] = self.repo_url
        if self.commit_sha:
            result["commit_sha"] = self.commit_sha
        if self.run_id:
            result["run_id"] = self.run_id
        return result


# ============================================================================
# Abstract RAG Adapter
# ============================================================================

class RAGAdapter(ABC):
    """
    Abstract RAG Adapter Interface.

    All RAG implementations must implement this interface.
    Supports:
    - at_time fixed query (drift values forbidden)
    - repo_url + commit_sha + at_time combination
    - replay_pointer output
    """

    @abstractmethod
    def query(
        self,
        query: str,
        at_time: str,
        repo_url: Optional[str] = None,
        commit_sha: Optional[str] = None,
        top_k: int = 5,
        **kwargs,
    ) -> RAGQueryResult:
        """
        Execute a RAG query.

        Args:
            query: Query string
            at_time: ISO-8601 timestamp (MUST be fixed, no drift values)
            repo_url: Optional repository URL
            commit_sha: Optional commit SHA
            top_k: Number of results to return
            **kwargs: Additional adapter-specific parameters

        Returns:
            RAGQueryResult with results and replay_pointer

        Raises:
            RAGQueryError if query fails or at_time is invalid
        """
        pass

    def validate_at_time(self, at_time: Optional[str]) -> tuple[bool, Optional[RAGQueryError]]:
        """
        Validate at_time is a fixed timestamp, not a drift value.

        Args:
            at_time: The at_time value to validate

        Returns:
            Tuple of (is_valid, error_if_invalid)
        """
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        # Check if at_time is missing
        if at_time is None:
            return False, RAGQueryError(
                error_code=RAGErrorCode.AT_TIME_MISSING,
                error_message="at_time is required and must be a fixed ISO-8601 timestamp.",
                timestamp=timestamp,
                details={"allowed_values": "ISO-8601 timestamp", "forbidden_values": list(AT_TIME_FORBIDDEN_VALUES)},
            )

        # Check if at_time is a forbidden drift value
        if isinstance(at_time, str) and at_time.lower() in AT_TIME_FORBIDDEN_VALUES:
            return False, RAGQueryError(
                error_code=RAGErrorCode.AT_TIME_DRIFT_FORBIDDEN,
                error_message=f"at_time must be a fixed ISO-8601 timestamp. '{at_time}' is a drift value and is not allowed.",
                timestamp=timestamp,
                details={
                    "provided_value": at_time,
                    "forbidden_values": list(AT_TIME_FORBIDDEN_VALUES),
                    "reason": "Drift values break replayability - queries must be deterministic",
                },
            )

        # Try to parse as ISO-8601
        try:
            if isinstance(at_time, str):
                # Handle 'Z' suffix
                at_time_normalized = at_time.replace("Z", "+00:00")
                datetime.fromisoformat(at_time_normalized)
        except (ValueError, AttributeError) as e:
            return False, RAGQueryError(
                error_code=RAGErrorCode.AT_TIME_INVALID_FORMAT,
                error_message=f"at_time must be a valid ISO-8601 timestamp. Parse error: {str(e)}",
                timestamp=timestamp,
                details={"provided_value": str(at_time), "expected_format": "ISO-8601 (e.g., 2026-02-20T10:00:00Z)"},
            )

        return True, None


# ============================================================================
# Mock RAG Adapter (for testing)
# ============================================================================

class MockRAGAdapter(RAGAdapter):
    """
    Mock RAG Adapter for testing.

    Returns predictable results without external dependencies.
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
        repo_url: Optional[str] = None,
        commit_sha: Optional[str] = None,
        top_k: int = 5,
        **kwargs,
    ) -> RAGQueryResult:
        """Execute mock RAG query."""
        # Validate at_time first
        is_valid, error = self.validate_at_time(at_time)
        if not is_valid:
            raise ValueError(f"at_time validation failed: {error.error_message}")

        # Validate query
        if not query or not query.strip():
            timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            raise ValueError(RAGQueryError(
                error_code=RAGErrorCode.QUERY_EMPTY,
                error_message="Query string cannot be empty.",
                timestamp=timestamp,
            ).error_message)

        self._call_count += 1
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        run_id = f"RAG-MOCK-{uuid.uuid4().hex[:8].upper()}"

        # Generate mock results
        results = [
            {
                "rank": i + 1,
                "content": f"Mock result {i + 1} for query: '{query[:50]}{'...' if len(query) > 50 else ''}'",
                "score": round(0.95 - (i * 0.05), 2),
                "source": f"doc://{repo_url or 'default'}/chunk_{i + 1}" if repo_url else f"doc://mock/chunk_{i + 1}",
                "metadata": {
                    "commit_sha": commit_sha,
                    "retrieved_at": at_time,
                },
            }
            for i in range(min(top_k, 10))
        ]

        # Build replay pointer
        replay_pointer = ReplayPointer(
            at_time=at_time,
            repo_url=repo_url,
            commit_sha=commit_sha,
            run_id=run_id,
        )

        return RAGQueryResult(
            query=query,
            at_time=at_time,
            repo_url=repo_url,
            commit_sha=commit_sha,
            results=results,
            total_hits=len(results),
            queried_at=timestamp,
            replay_pointer=replay_pointer.to_dict(),
        )


# ============================================================================
# Global Adapter Registry
# ============================================================================

# Default to mock adapter
_default_adapter: RAGAdapter = MockRAGAdapter()


def get_rag_adapter() -> RAGAdapter:
    """Get the current RAG adapter instance."""
    return _default_adapter


def set_rag_adapter(adapter: RAGAdapter) -> None:
    """Set the global RAG adapter instance."""
    global _default_adapter
    _default_adapter = adapter


def reset_rag_adapter() -> None:
    """Reset to default mock adapter."""
    global _default_adapter
    _default_adapter = MockRAGAdapter()
