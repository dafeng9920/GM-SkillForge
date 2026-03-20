"""
T1 Intake Compliance Tests

This test suite validates T1 requirements:
1. intent_id MUST be from approved whitelist
2. repo_url MUST be provided
3. commit_sha MUST be provided (min 7 chars)
4. Branch-only input MUST be rejected

Run:
    cd d:/GM-SkillForge
    python -m pytest tests/gates/test_t1_intake_compliance.py -v
    python tests/gates/test_t1_intake_compliance.py
"""
from __future__ import annotations

import sys
import hashlib
import json
from pathlib import Path
from typing import Any

# Setup paths
project_root = Path(__file__).parent.parent.parent
skillforge_src = project_root / "skillforge" / "src"
contracts_path = skillforge_src / "contracts"

sys.path.insert(0, str(skillforge_src))
sys.path.insert(0, str(contracts_path))

from skillforge.src.skills.gates.gate_intake import GateIntakeRepo, APPROVED_INTENTS
from intake_request import (
    IntakeRequest,
    validate_intake_request,
    create_intake_request,
    ErrorCode,
)


class TestT1_CommitShaRequired:
    """T1: commit_sha is required - missing commit_sha must fail."""

    def test_missing_commit_sha_rejected_by_gate(self):
        """Gate must reject input without commit_sha."""
        gate = GateIntakeRepo()
        input_data = {
            "intent_id": "AUDIT_REPO_SKILL",
            "repo_url": "https://github.com/test/repo",
        }
        errors = gate.validate_input(input_data)
        assert len(errors) > 0, "Expected validation errors for missing commit_sha"
        assert any("commit_sha" in e for e in errors), "Expected commit_sha error"

    def test_missing_commit_sha_rejected_by_intake_request(self):
        """IntakeRequest must reject input without commit_sha."""
        result = validate_intake_request({
            "intent_id": "AUDIT_REPO_SKILL",
            "repo_url": "https://github.com/test/repo",
        })
        assert not result.valid, "Expected validation to fail without commit_sha"
        assert any("commit_sha" in e for e in result.errors)

    def test_valid_commit_sha_accepted(self):
        """Valid commit_sha should be accepted."""
        gate = GateIntakeRepo()
        input_data = {
            "intent_id": "AUDIT_REPO_SKILL",
            "repo_url": "https://github.com/test/repo",
            "commit_sha": "abc123def456",
        }
        errors = gate.validate_input(input_data)
        assert not any("commit_sha" in e for e in errors), "Unexpected commit_sha error"

    def test_short_sha_accepted_min_7_chars(self):
        """Short SHA (min 7 chars) should be accepted."""
        gate = GateIntakeRepo()
        input_data = {
            "intent_id": "AUDIT_REPO_SKILL",
            "repo_url": "https://github.com/test/repo",
            "commit_sha": "abc1234",  # 7 chars
        }
        errors = gate.validate_input(input_data)
        assert not any("commit_sha" in e for e in errors), "7-char SHA should be accepted"

    def test_invalid_commit_sha_rejected(self):
        """Invalid commit_sha must be rejected."""
        gate = GateIntakeRepo()
        input_data = {
            "intent_id": "AUDIT_REPO_SKILL",
            "repo_url": "https://github.com/test/repo",
            "commit_sha": "too-short",
        }
        errors = gate.validate_input(input_data)
        assert any("commit_sha" in e for e in errors), "Expected commit_sha validation error"


class TestT1_IntentIdWhitelist:
    """T1: intent_id must be from approved whitelist."""

    def test_unknown_intent_id_rejected(self):
        """Unknown intent_id must be rejected."""
        gate = GateIntakeRepo()
        input_data = {
            "intent_id": "UNKNOWN_INTENT",
            "repo_url": "https://github.com/test/repo",
            "commit_sha": "abc123def456",
        }
        errors = gate.validate_input(input_data)
        assert len(errors) > 0, "Expected validation errors for unknown intent_id"
        assert any("not_approved" in e.lower() or "approved" in e.lower() for e in errors), \
            "Expected intent_id approval error"

    def test_missing_intent_id_rejected(self):
        """Missing intent_id must be rejected."""
        gate = GateIntakeRepo()
        input_data = {
            "repo_url": "https://github.com/test/repo",
            "commit_sha": "abc123def456",
        }
        errors = gate.validate_input(input_data)
        assert any("intent_id" in e for e in errors), "Expected intent_id error"

    def test_approved_intent_id_accepted(self):
        """Approved intent_id should be accepted."""
        for intent_id in APPROVED_INTENTS:
            gate = GateIntakeRepo()
            input_data = {
                "intent_id": intent_id,
                "repo_url": "https://github.com/test/repo",
                "commit_sha": "abc123def456",
            }
            errors = gate.validate_input(input_data)
            intent_errors = [e for e in errors if "intent_id" in e]
            assert len(intent_errors) == 0, f"Approved intent {intent_id} was rejected: {intent_errors}"


class TestT1_RepoUrlRequired:
    """T1: repo_url is required."""

    def test_missing_repo_url_rejected(self):
        """Missing repo_url must be rejected."""
        gate = GateIntakeRepo()
        input_data = {
            "intent_id": "AUDIT_REPO_SKILL",
            "commit_sha": "abc123def456",
        }
        errors = gate.validate_input(input_data)
        assert any("repo_url" in e for e in errors), "Expected repo_url error"

    def test_invalid_repo_url_rejected(self):
        """Invalid repo_url format must be rejected."""
        gate = GateIntakeRepo()
        input_data = {
            "intent_id": "AUDIT_REPO_SKILL",
            "repo_url": "not-a-url",
            "commit_sha": "abc123def456",
        }
        errors = gate.validate_input(input_data)
        assert any("repo_url" in e for e in errors), "Expected repo_url validation error"


class TestT1_NoBranchOnlyInput:
    """T1: Branch-only input must be rejected."""

    def test_branch_without_commit_sha_rejected(self):
        """Branch parameter without commit_sha must be rejected."""
        gate = GateIntakeRepo()
        input_data = {
            "intent_id": "AUDIT_REPO_SKILL",
            "repo_url": "https://github.com/test/repo",
            "branch": "main",  # branch without commit_sha
        }
        errors = gate.validate_input(input_data)
        assert len(errors) > 0, "Expected errors for branch-only input"
        assert any("branch" in e.lower() for e in errors), "Expected branch-only error"

    def test_branch_with_commit_sha_not_error(self):
        """Branch with commit_sha should not trigger branch-only error."""
        gate = GateIntakeRepo()
        input_data = {
            "intent_id": "AUDIT_REPO_SKILL",
            "repo_url": "https://github.com/test/repo",
            "branch": "main",
            "commit_sha": "abc123def456",
        }
        errors = gate.validate_input(input_data)
        branch_errors = [e for e in errors if "branch" in e.lower()]
        assert len(branch_errors) == 0, "Branch with commit_sha should not be rejected as branch-only"


class TestT1_DeterministicOutput:
    """T1: Same input must produce same output."""

    def test_same_input_produces_same_hash(self):
        """Same input must produce same content hash."""
        input_data = {
            "intent_id": "AUDIT_REPO_SKILL",
            "repo_url": "https://github.com/test/repo",
            "commit_sha": "abc123def456789",
        }

        # Create two requests from same input
        request1 = create_intake_request(**input_data)
        request2 = create_intake_request(**input_data)

        # Hashes should be identical
        hash1 = request1.compute_hash()
        hash2 = request2.compute_hash()
        assert hash1 == hash2, f"Same input produced different hashes: {hash1} vs {hash2}"

    def test_different_commit_sha_produces_different_hash(self):
        """Different commit_sha must produce different hash."""
        base_input = {
            "intent_id": "AUDIT_REPO_SKILL",
            "repo_url": "https://github.com/test/repo",
            "commit_sha": "abc123def456789",
        }

        request1 = create_intake_request(**base_input)

        # Change commit_sha
        base_input["commit_sha"] = "def456abc123789"
        request2 = create_intake_request(**base_input)

        hash1 = request1.compute_hash()
        hash2 = request2.compute_hash()
        assert hash1 != hash2, "Different commit_sha should produce different hash"

    def test_serialization_consistency(self):
        """JSON serialization must be deterministic."""
        input_data = {
            "intent_id": "AUDIT_REPO_SKILL",
            "repo_url": "https://github.com/test/repo",
            "commit_sha": "abc123def456789",
        }

        request = create_intake_request(**input_data)

        # Serialize multiple times
        json1 = request.to_json()
        json2 = request.to_json()

        assert json1 == json2, "JSON serialization must be deterministic"


class TestT1_IntakeRequestJsonGeneration:
    """T1: intake_request.json generation."""

    def test_intake_request_json_structure(self):
        """Generated intake_request.json must have required fields."""
        input_data = {
            "intent_id": "AUDIT_REPO_SKILL",
            "repo_url": "https://github.com/test/repo",
            "commit_sha": "abc123def456789",
        }

        request = create_intake_request(**input_data)
        data = request.to_dict()

        # Verify required fields
        assert "intent_id" in data, "intent_id missing from output"
        assert "repo_url" in data, "repo_url missing from output"
        assert "commit_sha" in data, "commit_sha missing from output"
        assert data["intent_id"] == "AUDIT_REPO_SKILL"
        assert data["repo_url"] == "https://github.com/test/repo"
        assert data["commit_sha"] == "abc123def456789"

    def test_intake_request_auto_generates_fields(self):
        """Auto-generated fields (at_time, issue_key) must be present."""
        input_data = {
            "intent_id": "AUDIT_REPO_SKILL",
            "repo_url": "https://github.com/test/repo",
            "commit_sha": "abc123def456789",
        }

        request = create_intake_request(**input_data)
        data = request.to_dict()

        assert "at_time" in data, "at_time should be auto-generated"
        assert "issue_key" in data, "issue_key should be auto-generated"
        assert data["at_time"] is not None
        assert data["issue_key"] is not None


# ============================================================================
# Verification Script (can be run standalone)
# ============================================================================
def main():
    """Run T1 compliance checks and print results."""
    import tempfile

    print("=" * 60)
    print("T1 Intake Compliance Verification")
    print("=" * 60)

    passed = 0
    failed = 0

    # Test 1: Missing commit_sha fails
    print("\n[Test 1] Missing commit_sha must be rejected...")
    try:
        gate = GateIntakeRepo()
        errors = gate.validate_input({
            "intent_id": "AUDIT_REPO_SKILL",
            "repo_url": "https://github.com/test/repo",
        })
        if any("commit_sha" in e for e in errors):
            print("  PASS: Missing commit_sha correctly rejected")
            passed += 1
        else:
            print("  FAIL: Missing commit_sha was not rejected")
            failed += 1
    except Exception as e:
        print(f"  FAIL: Exception: {e}")
        failed += 1

    # Test 2: Unknown intent_id fails
    print("\n[Test 2] Unknown intent_id must be rejected...")
    try:
        gate = GateIntakeRepo()
        errors = gate.validate_input({
            "intent_id": "UNKNOWN_INTENT",
            "repo_url": "https://github.com/test/repo",
            "commit_sha": "abc123def456",
        })
        if any("approved" in e.lower() for e in errors):
            print("  PASS: Unknown intent_id correctly rejected")
            passed += 1
        else:
            print("  FAIL: Unknown intent_id was not rejected")
            failed += 1
    except Exception as e:
        print(f"  FAIL: Exception: {e}")
        failed += 1

    # Test 3: Branch-only input fails
    print("\n[Test 3] Branch-only input must be rejected...")
    try:
        gate = GateIntakeRepo()
        errors = gate.validate_input({
            "intent_id": "AUDIT_REPO_SKILL",
            "repo_url": "https://github.com/test/repo",
            "branch": "main",
        })
        if any("branch" in e.lower() for e in errors):
            print("  PASS: Branch-only input correctly rejected")
            passed += 1
        else:
            print("  FAIL: Branch-only input was not rejected")
            failed += 1
    except Exception as e:
        print(f"  FAIL: Exception: {e}")
        failed += 1

    # Test 4: Same input produces same output
    print("\n[Test 4] Same input must produce same output...")
    try:
        input_data = {
            "intent_id": "AUDIT_REPO_SKILL",
            "repo_url": "https://github.com/test/repo",
            "commit_sha": "abc123def456789",
        }
        request1 = create_intake_request(**input_data)
        request2 = create_intake_request(**input_data)

        if request1.compute_hash() == request2.compute_hash():
            print("  PASS: Same input produces same hash")
            passed += 1
        else:
            print("  FAIL: Same input produced different hashes")
            failed += 1
    except Exception as e:
        print(f"  FAIL: Exception: {e}")
        failed += 1

    # Test 5: Valid input accepted
    print("\n[Test 5] Valid input must be accepted...")
    try:
        gate = GateIntakeRepo()
        errors = gate.validate_input({
            "intent_id": "AUDIT_REPO_SKILL",
            "repo_url": "https://github.com/test/repo",
            "commit_sha": "abc123def456789",
        })
        if len(errors) == 0:
            print("  PASS: Valid input correctly accepted")
            passed += 1
        else:
            print(f"  FAIL: Valid input was rejected: {errors}")
            failed += 1
    except Exception as e:
        print(f"  FAIL: Exception: {e}")
        failed += 1

    # Test 6: Generate intake_request.json
    print("\n[Test 6] Generate intake_request.json...")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "intake_request.json"
            request = create_intake_request(
                intent_id="AUDIT_REPO_SKILL",
                repo_url="https://github.com/test/repo",
                commit_sha="abc123def456789",
            )
            request.save(output_path)

            if output_path.exists():
                with open(output_path) as f:
                    data = json.load(f)
                if all(k in data for k in ["intent_id", "repo_url", "commit_sha"]):
                    print(f"  PASS: intake_request.json generated")
                    passed += 1
                else:
                    print("  FAIL: Generated JSON missing required fields")
                    failed += 1
            else:
                print("  FAIL: intake_request.json was not created")
                failed += 1
    except Exception as e:
        print(f"  FAIL: Exception: {e}")
        failed += 1

    # Summary
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
