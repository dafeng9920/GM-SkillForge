"""
Test suite for GatePermit - Permit 校验 Gate 测试矩阵。

测试矩阵（T1-T9）：
- T1: 正常 permit - ALLOW, VALID, release_allowed=true
- T2: 缺 permit - BLOCK, INVALID, E001, release_allowed=false
- T3: 格式错误 - BLOCK, INVALID, E002
- T4: 签名无效 - BLOCK, INVALID, E003
- T5: 已过期 - BLOCK, INVALID, E004
- T6: scope 不匹配 - BLOCK, INVALID, E005
- T7: subject 不匹配 - BLOCK, INVALID, E006
- T8: 已撤销 - BLOCK, INVALID, E007
- T9: PASSED_NO_PERMIT 兼容性 - release_allowed=false

遵循 permit_contract_v1.yml 契约。
"""
import copy
import unittest
from typing import Any

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from skills.gates.gate_permit import (
    GatePermit,
    validate_permit,
    ERROR_CODES,
)


# ============================================================================
# Test Fixtures
# ============================================================================

VALID_PERMIT: dict[str, Any] = {
    "permit_id": "PERMIT-20260218-001",
    "issuer": {
        "issuer_id": "skillforge-permit-service",
        "issuer_type": "AUTOMATED_GATE"
    },
    "issued_at": "2026-02-18T12:00:00Z",
    "expires_at": "2026-02-18T23:59:59Z",
    "subject": {
        "repo_url": "https://github.com/local/NEW-GM",
        "commit_sha": "4ea179d31a66fc2616f0cf953cd0e5c5c43d8ea8",
        "run_id": "RUN-20260218-001",
        "intent_id": "generate_skill_from_repo"
    },
    "scope": {
        "allowed_actions": ["release", "deploy"],
        "environment": "development",
        "gate_profile": "batch2_8gate"
    },
    "constraints": {
        "at_time": "2026-02-18T08:41:10Z",
        "max_release_count": 1,
        "time_window_seconds": 3600
    },
    "decision_binding": {
        "final_gate_decision": "PASSED_NO_PERMIT",
        "gate_count": 8,
        "audit_pack_ref": "audit-10465f76",
        "evidence_count": 8
    },
    "signature": {
        "algo": "HS256",
        "value": "BASE64_ENCODED_SIGNATURE",
        "key_id": "skillforge-permit-key-2026",
        "signed_at": "2026-02-18T12:00:00Z"
    },
    "revocation": {
        "revoked": False,
        "revoked_at": None,
        "revoked_by": None,
        "reason": None
    }
}

EXECUTION_CONTEXT = {
    "repo_url": "https://github.com/local/NEW-GM",
    "commit_sha": "4ea179d31a66fc2616f0cf953cd0e5c5c43d8ea8",
    "run_id": "RUN-20260218-001",
    "requested_action": "release",
    "current_time": "2026-02-18T14:00:00Z"  # Before expires_at
}


# ============================================================================
# Test Cases
# ============================================================================

class TestGatePermit(unittest.TestCase):
    """Test suite for GatePermit."""

    def setUp(self):
        """Set up test fixtures."""
        self.gate = GatePermit()
        import os, json, base64, hmac, hashlib
        self.test_key = "test-secret-key-123456"
        os.environ["PERMIT_HS256_KEY"] = self.test_key
        
        # Calculate real signature for VALID_PERMIT
        VALID_PERMIT["signature"]["value"] = self._sign_permit(VALID_PERMIT)

    def tearDown(self):
        import os
        os.environ.pop("PERMIT_HS256_KEY", None)
        
    def _sign_permit(self, permit):
        import json, base64, hmac, hashlib
        payload = dict(permit)
        payload.pop("signature", None)
        payload.pop("revocation", None)
        canonical = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        return base64.b64encode(
            hmac.new(self.test_key.encode("utf-8"), canonical.encode("utf-8"), hashlib.sha256).digest()
        ).decode("utf-8")
    # -------------------------------------------------------------------------
    # T1: 正常 permit
    # -------------------------------------------------------------------------
    def test_t1_valid_permit(self):
        """T1: 正常 permit - ALLOW, VALID, release_allowed=true"""
        input_data = {
            "permit_token": VALID_PERMIT,
            **EXECUTION_CONTEXT
        }

        result = self.gate.execute(input_data)

        self.assertEqual(result["gate_decision"], "ALLOW")
        self.assertEqual(result["permit_validation_status"], "VALID")
        self.assertTrue(result["release_allowed"])
        self.assertIsNone(result["release_blocked_by"])
        self.assertIsNone(result["error_code"])
        self.assertEqual(len(result["evidence_refs"]), 1)

    # -------------------------------------------------------------------------
    # T2: 缺 permit
    # -------------------------------------------------------------------------
    def test_t2_missing_permit_null(self):
        """T2: 缺 permit (null) - BLOCK, INVALID, E001"""
        input_data = {
            "permit_token": None,
            **EXECUTION_CONTEXT
        }

        result = self.gate.execute(input_data)

        self.assertEqual(result["gate_decision"], "BLOCK")
        self.assertEqual(result["permit_validation_status"], "INVALID")
        self.assertFalse(result["release_allowed"])
        self.assertEqual(result["release_blocked_by"], "PERMIT_REQUIRED")
        self.assertEqual(result["error_code"], "E001")

    def test_t2_missing_permit_empty(self):
        """T2: 缺 permit (empty) - BLOCK, INVALID, E001"""
        input_data = {
            "permit_token": "",
            **EXECUTION_CONTEXT
        }

        result = self.gate.execute(input_data)

        self.assertEqual(result["gate_decision"], "BLOCK")
        self.assertEqual(result["permit_validation_status"], "INVALID")
        self.assertFalse(result["release_allowed"])
        self.assertEqual(result["release_blocked_by"], "PERMIT_REQUIRED")
        self.assertEqual(result["error_code"], "E001")

    # -------------------------------------------------------------------------
    # T3: 格式错误
    # -------------------------------------------------------------------------
    def test_t3_invalid_format_json(self):
        """T3: 格式错误 (invalid JSON) - BLOCK, INVALID, E002"""
        input_data = {
            "permit_token": "not a valid json string",
            **EXECUTION_CONTEXT
        }

        result = self.gate.execute(input_data)

        self.assertEqual(result["gate_decision"], "BLOCK")
        self.assertEqual(result["permit_validation_status"], "INVALID")
        self.assertFalse(result["release_allowed"])
        self.assertEqual(result["release_blocked_by"], "PERMIT_INVALID")
        self.assertEqual(result["error_code"], "E002")

    def test_t3_missing_required_field(self):
        """T3: 格式错误 (missing required field) - BLOCK, INVALID, E002"""
        invalid_permit = copy.deepcopy(VALID_PERMIT)
        del invalid_permit["expires_at"]

        input_data = {
            "permit_token": invalid_permit,
            **EXECUTION_CONTEXT
        }

        result = self.gate.execute(input_data)

        self.assertEqual(result["gate_decision"], "BLOCK")
        self.assertEqual(result["error_code"], "E002")

    # -------------------------------------------------------------------------
    # T4: 签名无效
    # -------------------------------------------------------------------------
    def test_t4_invalid_signature_missing(self):
        """T4: 签名无效 (missing signature) - BLOCK, INVALID, E003"""
        invalid_permit = copy.deepcopy(VALID_PERMIT)
        invalid_permit["signature"] = {}

        input_data = {
            "permit_token": invalid_permit,
            **EXECUTION_CONTEXT
        }

        result = self.gate.execute(input_data)

        self.assertEqual(result["gate_decision"], "BLOCK")
        self.assertEqual(result["permit_validation_status"], "INVALID")
        self.assertFalse(result["release_allowed"])
        self.assertEqual(result["release_blocked_by"], "PERMIT_INVALID")
        self.assertEqual(result["error_code"], "E003")

    def test_t4_invalid_signature_algo(self):
        """T4: 签名无效 (unsupported algo) - BLOCK, INVALID, E003"""
        invalid_permit = copy.deepcopy(VALID_PERMIT)
        invalid_permit["signature"]["algo"] = "UNSUPPORTED"

        input_data = {
            "permit_token": invalid_permit,
            **EXECUTION_CONTEXT
        }

        result = self.gate.execute(input_data)

        self.assertEqual(result["gate_decision"], "BLOCK")
        self.assertEqual(result["error_code"], "E003")

    # -------------------------------------------------------------------------
    # T5: 已过期
    # -------------------------------------------------------------------------
    def test_t5_expired_permit(self):
        """T5: 已过期 - BLOCK, INVALID, E004"""
        expired_permit = copy.deepcopy(VALID_PERMIT)
        expired_permit["expires_at"] = "2026-02-18T10:00:00Z"  # Earlier than current_time
        expired_permit["signature"]["value"] = self._sign_permit(expired_permit)

        input_data = {
            "permit_token": expired_permit,
            **EXECUTION_CONTEXT  # current_time = "2026-02-18T14:00:00Z"
        }

        result = self.gate.execute(input_data)

        self.assertEqual(result["gate_decision"], "BLOCK")
        self.assertEqual(result["permit_validation_status"], "INVALID")
        self.assertFalse(result["release_allowed"])
        self.assertEqual(result["release_blocked_by"], "PERMIT_EXPIRED")
        self.assertEqual(result["error_code"], "E004")

    # -------------------------------------------------------------------------
    # T6: scope 不匹配
    # -------------------------------------------------------------------------
    def test_t6_scope_mismatch(self):
        """T6: scope 不匹配 - BLOCK, INVALID, E005"""
        scope_mismatch_permit = copy.deepcopy(VALID_PERMIT)
        scope_mismatch_permit["scope"]["allowed_actions"] = ["deploy"]  # No "release"
        scope_mismatch_permit["signature"]["value"] = self._sign_permit(scope_mismatch_permit)

        input_data = {
            "permit_token": scope_mismatch_permit,
            **EXECUTION_CONTEXT  # requested_action = "release"
        }

        result = self.gate.execute(input_data)

        self.assertEqual(result["gate_decision"], "BLOCK")
        self.assertEqual(result["permit_validation_status"], "INVALID")
        self.assertFalse(result["release_allowed"])
        self.assertEqual(result["release_blocked_by"], "PERMIT_SCOPE_MISMATCH")
        self.assertEqual(result["error_code"], "E005")

    # -------------------------------------------------------------------------
    # T7: subject 不匹配
    # -------------------------------------------------------------------------
    def test_t7_subject_mismatch_repo_url(self):
        """T7: subject 不匹配 (repo_url) - BLOCK, INVALID, E006"""
        mismatch_permit = copy.deepcopy(VALID_PERMIT)
        mismatch_permit["subject"]["repo_url"] = "https://github.com/other/REPO"
        mismatch_permit["signature"]["value"] = self._sign_permit(mismatch_permit)

        input_data = {
            "permit_token": mismatch_permit,
            **EXECUTION_CONTEXT
        }

        result = self.gate.execute(input_data)

        self.assertEqual(result["gate_decision"], "BLOCK")
        self.assertEqual(result["permit_validation_status"], "INVALID")
        self.assertFalse(result["release_allowed"])
        self.assertEqual(result["release_blocked_by"], "PERMIT_SUBJECT_MISMATCH")
        self.assertEqual(result["error_code"], "E006")

    def test_t7_subject_mismatch_commit_sha(self):
        """T7: subject 不匹配 (commit_sha) - BLOCK, INVALID, E006"""
        mismatch_permit = copy.deepcopy(VALID_PERMIT)
        mismatch_permit["subject"]["commit_sha"] = "0000000000000000000000000000000000000000"
        mismatch_permit["signature"]["value"] = self._sign_permit(mismatch_permit)

        input_data = {
            "permit_token": mismatch_permit,
            **EXECUTION_CONTEXT
        }

        result = self.gate.execute(input_data)

        self.assertEqual(result["gate_decision"], "BLOCK")
        self.assertEqual(result["error_code"], "E006")

    def test_t7_subject_mismatch_run_id(self):
        """T7: subject 不匹配 (run_id) - BLOCK, INVALID, E006"""
        mismatch_permit = copy.deepcopy(VALID_PERMIT)
        mismatch_permit["subject"]["run_id"] = "RUN-99999999-999"
        mismatch_permit["signature"]["value"] = self._sign_permit(mismatch_permit)

        input_data = {
            "permit_token": mismatch_permit,
            **EXECUTION_CONTEXT
        }

        result = self.gate.execute(input_data)

        self.assertEqual(result["gate_decision"], "BLOCK")
        self.assertEqual(result["error_code"], "E006")

    # -------------------------------------------------------------------------
    # T8: 已撤销
    # -------------------------------------------------------------------------
    def test_t8_revoked_permit(self):
        """T8: 已撤销 - BLOCK, INVALID, E007"""
        revoked_permit = copy.deepcopy(VALID_PERMIT)
        revoked_permit["revocation"] = {
            "revoked": True,
            "revoked_at": "2026-02-18T13:00:00Z",
            "revoked_by": "security-team",
            "reason": "CVE detected"
        }

        input_data = {
            "permit_token": revoked_permit,
            **EXECUTION_CONTEXT
        }

        result = self.gate.execute(input_data)

        self.assertEqual(result["gate_decision"], "BLOCK")
        self.assertEqual(result["permit_validation_status"], "INVALID")
        self.assertFalse(result["release_allowed"])
        self.assertEqual(result["release_blocked_by"], "PERMIT_REVOKED")
        self.assertEqual(result["error_code"], "E007")

    # -------------------------------------------------------------------------
    # T9: PASSED_NO_PERMIT 兼容性
    # -------------------------------------------------------------------------
    def test_t9_passed_no_permit_compatibility(self):
        """T9: PASSED_NO_PERMIT + 无 permit - release_allowed=false"""
        # Simulate the PASSED_NO_PERMIT scenario
        input_data = {
            "permit_token": None,  # No permit
            "final_gate_decision": "PASSED_NO_PERMIT",  # Context info
            **EXECUTION_CONTEXT
        }

        result = self.gate.execute(input_data)

        # Should be blocked due to missing permit
        self.assertEqual(result["gate_decision"], "BLOCK")
        self.assertFalse(result["release_allowed"])
        self.assertEqual(result["release_blocked_by"], "PERMIT_REQUIRED")
        self.assertEqual(result["error_code"], "E001")

    # -------------------------------------------------------------------------
    # Additional Tests: Evidence and Output Validation
    # -------------------------------------------------------------------------
    def test_evidence_ref_structure(self):
        """EvidenceRef 必须包含必要字段"""
        input_data = {
            "permit_token": VALID_PERMIT,
            **EXECUTION_CONTEXT
        }

        result = self.gate.execute(input_data)

        self.assertEqual(len(result["evidence_refs"]), 1)
        evidence = result["evidence_refs"][0]

        required_fields = ["issue_key", "source_locator", "content_hash", "tool_revision", "timestamp"]
        for field in required_fields:
            self.assertIn(field, evidence)

    def test_output_validation_valid(self):
        """Output validation should pass for valid output"""
        input_data = {
            "permit_token": VALID_PERMIT,
            **EXECUTION_CONTEXT
        }

        result = self.gate.execute(input_data)
        errors = self.gate.validate_output(result)

        self.assertEqual(len(errors), 0)

    def test_output_validation_invalid(self):
        """Output validation should fail for invalid output"""
        invalid_output = {
            "gate_name": "permit_gate",
            # Missing required fields
        }

        errors = self.gate.validate_output(invalid_output)

        self.assertGreater(len(errors), 0)

    def test_convenience_function(self):
        """Convenience function validate_permit should work"""
        result = validate_permit(
            permit_token=VALID_PERMIT,
            repo_url=EXECUTION_CONTEXT["repo_url"],
            commit_sha=EXECUTION_CONTEXT["commit_sha"],
            run_id=EXECUTION_CONTEXT["run_id"],
            requested_action=EXECUTION_CONTEXT["requested_action"],
            current_time=EXECUTION_CONTEXT["current_time"]
        )

        self.assertEqual(result["gate_decision"], "ALLOW")
        self.assertTrue(result["release_allowed"])

    def test_error_codes_mapping(self):
        """Error codes should map correctly"""
        self.assertEqual(ERROR_CODES["E001"], "PERMIT_REQUIRED")
        self.assertEqual(ERROR_CODES["E002"], "PERMIT_INVALID")
        self.assertEqual(ERROR_CODES["E003"], "PERMIT_INVALID")
        self.assertEqual(ERROR_CODES["E004"], "PERMIT_EXPIRED")
        self.assertEqual(ERROR_CODES["E005"], "PERMIT_SCOPE_MISMATCH")
        self.assertEqual(ERROR_CODES["E006"], "PERMIT_SUBJECT_MISMATCH")
        self.assertEqual(ERROR_CODES["E007"], "PERMIT_REVOKED")


# ============================================================================
# Test Runner
# ============================================================================

def run_tests():
    """Run all tests and return results."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestGatePermit)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result


if __name__ == "__main__":
    run_tests()
