import asyncio
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from api.routes.n8n_orchestration import RunIntentRequest, run_intent


class TestRunIntentInternalPermit(unittest.TestCase):
    @staticmethod
    def _execution_contract() -> dict:
        return {
            "contract_version": "v1",
            "intent_id": "intent-test",
            "ruleset_revision": "ruleset-v1",
            "constitution_ref": "constitution-hash-v1",
            "inputs": {"repo_url": "https://github.com/skillforge/workflow-orchestration"},
            "outputs": {"status": "COMPLETED"},
            "controls": {
                "timeout_ms": 30000,
                "max_targets": 1,
                "network_policy": "DENY_BY_DEFAULT",
                "file_policy": "ALLOWLIST",
            },
            "side_effects": [{"kind": "EXTERNAL_API", "details": "n8n trigger"}],
            "roles": {
                "execution": {"responsibilities": ["execute"], "allowed_actions": ["run_intent"]},
                "review": {"responsibilities": ["review"], "checks": ["acceptance"]},
                "compliance": {"responsibilities": ["compliance"], "must_follow": "B-v1"},
            },
            "acceptance_tests": [{"id": "AT-001", "assertion": "ok=true", "evidence_required": ["EV_KIND:LOG"]}],
            "artifacts_expected": ["EVIDENCE"],
            "evidence_requirements": [{"for_acceptance_id": "AT-001", "evidence_kind": "LOG", "locator_hint": "api-response"}],
        }

    def _compliance_attestation(self, execution_contract: dict) -> dict:
        from api.routes.n8n_orchestration import _canonical_contract_hash
        return {
            "decision": "PASS",
            "reasons": ["all checks passed"],
            "evidence_refs": [{"id": "EV-COMP-001"}],
            "contract_hash": _canonical_contract_hash(execution_contract),
            "reviewed_at": "2026-02-21T10:00:00Z",
        }

    def test_blocks_external_permit_injection(self):
        req = RunIntentRequest(
            repo_url="https://github.com/skillforge/workflow-orchestration",
            commit_sha="a1b2c3d4e5f6789012345678901234567890abcd",
            at_time="2026-02-20T14:30:00Z",
            intent_id="intent-test-001",
            requester_id="user-n8n-test",
            tier="STUDIO",
            permit_token="FORBIDDEN",
        )
        out = asyncio.run(run_intent(req))
        self.assertFalse(out["ok"])
        self.assertEqual(out["error_code"], "N8N_FORBIDDEN_FIELD_INJECTION")

    def test_allows_internal_permit_for_studio(self):
        os.environ["PERMIT_HS256_KEY"] = "test-signing-key-for-unit-tests-2026"
        contract = self._execution_contract()
        req = RunIntentRequest(
            repo_url="https://github.com/skillforge/workflow-orchestration",
            commit_sha="a1b2c3d4e5f6789012345678901234567890abcd",
            at_time="2026-02-20T14:30:00Z",
            intent_id="intent-test-allow",
            requester_id="user-n8n-test",
            tier="STUDIO",
            execution_contract=contract,
            compliance_attestation=self._compliance_attestation(contract),
        )
        out = asyncio.run(run_intent(req))
        self.assertTrue(out["ok"])
        self.assertEqual(out["gate_decision"], "ALLOW")
        self.assertTrue(out["release_allowed"])
        self.assertTrue(str(out["run_id"]).startswith("RUN-N8N-"))
        self.assertTrue(str(out["evidence_ref"]).startswith("EV-N8N-INTENT-"))

    def test_fails_closed_when_internal_permit_key_missing(self):
        old = os.environ.pop("PERMIT_HS256_KEY", None)
        try:
            contract = self._execution_contract()
            req = RunIntentRequest(
                repo_url="https://github.com/skillforge/workflow-orchestration",
                commit_sha="a1b2c3d4e5f6789012345678901234567890abcd",
                at_time="2026-02-20T14:30:00Z",
                intent_id="intent-test-key-missing",
                requester_id="user-n8n-test",
                tier="STUDIO",
                execution_contract=contract,
                compliance_attestation=self._compliance_attestation(contract),
            )
            out = asyncio.run(run_intent(req))
            self.assertFalse(out["ok"])
            self.assertEqual(out["error_code"], "N8N_PERMIT_ISSUE_FAILED")
        finally:
            if old is not None:
                os.environ["PERMIT_HS256_KEY"] = old

    def test_blocks_when_compliance_missing(self):
        os.environ["PERMIT_HS256_KEY"] = "test-signing-key-for-unit-tests-2026"
        req = RunIntentRequest(
            repo_url="https://github.com/skillforge/workflow-orchestration",
            commit_sha="a1b2c3d4e5f6789012345678901234567890abcd",
            at_time="2026-02-20T14:30:00Z",
            intent_id="intent-test-missing-compliance",
            requester_id="user-n8n-test",
            tier="STUDIO",
            execution_contract=self._execution_contract(),
            compliance_attestation=None,
        )
        out = asyncio.run(run_intent(req))
        self.assertFalse(out["ok"])
        self.assertEqual(out["blocked_by"], "EXECUTION_GUARD")
        self.assertIn("required_changes", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
