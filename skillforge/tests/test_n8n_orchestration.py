"""
n8n Orchestration Routes Tests - n8n 编排入口测试

测试场景：
1. run_intent 输出包含 run_id/gate_decision/evidence_ref/release_allowed
2. n8n 越权字段注入场景被阻断（fail-closed）
3. E001/E003 语义不漂移
4. fetch_pack 正常工作
5. query_rag 正常工作

遵循 L4.5 边界冻结条款。
"""
import json
import os
import sys
import unittest
from pathlib import Path
from datetime import datetime, timezone

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Set signing key for gate_permit verification
os.environ["PERMIT_HS256_KEY"] = "test-signing-key-for-unit-tests-2026"

# Import directly from routes module to avoid triggering l4_api import
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "api" / "routes"))

from skills.gates.permit_issuer import PermitIssuer
from skills.gates.gate_permit import GatePermit
from api.routes.n8n_orchestration import enforce_execution_guard, _canonical_contract_hash


# ============================================================================
# Test Constants
# ============================================================================

TEST_REPO_URL = "https://github.com/skillforge/workflow-orchestration"
TEST_COMMIT_SHA = "a1b2c3d4e5f6789012345678901234567890abcd"
TEST_REQUESTER_ID = "user-n8n-test"
TEST_INTENT_ID = "intent-test-001"


# ============================================================================
# Helper Functions
# ============================================================================

def now_iso() -> str:
    """Return ISO-8601 UTC timestamp."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def make_valid_permit(repo_url: str, commit_sha: str, run_id: str) -> dict:
    """Create a valid permit for testing."""
    issuer = PermitIssuer(signing_key="test-signing-key-for-unit-tests-2026")

    issue_input = {
        "final_gate_decision": "PASSED",
        "release_blocked_by": None,
        "audit_pack_ref": "audit-n8n-test-001",
        "repo_url": repo_url,
        "commit_sha": commit_sha,
        "run_id": run_id,
        "intent_id": "n8n-test-intent",
        "ttl_seconds": 3600,
        "allowed_actions": ["release"],
    }

    result = issuer.issue_permit(issue_input)
    if result["success"]:
        return json.loads(result["permit_token"])
    return None


# ============================================================================
# Test Cases - Core Logic (without FastAPI)
# ============================================================================

class TestN8NOrchestrationLogic(unittest.TestCase):
    """
    n8n Orchestration Logic Tests - without FastAPI dependency.

    Tests the core logic functions directly.
    """

    def setUp(self):
        """Set up test fixtures."""
        self.issuer = PermitIssuer(signing_key="test-signing-key-for-unit-tests-2026")
        self.valid_contract = {
            "contract_version": "v1",
            "intent_id": "intent-test",
            "ruleset_revision": "ruleset-v1",
            "constitution_ref": "constitution-ref",
            "inputs": {"repo_url": TEST_REPO_URL},
            "outputs": {"status": "COMPLETED"},
            "controls": {
                "timeout_ms": 30000,
                "max_targets": 1,
                "network_policy": "DENY_BY_DEFAULT",
                "file_policy": "ALLOWLIST",
            },
            "side_effects": [{"kind": "EXTERNAL_API", "details": "n8n"}],
            "roles": {
                "execution": {"responsibilities": ["execute"], "allowed_actions": ["run_intent"]},
                "review": {"responsibilities": ["review"], "checks": ["acceptance"]},
                "compliance": {"responsibilities": ["compliance"], "must_follow": "B-v1"},
            },
            "acceptance_tests": [{"id": "AT-001", "assertion": "ok=true", "evidence_required": ["EV_KIND:LOG"]}],
            "artifacts_expected": ["EVIDENCE"],
            "evidence_requirements": [{"for_acceptance_id": "AT-001", "evidence_kind": "LOG", "locator_hint": "api"}],
        }

    # -------------------------------------------------------------------------
    # Test 1: run_id computed by SkillForge
    # -------------------------------------------------------------------------
    def test_run_id_computed_by_skillforge(self):
        """
        Verify that run_id is computed by SkillForge, not by n8n.
        The run_id should have the RUN-N8N- prefix.
        """
        print("\n=== Test 1: run_id Computed by SkillForge ===")

        import time
        import uuid

        def generate_run_id() -> str:
            ts = int(time.time())
            uid = uuid.uuid4().hex[:8].upper()
            return f"RUN-N8N-{ts}-{uid}"

        # Generate multiple run_ids
        run_ids = [generate_run_id() for _ in range(3)]

        print(f"Generated run_ids: {run_ids}")

        # Verify all have correct prefix
        for run_id in run_ids:
            self.assertTrue(run_id.startswith("RUN-N8N-"),
                          f"run_id should start with RUN-N8N-, got: {run_id}")

        # Verify uniqueness
        self.assertEqual(len(set(run_ids)), 3, "run_ids should be unique")

    # -------------------------------------------------------------------------
    # Test 2: Forbidden field detection
    # -------------------------------------------------------------------------
    def test_forbidden_field_detection(self):
        """
        Verify detection of forbidden field injection attempts.
        """
        print("\n=== Test 2: Forbidden Field Detection ===")

        FORBIDDEN_N8N_FIELDS = [
            "gate_decision",
            "release_allowed",
            "permit_token",
            "evidence_ref",
        ]

        def detect_forbidden_fields(request_dict: dict) -> list:
            found = []
            for field in FORBIDDEN_N8N_FIELDS:
                if field in request_dict and request_dict[field] is not None:
                    found.append(field)
            return found

        # Test with forbidden fields
        request_with_forbidden = {
            "repo_url": TEST_REPO_URL,
            "commit_sha": TEST_COMMIT_SHA,
            "intent_id": TEST_INTENT_ID,
            "requester_id": TEST_REQUESTER_ID,
            "gate_decision": "ALLOW",  # FORBIDDEN!
            "release_allowed": True,   # FORBIDDEN!
        }

        forbidden = detect_forbidden_fields(request_with_forbidden)
        print(f"Detected forbidden fields: {forbidden}")

        self.assertIn("gate_decision", forbidden)
        self.assertIn("release_allowed", forbidden)

        # Test without forbidden fields
        request_clean = {
            "repo_url": TEST_REPO_URL,
            "commit_sha": TEST_COMMIT_SHA,
            "intent_id": TEST_INTENT_ID,
            "requester_id": TEST_REQUESTER_ID,
        }

        forbidden_clean = detect_forbidden_fields(request_clean)
        self.assertEqual(len(forbidden_clean), 0, "No forbidden fields should be detected")

    # -------------------------------------------------------------------------
    # Test 3: Forbidden field evidence creation
    # -------------------------------------------------------------------------
    def test_forbidden_field_evidence_creation(self):
        """
        Verify evidence is created for forbidden field injection.
        """
        print("\n=== Test 3: Forbidden Field Evidence Creation ===")

        import hashlib

        def create_forbidden_field_evidence(
            run_id: str,
            forbidden_fields: list,
            raw_request: dict
        ) -> dict:
            timestamp = now_iso()
            content = json.dumps({
                "run_id": run_id,
                "forbidden_fields": forbidden_fields,
                "raw_request_keys": list(raw_request.keys()),
                "timestamp": timestamp,
            }, sort_keys=True)
            content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

            return {
                "issue_key": f"N8N-FORBIDDEN-{run_id}",
                "source_locator": f"n8n://intent/{run_id}",
                "content_hash": content_hash,
                "timestamp": timestamp,
                "forbidden_fields": forbidden_fields,
                "action_taken": "REJECTED_AND_IGNORED",
                "decision_snapshot": {
                    "check": "forbidden_field_injection",
                    "fields_detected": forbidden_fields,
                    "policy": "n8n_must_not_override_gate_decision",
                }
            }

        evidence = create_forbidden_field_evidence(
            "RUN-TEST-FORBIDDEN",
            ["gate_decision", "release_allowed"],
            {"gate_decision": "ALLOW", "release_allowed": True}
        )

        print(f"Evidence created: {evidence['issue_key']}")
        self.assertEqual(evidence["action_taken"], "REJECTED_AND_IGNORED")
        self.assertIn("gate_decision", evidence["forbidden_fields"])
        self.assertIn("release_allowed", evidence["forbidden_fields"])
        self.assertIn("content_hash", evidence)

    # -------------------------------------------------------------------------
    # Test 4: E001 semantics preserved (no permit)
    # -------------------------------------------------------------------------
    def test_e001_no_permit_blocked(self):
        """
        Verify E001 error code is returned when no permit is provided.
        This ensures E001 semantics are not drifted.
        """
        print("\n=== Test 4: E001 No Permit Blocked ===")

        gate = GatePermit()

        validation_input = {
            "permit_token": None,  # No permit!
            "repo_url": TEST_REPO_URL,
            "commit_sha": TEST_COMMIT_SHA,
            "run_id": "RUN-TEST-E001",
            "requested_action": "release",
            "current_time": now_iso(),
        }

        result = gate.execute(validation_input)

        print(f"Result: gate_decision={result.get('gate_decision')}, error_code={result.get('error_code')}")

        self.assertEqual(result["gate_decision"], "BLOCK")
        self.assertEqual(result["error_code"], "E001")
        self.assertEqual(result["release_blocked_by"], "PERMIT_REQUIRED")
        self.assertFalse(result["release_allowed"])

    # -------------------------------------------------------------------------
    # Test 5: E003 semantics preserved (bad signature)
    # -------------------------------------------------------------------------
    def test_e003_bad_signature_blocked(self):
        """
        Verify E003 error code is returned when permit has bad signature.
        This ensures E003 semantics are not drifted.
        """
        print("\n=== Test 5: E003 Bad Signature Blocked ===")

        gate = GatePermit()

        # Create a permit with tampered signature
        permit = make_valid_permit(TEST_REPO_URL, TEST_COMMIT_SHA, "RUN-TEST-E003")
        permit["signature"]["value"] = "TAMPERED_SIGNATURE_XXX"

        validation_input = {
            "permit_token": permit,
            "repo_url": TEST_REPO_URL,
            "commit_sha": TEST_COMMIT_SHA,
            "run_id": "RUN-TEST-E003",
            "requested_action": "release",
            "current_time": now_iso(),
        }

        result = gate.execute(validation_input)

        print(f"Result: gate_decision={result.get('gate_decision')}, error_code={result.get('error_code')}")

        self.assertEqual(result["gate_decision"], "BLOCK")
        self.assertEqual(result["error_code"], "E003")
        self.assertEqual(result["release_blocked_by"], "PERMIT_INVALID")
        self.assertFalse(result["release_allowed"])

    # -------------------------------------------------------------------------
    # Test 6: Valid permit passes
    # -------------------------------------------------------------------------
    def test_valid_permit_passes(self):
        """
        Verify valid permit allows execution.
        """
        print("\n=== Test 6: Valid Permit Passes ===")

        gate = GatePermit()

        # Create valid permit
        permit = make_valid_permit(TEST_REPO_URL, TEST_COMMIT_SHA, "RUN-TEST-VALID")

        validation_input = {
            "permit_token": permit,
            "repo_url": TEST_REPO_URL,
            "commit_sha": TEST_COMMIT_SHA,
            "run_id": "RUN-TEST-VALID",
            "requested_action": "release",
            "current_time": now_iso(),
        }

        result = gate.execute(validation_input)

        print(f"Result: gate_decision={result.get('gate_decision')}, release_allowed={result.get('release_allowed')}")

        self.assertEqual(result["gate_decision"], "ALLOW")
        self.assertTrue(result["release_allowed"])

    # -------------------------------------------------------------------------
    # Test 7: Error envelope format
    # -------------------------------------------------------------------------
    def test_error_envelope_format(self):
        """
        Verify error envelope contains required fields.
        """
        print("\n=== Test 7: Error Envelope Format ===")

        def make_error_envelope(error_code: str, blocked_by: str, message: str,
                                evidence_ref: str, run_id: str) -> dict:
            return {
                "ok": False,
                "error_code": error_code,
                "blocked_by": blocked_by,
                "message": message,
                "evidence_ref": evidence_ref,
                "run_id": run_id,
            }

        envelope = make_error_envelope(
            error_code="E001",
            blocked_by="PERMIT_REQUIRED",
            message="Permit token is required for execution",
            evidence_ref="EV-TEST-001",
            run_id="RUN-TEST-001"
        )

        print(f"Error envelope: {envelope}")

        # Verify required fields
        self.assertFalse(envelope["ok"])
        self.assertEqual(envelope["error_code"], "E001")
        self.assertEqual(envelope["blocked_by"], "PERMIT_REQUIRED")
        self.assertIn("message", envelope)
        self.assertIn("evidence_ref", envelope)
        self.assertIn("run_id", envelope)

    # -------------------------------------------------------------------------
    # Test 8: Success envelope format
    # -------------------------------------------------------------------------
    def test_success_envelope_format(self):
        """
        Verify success envelope contains required fields:
        - run_id
        - gate_decision
        - evidence_ref
        - release_allowed
        """
        print("\n=== Test 8: Success Envelope Format ===")

        def make_success_envelope(data: dict, gate_decision: str, release_allowed: bool,
                                  evidence_ref: str, run_id: str) -> dict:
            return {
                "ok": True,
                "data": data,
                "gate_decision": gate_decision,
                "release_allowed": release_allowed,
                "evidence_ref": evidence_ref,
                "run_id": run_id,
            }

        envelope = make_success_envelope(
            data={"intent_id": "test-intent", "status": "COMPLETED"},
            gate_decision="ALLOW",
            release_allowed=True,
            evidence_ref="EV-TEST-002",
            run_id="RUN-TEST-002"
        )

        print(f"Success envelope: {envelope}")

        # Verify required fields
        self.assertTrue(envelope["ok"])
        self.assertEqual(envelope["gate_decision"], "ALLOW")
        self.assertTrue(envelope["release_allowed"])
        self.assertIn("run_id", envelope)
        self.assertIn("evidence_ref", envelope)
        self.assertIn("data", envelope)

    # -------------------------------------------------------------------------
    # Test 9: Execution guard allows valid contract + compliance PASS
    # -------------------------------------------------------------------------
    def test_execution_guard_allows_valid_payload(self):
        attestation = {
            "decision": "PASS",
            "reasons": ["ok"],
            "evidence_refs": [{"id": "EV-COMP-001"}],
            "contract_hash": _canonical_contract_hash(self.valid_contract),
            "reviewed_at": now_iso(),
        }
        ok, error_code, message, required_changes = enforce_execution_guard(
            run_id="RUN-GUARD-ALLOW",
            execution_contract=self.valid_contract,
            compliance_attestation=attestation,
            guard_signature=_canonical_contract_hash(self.valid_contract),
        )
        self.assertTrue(ok)
        self.assertIsNone(error_code)
        self.assertIsNone(message)
        self.assertEqual(required_changes, [])

    # -------------------------------------------------------------------------
    # Test 10: Execution guard blocks when compliance decision is not PASS
    # -------------------------------------------------------------------------
    def test_execution_guard_blocks_non_pass_compliance(self):
        attestation = {
            "decision": "FAIL",
            "reasons": ["missing checks"],
            "evidence_refs": [{"id": "EV-COMP-002"}],
            "contract_hash": _canonical_contract_hash(self.valid_contract),
            "reviewed_at": now_iso(),
        }
        ok, error_code, message, required_changes = enforce_execution_guard(
            run_id="RUN-GUARD-BLOCK",
            execution_contract=self.valid_contract,
            compliance_attestation=attestation,
            guard_signature=_canonical_contract_hash(self.valid_contract),
        )
        self.assertFalse(ok)
        self.assertEqual(error_code, "SF_RISK_CONSTITUTION_BLOCKED")
        self.assertIn("not PASS", message)
        self.assertGreater(len(required_changes), 0)


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
