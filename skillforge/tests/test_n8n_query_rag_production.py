"""
Production Tests for n8n query_rag endpoint.

Tests the production-ready query_rag implementation including:
- at_time fixed input validation (drift values forbidden)
- replay_pointer output
- repo_url + commit_sha + at_time combination queries
- Swappable adapter (mock vs real)

Job ID: L45-D2-ORCH-MINCAP-20260220-002
Skill ID: l45_orchestration_min_capabilities
"""
from __future__ import annotations

import pytest
from datetime import datetime, timezone

# Test fixtures
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from adapters.rag_adapter import (
    MockRAGAdapter,
    get_rag_adapter,
    set_rag_adapter,
    reset_rag_adapter,
    RAGQueryResult,
    AT_TIME_FORBIDDEN_VALUES,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def reset_adapter():
    """Reset adapter before and after each test."""
    reset_rag_adapter()
    yield
    reset_rag_adapter()


# ============================================================================
# RAG Adapter Tests
# ============================================================================

class TestRAGAdapterAtTimeValidation:
    """Tests for at_time validation in RAG adapter."""

    def test_valid_iso8601_at_time_accepted(self):
        """Valid ISO-8601 timestamps should be accepted."""
        adapter = MockRAGAdapter()
        valid_at_time = "2026-02-20T10:00:00Z"

        result = adapter.query(
            query="test query",
            at_time=valid_at_time,
        )

        assert result.at_time == valid_at_time
        assert result.query == "test query"

    def test_valid_iso8601_with_timezone_accepted(self):
        """Valid ISO-8601 with timezone should be accepted."""
        adapter = MockRAGAdapter()
        valid_at_time = "2026-02-20T10:00:00+00:00"

        result = adapter.query(
            query="test query",
            at_time=valid_at_time,
        )

        assert result.at_time == valid_at_time

    @pytest.mark.parametrize("drift_value", list(AT_TIME_FORBIDDEN_VALUES))
    def test_drift_values_rejected(self, drift_value):
        """All drift values should be rejected."""
        adapter = MockRAGAdapter()

        with pytest.raises(ValueError) as exc_info:
            adapter.query(
                query="test query",
                at_time=drift_value,
            )

        assert "drift" in str(exc_info.value).lower() or "forbidden" in str(exc_info.value).lower()

    def test_empty_at_time_rejected(self):
        """Empty at_time should be rejected."""
        adapter = MockRAGAdapter()

        with pytest.raises(ValueError):
            adapter.query(
                query="test query",
                at_time="",
            )

    def test_none_at_time_rejected(self):
        """None at_time should be rejected."""
        adapter = MockRAGAdapter()

        with pytest.raises(ValueError):
            adapter.query(
                query="test query",
                at_time=None,
            )


class TestRAGAdapterReplayPointer:
    """Tests for replay_pointer output."""

    def test_replay_pointer_included(self):
        """Response must include replay_pointer."""
        adapter = MockRAGAdapter()

        result = adapter.query(
            query="test query",
            at_time="2026-02-20T10:00:00Z",
        )

        assert result.replay_pointer is not None
        assert isinstance(result.replay_pointer, dict)

    def test_replay_pointer_contains_at_time(self):
        """replay_pointer must contain at_time."""
        adapter = MockRAGAdapter()
        at_time = "2026-02-20T10:00:00Z"

        result = adapter.query(
            query="test query",
            at_time=at_time,
        )

        assert result.replay_pointer.get("at_time") == at_time

    def test_replay_pointer_contains_repo_url(self):
        """replay_pointer should include repo_url when provided."""
        adapter = MockRAGAdapter()
        repo_url = "https://github.com/test/repo"

        result = adapter.query(
            query="test query",
            at_time="2026-02-20T10:00:00Z",
            repo_url=repo_url,
        )

        assert result.replay_pointer.get("repo_url") == repo_url

    def test_replay_pointer_contains_commit_sha(self):
        """replay_pointer should include commit_sha when provided."""
        adapter = MockRAGAdapter()
        commit_sha = "a1b2c3d4e5f6789012345678901234567890abcd"

        result = adapter.query(
            query="test query",
            at_time="2026-02-20T10:00:00Z",
            commit_sha=commit_sha,
        )

        assert result.replay_pointer.get("commit_sha") == commit_sha

    def test_replay_pointer_contains_run_id(self):
        """replay_pointer should include run_id for traceability."""
        adapter = MockRAGAdapter()

        result = adapter.query(
            query="test query",
            at_time="2026-02-20T10:00:00Z",
        )

        assert "run_id" in result.replay_pointer
        assert result.replay_pointer["run_id"].startswith("RAG-MOCK-")


class TestRAGAdapterCombinationQuery:
    """Tests for repo_url + commit_sha + at_time combination queries."""

    def test_combination_query_accepted(self):
        """Full combination query should be accepted."""
        adapter = MockRAGAdapter()

        result = adapter.query(
            query="test query",
            at_time="2026-02-20T10:00:00Z",
            repo_url="https://github.com/test/repo",
            commit_sha="a1b2c3d4e5f6789012345678901234567890abcd",
            top_k=10,
        )

        assert result.query == "test query"
        assert result.at_time == "2026-02-20T10:00:00Z"
        assert result.repo_url == "https://github.com/test/repo"
        assert result.commit_sha == "a1b2c3d4e5f6789012345678901234567890abcd"
        assert len(result.results) <= 10

    def test_results_include_metadata(self):
        """Results should include commit_sha and at_time metadata."""
        adapter = MockRAGAdapter()
        commit_sha = "a1b2c3d4e5f6789012345678901234567890abcd"
        at_time = "2026-02-20T10:00:00Z"

        result = adapter.query(
            query="test query",
            at_time=at_time,
            commit_sha=commit_sha,
        )

        for item in result.results:
            assert "metadata" in item
            assert item["metadata"].get("commit_sha") == commit_sha
            assert item["metadata"].get("retrieved_at") == at_time


class TestRAGAdapterSwappable:
    """Tests for swappable adapter functionality."""

    def test_default_adapter_is_mock(self):
        """Default adapter should be MockRAGAdapter."""
        adapter = get_rag_adapter()
        assert isinstance(adapter, MockRAGAdapter)

    def test_adapter_can_be_swapped(self):
        """Adapter can be swapped at runtime."""
        # Create custom adapter
        custom_adapter = MockRAGAdapter(delay_ms=100)
        set_rag_adapter(custom_adapter)

        # Verify it's the same instance
        current_adapter = get_rag_adapter()
        assert current_adapter is custom_adapter

    def test_adapter_can_be_reset(self):
        """Adapter can be reset to default."""
        # Set custom adapter
        set_rag_adapter(MockRAGAdapter(delay_ms=200))

        # Reset
        reset_rag_adapter()

        # Verify it's a new default instance
        adapter = get_rag_adapter()
        assert isinstance(adapter, MockRAGAdapter)
        assert adapter.delay_ms == 0


class TestRAGAdapterQueryValidation:
    """Tests for query validation."""

    def test_empty_query_rejected(self):
        """Empty query should be rejected."""
        adapter = MockRAGAdapter()

        with pytest.raises(ValueError):
            adapter.query(
                query="",
                at_time="2026-02-20T10:00:00Z",
            )

    def test_whitespace_only_query_rejected(self):
        """Whitespace-only query should be rejected."""
        adapter = MockRAGAdapter()

        with pytest.raises(ValueError):
            adapter.query(
                query="   ",
                at_time="2026-02-20T10:00:00Z",
            )

    def test_top_k_respected(self):
        """top_k parameter should limit results."""
        adapter = MockRAGAdapter()

        result = adapter.query(
            query="test query",
            at_time="2026-02-20T10:00:00Z",
            top_k=3,
        )

        assert len(result.results) <= 3
        assert result.total_hits <= 3


class TestRAGQueryResult:
    """Tests for RAGQueryResult dataclass."""

    def test_to_dict_includes_all_fields(self):
        """to_dict should include all required fields."""
        result = RAGQueryResult(
            query="test",
            at_time="2026-02-20T10:00:00Z",
            results=[{"rank": 1, "content": "test"}],
            replay_pointer={"at_time": "2026-02-20T10:00:00Z"},
            repo_url="https://github.com/test/repo",
            commit_sha="abc123",
            total_hits=1,
        )

        d = result.to_dict()

        assert d["query"] == "test"
        assert d["at_time"] == "2026-02-20T10:00:00Z"
        assert d["repo_url"] == "https://github.com/test/repo"
        assert d["commit_sha"] == "abc123"
        assert d["results"] == [{"rank": 1, "content": "test"}]
        assert d["total_hits"] == 1
        assert "replay_pointer" in d
        assert "queried_at" in d


# ============================================================================
# Integration Tests (via API route if available)
# ============================================================================

class TestQueryRagViaAPI:
    """Tests for query_rag via FastAPI route (if available)."""

    @pytest.fixture
    def client(self):
        """Get test client if available."""
        try:
            from fastapi.testclient import TestClient
            from api.l4_api import app
            return TestClient(app)
        except ImportError:
            pytest.skip("FastAPI test client not available")

    def test_api_rejects_missing_at_time(self, client):
        """API should reject request with missing at_time."""
        response = client.post(
            "/api/v1/n8n/query_rag",
            json={
                "query": "test query",
            }
        )

        data = response.json()
        assert data["ok"] is False
        assert "AT-TIME" in data["error_code"].upper()

    def test_api_rejects_latest_at_time(self, client):
        """API should reject 'latest' as at_time value."""
        response = client.post(
            "/api/v1/n8n/query_rag",
            json={
                "query": "test query",
                "at_time": "latest",
            }
        )

        data = response.json()
        assert data["ok"] is False
        assert "DRIFT" in data["error_code"].upper() or "FORBIDDEN" in data["error_code"].upper()

    def test_api_returns_replay_pointer(self, client):
        """API should return replay_pointer on success."""
        response = client.post(
            "/api/v1/n8n/query_rag",
            json={
                "query": "test query",
                "at_time": "2026-02-20T10:00:00Z",
                "repo_url": "https://github.com/test/repo",
                "commit_sha": "a1b2c3d4e5f6789012345678901234567890abcd",
            }
        )

        data = response.json()
        assert data["ok"] is True
        assert "replay_pointer" in data["data"]
        assert data["data"]["replay_pointer"]["at_time"] == "2026-02-20T10:00:00Z"


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
