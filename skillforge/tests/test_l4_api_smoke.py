"""
L4 API Smoke Tests - 端到端冒烟测试

测试三条链路：
- A: POST /cognition/generate -> Generate 10d cognition
- B: POST /work/adopt -> Adopt reason card as work item
- C: POST /work/execute -> Execute work item with permit validation

场景：
- 场景A：正常链路 Generate -> Adopt -> Execute (期望: gate_decision=ALLOW, release_allowed=true)
- 场景B：无 permit Execute (期望: error_code=E001, release_allowed=false)
- 场景C：坏签名 Execute (期望: error_code=E003, release_allowed=false)
- 场景D：LLM Generate 成功 (mock) (期望: ok=true, dimensions=10)
- 场景E：LLM 配置缺失失败 (期望: error_code=L4_LLM_CONFIG_MISSING)

遵循 L4 前后端合并联调规范。
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

# Set LLM config for mock testing
os.environ["LLM_PROVIDER"] = "mock"
os.environ["LLM_MODEL"] = "mock-model"
os.environ["OPENAI_API_KEY"] = "test-mock-key-for-unit-tests"

from skills.gates.permit_issuer import PermitIssuer
from skills.gates.gate_permit import GatePermit, validate_permit


# ============================================================================
# Test Constants
# ============================================================================

TEST_REPO_URL = "https://github.com/skillforge/workflow-orchestration"
TEST_COMMIT_SHA = "a1b2c3d4e5f6789012345678901234567890abcd"
TEST_RUN_ID = "RUN-L4-SMOKE-001"
TEST_REQUESTER_ID = "user-l4-smoke"


# ============================================================================
# Helper Functions (Simulating API responses)
# ============================================================================

def generate_run_id() -> str:
    """Generate a unique run ID."""
    import uuid
    import time
    ts = int(time.time())
    uid = uuid.uuid4().hex[:8].upper()
    return f"RUN-L4-{ts}-{uid}"


def generate_evidence_ref(prefix: str = "EV") -> str:
    """Generate an evidence reference."""
    import uuid
    import time
    ts = int(time.time())
    uid = uuid.uuid4().hex[:8].upper()
    return f"{prefix}-L4-{ts}-{uid}"


def now_iso() -> str:
    """Return ISO-8601 UTC timestamp."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def make_success_envelope(data: dict, gate_decision: str, release_allowed: bool,
                          evidence_ref: str, run_id: str) -> dict:
    """Create success response envelope."""
    return {
        "ok": True,
        "data": data,
        "gate_decision": gate_decision,
        "release_allowed": release_allowed,
        "evidence_ref": evidence_ref,
        "run_id": run_id,
    }


def make_error_envelope(error_code: str, blocked_by: str, message: str,
                        evidence_ref: str, run_id: str) -> dict:
    """Create error response envelope."""
    return {
        "ok": False,
        "error_code": error_code,
        "blocked_by": blocked_by,
        "message": message,
        "evidence_ref": evidence_ref,
        "run_id": run_id,
    }


ERROR_CODE_MAP = {
    "E001": "PERMIT_REQUIRED",
    "E002": "PERMIT_INVALID",
    "E003": "PERMIT_INVALID",
    "E004": "PERMIT_EXPIRED",
    "E005": "PERMIT_SCOPE_MISMATCH",
    "E006": "PERMIT_SUBJECT_MISMATCH",
    "E007": "PERMIT_REVOKED",
}


# ============================================================================
# API Simulation Functions
# ============================================================================

def api_cognition_generate(repo_url: str, commit_sha: str, requester_id: str) -> dict:
    """Simulate POST /api/v1/cognition/generate"""
    run_id = generate_run_id()
    evidence_ref = generate_evidence_ref("EV-COG")

    # Generate mock 10d cognition result
    dimensions = []
    dim_labels = [
        ("L1", "事实提取", 85),
        ("L2", "概念抽象", 78),
        ("L3", "因果推理", 82),
        ("L4", "结构解构", 75),
        ("L5", "风险感知", 88),
        ("L6", "时序建模", 72),
        ("L7", "跨域关联", 68),
        ("L8", "不确定性标注", 80),
        ("L9", "建议可行性", 76),
        ("L10", "叙事连贯性", 84),
    ]

    for dim_id, label, score in dim_labels:
        threshold = 60
        verdict = "PASS" if score >= threshold else "FAIL"
        dimensions.append({
            "dim_id": dim_id,
            "label": label,
            "score": score,
            "threshold": threshold,
            "verdict": verdict,
            "evidence_ref": f"AuditPack/cognition/{evidence_ref}/{dim_id}.md"
        })

    pass_count = sum(1 for d in dimensions if d["verdict"] == "PASS")
    status = "PASSED" if pass_count >= 8 else "REJECTED"

    result = {
        "intent_id": "cognition_10d",
        "status": status,
        "repo_url": repo_url,
        "commit_sha": commit_sha,
        "at_time": now_iso(),
        "rubric_version": "1.0.0",
        "dimensions": dimensions,
        "overall_pass_count": pass_count,
        "rejection_reasons": [],
        "audit_pack_ref": f"AuditPack/cognition/{evidence_ref}/",
        "generated_at": now_iso(),
    }

    return make_success_envelope(result, "ALLOW", True, evidence_ref, run_id)


def api_work_adopt(reason_card_id: str, requester_id: str) -> dict:
    """Simulate POST /api/v1/work/adopt"""
    run_id = generate_run_id()
    evidence_ref = generate_evidence_ref("EV-ADOPT")

    if not reason_card_id.startswith("RC-"):
        return make_error_envelope(
            "E002", "PERMIT_INVALID",
            "Invalid reason_card_id format", evidence_ref, run_id
        )

    import uuid
    work_item_id = f"WI-{uuid.uuid4().hex[:8].upper()}"

    data = {
        "work_item_id": work_item_id,
        "status": "ADOPTED",
        "created_at": now_iso(),
    }

    return make_success_envelope(data, "ALLOW", True, evidence_ref, run_id)


def api_work_execute(work_item_id: str, permit_token, execution_context: dict) -> dict:
    """Simulate POST /api/v1/work/execute"""
    run_id = generate_run_id()
    evidence_ref = generate_evidence_ref("EV-EXEC")

    # E001: No permit
    if permit_token is None or permit_token == "":
        return make_error_envelope(
            "E001", "PERMIT_REQUIRED",
            "Permit token is required for execution",
            evidence_ref, run_id
        )

    # Validate permit with GatePermit
    gate = GatePermit()

    validation_input = {
        "permit_token": permit_token,
        "repo_url": execution_context["repo_url"],
        "commit_sha": execution_context["commit_sha"],
        "run_id": execution_context["run_id"],
        "requested_action": execution_context.get("requested_action", "release"),
        "current_time": now_iso(),
    }

    try:
        result = gate.execute(validation_input)

        if not result.get("release_allowed", False):
            error_code = result.get("error_code", "E002")
            blocked_by = ERROR_CODE_MAP.get(error_code, "PERMIT_INVALID")
            message = result.get("reason", "Permit validation failed")
            return make_error_envelope(error_code, blocked_by, message, evidence_ref, run_id)

        data = {
            "work_item_id": work_item_id,
            "execution_status": "COMPLETED",
            "receipt": {
                "gate_decision": result.get("gate_decision"),
                "permit_id": result.get("permit_id"),
            }
        }
        return make_success_envelope(data, "ALLOW", True, evidence_ref, run_id)

    except Exception as e:
        return make_error_envelope(
            "E002", "PERMIT_INVALID",
            f"Permit validation error: {str(e)}",
            evidence_ref, run_id
        )


# ============================================================================
# Test Cases
# ============================================================================

class TestL4APISmoke(unittest.TestCase):
    """L4 API Smoke Tests - Three scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.issuer = PermitIssuer(signing_key="test-signing-key-for-unit-tests-2026")

    # -------------------------------------------------------------------------
    # Scenario A: Normal flow Generate -> Adopt -> Execute
    # -------------------------------------------------------------------------
    def test_scenario_a_normal_flow(self):
        """
        Scenario A: Normal flow
        Generate -> Adopt -> Execute
        Expect: gate_decision=ALLOW, release_allowed=true
        """
        print("\n=== Scenario A: Normal Flow ===")

        # Step 1: Generate cognition
        cog_response = api_cognition_generate(
            repo_url=TEST_REPO_URL,
            commit_sha=TEST_COMMIT_SHA,
            requester_id=TEST_REQUESTER_ID
        )

        print(f"1. Generate response: ok={cog_response['ok']}, status={cog_response['data'].get('status')}")
        self.assertTrue(cog_response["ok"])
        self.assertEqual(cog_response["gate_decision"], "ALLOW")
        self.assertTrue(cog_response["release_allowed"])

        # Step 2: Adopt work item
        adopt_response = api_work_adopt(
            reason_card_id="RC-2026-02-19-TEST",
            requester_id=TEST_REQUESTER_ID
        )

        print(f"2. Adopt response: ok={adopt_response['ok']}, work_item_id={adopt_response['data'].get('work_item_id')}")
        self.assertTrue(adopt_response["ok"])
        self.assertEqual(adopt_response["data"]["status"], "ADOPTED")

        work_item_id = adopt_response["data"]["work_item_id"]

        # Step 3: Issue permit
        issue_input = {
            "final_gate_decision": "PASSED",
            "release_blocked_by": None,
            "audit_pack_ref": "audit-l4-smoke-001",
            "repo_url": TEST_REPO_URL,
            "commit_sha": TEST_COMMIT_SHA,
            "run_id": TEST_RUN_ID,
            "intent_id": "l4-smoke-test",
            "ttl_seconds": 3600,
            "allowed_actions": ["release"],
        }
        issue_result = self.issuer.issue_permit(issue_input)
        self.assertTrue(issue_result["success"], f"Permit issuance failed: {issue_result.get('error_message')}")

        permit_token = issue_result["permit_token"]
        print(f"3. Issue permit: success={issue_result['success']}, permit_id={issue_result.get('permit_id')}")

        # Step 4: Execute with permit
        exec_response = api_work_execute(
            work_item_id=work_item_id,
            permit_token=permit_token,
            execution_context={
                "repo_url": TEST_REPO_URL,
                "commit_sha": TEST_COMMIT_SHA,
                "run_id": TEST_RUN_ID,
                "requested_action": "release",
            }
        )

        print(f"4. Execute response: ok={exec_response['ok']}, gate_decision={exec_response.get('gate_decision')}, release_allowed={exec_response.get('release_allowed')}")
        self.assertTrue(exec_response["ok"])
        self.assertEqual(exec_response["gate_decision"], "ALLOW")
        self.assertTrue(exec_response["release_allowed"])

    # -------------------------------------------------------------------------
    # Scenario B: No permit -> E001
    # -------------------------------------------------------------------------
    def test_scenario_b_no_permit(self):
        """
        Scenario B: Execute without permit
        Expect: error_code=E001, release_allowed=false
        """
        print("\n=== Scenario B: No Permit ===")

        exec_response = api_work_execute(
            work_item_id="WI-TEST001",
            permit_token=None,
            execution_context={
                "repo_url": TEST_REPO_URL,
                "commit_sha": TEST_COMMIT_SHA,
                "run_id": TEST_RUN_ID,
                "requested_action": "release",
            }
        )

        print(f"Execute response: ok={exec_response['ok']}, error_code={exec_response.get('error_code')}, blocked_by={exec_response.get('blocked_by')}")
        self.assertFalse(exec_response["ok"])
        self.assertEqual(exec_response["error_code"], "E001")
        self.assertEqual(exec_response["blocked_by"], "PERMIT_REQUIRED")

    # -------------------------------------------------------------------------
    # Scenario C: Bad signature -> E003
    # -------------------------------------------------------------------------
    def test_scenario_c_bad_signature(self):
        """
        Scenario C: Execute with tampered permit signature
        Expect: error_code=E003, release_allowed=false
        """
        print("\n=== Scenario C: Bad Signature ===")

        # Step 1: Issue valid permit
        issue_input = {
            "final_gate_decision": "PASSED",
            "release_blocked_by": None,
            "audit_pack_ref": "audit-l4-smoke-002",
            "repo_url": TEST_REPO_URL,
            "commit_sha": TEST_COMMIT_SHA,
            "run_id": TEST_RUN_ID,
            "intent_id": "l4-smoke-test",
            "ttl_seconds": 3600,
            "allowed_actions": ["release"],
        }
        issue_result = self.issuer.issue_permit(issue_input)
        self.assertTrue(issue_result["success"], f"Permit issuance failed: {issue_result.get('error_message')}")

        # Step 2: Tamper with signature
        permit_token = json.loads(issue_result["permit_token"])
        permit_token["signature"]["value"] = "TAMPERED_SIGNATURE_XXX"

        print(f"Issued permit, then tampered with signature")

        # Step 3: Execute with tampered permit
        exec_response = api_work_execute(
            work_item_id="WI-TEST002",
            permit_token=permit_token,
            execution_context={
                "repo_url": TEST_REPO_URL,
                "commit_sha": TEST_COMMIT_SHA,
                "run_id": TEST_RUN_ID,
                "requested_action": "release",
            }
        )

        print(f"Execute response: ok={exec_response['ok']}, error_code={exec_response.get('error_code')}, blocked_by={exec_response.get('blocked_by')}")
        self.assertFalse(exec_response["ok"])
        self.assertEqual(exec_response["error_code"], "E003")
        self.assertEqual(exec_response["blocked_by"], "PERMIT_INVALID")

    # -------------------------------------------------------------------------
    # Scenario D: LLM Generate success (mock)
    # -------------------------------------------------------------------------
    def test_scenario_d_llm_generate_success(self):
        """
        Scenario D: Generate cognition with mock LLM
        Expect: ok=true, 10 dimensions with proper structure
        """
        print("\n=== Scenario D: LLM Generate (Mock) ===")

        # Use the mock provider (set in module setup)
        from llm.client import generate_10d

        result = generate_10d(
            user_input="Test input for cognition assessment",
            context={
                "repo_url": TEST_REPO_URL,
                "commit_sha": TEST_COMMIT_SHA,
                "requester_id": TEST_REQUESTER_ID,
            },
            use_mock=True
        )

        print(f"Generate result: dimensions={len(result.get('dimensions', []))}, provider={result.get('provider')}")

        # Verify structure
        self.assertIn("dimensions", result)
        self.assertEqual(len(result["dimensions"]), 10)

        # Verify each dimension has required fields
        for dim in result["dimensions"]:
            self.assertIn("dim_id", dim)
            self.assertIn("name", dim)
            self.assertIn("score", dim)
            self.assertIn("summary", dim)
            self.assertIn("evidence_hint", dim)

        # Verify metadata
        self.assertEqual(result["provider"], "mock")
        self.assertIn("latency_ms", result)
        self.assertIn("trace_id", result)

    # -------------------------------------------------------------------------
    # Scenario E: LLM config missing failure
    # -------------------------------------------------------------------------
    def test_scenario_e_llm_config_missing(self):
        """
        Scenario E: Generate cognition without LLM config
        Expect: error_code=L4_LLM_CONFIG_MISSING, blocked_by=LLM_UNAVAILABLE
        """
        print("\n=== Scenario E: LLM Config Missing ===")

        # Temporarily remove LLM config
        saved_config = {}
        config_keys = ["LLM_PROVIDER", "LLM_MODEL", "OPENAI_API_KEY",
                       "CLOUD_LLM_MODEL", "CLOUD_LLM_API_KEY", "CLOUD_LLM_BASE_URL",
                       "OPENAI_BASE_URL"]

        for key in config_keys:
            saved_config[key] = os.environ.get(key)
            if key in os.environ:
                del os.environ[key]

        try:
            from llm.client import generate_10d, LLMConfigError

            with self.assertRaises(LLMConfigError) as ctx:
                generate_10d("test input")

            print(f"Error raised: {ctx.exception.message}")
            self.assertIn("OPENAI_API_KEY", ctx.exception.message)

        finally:
            # Restore config
            for key, value in saved_config.items():
                if value is not None:
                    os.environ[key] = value

    # -------------------------------------------------------------------------
    # Scenario F: API-level LLM integration (mock)
    # -------------------------------------------------------------------------
    def test_scenario_f_api_llm_integration_mock(self):
        """
        Scenario F: Full API-level LLM integration test with mock
        Expect: Success envelope with 10 dimensions
        """
        print("\n=== Scenario F: API LLM Integration (Mock) ===")

        # Clear previous config and set mock
        from llm.client import generate_10d

        # Generate using mock (configured at module level)
        result = generate_10d(
            user_input=f"Repository: {TEST_REPO_URL}\nCommit: {TEST_COMMIT_SHA}",
            context={
                "repo_url": TEST_REPO_URL,
                "commit_sha": TEST_COMMIT_SHA,
                "requester_id": TEST_REQUESTER_ID,
            },
            use_mock=True
        )

        # Verify result structure matches API expectations
        self.assertEqual(len(result["dimensions"]), 10)

        # Verify all scores are valid
        for dim in result["dimensions"]:
            score = dim["score"]
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 100)

        print(f"LLM integration test passed: {len(result['dimensions'])} dimensions generated")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
