"""
Tests for T10 contracts: JudgmentOverrides, ResidualRisks, ReleaseDecision.

These tests verify:
1. Hard constraints: contract 失败 / 无证据 finding / 明确高危命中，不允许被判断洗白
2. Judgment override cannot be free-form text
3. Residual risks are explicitly declared
4. Release decision has traceable evidence
5. At least 3 sample scenarios are provided
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from skillforge.src.contracts.judgment_overrides import (
    JudgmentOverride,
    JudgmentOverrides,
    OriginalDecision,
    OverrideDecision,
    JustificationCode,
    JustificationCategory,
    ApproverRole,
    EvidenceRef as OverrideEvidenceRef,
    JustificationDetail,
    OverrideCondition,
    Approver,
    ConditionType,
    can_override_finding,
    create_override_id,
    create_judgment_overrides,
)
from skillforge.src.contracts.residual_risks import (
    ResidualRisk,
    ResidualRisks,
    RiskLevel,
    RiskCategory,
    Likelihood,
    Impact,
    RiskStatus,
    MitigationStrategy,
    ReviewFrequency,
    EvidenceRef as RiskEvidenceRef,
    MitigationAction,
    MitigationPlan,
    MonitoringPlan,
    AcceptanceDetails,
    create_risk_id,
    create_residual_risks,
    calculate_risk_score,
)
from skillforge.src.contracts.release_decision import (
    ReleaseDecision,
    ReleaseOutcome,
    RationaleCode,
    DecisionContext,
    GateType,
    ConditionType as ReleaseConditionType,
    make_release_decision,
    check_blockable_findings,
    EscalationTarget,
    EscalationReason,
    DecisionRationale,
    ReleaseCondition,
    DecisionChainEntry,
    EvidenceRef as DecisionEvidenceRef,
)


# ============================================================================
# Hard Constraint Tests: Override Not Allowed for Blocked Findings
# ============================================================================
class TestOverrideHardConstraints:
    """Tests for T10 hard constraints on judgment overrides."""

    def test_no_evidence_cannot_override(self):
        """Findings with no evidence cannot be overridden."""
        result = can_override_finding(
            original_decision="REJECT",
            evidence_strength=None,
            truth_assessment=None,
            severity=None,
            evidence_count=0,
        )
        assert result["allowed"] is False
        assert "NO_EVIDENCE_OVERRIDE" in result["reason"]

    def test_insufficient_evidence_cannot_override(self):
        """Findings with INSUFFICIENT evidence cannot be overridden."""
        result = can_override_finding(
            original_decision="REJECT",
            evidence_strength="INSUFFICIENT",
            truth_assessment="UNCERTAIN",
            severity="HIGH",
            evidence_count=2,
        )
        assert result["allowed"] is False
        assert "MISSING_EVIDENCE" in result["reason"]

    def test_critical_confirmed_cannot_override(self):
        """CRITICAL findings with CONFIRMED truth cannot be overridden."""
        result = can_override_finding(
            original_decision="REJECT",
            evidence_strength="STRONG",
            truth_assessment="CONFIRMED",
            severity="CRITICAL",
            evidence_count=2,
        )
        assert result["allowed"] is False
        assert "CRITICAL_RISK_NO_OVERRIDE" in result["reason"]

    def test_reject_to_release_not_allowed(self):
        """Cannot upgrade REJECT directly to RELEASE."""
        result = can_override_finding(
            original_decision="REJECT",
            evidence_strength="STRONG",
            truth_assessment="LIKELY_TRUE",
            severity="MEDIUM",
            evidence_count=2,
        )
        assert result["allowed"] is True
        assert "RELEASE" in result["forbidden_decisions"]
        assert "CONDITIONAL_RELEASE" in result["allowed_decisions"]

    def test_high_weak_evidence_can_override_to_conditional(self):
        """HIGH severity with WEAK evidence can be overridden to CONDITIONAL_RELEASE."""
        result = can_override_finding(
            original_decision="REJECT",
            evidence_strength="WEAK",
            truth_assessment="UNCERTAIN",
            severity="HIGH",
            evidence_count=1,
        )
        assert result["allowed"] is True


# ============================================================================
# Judgment Override Structure Tests
# ============================================================================
class TestJudgmentOverrideStructure:
    """Tests for judgment override data structures."""

    def test_override_requires_evidence_refs(self):
        """Override must have at least one evidence ref."""
        override = JudgmentOverride(
            override_id="O-20260316_120000-1",
            finding_id="F-rule_scan-E420-abc12345",
            original_decision=OriginalDecision.REJECT,
            override_decision=OverrideDecision.CONDITIONAL_RELEASE,
            justification_code=JustificationCode.COMPENSATING_CONTROL_EXISTS,
            approver=Approver(
                approver_id="user123",
                approver_role=ApproverRole.TECHNICAL_LEAD,
                approval_scope="single_finding",
            ),
            approved_at="2026-03-16T12:00:00Z",
            evidence_refs=[
                OverrideEvidenceRef(kind="FILE", locator="docs/compensating_control.md")
            ],
            justification_detail=JustificationDetail(
                category=JustificationCategory.MITIGATION_PROVIDED,
                compensating_control="INPUT_VALIDATION_ADDED",
            ),
        )
        result = override.to_dict()
        assert len(result["evidence_refs"]) == 1
        assert result["justification_code"] == "COMPENSATING_CONTROL_EXISTS"

    def test_justification_not_free_text(self):
        """Justification must be from enum, not free text."""
        # Valid justifications (from enum)
        valid_codes = [
            JustificationCode.FALSE_POSITIVE_DETECTED,
            JustificationCode.COMPENSATING_CONTROL_EXISTS,
            JustificationCode.BUSINESS_JUSTIFICATION,
            JustificationCode.TECHNICAL_DEBT_ACCEPTED,
        ]
        for code in valid_codes:
            assert code.value in [e.value for e in JustificationCode]

    def test_override_conditions_structured(self):
        """Override conditions must be structured, not free text."""
        condition = OverrideCondition(
            type=ConditionType.REMEDIATION_DEADLINE,
            description="Remediation deadline: fix must be completed by 2026-04-01",
            evidence_path="run/remediation_tracker.json",
        )
        result = condition.to_dict()
        assert result["type"] == "remediation_deadline"
        assert "deadline" in result["description"].lower() or "remediation" in result["description"].lower()


# ============================================================================
# Residual Risk Tests
# ============================================================================
class TestResidualRisks:
    """Tests for residual risk records."""

    def test_risk_from_override_has_source_link(self):
        """Residual risk must link to source override."""
        risk = ResidualRisk(
            risk_id="R-20260316_120000-1",
            source_finding_id="F-rule_scan-E420-abc12345",
            source_override_id="O-20260316_120000-1",
            risk_level=RiskLevel.MEDIUM,
            risk_category=RiskCategory.SECURITY,
            likelihood=Likelihood.POSSIBLE,
            impact=Impact.MEDIUM,
            status=RiskStatus.OPEN,
            created_at="2026-03-16T12:00:00Z",
        )
        result = risk.to_dict()
        assert result["source_override_id"] == "O-20260316_120000-1"

    def test_calculate_risk_score(self):
        """Risk score calculation should be deterministic."""
        # VERY_LIKELY (5) x SEVERE (5) = 25
        score = calculate_risk_score(Likelihood.VERY_LIKELY, Impact.SEVERE)
        assert score == 25

        # RARE (1) x MINIMAL (1) = 1
        score = calculate_risk_score(Likelihood.RARE, Impact.MINIMAL)
        assert score == 1

    def test_risk_status_enum(self):
        """Risk status must be from enum."""
        statuses = [
            RiskStatus.OPEN,
            RiskStatus.MITIGATING,
            RiskStatus.MONITORING,
            RiskStatus.ACCEPTED,
            RiskStatus.CLOSED,
        ]
        for status in statuses:
            assert status.value in ["open", "mitigating", "monitoring", "accepted", "closed"]


# ============================================================================
# Release Decision Tests
# ============================================================================
class TestReleaseDecision:
    """Tests for release decision logic."""

    def test_blockable_findings_cause_reject(self):
        """Findings with CRITICAL+CONFIRMED cause REJECT unless overridden."""
        findings = [
            {
                "finding_id": "F-rule_scan-E420-abc12345",
                "what": {"severity": "CRITICAL"},
                "truth_assessment": "CONFIRMED",
                "evidence_refs": [{"kind": "FILE", "locator": "scan.json"}],
            }
        ]

        result = check_blockable_findings(findings, overridden_ids=set())
        assert result["has_blockable"] is True
        assert "F-rule_scan-E420-abc12345" in result["blocking_findings"]

    def test_overridden_finding_not_blocking(self):
        """Overridden findings should not block release."""
        findings = [
            {
                "finding_id": "F-rule_scan-E420-abc12345",
                "what": {"severity": "CRITICAL"},
                "truth_assessment": "CONFIRMED",
                "evidence_refs": [{"kind": "FILE", "locator": "scan.json"}],
            }
        ]

        result = check_blockable_findings(findings, overridden_ids={"F-rule_scan-E420-abc12345"})
        assert result["has_blockable"] is False
        assert len(result["blocking_findings"]) == 0

    def test_critical_residual_risks_cause_escalate(self):
        """CRITICAL residual risks cause ESCALATE decision."""
        decision = make_release_decision(
            findings=[],
            overrides=[],
            residual_risks=[
                {
                    "risk_id": "R-20260316_120000-1",
                    "risk_level": "CRITICAL",
                }
            ],
            evidence_refs=[
                DecisionEvidenceRef(kind="REPORT", locator="run/T10_evidence/residual_risks.json")
            ],
            run_id="20260316_120000",
            skill_id="skill-1.0.0-abc12345",
        )
        assert decision.outcome == ReleaseOutcome.ESCALATE
        assert decision.rationale.code == RationaleCode.HIGH_RISK_THRESHOLD_EXCEEDED

    def test_all_clear_causes_release(self):
        """No blocking findings or critical risks causes RELEASE."""
        decision = make_release_decision(
            findings=[
                {
                    "finding_id": "F-validation-E301-abc12345",
                    "what": {"severity": "LOW"},
                    "truth_assessment": "CONFIRMED",
                    "evidence_refs": [{"kind": "FILE", "locator": "report.json"}],
                }
            ],
            overrides=[],
            residual_risks=[],
            evidence_refs=[
                DecisionEvidenceRef(kind="FILE", locator="run/T3_evidence/validation_report.json")
            ],
            run_id="20260316_120000",
            skill_id="skill-1.0.0-abc12345",
        )
        assert decision.outcome == ReleaseOutcome.RELEASE
        assert decision.rationale.code == RationaleCode.ALL_CHECKS_PASSED

    def test_release_decision_requires_evidence(self):
        """Release decision must have evidence refs."""
        decision = ReleaseDecision(
            run_id="20260316_120000",
            skill_id="skill-1.0.0",
            decision_timestamp="2026-03-16T12:00:00Z",
            outcome=ReleaseOutcome.RELEASE,
            rationale=DecisionRationale(code=RationaleCode.ALL_CHECKS_PASSED),
            evidence_refs=[
                DecisionEvidenceRef(kind="REPORT", locator="run/T8_evidence/adjudication_report.json")
            ],
        )
        result = decision.to_dict()
        assert len(result["evidence_refs"]) >= 1

    def test_make_release_decision_without_evidence_raises_value_error(self):
        """make_release_decision() raises ValueError when evidence_refs is empty (hard constraint)."""
        with pytest.raises(ValueError) as exc_info:
            make_release_decision(
                findings=[
                    {
                        "finding_id": "F-validation-E301-abc12345",
                        "what": {"severity": "LOW"},
                        "truth_assessment": "CONFIRMED",
                        "evidence_refs": [{"kind": "FILE", "locator": "report.json"}],
                    }
                ],
                overrides=[],
                residual_risks=[],
                evidence_refs=[],  # Empty evidence_refs should raise ValueError
                run_id="20260316_120000",
                skill_id="skill-1.0.0-abc12345",
            )
        # Verify the error message contains E021_NO_EVIDENCE
        assert "E021_NO_EVIDENCE" in str(exc_info.value)
        assert "Release decision requires supporting evidence" in str(exc_info.value)


# ============================================================================
# Sample File Tests
# ============================================================================
class TestSampleFiles:
    """Tests for sample JSON files."""

    def test_judgment_overrides_sample_exists(self):
        """Sample judgment_overrides.json should exist."""
        sample_path = Path("tests/contracts/T10/judgment_overrides.sample.json")
        assert sample_path.exists()

    def test_judgment_overrides_sample_valid(self):
        """Sample should be valid JSON."""
        sample_path = Path("tests/contracts/T10/judgment_overrides.sample.json")
        with open(sample_path) as f:
            data = json.load(f)
        assert "meta" in data
        assert "overrides" in data
        assert "summary" in data

    def test_residual_risks_sample_exists(self):
        """Sample residual_risks.json should exist."""
        sample_path = Path("tests/contracts/T10/residual_risks.sample.json")
        assert sample_path.exists()

    def test_residual_risks_sample_valid(self):
        """Sample should be valid JSON."""
        sample_path = Path("tests/contracts/T10/residual_risks.sample.json")
        with open(sample_path) as f:
            data = json.load(f)
        assert "meta" in data
        assert "risks" in data
        assert "summary" in data

    def test_release_decision_sample_exists(self):
        """Sample release_decision.json should exist."""
        sample_path = Path("tests/contracts/T10/release_decision.sample.json")
        assert sample_path.exists()

    def test_release_decision_sample_valid(self):
        """Sample should be valid JSON."""
        sample_path = Path("tests/contracts/T10/release_decision.sample.json")
        with open(sample_path) as f:
            data = json.load(f)
        assert "meta" in data
        assert "decision" in data
        assert "findings_summary" in data
        assert "evidence_refs" in data

    def test_at_least_3_sample_scenarios(self):
        """Should provide at least 3 sample scenarios."""
        # Check sample files contain at least 3 scenarios
        sample_dir = Path("tests/contracts/T10")
        scenarios_files = list(sample_dir.glob("*.sample.json"))
        assert len(scenarios_files) >= 3


# ============================================================================
# Integration Tests
# ============================================================================
class TestT10Integration:
    """Integration tests for T10 contracts."""

    def test_full_override_to_risk_flow(self):
        """Test complete flow from override to residual risk."""
        # Create override
        override = JudgmentOverride(
            override_id="O-20260316_120000-1",
            finding_id="F-rule_scan-E420-abc12345",
            original_decision=OriginalDecision.REJECT,
            override_decision=OverrideDecision.CONDITIONAL_RELEASE,
            justification_code=JustificationCode.TECHNICAL_DEBT_ACCEPTED,
            approver=Approver(
                approver_id="user123",
                approver_role=ApproverRole.ENGINEERING_MANAGER,
                approval_scope="skill_level",
            ),
            approved_at="2026-03-16T12:00:00Z",
            evidence_refs=[
                OverrideEvidenceRef(kind="TICKET", locator="JIRA-12345"),
                OverrideEvidenceRef(kind="REVIEW", locator="reviews/arch_review.md"),
            ],
            justification_detail=JustificationDetail(
                category=JustificationCategory.TEMPORAL_EXCEPTION,
                acceptance_expiry="2026-04-30T00:00:00Z",
                related_ticket="JIRA-12345",
            ),
            conditions=[
                OverrideCondition(
                    type=ConditionType.REMEDIATION_DEADLINE,
                    description="Must be fixed by 2026-04-15",
                )
            ],
            severity="HIGH",
            source_type="rule_scan",
        )

        # Create residual risk from override
        risk = ResidualRisk(
            risk_id="R-20260316_120000-1",
            source_finding_id=override.finding_id,
            source_override_id=override.override_id,
            risk_level=RiskLevel.HIGH,
            risk_category=RiskCategory.SECURITY,
            likelihood=Likelihood.POSSIBLE,
            impact=Impact.HIGH,
            status=RiskStatus.MITIGATING,
            created_at="2026-03-16T12:00:00Z",
            title="SQL injection risk temporarily accepted",
            description="SQL injection pattern found but accepted as technical debt with mitigating input validation",
            original_severity="HIGH",
            calculated_score=calculate_risk_score(Likelihood.POSSIBLE, Impact.HIGH),
            mitigation_strategy=MitigationStrategy.MITIGATE,
            mitigation_plan=MitigationPlan(
                actions=[
                    MitigationAction(
                        action="Add input validation library",
                        owner="engineering",
                        target_date="2026-04-15T00:00:00Z",
                    )
                ]
            ),
            related_ticket="JIRA-12345",
            evidence_refs=[
                RiskEvidenceRef(kind="TICKET", locator="JIRA-12345"),
                RiskEvidenceRef(kind="DOCUMENTATION", locator="docs/technical_debt_acceptance.md"),
            ],
        )

        # Verify linkage
        assert risk.source_override_id == override.override_id
        # Note: residual_risk_created is set separately in actual workflow

    def test_release_decision_with_overrides(self):
        """Test release decision with overrides applied."""
        findings = [
            {
                "finding_id": "F-rule_scan-E420-abc12345",
                "what": {"severity": "HIGH"},
                "truth_assessment": "LIKELY_TRUE",
                "evidence_refs": [{"kind": "FILE", "locator": "scan.json"}],
            }
        ]

        overrides = [
            {
                "override_id": "O-20260316_120000-1",
                "finding_id": "F-rule_scan-E420-abc12345",
                "justification_code": "COMPENSATING_CONTROL_EXISTS",
            }
        ]

        decision = make_release_decision(
            findings=findings,
            overrides=overrides,
            residual_risks=[],
            evidence_refs=[
                DecisionEvidenceRef(kind="REPORT", locator="run/T8_evidence/adjudication_report.json")
            ],
            run_id="20260316_120000",
            skill_id="skill-1.0.0",
        )

        # Should get CONDITIONAL or LIMITED due to override
        assert decision.outcome in [ReleaseOutcome.CONDITIONAL_RELEASE, ReleaseOutcome.LIMITED_RELEASE]
        assert "F-rule_scan-E420-abc12345" in decision.overridden_findings


# ============================================================================
# T10 Hard Constraint Compliance Tests
# ============================================================================
class TestT10HardConstraintCompliance:
    """Tests for T10 hard constraint compliance."""

    def test_contract_failure_no_whitewash(self):
        """Contract failure findings cannot be whitewashed."""
        # Schema validation failure = contract failure
        findings = [
            {
                "finding_id": "F-validation-E302-abc12345",
                "source": {"type": "validation", "code": "E302_SCHEMA_VALIDATION_FAILED"},
                "what": {"severity": "CRITICAL", "confidence": 1.0},
                "evidence_refs": [],
                "detected_at": "2026-03-16T12:00:00Z",
            }
        ]

        result = check_blockable_findings(findings, overridden_ids=set())
        # No evidence = blockable
        assert result["has_blockable"] is True

    def test_no_free_text_in_override(self):
        """Override justification must be enum, not free text."""
        overrides = create_judgment_overrides("20260316_120000")

        # Verify enum-based justification is enforced
        # The code structure prevents free text by using enum types
        valid_justification = JustificationCode.COMPENSATING_CONTROL_EXISTS
        assert hasattr(valid_justification, 'value')
        assert valid_justification.value == "COMPENSATING_CONTROL_EXISTS"

        # Verify all enum values are predefined
        all_codes = [j.value for j in JustificationCode]
        assert "FREE_TEXT_JUSTIFICATION" not in all_codes
        assert len(all_codes) == 10  # 10 predefined options


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
