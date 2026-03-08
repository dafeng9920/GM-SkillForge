"""
Tests for External Skill RAG Adapter - T14

Tests cover:
- at_time fixed input validation (fail-closed)
- Drift value blocking (latest, now, today, etc.)
- replay_pointer presence and consistency
- repo_url + commit_sha + at_time combination verification
- External skill governance input validation

Job ID: L45-D3-EXT-SKILL-GOV-20260220-003
Skill ID: l45_external_skill_governance_batch1
Task ID: T14
Executor: vs--cc2
"""
from __future__ import annotations

import pytest
from datetime import datetime, timezone

from skillforge.src.adapters.external_skill_rag_adapter import (
    AT_TIME_FORBIDDEN_VALUES,
    ExternalSkillRAGAdapter,
    ExternalSkillRAGError,
    ExternalSkillRAGErrorCode,
    ExternalSkillRAGResult,
    ExternalSkillReplayPointer,
    MockExternalSkillRAGAdapter,
    get_external_skill_rag_adapter,
    set_external_skill_rag_adapter,
    reset_external_skill_rag_adapter,
    query_external_skill_evidence,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def adapter():
    """Create a fresh mock adapter for each test."""
    reset_external_skill_rag_adapter()
    return MockExternalSkillRAGAdapter()


@pytest.fixture
def valid_inputs():
    """Valid input parameters for testing."""
    return {
        "query": "find governance evidence for skill validation",
        "at_time": "2026-02-20T10:00:00Z",
        "external_skill_ref": "external/validation@v1.0.0",
        "repo_url": "https://github.com/example/external-skill",
        "commit_sha": "abc123def456789012345678901234567890abcd",
    }


# ============================================================================
# Test: at_time Validation - Fixed Input (Pass)
# ============================================================================

class TestAtTimeFixedInput:
    """Tests for at_time fixed input validation."""

    def test_valid_iso8601_with_z_suffix(self, adapter, valid_inputs):
        """Valid ISO-8601 timestamp with Z suffix should be accepted."""
        result = adapter.query(**valid_inputs)
        assert isinstance(result, ExternalSkillRAGResult)
        assert result.at_time == valid_inputs["at_time"]

    def test_valid_iso8601_with_timezone(self, adapter, valid_inputs):
        """Valid ISO-8601 timestamp with timezone should be accepted."""
        valid_inputs["at_time"] = "2026-02-20T10:00:00+00:00"
        result = adapter.query(**valid_inputs)
        assert isinstance(result, ExternalSkillRAGResult)

    def test_valid_iso8601_without_timezone(self, adapter, valid_inputs):
        """Valid ISO-8601 timestamp without timezone should be accepted."""
        valid_inputs["at_time"] = "2026-02-20T10:00:00"
        result = adapter.query(**valid_inputs)
        assert isinstance(result, ExternalSkillRAGResult)


# ============================================================================
# Test: at_time Validation - Drift Values (Fail-Closed)
# ============================================================================

class TestAtTimeDriftBlocking:
    """Tests for drift value blocking - all must be rejected."""

    @pytest.mark.parametrize("drift_value", list(AT_TIME_FORBIDDEN_VALUES))
    def test_drift_value_rejected(self, adapter, valid_inputs, drift_value):
        """All drift values must be rejected with AT_TIME_DRIFT_FORBIDDEN error."""
        valid_inputs["at_time"] = drift_value

        is_valid, error = adapter.validate_at_time(drift_value)

        assert is_valid is False
        assert error is not None
        assert error.error_code == ExternalSkillRAGErrorCode.AT_TIME_DRIFT_FORBIDDEN
        assert "drift" in error.error_message.lower()

    def test_latest_rejected(self, adapter, valid_inputs):
        """'latest' must be rejected."""
        valid_inputs["at_time"] = "latest"
        with pytest.raises(ValueError) as exc_info:
            adapter.query(**valid_inputs)
        assert "drift" in str(exc_info.value).lower()

    def test_now_rejected(self, adapter, valid_inputs):
        """'now' must be rejected."""
        valid_inputs["at_time"] = "now"
        with pytest.raises(ValueError) as exc_info:
            adapter.query(**valid_inputs)
        assert "drift" in str(exc_info.value).lower()

    def test_today_rejected(self, adapter, valid_inputs):
        """'today' must be rejected."""
        valid_inputs["at_time"] = "today"
        with pytest.raises(ValueError) as exc_info:
            adapter.query(**valid_inputs)
        assert "drift" in str(exc_info.value).lower()

    def test_current_rejected(self, adapter, valid_inputs):
        """'current' must be rejected."""
        valid_inputs["at_time"] = "current"
        with pytest.raises(ValueError) as exc_info:
            adapter.query(**valid_inputs)
        assert "drift" in str(exc_info.value).lower()

    def test_case_insensitive_drift_blocking(self, adapter, valid_inputs):
        """Drift values should be blocked regardless of case."""
        for drift_value in ["LATEST", "Now", "TODAY", "CURRENT"]:
            valid_inputs["at_time"] = drift_value
            with pytest.raises(ValueError):
                adapter.query(**valid_inputs)


# ============================================================================
# Test: at_time Missing (Fail-Closed)
# ============================================================================

class TestAtTimeMissing:
    """Tests for missing at_time - must fail-closed."""

    def test_at_time_none_rejected(self, adapter, valid_inputs):
        """None at_time must be rejected with AT_TIME_MISSING error."""
        is_valid, error = adapter.validate_at_time(None)

        assert is_valid is False
        assert error is not None
        assert error.error_code == ExternalSkillRAGErrorCode.AT_TIME_MISSING

    def test_at_time_empty_string_rejected(self, adapter, valid_inputs):
        """Empty string at_time must be rejected."""
        is_valid, error = adapter.validate_at_time("")

        assert is_valid is False
        assert error is not None
        assert error.error_code == ExternalSkillRAGErrorCode.AT_TIME_MISSING

    def test_at_time_none_raises_in_query(self, adapter, valid_inputs):
        """Query with None at_time must raise."""
        valid_inputs["at_time"] = None
        with pytest.raises(ValueError) as exc_info:
            adapter.query(**valid_inputs)
        assert "required" in str(exc_info.value).lower()


# ============================================================================
# Test: replay_pointer Presence
# ============================================================================

class TestReplayPointerPresence:
    """Tests for replay_pointer presence in successful responses."""

    def test_result_contains_replay_pointer(self, adapter, valid_inputs):
        """Successful response must contain replay_pointer."""
        result = adapter.query(**valid_inputs)
        assert result.replay_pointer is not None
        assert isinstance(result.replay_pointer, ExternalSkillReplayPointer)

    def test_replay_pointer_contains_at_time(self, adapter, valid_inputs):
        """replay_pointer must contain at_time."""
        result = adapter.query(**valid_inputs)
        assert result.replay_pointer.at_time == valid_inputs["at_time"]

    def test_replay_pointer_contains_repo_url(self, adapter, valid_inputs):
        """replay_pointer must contain repo_url."""
        result = adapter.query(**valid_inputs)
        assert result.replay_pointer.repo_url == valid_inputs["repo_url"]

    def test_replay_pointer_contains_commit_sha(self, adapter, valid_inputs):
        """replay_pointer must contain commit_sha."""
        result = adapter.query(**valid_inputs)
        assert result.replay_pointer.commit_sha == valid_inputs["commit_sha"]

    def test_replay_pointer_contains_external_skill_ref(self, adapter, valid_inputs):
        """replay_pointer must contain external_skill_ref."""
        result = adapter.query(**valid_inputs)
        assert result.replay_pointer.external_skill_ref == valid_inputs["external_skill_ref"]

    def test_replay_pointer_contains_run_id(self, adapter, valid_inputs):
        """replay_pointer must contain run_id for traceability."""
        result = adapter.query(**valid_inputs)
        assert result.replay_pointer.run_id is not None
        assert result.replay_pointer.run_id.startswith("EXT-RAG-")

    def test_replay_pointer_contains_content_hash(self, adapter, valid_inputs):
        """replay_pointer must contain content_hash for verification."""
        result = adapter.query(**valid_inputs)
        assert result.replay_pointer.content_hash is not None
        assert len(result.replay_pointer.content_hash) == 64  # SHA-256 hex


# ============================================================================
# Test: at_time Consistency
# ============================================================================

class TestAtTimeConsistency:
    """Tests for at_time consistency between input and replay_pointer."""

    def test_replay_pointer_at_time_matches_input(self, adapter, valid_inputs):
        """replay_pointer.at_time must match input at_time."""
        result = adapter.query(**valid_inputs)
        assert result.replay_pointer.at_time == valid_inputs["at_time"]

    def test_verify_replay_consistency(self, adapter, valid_inputs):
        """verify_replay_consistency() must return all True."""
        result = adapter.query(**valid_inputs)
        consistency = result.verify_replay_consistency()
        assert consistency["at_time_consistent"] is True
        assert consistency["repo_url_consistent"] is True
        assert consistency["commit_sha_consistent"] is True
        assert consistency["external_skill_ref_consistent"] is True

    def test_replay_pointer_verify_consistency_method(self, adapter, valid_inputs):
        """ExternalSkillReplayPointer.verify_consistency() must work."""
        result = adapter.query(**valid_inputs)
        assert result.replay_pointer.verify_consistency(valid_inputs["at_time"]) is True


# ============================================================================
# Test: Required Governance Inputs
# ============================================================================

class TestRequiredGovernanceInputs:
    """Tests for required governance input validation."""

    def test_missing_external_skill_ref_rejected(self, adapter, valid_inputs):
        """Missing external_skill_ref must be rejected."""
        valid_inputs["external_skill_ref"] = None
        is_valid, error = adapter.validate_required_inputs(
            None, valid_inputs["repo_url"], valid_inputs["commit_sha"]
        )
        assert is_valid is False
        assert error.error_code == ExternalSkillRAGErrorCode.EXTERNAL_SKILL_REF_MISSING

    def test_missing_repo_url_rejected(self, adapter, valid_inputs):
        """Missing repo_url must be rejected."""
        is_valid, error = adapter.validate_required_inputs(
            valid_inputs["external_skill_ref"], None, valid_inputs["commit_sha"]
        )
        assert is_valid is False
        assert error.error_code == ExternalSkillRAGErrorCode.REPO_URL_MISSING

    def test_missing_commit_sha_rejected(self, adapter, valid_inputs):
        """Missing commit_sha must be rejected."""
        is_valid, error = adapter.validate_required_inputs(
            valid_inputs["external_skill_ref"], valid_inputs["repo_url"], None
        )
        assert is_valid is False
        assert error.error_code == ExternalSkillRAGErrorCode.COMMIT_SHA_MISSING

    def test_empty_external_skill_ref_rejected(self, adapter, valid_inputs):
        """Empty external_skill_ref must be rejected."""
        valid_inputs["external_skill_ref"] = ""
        with pytest.raises(ValueError):
            adapter.query(**valid_inputs)

    def test_empty_repo_url_rejected(self, adapter, valid_inputs):
        """Empty repo_url must be rejected."""
        valid_inputs["repo_url"] = ""
        with pytest.raises(ValueError):
            adapter.query(**valid_inputs)

    def test_empty_commit_sha_rejected(self, adapter, valid_inputs):
        """Empty commit_sha must be rejected."""
        valid_inputs["commit_sha"] = ""
        with pytest.raises(ValueError):
            adapter.query(**valid_inputs)


# ============================================================================
# Test: Query Validation
# ============================================================================

class TestQueryValidation:
    """Tests for query string validation."""

    def test_empty_query_rejected(self, adapter, valid_inputs):
        """Empty query must be rejected."""
        valid_inputs["query"] = ""
        with pytest.raises(ValueError) as exc_info:
            adapter.query(**valid_inputs)
        assert "empty" in str(exc_info.value).lower()

    def test_whitespace_only_query_rejected(self, adapter, valid_inputs):
        """Whitespace-only query must be rejected."""
        valid_inputs["query"] = "   "
        with pytest.raises(ValueError):
            adapter.query(**valid_inputs)

    def test_valid_query_accepted(self, adapter, valid_inputs):
        """Valid query should be accepted."""
        result = adapter.query(**valid_inputs)
        assert result.query == valid_inputs["query"]


# ============================================================================
# Test: Adapter Registry
# ============================================================================

class TestAdapterRegistry:
    """Tests for global adapter registry."""

    def test_get_default_adapter(self):
        """get_external_skill_rag_adapter() returns default adapter."""
        reset_external_skill_rag_adapter()
        adapter = get_external_skill_rag_adapter()
        assert isinstance(adapter, MockExternalSkillRAGAdapter)

    def test_set_adapter(self):
        """set_external_skill_rag_adapter() changes the adapter."""
        custom_adapter = MockExternalSkillRAGAdapter(delay_ms=100)
        set_external_skill_rag_adapter(custom_adapter)
        assert get_external_skill_rag_adapter() is custom_adapter

    def test_reset_adapter(self):
        """reset_external_skill_rag_adapter() resets to default."""
        custom_adapter = MockExternalSkillRAGAdapter(delay_ms=100)
        set_external_skill_rag_adapter(custom_adapter)
        reset_external_skill_rag_adapter()
        adapter = get_external_skill_rag_adapter()
        assert isinstance(adapter, MockExternalSkillRAGAdapter)
        assert adapter.delay_ms == 0


# ============================================================================
# Test: Convenience Function
# ============================================================================

class TestConvenienceFunction:
    """Tests for query_external_skill_evidence convenience function."""

    def test_convenience_function_success(self, valid_inputs):
        """query_external_skill_evidence returns ok=True on success."""
        reset_external_skill_rag_adapter()
        result = query_external_skill_evidence(**valid_inputs)
        assert result["ok"] is True
        assert "result" in result
        assert "replay_pointer" in result["result"]

    def test_convenience_function_at_time_missing(self, valid_inputs):
        """query_external_skill_evidence returns error on missing at_time."""
        reset_external_skill_rag_adapter()
        valid_inputs["at_time"] = None
        result = query_external_skill_evidence(**valid_inputs)
        assert result["ok"] is False
        assert "error" in result
        assert result["error"]["error_code"] == "EXT-RAG-AT-TIME-MISSING"

    def test_convenience_function_drift_blocked(self, valid_inputs):
        """query_external_skill_evidence returns error on drift value."""
        reset_external_skill_rag_adapter()
        valid_inputs["at_time"] = "latest"
        result = query_external_skill_evidence(**valid_inputs)
        assert result["ok"] is False
        assert result["error"]["error_code"] == "EXT-RAG-AT-TIME-DRIFT-FORBIDDEN"

    def test_convenience_function_replay_consistency(self, valid_inputs):
        """query_external_skill_evidence verifies replay consistency."""
        reset_external_skill_rag_adapter()
        result = query_external_skill_evidence(**valid_inputs)
        assert result["ok"] is True
        replay = result["result"]["replay_pointer"]
        assert replay["at_time"] == valid_inputs["at_time"]
        assert replay["repo_url"] == valid_inputs["repo_url"]
        assert replay["commit_sha"] == valid_inputs["commit_sha"]
        assert replay["external_skill_ref"] == valid_inputs["external_skill_ref"]


# ============================================================================
# Test: Error Codes Consistency
# ============================================================================

class TestErrorCodes:
    """Tests for error code consistency with T9."""

    def test_error_codes_are_strings(self):
        """All error codes should be string values."""
        for code in ExternalSkillRAGErrorCode:
            assert isinstance(code.value, str)

    def test_error_codes_prefix(self):
        """Error codes should have EXT-RAG prefix."""
        for code in ExternalSkillRAGErrorCode:
            assert code.value.startswith("EXT-RAG-")

    def test_at_time_missing_error_code(self):
        """AT_TIME_MISSING error code should match spec."""
        assert ExternalSkillRAGErrorCode.AT_TIME_MISSING.value == "EXT-RAG-AT-TIME-MISSING"

    def test_at_time_drift_error_code(self):
        """AT_TIME_DRIFT_FORBIDDEN error code should match spec."""
        assert ExternalSkillRAGErrorCode.AT_TIME_DRIFT_FORBIDDEN.value == "EXT-RAG-AT-TIME-DRIFT-FORBIDDEN"


# ============================================================================
# Test: Result Structure
# ============================================================================

class TestResultStructure:
    """Tests for result structure completeness."""

    def test_result_to_dict(self, adapter, valid_inputs):
        """Result.to_dict() should contain all required fields."""
        result = adapter.query(**valid_inputs)
        d = result.to_dict()

        assert "query" in d
        assert "at_time" in d
        assert "external_skill_ref" in d
        assert "repo_url" in d
        assert "commit_sha" in d
        assert "results" in d
        assert "total_hits" in d
        assert "queried_at" in d
        assert "replay_pointer" in d
        assert "job_id" in d

    def test_result_contains_job_id(self, adapter, valid_inputs):
        """Result should contain job_id for traceability."""
        result = adapter.query(**valid_inputs)
        assert result.job_id == "L45-D3-EXT-SKILL-GOV-20260220-003"

    def test_results_have_metadata(self, adapter, valid_inputs):
        """Each result should have governance metadata."""
        result = adapter.query(**valid_inputs)
        for r in result.results:
            assert "metadata" in r
            assert "external_skill_ref" in r["metadata"]
            assert "repo_url" in r["metadata"]
            assert "commit_sha" in r["metadata"]
            assert "retrieved_at" in r["metadata"]


# ============================================================================
# Test: No Implicit Degradation
# ============================================================================

class TestNoImplicitDegradation:
    """Tests to ensure no implicit time degradation."""

    def test_no_implicit_current_time(self, adapter, valid_inputs):
        """Adapter must not implicitly use current time."""
        # Query with fixed at_time
        result = adapter.query(**valid_inputs)

        # Verify at_time is exactly what was provided
        assert result.at_time == valid_inputs["at_time"]
        assert result.replay_pointer.at_time == valid_inputs["at_time"]

        # Verify it's not the current time
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        assert result.at_time != now

    def test_no_relative_time_acceptance(self, adapter, valid_inputs):
        """Adapter must not accept relative time inputs."""
        relative_times = [
            "+1h",
            "-1d",
            "1 hour ago",
            "tomorrow at noon",
        ]
        for rel_time in relative_times:
            valid_inputs["at_time"] = rel_time
            # These should fail validation (invalid format)
            is_valid, error = adapter.validate_at_time(rel_time)
            assert is_valid is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
