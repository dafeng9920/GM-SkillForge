"""
Unit tests for Batch Permit Issuer.

Tests:
- Batch permit issuance with N targets (up to 5)
- Failure strategies: all_or_nothing, best_effort, majority_vote
- Tombstone generation for failed targets
- All-or-nothing rollback behavior

Contract: skillforge/src/contracts/gates/batch_permit.yaml
"""
from __future__ import annotations

import pytest

from skillforge.src.skills.gates.batch_permit_issuer import (
    BatchPermitIssuer,
    FailureStrategy,
    BatchDecision,
    issue_batch_permits,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def signing_key():
    """Test signing key."""
    return "test-secret-key-12345"


@pytest.fixture
def valid_target():
    """Single valid target configuration."""
    return {
        "target_id": "target-001",
        "repo_url": "https://github.com/example/repo1.git",
        "commit_sha": "abc123def456789012345678901234567890abcd",
        "run_id": "run-001",
        "intent_id": "intent-001",
        "ttl_seconds": 3600,
    }


@pytest.fixture
def valid_batch_input(valid_target):
    """Valid batch input with 2 targets."""
    return {
        "targets": [
            valid_target,
            {
                "target_id": "target-002",
                "repo_url": "https://github.com/example/repo2.git",
                "commit_sha": "def456abc789012345678901234567890abc12de",
                "run_id": "run-001",
                "intent_id": "intent-002",
                "ttl_seconds": 3600,
            },
        ],
        "final_gate_decision": "PASSED",
        "audit_pack_ref": "audit-pack-001",
        "allowed_actions": ["release"],
    }


@pytest.fixture
def five_target_batch_input():
    """Valid batch input with 5 targets (max batch size)."""
    targets = []
    for i in range(5):
        targets.append({
            "target_id": f"target-{i+1:03d}",
            "repo_url": f"https://github.com/example/repo{i+1}.git",
            "commit_sha": f"abc{i:03d}def{i:03d}456{i:03d}789{i:03d}012{i:03d}345{i:03d}678{i:03d}90ab",
            "run_id": "run-batch-001",
            "intent_id": f"intent-{i+1:03d}",
            "ttl_seconds": 3600,
        })
    return {
        "targets": targets,
        "final_gate_decision": "PASSED",
        "audit_pack_ref": "audit-pack-batch-001",
        "allowed_actions": ["release"],
    }


# =============================================================================
# Tests for Input Validation
# =============================================================================

class TestBatchInputValidation:
    """Tests for batch input validation."""

    def test_valid_batch_input_passes(self, signing_key, valid_batch_input):
        """Valid batch input MUST pass validation."""
        issuer = BatchPermitIssuer(signing_key=signing_key)
        errors = issuer.validate_batch_input(valid_batch_input)
        assert len(errors) == 0

    def test_missing_targets_fails(self, signing_key):
        """Missing targets array MUST fail."""
        issuer = BatchPermitIssuer(signing_key=signing_key)
        errors = issuer.validate_batch_input({
            "final_gate_decision": "PASSED",
            "audit_pack_ref": "audit-001",
        })
        assert len(errors) > 0
        assert any("targets" in e for e in errors)

    def test_empty_targets_fails(self, signing_key):
        """Empty targets array MUST fail."""
        issuer = BatchPermitIssuer(signing_key=signing_key)
        errors = issuer.validate_batch_input({
            "targets": [],
            "final_gate_decision": "PASSED",
            "audit_pack_ref": "audit-001",
        })
        assert len(errors) > 0

    def test_batch_size_exceeds_max_fails(self, signing_key):
        """Batch size > 5 MUST fail."""
        issuer = BatchPermitIssuer(signing_key=signing_key)
        targets = [{"target_id": f"t{i}", "repo_url": "url", "commit_sha": "sha",
                    "run_id": "r", "intent_id": "i", "ttl_seconds": 3600}
                   for i in range(6)]  # 6 targets > max 5
        errors = issuer.validate_batch_input({
            "targets": targets,
            "final_gate_decision": "PASSED",
            "audit_pack_ref": "audit-001",
        })
        assert any("batch size" in e.lower() for e in errors)

    def test_missing_target_field_fails(self, signing_key):
        """Missing required field in target MUST fail."""
        issuer = BatchPermitIssuer(signing_key=signing_key)
        errors = issuer.validate_batch_input({
            "targets": [{"target_id": "t1"}],  # Missing other required fields
            "final_gate_decision": "PASSED",
            "audit_pack_ref": "audit-001",
        })
        assert len(errors) > 0

    def test_invalid_failure_strategy_fails(self, signing_key, valid_batch_input):
        """Invalid failure_strategy MUST fail."""
        issuer = BatchPermitIssuer(signing_key=signing_key)
        valid_batch_input["failure_strategy"] = "invalid_strategy"
        errors = issuer.validate_batch_input(valid_batch_input)
        assert any("failure_strategy" in e for e in errors)


# =============================================================================
# Tests for All-or-Nothing Strategy (Default)
# =============================================================================

class TestAllOrNothingStrategy:
    """
    Tests for ALL_OR_NOTHING failure strategy.

    任一失败则全部回滚 - 这是默认策略，符合审计要求。
    """

    def test_all_success_returns_success(self, signing_key, five_target_batch_input):
        """All 5 targets successful MUST return SUCCESS."""
        issuer = BatchPermitIssuer(
            signing_key=signing_key,
            failure_strategy=FailureStrategy.ALL_OR_NOTHING,
        )
        result = issuer.issue_batch(five_target_batch_input)

        assert result["batch_decision"] == BatchDecision.SUCCESS.value
        assert result["successful_count"] == 5
        assert result["failed_count"] == 0
        assert len(result["rolled_back_permits"]) == 0
        assert len(result["tombstones"]) == 0

    def test_one_failure_triggers_rollback(self, signing_key, five_target_batch_input):
        """
        任一目标失败 MUST 触发全部回滚。

        This is the core verification for all-or-nothing strategy.
        """
        # Make target-003 fail by using invalid TTL
        five_target_batch_input["targets"][2]["ttl_seconds"] = -1

        issuer = BatchPermitIssuer(
            signing_key=signing_key,
            failure_strategy=FailureStrategy.ALL_OR_NOTHING,
        )
        result = issuer.issue_batch(five_target_batch_input)

        # MUST be ROLLED_BACK, not PARTIAL_SUCCESS
        assert result["batch_decision"] == BatchDecision.ROLLED_BACK.value
        assert result["successful_count"] == 0  # All rolled back
        assert result["failed_count"] == 5

        # MUST have rolled back the successful permits
        # (4 succeeded before the failure, all should be in rolled_back_permits)
        assert len(result["rolled_back_permits"]) == 4

        # All targets MUST have tombstones (including the rolled-back ones)
        assert len(result["tombstones"]) == 5

    def test_rollback_creates_tombstones_for_all(self, signing_key, five_target_batch_input):
        """Rollback MUST create tombstones for ALL targets, not just failed one."""
        # Make target-002 fail
        five_target_batch_input["targets"][1]["ttl_seconds"] = -1

        issuer = BatchPermitIssuer(
            signing_key=signing_key,
            failure_strategy=FailureStrategy.ALL_OR_NOTHING,
        )
        result = issuer.issue_batch(five_target_batch_input)

        # Verify tombstones exist for all targets
        tombstone_target_ids = {t["target_id"] for t in result["tombstones"]}
        expected_target_ids = {f"target-{i+1:03d}" for i in range(5)}
        assert tombstone_target_ids == expected_target_ids

    def test_rollback_tombstone_has_correct_error_code(self, signing_key, five_target_batch_input):
        """Rolled back targets MUST have BATCH_ROLLBACK error code."""
        # Make target-005 fail
        five_target_batch_input["targets"][4]["ttl_seconds"] = -1

        issuer = BatchPermitIssuer(
            signing_key=signing_key,
            failure_strategy=FailureStrategy.ALL_OR_NOTHING,
        )
        result = issuer.issue_batch(five_target_batch_input)

        # Check that rolled-back targets have BATCH_ROLLBACK error
        for tombstone in result["tombstones"]:
            if tombstone["target_id"] != "target-005":  # Not the original failure
                assert tombstone["error_code"] == "BATCH_ROLLBACK"

    def test_all_fail_returns_rolled_back(self, signing_key):
        """All targets failing MUST return ROLLED_BACK."""
        issuer = BatchPermitIssuer(
            signing_key=signing_key,
            failure_strategy=FailureStrategy.ALL_OR_NOTHING,
        )

        # All targets have invalid TTL
        targets = [
            {
                "target_id": f"target-{i}",
                "repo_url": "url",
                "commit_sha": "sha",
                "run_id": "r",
                "intent_id": "i",
                "ttl_seconds": -1,  # Invalid
            }
            for i in range(3)
        ]

        result = issuer.issue_batch({
            "targets": targets,
            "final_gate_decision": "PASSED",
            "audit_pack_ref": "audit-001",
        })

        assert result["batch_decision"] == BatchDecision.ROLLED_BACK.value
        assert result["successful_count"] == 0
        assert result["failed_count"] == 3


# =============================================================================
# Tests for Best-Effort Strategy
# =============================================================================

class TestBestEffortStrategy:
    """
    Tests for BEST_EFFORT failure strategy.

    允许部分成功，失败目标生成 tombstone。
    """

    def test_all_success_returns_success(self, signing_key, five_target_batch_input):
        """All successful MUST return SUCCESS."""
        issuer = BatchPermitIssuer(
            signing_key=signing_key,
            failure_strategy=FailureStrategy.BEST_EFFORT,
        )
        result = issuer.issue_batch(five_target_batch_input)

        assert result["batch_decision"] == BatchDecision.SUCCESS.value
        assert result["successful_count"] == 5
        assert len(result["tombstones"]) == 0

    def test_partial_success_returns_partial(self, signing_key, five_target_batch_input):
        """Partial success MUST return PARTIAL_SUCCESS."""
        # Make 2 targets fail
        five_target_batch_input["targets"][1]["ttl_seconds"] = -1
        five_target_batch_input["targets"][3]["ttl_seconds"] = -1

        issuer = BatchPermitIssuer(
            signing_key=signing_key,
            failure_strategy=FailureStrategy.BEST_EFFORT,
        )
        result = issuer.issue_batch(five_target_batch_input)

        assert result["batch_decision"] == BatchDecision.PARTIAL_SUCCESS.value
        assert result["successful_count"] == 3
        assert result["failed_count"] == 2
        assert len(result["rolled_back_permits"]) == 0  # No rollback

    def test_failed_targets_have_tombstones(self, signing_key, five_target_batch_input):
        """Only failed targets MUST have tombstones in BEST_EFFORT."""
        # Make target-002 fail
        five_target_batch_input["targets"][1]["ttl_seconds"] = -1

        issuer = BatchPermitIssuer(
            signing_key=signing_key,
            failure_strategy=FailureStrategy.BEST_EFFORT,
        )
        result = issuer.issue_batch(five_target_batch_input)

        # Only 1 tombstone for the failed target
        assert len(result["tombstones"]) == 1
        assert result["tombstones"][0]["target_id"] == "target-002"

    def test_all_fail_returns_failed(self, signing_key):
        """All targets failing MUST return FAILED."""
        issuer = BatchPermitIssuer(
            signing_key=signing_key,
            failure_strategy=FailureStrategy.BEST_EFFORT,
        )

        targets = [
            {
                "target_id": f"target-{i}",
                "repo_url": "url",
                "commit_sha": "sha",
                "run_id": "r",
                "intent_id": "i",
                "ttl_seconds": -1,
            }
            for i in range(3)
        ]

        result = issuer.issue_batch({
            "targets": targets,
            "final_gate_decision": "PASSED",
            "audit_pack_ref": "audit-001",
        })

        assert result["batch_decision"] == BatchDecision.FAILED.value
        assert result["successful_count"] == 0
        assert result["failed_count"] == 3


# =============================================================================
# Tests for Majority-Vote Strategy
# =============================================================================

class TestMajorityVoteStrategy:
    """
    Tests for MAJORITY_VOTE failure strategy.

    多数成功则批次成功。
    """

    def test_majority_success_returns_success(self, signing_key, five_target_batch_input):
        """Majority (>50%) successful MUST return SUCCESS."""
        # Make 2 targets fail (3 succeed = 60% = majority)
        five_target_batch_input["targets"][1]["ttl_seconds"] = -1
        five_target_batch_input["targets"][4]["ttl_seconds"] = -1

        issuer = BatchPermitIssuer(
            signing_key=signing_key,
            failure_strategy=FailureStrategy.MAJORITY_VOTE,
        )
        result = issuer.issue_batch(five_target_batch_input)

        assert result["batch_decision"] == BatchDecision.SUCCESS.value
        assert result["successful_count"] == 3
        assert len(result["rolled_back_permits"]) == 0

    def test_minority_success_returns_failed(self, signing_key, five_target_batch_input):
        """Minority (<=50%) successful MUST return FAILED."""
        # Make 3 targets fail (2 succeed = 40% = minority)
        five_target_batch_input["targets"][0]["ttl_seconds"] = -1
        five_target_batch_input["targets"][2]["ttl_seconds"] = -1
        five_target_batch_input["targets"][4]["ttl_seconds"] = -1

        issuer = BatchPermitIssuer(
            signing_key=signing_key,
            failure_strategy=FailureStrategy.MAJORITY_VOTE,
        )
        result = issuer.issue_batch(five_target_batch_input)

        assert result["batch_decision"] == BatchDecision.FAILED.value
        assert result["successful_count"] == 2

    def test_exact_half_returns_failed(self, signing_key):
        """Exactly 50% success MUST return FAILED (needs >50%)."""
        issuer = BatchPermitIssuer(
            signing_key=signing_key,
            failure_strategy=FailureStrategy.MAJORITY_VOTE,
        )

        # 4 targets, 2 fail, 2 succeed = 50%
        targets = []
        for i in range(4):
            targets.append({
                "target_id": f"target-{i}",
                "repo_url": "url",
                "commit_sha": "sha",
                "run_id": "r",
                "intent_id": f"intent-{i}",
                "ttl_seconds": -1 if i < 2 else 3600,  # First 2 fail
            })

        result = issuer.issue_batch({
            "targets": targets,
            "final_gate_decision": "PASSED",
            "audit_pack_ref": "audit-001",
        })

        assert result["batch_decision"] == BatchDecision.FAILED.value


# =============================================================================
# Tests for Tombstone Rules
# =============================================================================

class TestTombstoneRules:
    """Tests for tombstone generation and rules."""

    def test_tombstone_has_required_fields(self, signing_key, valid_batch_input):
        """Tombstone MUST have all required fields."""
        # Make one target fail
        valid_batch_input["targets"][1]["ttl_seconds"] = -1

        issuer = BatchPermitIssuer(
            signing_key=signing_key,
            failure_strategy=FailureStrategy.ALL_OR_NOTHING,
        )
        result = issuer.issue_batch(valid_batch_input)

        for tombstone in result["tombstones"]:
            assert "tombstone_id" in tombstone
            assert "target_id" in tombstone
            assert "target_index" in tombstone
            assert "error_code" in tombstone
            assert "error_message" in tombstone
            assert "retryable" in tombstone
            assert "created_at" in tombstone
            assert "batch_id" in tombstone

    def test_retryable_errors_are_marked(self, signing_key, valid_batch_input):
        """Retryable error codes MUST have retryable=True."""
        # TTL_INVALID is retryable
        valid_batch_input["targets"][0]["ttl_seconds"] = 8640000  # Exceeds max

        issuer = BatchPermitIssuer(
            signing_key=signing_key,
            failure_strategy=FailureStrategy.BEST_EFFORT,
        )
        result = issuer.issue_batch(valid_batch_input)

        assert len(result["tombstones"]) == 1
        assert result["tombstones"][0]["retryable"] is True

    def test_non_retryable_errors_are_marked(self, signing_key):
        """Non-retryable error codes MUST have retryable=False."""
        issuer = BatchPermitIssuer(
            signing_key=signing_key,
            failure_strategy=FailureStrategy.BEST_EFFORT,
        )

        # I001 (ISSUE_CONDITION_NOT_MET) is non-retryable
        result = issuer.issue_batch({
            "targets": [
                {
                    "target_id": "t1",
                    "repo_url": "url",
                    "commit_sha": "sha",
                    "run_id": "r",
                    "intent_id": "i",
                    "ttl_seconds": 3600,
                }
            ],
            "final_gate_decision": "FAILED",  # This triggers I001
            "audit_pack_ref": "audit-001",
        })

        assert len(result["tombstones"]) == 1
        assert result["tombstones"][0]["retryable"] is False


# =============================================================================
# Tests for Evidence Generation
# =============================================================================

class TestEvidenceGeneration:
    """Tests for evidence reference generation."""

    def test_batch_evidence_ref_generated(self, signing_key, five_target_batch_input):
        """Batch MUST generate batch-level evidence reference."""
        issuer = BatchPermitIssuer(signing_key=signing_key)
        result = issuer.issue_batch(five_target_batch_input)

        evidence = result["batch_evidence_ref"]
        assert "issue_key" in evidence
        assert "source_locator" in evidence
        assert "content_hash" in evidence
        assert "tool_revision" in evidence
        assert "timestamp" in evidence
        assert "decision_snapshot" in evidence

    def test_batch_evidence_contains_decision(self, signing_key, five_target_batch_input):
        """Batch evidence MUST contain decision snapshot."""
        issuer = BatchPermitIssuer(signing_key=signing_key)
        result = issuer.issue_batch(five_target_batch_input)

        snapshot = result["batch_evidence_ref"]["decision_snapshot"]
        assert snapshot["batch_decision"] == "SUCCESS"
        assert snapshot["successful_count"] == 5
        assert snapshot["failed_count"] == 0

    def test_target_results_have_permit_ids(self, signing_key, five_target_batch_input):
        """Successful targets MUST have permit_id."""
        issuer = BatchPermitIssuer(signing_key=signing_key)
        result = issuer.issue_batch(five_target_batch_input)

        for target_result in result["target_results"]:
            assert target_result["success"] is True
            assert target_result["permit_id"] is not None


# =============================================================================
# Tests for Convenience Function
# =============================================================================

class TestConvenienceFunction:
    """Tests for issue_batch_permits convenience function."""

    def test_convenience_function_works(self, signing_key, valid_target):
        """Convenience function MUST work with basic parameters."""
        result = issue_batch_permits(
            targets=[valid_target],
            final_gate_decision="PASSED",
            audit_pack_ref="audit-001",
            signing_key=signing_key,
            failure_strategy="all_or_nothing",
        )

        assert result["batch_decision"] == "SUCCESS"

    def test_strategy_override_works(self, signing_key, valid_target):
        """failure_strategy override MUST work."""
        result = issue_batch_permits(
            targets=[valid_target],
            final_gate_decision="PASSED",
            audit_pack_ref="audit-001",
            signing_key=signing_key,
            failure_strategy="best_effort",
        )

        assert result["failure_strategy"] == "best_effort"


# =============================================================================
# Edge Case Tests
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_single_target_batch(self, signing_key, valid_target):
        """Single target batch MUST work (min batch size = 1)."""
        issuer = BatchPermitIssuer(signing_key=signing_key)
        result = issuer.issue_batch({
            "targets": [valid_target],
            "final_gate_decision": "PASSED",
            "audit_pack_ref": "audit-001",
        })

        assert result["total_targets"] == 1
        assert result["batch_decision"] == "SUCCESS"

    def test_two_target_batch(self, signing_key, valid_batch_input):
        """Two target batch MUST work (original 2-target case)."""
        issuer = BatchPermitIssuer(signing_key=signing_key)
        result = issuer.issue_batch(valid_batch_input)

        assert result["total_targets"] == 2
        assert result["batch_decision"] == "SUCCESS"

    def test_five_target_batch(self, signing_key, five_target_batch_input):
        """Five target batch MUST work (max batch size = 5)."""
        issuer = BatchPermitIssuer(signing_key=signing_key)
        result = issuer.issue_batch(five_target_batch_input)

        assert result["total_targets"] == 5
        assert result["batch_decision"] == "SUCCESS"

    def test_strategy_override_per_request(self, signing_key, valid_batch_input):
        """failure_strategy MUST be overridable per request."""
        issuer = BatchPermitIssuer(
            signing_key=signing_key,
            failure_strategy=FailureStrategy.ALL_OR_NOTHING,
        )

        # Override to best_effort
        valid_batch_input["failure_strategy"] = "best_effort"
        result = issuer.issue_batch(valid_batch_input)

        assert result["failure_strategy"] == "best_effort"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
