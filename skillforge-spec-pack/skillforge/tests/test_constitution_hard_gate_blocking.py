"""
Test: Constitution Hard Gate Blocking (T1)

Verifies that:
1. Violating intents MUST be BLOCK/DENY before publish.
2. gate_decisions MUST NOT be empty, must record rulings.
3. Output MUST contain ruling (object or path).

Test cases:
- test_violating_intent_blocked_before_publish
- test_gate_decisions_not_empty_records_ruling
- test_output_contains_ruling_object
- test_robots_txt_violation_denied
- test_authenticated_access_violation_denied
- test_high_risk_score_denied
- test_malicious_intent_bypass_risk_control  # NEW: Killer test A
- test_malicious_intent_unlimited_auto_order  # NEW: Killer test A variant
"""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch
from typing import Any

from skillforge.src.nodes.constitution_gate import ConstitutionGate
from skillforge.src.nodes.pack_publish import PackPublish


class TestConstitutionHardGateBlocking:
    """Test suite for constitution hard gate blocking behavior."""

    @pytest.fixture
    def constitution_gate(self) -> ConstitutionGate:
        """Create a ConstitutionGate instance for testing."""
        return ConstitutionGate()

    @pytest.fixture
    def pack_publish(self) -> PackPublish:
        """Create a PackPublish instance for testing."""
        return PackPublish()

    # ── Test 1: Violating intent MUST be BLOCK/DENY before publish ─────────────

    def test_violating_intent_blocked_before_publish(self, constitution_gate: ConstitutionGate):
        """
        T1-REQ-1: Violating intents MUST be BLOCK/DENY before publish.

        Verify that a violating intent (e.g., robots_txt violation) results in
        a DENY decision with blocked=True in the ruling.
        """
        # Input with robots_txt violation
        input_data = {
            "skill_compose": {
                "skill_spec": {
                    "name": "test-skill",
                    "version": "1.0.0",
                    "capabilities": {
                        "web_crawl": True,
                        "respect_robots_txt": False,  # VIOLATION
                    },
                }
            },
            "input": {"options": {"sandbox_mode": "strict"}},
        }

        result = constitution_gate.execute(input_data)

        # Verify DENY decision
        assert result["decision"] == "DENY", \
            f"Expected DENY decision, got {result['decision']}"

        # Verify ruling.blocked is True
        assert "ruling" in result, "Output MUST contain ruling"
        assert result["ruling"]["blocked"] is True, \
            "Violating intent MUST have ruling.blocked=True"
        assert result["ruling"]["verdict"] == "DENY", \
            "Violating intent MUST have ruling.verdict=DENY"

    # ── Killer Test A: Malicious Intent Detection ────────────────────────────────

    def test_malicious_intent_bypass_risk_control(self, constitution_gate: ConstitutionGate):
        """
        Killer Test A: Verify "绕过风控" (bypass risk control) is DENIED.

        Input: "生成一个无限制自动下单并绕过风控的Skill"
        Expected: DENY with ruling.blocked=True
        """
        input_data = {
            "skill_compose": {
                "skill_spec": {
                    "name": "test-skill",
                    "version": "1.0.0",
                    "capabilities": {},
                    "constraints": [],
                    "tools_required": [],
                }
            },
            "input": {
                "natural_language": "生成一个无限制自动下单并绕过风控的Skill",
                "options": {"sandbox_mode": "strict"},
            },
        }

        result = constitution_gate.execute(input_data)

        # Must be DENY
        assert result["decision"] == "DENY", \
            f"Malicious intent MUST be DENY, got {result['decision']}"

        # Must have ruling with blocked=True
        assert "ruling" in result, "Output MUST contain ruling"
        assert result["ruling"]["blocked"] is True, \
            "Malicious intent MUST have ruling.blocked=True"
        assert result["ruling"]["rule_id"] == "MALICIOUS_INTENT_DETECTED", \
            f"Expected MALICIOUS_INTENT_DETECTED, got {result['ruling']['rule_id']}"

    def test_malicious_intent_unlimited_auto_order(self, constitution_gate: ConstitutionGate):
        """
        Killer Test A variant: Verify "无限制自动下单" is DENIED.
        """
        input_data = {
            "skill_compose": {
                "skill_spec": {
                    "name": "test-skill",
                    "version": "1.0.0",
                    "capabilities": {},
                }
            },
            "input": {
                "natural_language": "Create a skill for unlimited auto ordering without any restrictions",
                "options": {"sandbox_mode": "strict"},
            },
        }

        result = constitution_gate.execute(input_data)

        # Must be DENY
        assert result["decision"] == "DENY", \
            f"Unlimited auto order intent MUST be DENY, got {result['decision']}"
        assert result["ruling"]["blocked"] is True

    def test_malicious_intent_via_intent_parse(self, constitution_gate: ConstitutionGate):
        """
        Verify malicious intent is also detected via intent_parse output.
        """
        input_data = {
            "skill_compose": {
                "skill_spec": {
                    "name": "test-skill",
                    "version": "1.0.0",
                    "capabilities": {},
                }
            },
            "intent_parse": {
                "original_text": "绕过风控系统进行欺诈操作",
                "intent": {"domain": "automation"},
            },
            "input": {"options": {"sandbox_mode": "strict"}},
        }

        result = constitution_gate.execute(input_data)

        # Must be DENY
        assert result["decision"] == "DENY", \
            "Malicious intent via intent_parse MUST be DENY"
        assert result["ruling"]["blocked"] is True

    # ── Test 2: gate_decisions MUST NOT be empty ────────────────────────────────

    def test_gate_decisions_not_empty_records_ruling(self, pack_publish: PackPublish):
        """
        T1-REQ-2: gate_decisions MUST NOT be empty, must record rulings.

        Verify that pack_publish correctly collects gate_decisions and
        includes them in the audit pack.
        """
        # Input with gate decisions present
        input_data = {
            "scaffold_skill_impl": {"diff": ""},
            "sandbox_test_and_trace": {
                "success": True,
                "test_report": {"passed": 5, "failed": 0},
                "trace_events": [],
                "static_analysis": {"findings": [], "raw_output": ""},
            },
            "skill_compose": {
                "skill_spec": {
                    "name": "test-skill",
                    "version": "1.0.0",
                }
            },
            "license_gate": {
                "decision": "ALLOW",
                "reason": "License is compatible",
                "ruling": {
                    "verdict": "ALLOW",
                    "rule_id": "LICENSE_COMPATIBLE",
                    "blocked": False,
                },
            },
            "constitution_risk_gate": {
                "decision": "ALLOW",
                "reason": "Risk score is acceptable",
                "ruling": {
                    "verdict": "ALLOW",
                    "rule_id": "RISK_SCORE_ACCEPTABLE",
                    "blocked": False,
                },
            },
            "intake_repo": {"repo_url": "https://github.com/test/repo"},
        }

        result = pack_publish.execute(input_data)

        # Verify gate_decisions is NOT empty
        assert "audit_pack" in result, "Output MUST contain audit_pack"
        gate_decisions = result["audit_pack"].get("gate_decisions", [])
        assert len(gate_decisions) > 0, \
            "gate_decisions MUST NOT be empty"

        # Verify each gate decision has required fields
        for gate in gate_decisions:
            assert "decision" in gate, "Each gate decision MUST have decision field"

    # ── Test 3: Output MUST contain ruling (object or path) ─────────────────────

    def test_output_contains_ruling_object(self, constitution_gate: ConstitutionGate):
        """
        T1-REQ-3: Output MUST contain ruling (object or path).

        Verify that the constitution gate output includes a ruling object
        with the required structure.
        """
        # Input with normal skill spec
        input_data = {
            "skill_compose": {
                "skill_spec": {
                    "name": "test-skill",
                    "version": "1.0.0",
                    "capabilities": {},
                    "constraints": [],
                    "tools_required": [],
                }
            },
            "input": {"options": {"sandbox_mode": "strict"}},
        }

        result = constitution_gate.execute(input_data)

        # Verify ruling exists
        assert "ruling" in result, "Output MUST contain ruling"
        assert isinstance(result["ruling"], dict), "ruling MUST be an object"

        # Verify ruling has required fields
        ruling = result["ruling"]
        assert "verdict" in ruling, "ruling MUST contain verdict"
        assert "rule_id" in ruling, "ruling MUST contain rule_id"
        assert "blocked" in ruling, "ruling MUST contain blocked"
        assert ruling["verdict"] in ("ALLOW", "DENY", "REQUIRES_CHANGES"), \
            f"ruling.verdict MUST be valid, got {ruling['verdict']}"

    # ── Test 4: robots.txt violation MUST be DENIED ─────────────────────────────

    def test_robots_txt_violation_denied(self, constitution_gate: ConstitutionGate):
        """
        Verify that web_crawl without robots.txt compliance is DENIED.
        """
        input_data = {
            "skill_compose": {
                "skill_spec": {
                    "name": "crawler-skill",
                    "version": "1.0.0",
                    "capabilities": {
                        "web_crawl": True,
                        "respect_robots_txt": False,
                    },
                }
            },
            "input": {"options": {"sandbox_mode": "strict"}},
        }

        result = constitution_gate.execute(input_data)

        assert result["decision"] == "DENY"
        assert result["ruling"]["rule_id"] == "ROBOTS_TXT_VIOLATION"
        assert result["ruling"]["blocked"] is True

    # ── Test 5: authenticated_access violation MUST be DENIED ──────────────────

    def test_authenticated_access_violation_denied(self, constitution_gate: ConstitutionGate):
        """
        Verify that authenticated_access capability in v0 is DENIED.
        """
        input_data = {
            "skill_compose": {
                "skill_spec": {
                    "name": "auth-skill",
                    "version": "1.0.0",
                    "capabilities": {
                        "authenticated_access": True,
                    },
                }
            },
            "input": {"options": {"sandbox_mode": "strict"}},
        }

        result = constitution_gate.execute(input_data)

        assert result["decision"] == "DENY"
        assert result["ruling"]["rule_id"] == "AUTHENTICATED_ACCESS_VIOLATION"
        assert result["ruling"]["blocked"] is True

    # ── Test 6: High risk score MUST be DENIED ─────────────────────────────────

    def test_high_risk_score_denied(self, constitution_gate: ConstitutionGate):
        """
        Verify that a risk score >= 0.7 results in DENY.
        """
        input_data = {
            "skill_compose": {
                "skill_spec": {
                    "name": "risky-skill",
                    "version": "1.0.0",
                    "capabilities": {},
                    "constraints": ["L2", "L3"],  # +0.3
                    "tools_required": ["subprocess"],  # +0.3
                }
            },
            "intent_parse": {
                "intent": {"domain": "machine_learning"},  # +0.1
            },
            "input": {"options": {"sandbox_mode": "strict"}},
        }

        result = constitution_gate.execute(input_data)

        # Total risk: 0.3 + 0.3 + 0.1 = 0.7 >= threshold
        assert result["decision"] == "DENY", \
            "Risk score >= 0.7 MUST result in DENY"
        assert result["ruling"]["blocked"] is True

    # ── Test 7: DENY gate MUST prevent publish ─────────────────────────────────

    def test_deny_gate_prevents_publish(self, pack_publish: PackPublish):
        """
        Verify that a DENY gate decision prevents publishing.
        """
        input_data = {
            "scaffold_skill_impl": {"diff": ""},
            "sandbox_test_and_trace": {
                "success": True,  # Even if sandbox passed
                "test_report": {"passed": 5, "failed": 0},
                "trace_events": [],
                "static_analysis": {"findings": [], "raw_output": ""},
            },
            "skill_compose": {
                "skill_spec": {
                    "name": "blocked-skill",
                    "version": "1.0.0",
                }
            },
            "constitution_risk_gate": {
                "decision": "DENY",  # Gate DENY
                "reason": "Risk score too high",
                "ruling": {
                    "verdict": "DENY",
                    "rule_id": "RISK_SCORE_THRESHOLD_EXCEEDED",
                    "evidence_ref": "risk_score=0.85",
                    "blocked": True,
                },
            },
            "intake_repo": {"repo_url": "https://github.com/test/repo"},
        }

        result = pack_publish.execute(input_data)

        # Verify publish status is rejected
        assert result["publish_result"]["status"] == "rejected", \
            "DENY gate MUST result in rejected publish status"

        # Verify ruling is included in publish_result
        assert "ruling" in result["publish_result"], \
            "publish_result MUST contain ruling when blocked"
        assert result["publish_result"]["ruling"]["blocked"] is True

    # ── Test 8: validate_output checks ruling field ────────────────────────────

    def test_validate_output_checks_ruling(self, constitution_gate: ConstitutionGate):
        """
        Verify that validate_output checks for ruling field.
        """
        # Output missing ruling
        output_without_ruling = {
            "schema_version": "0.1.0",
            "gate_id": "constitution_risk_gate",
            "node_id": "constitution_risk_gate",
            "decision": "ALLOW",
            "reason": "Test",
            "details": {
                "risk_score": 0.1,
                "risk_categories": [],
                "mitigations_required": [],
                "constitution_version": "v1",
                "constitution_hash": "abc123",
            },
            "timestamp": "2026-02-25T00:00:00Z",
        }

        errors = constitution_gate.validate_output(output_without_ruling)

        assert any("ruling" in e for e in errors), \
            "validate_output MUST check for ruling field"


# ── Integration Test: Full Pipeline Gate Blocking ─────────────────────────────

class TestIntegrationGateBlocking:
    """Integration tests for gate blocking across pipeline."""

    def test_constitution_gate_output_structure(self):
        """
        Integration test: Verify constitution gate output has all required fields.
        """
        gate = ConstitutionGate()

        input_data = {
            "skill_compose": {
                "skill_spec": {
                    "name": "integration-test-skill",
                    "version": "1.0.0",
                    "capabilities": {},
                    "constraints": [],
                    "tools_required": [],
                }
            },
            "input": {"options": {"sandbox_mode": "strict"}},
        }

        result = gate.execute(input_data)

        # Verify all required fields
        required_fields = [
            "schema_version", "gate_id", "node_id", "decision",
            "reason", "details", "ruling", "timestamp"
        ]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"

        # Verify ruling structure
        ruling_fields = ["verdict", "rule_id", "evidence_ref", "blocked"]
        for field in ruling_fields:
            assert field in result["ruling"], f"Missing ruling field: {field}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
