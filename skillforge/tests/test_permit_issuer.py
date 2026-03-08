"""
Test suite for PermitIssuer - Permit 签发服务测试矩阵。

测试矩阵（S1-S8）：
- S1: 正常签发 - success=true, permit_token 非空
- S2: 决策不满足签发条件 - I001, permit_token 为空
- S3: subject 缺字段 - I002, permit_token 为空
- S4: TTL 非法（0或负数）- I003
- S5: TTL 超上限 - I003
- S6: 签名密钥缺失 - I004
- S7: 签名异常 - I005
- S8: 联通验证 - issuer 产物被 GatePermit 验证为 VALID

遵循 permit_contract_v1.yml 契约。
"""
import copy
import json
import os
import unittest
from typing import Any

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Set signing key for gate_permit verification (must be set before import)
os.environ["PERMIT_HS256_KEY"] = "test-signing-key-for-unit-tests-2026"

from skills.gates.permit_issuer import (
    PermitIssuer,
    issue_permit,
    ISSUER_ERROR_CODES,
    ISSUER_ID,
    ISSUER_TYPE,
)
from skills.gates.gate_permit import (
    GatePermit,
    validate_permit,
)


# ============================================================================
# Test Fixtures
# ============================================================================

# Test signing key (DO NOT use in production)
TEST_SIGNING_KEY = "test-signing-key-for-unit-tests-2026"

VALID_ISSUE_INPUT: dict[str, Any] = {
    "final_gate_decision": "PASSED_NO_PERMIT",
    "release_blocked_by": None,
    "audit_pack_ref": "audit-10465f76",
    "repo_url": "https://github.com/local/NEW-GM",
    "commit_sha": "4ea179d31a66fc2616f0cf953cd0e5c5c43d8ea8",
    "run_id": "RUN-20260218-001",
    "intent_id": "generate_skill_from_repo",
    "allowed_actions": ["release"],
    "at_time": "2026-02-18T08:41:10Z",
    "ttl_seconds": 3600,
    "environment": "development",
    "gate_profile": "batch2_8gate",
    "gate_count": 8,
    "evidence_count": 8,
}

EXECUTION_CONTEXT = {
    "repo_url": "https://github.com/local/NEW-GM",
    "commit_sha": "4ea179d31a66fc2616f0cf953cd0e5c5c43d8ea8",
    "run_id": "RUN-20260218-001",
    "requested_action": "release",
}


# ============================================================================
# Test Cases
# ============================================================================

class TestPermitIssuer(unittest.TestCase):
    """Test suite for PermitIssuer."""

    def setUp(self):
        """Set up test fixtures."""
        self.issuer = PermitIssuer(signing_key=TEST_SIGNING_KEY)

    # -------------------------------------------------------------------------
    # S1: 正常签发
    # -------------------------------------------------------------------------
    def test_s1_normal_issuance(self):
        """S1: 正常签发 - success=true, permit_token 非空"""
        result = self.issuer.issue_permit(VALID_ISSUE_INPUT)

        # Check success
        self.assertTrue(result["success"])
        self.assertIsNotNone(result["permit_token"])
        self.assertIsNotNone(result["permit_id"])
        self.assertIsNotNone(result["issued_at"])
        self.assertIsNotNone(result["expires_at"])
        self.assertIsNone(result["error_code"])
        self.assertIsNone(result["error_message"])

        # Check evidence_refs
        self.assertEqual(len(result["evidence_refs"]), 1)
        evidence = result["evidence_refs"][0]
        self.assertIn("issue_key", evidence)
        self.assertIn("source_locator", evidence)
        self.assertIn("content_hash", evidence)
        self.assertIn("tool_revision", evidence)
        self.assertIn("timestamp", evidence)

        # Check signature
        self.assertIsNotNone(result["signature"])
        self.assertEqual(result["signature"]["algo"], "HS256")
        self.assertEqual(result["signature"]["key_id"], "skillforge-permit-key-2026")

        # Parse and validate permit structure
        permit = json.loads(result["permit_token"])
        self.assertEqual(permit["issuer"]["issuer_id"], ISSUER_ID)
        self.assertEqual(permit["issuer"]["issuer_type"], ISSUER_TYPE)
        self.assertEqual(permit["subject"]["repo_url"], VALID_ISSUE_INPUT["repo_url"])
        self.assertEqual(permit["subject"]["commit_sha"], VALID_ISSUE_INPUT["commit_sha"])
        self.assertEqual(permit["subject"]["run_id"], VALID_ISSUE_INPUT["run_id"])
        self.assertEqual(permit["subject"]["intent_id"], VALID_ISSUE_INPUT["intent_id"])
        self.assertIn("release", permit["scope"]["allowed_actions"])
        self.assertFalse(permit["revocation"]["revoked"])

    # -------------------------------------------------------------------------
    # S2: 决策不满足签发条件
    # -------------------------------------------------------------------------
    def test_s2_decision_not_issuable_rejected(self):
        """S2: final_gate_decision=REJECTED - I001, permit_token 为空"""
        input_data = copy.deepcopy(VALID_ISSUE_INPUT)
        input_data["final_gate_decision"] = "REJECTED"

        result = self.issuer.issue_permit(input_data)

        self.assertFalse(result["success"])
        self.assertIsNone(result["permit_token"])
        self.assertEqual(result["error_code"], "I001")
        self.assertIn("final_gate_decision", result["error_message"])

    def test_s2_decision_not_issuable_require_hitl(self):
        """S2: final_gate_decision=REQUIRE_HITL - I001"""
        input_data = copy.deepcopy(VALID_ISSUE_INPUT)
        input_data["final_gate_decision"] = "REQUIRE_HITL"

        result = self.issuer.issue_permit(input_data)

        self.assertFalse(result["success"])
        self.assertIsNone(result["permit_token"])
        self.assertEqual(result["error_code"], "I001")

    def test_s2_release_blocked(self):
        """S2: release_blocked_by 非空 - I001"""
        input_data = copy.deepcopy(VALID_ISSUE_INPUT)
        input_data["release_blocked_by"] = "PERMIT_REQUIRED"

        result = self.issuer.issue_permit(input_data)

        self.assertFalse(result["success"])
        self.assertIsNone(result["permit_token"])
        self.assertEqual(result["error_code"], "I001")
        self.assertIn("release_blocked_by", result["error_message"])

    # -------------------------------------------------------------------------
    # S3: subject 缺字段
    # -------------------------------------------------------------------------
    def test_s3_subject_missing_repo_url(self):
        """S3: 缺 repo_url - I002"""
        input_data = copy.deepcopy(VALID_ISSUE_INPUT)
        del input_data["repo_url"]

        result = self.issuer.issue_permit(input_data)

        self.assertFalse(result["success"])
        self.assertIsNone(result["permit_token"])
        self.assertEqual(result["error_code"], "I002")
        self.assertIn("repo_url", result["error_message"])

    def test_s3_subject_missing_commit_sha(self):
        """S3: 缺 commit_sha - I002"""
        input_data = copy.deepcopy(VALID_ISSUE_INPUT)
        del input_data["commit_sha"]

        result = self.issuer.issue_permit(input_data)

        self.assertFalse(result["success"])
        self.assertEqual(result["error_code"], "I002")

    def test_s3_subject_missing_run_id(self):
        """S3: 缺 run_id - I002"""
        input_data = copy.deepcopy(VALID_ISSUE_INPUT)
        del input_data["run_id"]

        result = self.issuer.issue_permit(input_data)

        self.assertFalse(result["success"])
        self.assertEqual(result["error_code"], "I002")

    def test_s3_subject_missing_intent_id(self):
        """S3: 缺 intent_id - I002"""
        input_data = copy.deepcopy(VALID_ISSUE_INPUT)
        del input_data["intent_id"]

        result = self.issuer.issue_permit(input_data)

        self.assertFalse(result["success"])
        self.assertEqual(result["error_code"], "I002")

    # -------------------------------------------------------------------------
    # S4: TTL 非法（0或负数）
    # -------------------------------------------------------------------------
    def test_s4_ttl_zero(self):
        """S4: TTL=0 - I003"""
        input_data = copy.deepcopy(VALID_ISSUE_INPUT)
        input_data["ttl_seconds"] = 0

        result = self.issuer.issue_permit(input_data)

        self.assertFalse(result["success"])
        self.assertIsNone(result["permit_token"])
        self.assertEqual(result["error_code"], "I003")
        self.assertIn("TTL", result["error_message"])

    def test_s4_ttl_negative(self):
        """S4: TTL<0 - I003"""
        input_data = copy.deepcopy(VALID_ISSUE_INPUT)
        input_data["ttl_seconds"] = -100

        result = self.issuer.issue_permit(input_data)

        self.assertFalse(result["success"])
        self.assertEqual(result["error_code"], "I003")

    # -------------------------------------------------------------------------
    # S5: TTL 超上限
    # -------------------------------------------------------------------------
    def test_s5_ttl_exceeds_max(self):
        """S5: TTL 超上限 - I003"""
        input_data = copy.deepcopy(VALID_ISSUE_INPUT)
        input_data["ttl_seconds"] = 100000  # > 86400

        result = self.issuer.issue_permit(input_data)

        self.assertFalse(result["success"])
        self.assertIsNone(result["permit_token"])
        self.assertEqual(result["error_code"], "I003")
        self.assertIn("exceeds max", result["error_message"])

    # -------------------------------------------------------------------------
    # S6: 签名密钥缺失
    # -------------------------------------------------------------------------
    def test_s6_signing_key_missing(self):
        """S6: 签名密钥缺失 - I004"""
        issuer_no_key = PermitIssuer(signing_key=None)
        result = issuer_no_key.issue_permit(VALID_ISSUE_INPUT)

        self.assertFalse(result["success"])
        self.assertIsNone(result["permit_token"])
        self.assertEqual(result["error_code"], "I004")
        self.assertIn("key", result["error_message"].lower())

    # -------------------------------------------------------------------------
    # S7: 签名异常
    # -------------------------------------------------------------------------
    def test_s7_signing_failed(self):
        """S7: 签名异常 - I005"""
        def failing_signer(payload: bytes, key: bytes) -> bytes:
            raise RuntimeError("Simulated signing failure")

        issuer_bad_signer = PermitIssuer(
            signing_key=TEST_SIGNING_KEY,
            signer=failing_signer
        )
        result = issuer_bad_signer.issue_permit(VALID_ISSUE_INPUT)

        self.assertFalse(result["success"])
        self.assertIsNone(result["permit_token"])
        self.assertEqual(result["error_code"], "I005")
        self.assertIn("Signing failed", result["error_message"])

    # -------------------------------------------------------------------------
    # S8: 联通验证
    # -------------------------------------------------------------------------
    def test_s8_integration_with_gate_permit(self):
        """S8: 联通验证 - issuer 产物被 GatePermit 验证为 VALID"""
        # Step 1: Issue permit
        issue_result = self.issuer.issue_permit(VALID_ISSUE_INPUT)
        self.assertTrue(issue_result["success"], "Permit issuance should succeed")

        permit_token = issue_result["permit_token"]
        self.assertIsNotNone(permit_token)

        # Step 2: Validate with GatePermit
        gate = GatePermit()
        validation_input = {
            "permit_token": permit_token,
            **EXECUTION_CONTEXT,
            "current_time": issue_result["issued_at"],  # Use same time for determinism
        }
        validation_result = gate.execute(validation_input)

        # Step 3: Check validation result
        self.assertEqual(validation_result["gate_decision"], "ALLOW")
        self.assertEqual(validation_result["permit_validation_status"], "VALID")
        self.assertTrue(validation_result["release_allowed"])
        self.assertIsNone(validation_result["release_blocked_by"])
        self.assertIsNone(validation_result["error_code"])

        # Step 4: Verify permit_id matches
        permit = json.loads(permit_token)
        self.assertEqual(validation_result["permit_id"], permit["permit_id"])

    # -------------------------------------------------------------------------
    # Additional Tests
    # -------------------------------------------------------------------------
    def test_audit_pack_ref_empty(self):
        """audit_pack_ref 为空 - I001"""
        input_data = copy.deepcopy(VALID_ISSUE_INPUT)
        input_data["audit_pack_ref"] = ""

        result = self.issuer.issue_permit(input_data)

        self.assertFalse(result["success"])
        self.assertEqual(result["error_code"], "I001")

    def test_convenience_function(self):
        """Convenience function issue_permit should work"""
        result = issue_permit(
            final_gate_decision="PASSED_NO_PERMIT",
            audit_pack_ref="audit-10465f76",
            repo_url="https://github.com/local/NEW-GM",
            commit_sha="4ea179d31a66fc2616f0cf953cd0e5c5c43d8ea8",
            run_id="RUN-20260218-001",
            intent_id="generate_skill_from_repo",
            ttl_seconds=3600,
            signing_key=TEST_SIGNING_KEY,
        )

        self.assertTrue(result["success"])
        self.assertIsNotNone(result["permit_token"])

    def test_error_codes_mapping(self):
        """Error codes should map correctly"""
        self.assertEqual(ISSUER_ERROR_CODES["I001"], "ISSUE_CONDITION_NOT_MET")
        self.assertEqual(ISSUER_ERROR_CODES["I002"], "SUBJECT_INCOMPLETE")
        self.assertEqual(ISSUER_ERROR_CODES["I003"], "TTL_INVALID")
        self.assertEqual(ISSUER_ERROR_CODES["I004"], "SIGNING_KEY_MISSING")
        self.assertEqual(ISSUER_ERROR_CODES["I005"], "SIGNING_FAILED")

    def test_permit_id_format(self):
        """Permit ID format should match PERMIT-YYYYMMDD-XXXXXXXX"""
        result = self.issuer.issue_permit(VALID_ISSUE_INPUT)
        permit_id = result["permit_id"]

        self.assertTrue(permit_id.startswith("PERMIT-"))
        parts = permit_id.split("-")
        self.assertEqual(len(parts), 3)
        self.assertEqual(len(parts[1]), 8)  # YYYYMMDD
        self.assertEqual(len(parts[2]), 8)  # 8 hex chars

    def test_expires_at_calculation(self):
        """expires_at should be issued_at + ttl_seconds"""
        input_data = copy.deepcopy(VALID_ISSUE_INPUT)
        input_data["ttl_seconds"] = 7200  # 2 hours

        result = self.issuer.issue_permit(input_data)
        self.assertTrue(result["success"])

        permit = json.loads(result["permit_token"])
        # expires_at should be about 2 hours after issued_at
        from datetime import datetime
        issued = datetime.fromisoformat(permit["issued_at"].replace("Z", "+00:00"))
        expires = datetime.fromisoformat(permit["expires_at"].replace("Z", "+00:00"))
        delta_seconds = (expires - issued).total_seconds()

        self.assertAlmostEqual(delta_seconds, 7200, delta=1)


class TestPermitIssuerGateIntegration(unittest.TestCase):
    """Integration tests between PermitIssuer and GatePermit."""

    def setUp(self):
        """Set up test fixtures."""
        self.issuer = PermitIssuer(signing_key=TEST_SIGNING_KEY)
        self.gate = GatePermit()

    def test_full_flow_issue_and_validate(self):
        """Full flow: issue permit -> validate -> release_allowed=true"""
        # Issue
        issue_result = self.issuer.issue_permit(VALID_ISSUE_INPUT)
        self.assertTrue(issue_result["success"])

        # Validate
        validation_result = validate_permit(
            permit_token=issue_result["permit_token"],
            repo_url=EXECUTION_CONTEXT["repo_url"],
            commit_sha=EXECUTION_CONTEXT["commit_sha"],
            run_id=EXECUTION_CONTEXT["run_id"],
            requested_action=EXECUTION_CONTEXT["requested_action"],
            current_time=issue_result["issued_at"],
        )

        self.assertTrue(validation_result["release_allowed"])
        self.assertEqual(validation_result["permit_validation_status"], "VALID")

    def test_subject_mismatch_after_issue(self):
        """Subject mismatch: permit issued for one repo, validated against another"""
        # Issue for NEW-GM
        issue_result = self.issuer.issue_permit(VALID_ISSUE_INPUT)
        self.assertTrue(issue_result["success"])

        # Try to validate against different repo
        validation_result = validate_permit(
            permit_token=issue_result["permit_token"],
            repo_url="https://github.com/other/REPO",  # Different!
            commit_sha=EXECUTION_CONTEXT["commit_sha"],
            run_id=EXECUTION_CONTEXT["run_id"],
            requested_action=EXECUTION_CONTEXT["requested_action"],
        )

        self.assertFalse(validation_result["release_allowed"])
        self.assertEqual(validation_result["error_code"], "E006")
        self.assertEqual(validation_result["release_blocked_by"], "PERMIT_SUBJECT_MISMATCH")

    def test_scope_mismatch_after_issue(self):
        """Scope mismatch: permit allows 'deploy', but request 'release'"""
        input_data = copy.deepcopy(VALID_ISSUE_INPUT)
        input_data["allowed_actions"] = ["deploy"]  # No 'release'

        issue_result = self.issuer.issue_permit(input_data)
        self.assertTrue(issue_result["success"])

        # Try to validate with 'release' action
        validation_result = validate_permit(
            permit_token=issue_result["permit_token"],
            repo_url=EXECUTION_CONTEXT["repo_url"],
            commit_sha=EXECUTION_CONTEXT["commit_sha"],
            run_id=EXECUTION_CONTEXT["run_id"],
            requested_action="release",  # Not in allowed_actions
        )

        self.assertFalse(validation_result["release_allowed"])
        self.assertEqual(validation_result["error_code"], "E005")

    def test_passed_all_gates_scenario(self):
        """Simulate PASSED_NO_PERMIT -> issue -> PASSED_WITH_PERMIT flow"""
        # Step 1: Gate passes, but no permit
        validation_no_permit = validate_permit(
            permit_token=None,
            repo_url=EXECUTION_CONTEXT["repo_url"],
            commit_sha=EXECUTION_CONTEXT["commit_sha"],
            run_id=EXECUTION_CONTEXT["run_id"],
        )
        self.assertFalse(validation_no_permit["release_allowed"])
        self.assertEqual(validation_no_permit["release_blocked_by"], "PERMIT_REQUIRED")

        # Step 2: Issue permit
        issue_result = self.issuer.issue_permit(VALID_ISSUE_INPUT)
        self.assertTrue(issue_result["success"])

        # Step 3: Validate with permit
        validation_with_permit = validate_permit(
            permit_token=issue_result["permit_token"],
            repo_url=EXECUTION_CONTEXT["repo_url"],
            commit_sha=EXECUTION_CONTEXT["commit_sha"],
            run_id=EXECUTION_CONTEXT["run_id"],
            current_time=issue_result["issued_at"],
        )
        self.assertTrue(validation_with_permit["release_allowed"])
        self.assertIsNone(validation_with_permit["release_blocked_by"])


class TestRealSignatureVerification(unittest.TestCase):
    """Real signature verification tests - 篡改 token 后必须失败。"""

    def setUp(self):
        """Set up test fixtures."""
        self.signing_key = TEST_SIGNING_KEY
        self.issuer = PermitIssuer(signing_key=self.signing_key)

    def _create_hmac_verifier(self, key: str):
        """Create a real HMAC-SHA256 verifier for GatePermit."""
        import hashlib
        import hmac
        import base64

        def verifier(permit: dict) -> bool:
            sig = permit.get("signature", {})
            if sig.get("algo") != "HS256":
                return False
            if not sig.get("value") or not sig.get("key_id"):
                return False

            # Reconstruct the payload (exclude signature and revocation)
            payload = {k: v for k, v in permit.items() if k not in ("signature", "revocation")}
            canonical = json.dumps(payload, sort_keys=True, separators=(',', ':'))

            # Compute expected signature
            expected_sig = hmac.new(
                key.encode('utf-8'),
                canonical.encode('utf-8'),
                hashlib.sha256
            ).digest()
            expected_b64 = base64.b64encode(expected_sig).decode('utf-8')

            # Compare
            return sig.get("value") == expected_b64

        return verifier

    def test_tampered_token_must_fail(self):
        """S9: 篡改 permit_token 后必须验证失败"""
        # Issue a valid permit
        issue_result = self.issuer.issue_permit(VALID_ISSUE_INPUT)
        self.assertTrue(issue_result["success"])

        permit = json.loads(issue_result["permit_token"])

        # Create GatePermit with REAL signature verifier
        real_verifier = self._create_hmac_verifier(self.signing_key)
        gate = GatePermit(signature_verifier=real_verifier)

        # Tamper the permit (modify a field after signing)
        tampered_permit = copy.deepcopy(permit)
        tampered_permit["subject"]["commit_sha"] = "0000000000000000000000000000000000000000"

        # Validation must FAIL (signature won't match tampered content)
        validation_result = gate.execute({
            "permit_token": tampered_permit,
            "repo_url": tampered_permit["subject"]["repo_url"],
            "commit_sha": tampered_permit["subject"]["commit_sha"],
            "run_id": tampered_permit["subject"]["run_id"],
            "requested_action": "release",
            "current_time": permit["issued_at"],
        })

        self.assertFalse(validation_result["release_allowed"])
        self.assertEqual(validation_result["error_code"], "E003")  # Signature invalid

    def test_valid_signature_must_pass(self):
        """Valid signature with real verifier must pass"""
        issue_result = self.issuer.issue_permit(VALID_ISSUE_INPUT)
        self.assertTrue(issue_result["success"])

        permit = json.loads(issue_result["permit_token"])

        # Create GatePermit with REAL signature verifier
        real_verifier = self._create_hmac_verifier(self.signing_key)
        gate = GatePermit(signature_verifier=real_verifier)

        # Validation must PASS
        validation_result = gate.execute({
            "permit_token": permit,
            "repo_url": permit["subject"]["repo_url"],
            "commit_sha": permit["subject"]["commit_sha"],
            "run_id": permit["subject"]["run_id"],
            "requested_action": "release",
            "current_time": permit["issued_at"],
        })

        self.assertTrue(validation_result["release_allowed"])
        self.assertEqual(validation_result["permit_validation_status"], "VALID")

    def test_wrong_key_must_fail(self):
        """Signature with wrong key must fail"""
        issue_result = self.issuer.issue_permit(VALID_ISSUE_INPUT)
        self.assertTrue(issue_result["success"])

        permit = json.loads(issue_result["permit_token"])

        # Create GatePermit with DIFFERENT key
        wrong_key_verifier = self._create_hmac_verifier("wrong-key-12345")
        gate = GatePermit(signature_verifier=wrong_key_verifier)

        # Validation must FAIL
        validation_result = gate.execute({
            "permit_token": permit,
            "repo_url": permit["subject"]["repo_url"],
            "commit_sha": permit["subject"]["commit_sha"],
            "run_id": permit["subject"]["run_id"],
            "requested_action": "release",
            "current_time": permit["issued_at"],
        })

        self.assertFalse(validation_result["release_allowed"])
        self.assertEqual(validation_result["error_code"], "E003")


# ============================================================================
# Test Runner
# ============================================================================

def run_tests():
    """Run all tests and return results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestPermitIssuer))
    suite.addTests(loader.loadTestsFromTestCase(TestPermitIssuerGateIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result


if __name__ == "__main__":
    run_tests()
