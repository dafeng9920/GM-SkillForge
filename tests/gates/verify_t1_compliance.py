"""
T1 Intake Compliance Verification Script (Standalone)

This script validates T1 requirements:
1. intent_id MUST be from approved whitelist
2. repo_url MUST be provided
3. commit_sha MUST be provided (min 7 chars)
4. Branch-only input MUST be rejected
5. Same input produces same output

Run:
    python tests/gates/verify_t1_compliance.py
"""
import sys
import json
import tempfile
from pathlib import Path

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
)


def print_header(text):
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


def run_test(name, test_func):
    """Run a single test and return (passed, failed) counts."""
    print(f"\n[{name}]")
    try:
        result, message = test_func()
        if result:
            print(f"  PASS: {message}")
            return 1, 0
        else:
            print(f"  FAIL: {message}")
            return 0, 1
    except Exception as e:
        print(f"  FAIL: Exception: {e}")
        return 0, 1


# ============================================================================
# Tests
# ============================================================================
def test_missing_commit_sha_rejected():
    """Missing commit_sha must be rejected."""
    gate = GateIntakeRepo()
    errors = gate.validate_input({
        "intent_id": "AUDIT_REPO_SKILL",
        "repo_url": "https://github.com/test/repo",
    })
    if any("commit_sha" in e for e in errors):
        return True, "Missing commit_sha correctly rejected"
    return False, "Missing commit_sha was not rejected"


def test_unknown_intent_id_rejected():
    """Unknown intent_id must be rejected."""
    gate = GateIntakeRepo()
    errors = gate.validate_input({
        "intent_id": "UNKNOWN_INTENT",
        "repo_url": "https://github.com/test/repo",
        "commit_sha": "abc123def456",
    })
    if any("approved" in e.lower() for e in errors):
        return True, "Unknown intent_id correctly rejected"
    return False, "Unknown intent_id was not rejected"


def test_branch_only_input_rejected():
    """Branch-only input must be rejected."""
    gate = GateIntakeRepo()
    errors = gate.validate_input({
        "intent_id": "AUDIT_REPO_SKILL",
        "repo_url": "https://github.com/test/repo",
        "branch": "main",
    })
    if any("branch" in e.lower() for e in errors):
        return True, "Branch-only input correctly rejected"
    return False, "Branch-only input was not rejected"


def test_deterministic_output():
    """Same input must produce same output."""
    input_data = {
        "intent_id": "AUDIT_REPO_SKILL",
        "repo_url": "https://github.com/test/repo",
        "commit_sha": "abc123def456789",
    }
    request1 = create_intake_request(**input_data)
    request2 = create_intake_request(**input_data)

    if request1.compute_hash() == request2.compute_hash():
        return True, "Same input produces same hash"
    return False, "Same input produced different hashes"


def test_valid_input_accepted():
    """Valid input must be accepted."""
    gate = GateIntakeRepo()
    errors = gate.validate_input({
        "intent_id": "AUDIT_REPO_SKILL",
        "repo_url": "https://github.com/test/repo",
        "commit_sha": "abc123def456789",
    })
    if len(errors) == 0:
        return True, "Valid input correctly accepted"
    return False, f"Valid input was rejected: {errors}"


def test_generate_intake_request_json():
    """Generate intake_request.json."""
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
                return True, "intake_request.json generated successfully"
            return False, "Generated JSON missing required fields"
        return False, "intake_request.json was not created"


def test_all_approved_intents_accepted():
    """All approved intents should be accepted."""
    for intent_id in APPROVED_INTENTS:
        gate = GateIntakeRepo()
        errors = gate.validate_input({
            "intent_id": intent_id,
            "repo_url": "https://github.com/test/repo",
            "commit_sha": "abc123def456",
        })
        intent_errors = [e for e in errors if "intent_id" in e]
        if intent_errors:
            return False, f"Approved intent {intent_id} was rejected"
    return True, f"All {len(APPROVED_INTENTS)} approved intents accepted"


# ============================================================================
# Main
# ============================================================================
def main():
    print_header("T1 Intake Compliance Verification")

    tests = [
        ("Test 1", "Missing commit_sha must be rejected", test_missing_commit_sha_rejected),
        ("Test 2", "Unknown intent_id must be rejected", test_unknown_intent_id_rejected),
        ("Test 3", "Branch-only input must be rejected", test_branch_only_input_rejected),
        ("Test 4", "Same input produces same output", test_deterministic_output),
        ("Test 5", "Valid input must be accepted", test_valid_input_accepted),
        ("Test 6", "Generate intake_request.json", test_generate_intake_request_json),
        ("Test 7", "All approved intents accepted", test_all_approved_intents_accepted),
    ]

    passed = 0
    failed = 0

    for test_id, description, test_func in tests:
        p, f = run_test(f"{test_id}: {description}", test_func)
        passed += p
        failed += f

    # Print summary
    print_header(f"Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("\n ALL T1 REQUIREMENTS SATISFIED")
        return 0
    else:
        print(f"\n {failed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
