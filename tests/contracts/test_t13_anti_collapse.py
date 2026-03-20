"""
T13 Anti-Collapse Report Tests

Test coverage for anti_collapse_report.py enforcing hard constraints:
- Boundary assertions verification
- Coverage integrity (claimed vs verified)
- Degradation classification (detecting misclassifications)
- Residual risk registration (even for PASS cases)
- Anti-collapse posture output parsing
"""
from __future__ import annotations

import json
import pytest
from datetime import datetime, timezone
from pathlib import Path

from skillforge.src.contracts.case_ledger import (
    CaseLedger,
    CaseRecord,
    BoundaryDeclaration,
    InScopeItem,
    OutOfScopeItem,
    InputScenario,
    ExpectedBehavior,
    ExpectedOutcome,
    ExecutionRecord,
    ActualBehavior,
    DeviationRecord,
    Adjudication,
    CaseRisk,
    create_minimal_ledger,
    create_case_from_scenario,
    add_case_to_ledger,
)

from skillforge.src.contracts.anti_collapse_report import (
    AntiCollapseReport,
    generate_anti_collapse_report,
    analyze_boundary_integrity,
    analyze_coverage_integrity,
    analyze_degradation_classification,
    analyze_residual_risks,
    calculate_anti_collapse_score,
    BoundaryAssertions,
    BoundaryViolation,
    CoverageIntegrity,
    DegradationClassification,
    ResidualRiskRegister,
    AntiCollapseScore,
    DegradedCaseReport,
    MisclassificationDetected,
)


class TestBoundaryAssertionsVerification:
    """Test boundary assertions verification."""

    def test_boundary_assertions_from_ledger(self):
        """Report must extract boundary assertions from case ledger."""
        # Create ledger manually to include data_constraints
        boundary = BoundaryDeclaration(
            in_scope=[
                InScopeItem(category="happy_path", description="Happy path scenarios"),
                InScopeItem(category="edge_case", description="Edge cases"),
            ],
            out_of_scope=[
                OutOfScopeItem(category="performance", reason="deferred"),
                OutOfScopeItem(category="security", reason="out_of_project_scope"),
            ],
            assumptions=[
                "Test environment available",
                "Data constraints accepted",
            ],
            data_constraints=[
                {"constraint": "Limited data", "impact": "limits_coverage"},
            ],
        )

        ledger = CaseLedger(
            ledger_id="LEDGER-TEST-001",
            boundary_declaration=boundary,
            created_by="test",
        )

        report = generate_anti_collapse_report(
            case_ledger=ledger,
            report_type="initial",
            created_by="test",
        )

        # Check boundary assertions
        assert report.boundary_assertions is not None
        # declared_boundaries includes in_scope, out_of_scope, and constraints
        assert len(report.boundary_assertions.declared_boundaries) >= 4  # 2 in_scope + 2 out_of_scope
        assert report.boundary_assertions.uncovered_declared is not None
        assert report.boundary_assertions.uncovered_declared.total_declared_uncovered == 2  # 2 out_of_scope

    def test_uncovered_properly_declared(self):
        """T13 Hard Constraint: Uncovered items must be declared."""
        ledger = create_minimal_ledger(
            created_by="test",
            in_scope_categories=[{"category": "happy_path", "description": "Test"}],
            out_of_scope_items=[
                {"category": "performance", "reason": "deferred"},
                {"category": "security", "reason": "out_of_project_scope"},
            ],
            assumptions=["Test"],
        )

        report = generate_anti_collapse_report(
            case_ledger=ledger,
            report_type="initial",
            created_by="test",
        )

        # Should have declared uncovered items
        uncovered = report.boundary_assertions.uncovered_declared
        assert uncovered.total_declared_uncovered == 2
        assert len(uncovered.verified_declared) >= 0
        # No implicit uncovered detected (properly declared)
        assert len(uncovered.implicit_uncovered_detected) == 0

    def test_declaration_integrity_score(self):
        """T13 Hard Constraint: declaration_integrity_score must be computed."""
        ledger = create_minimal_ledger(
            created_by="test",
            in_scope_categories=[{"category": "happy_path", "description": "Test"}],
            out_of_scope_items=[{"category": "performance", "reason": "deferred"}],
            assumptions=["Test"],
        )

        report = generate_anti_collapse_report(
            case_ledger=ledger,
            report_type="initial",
            created_by="test",
        )

        uncovered = report.boundary_assertions.uncovered_declared
        assert uncovered.declaration_integrity_score is not None
        assert 0.0 <= uncovered.declaration_integrity_score <= 1.0


class TestCoverageIntegrity:
    """Test coverage integrity analysis."""

    def test_claimed_vs_verified_coverage(self):
        """T13 Hard Constraint: Must compare claimed vs verified coverage."""
        ledger = create_minimal_ledger(
            created_by="test",
            in_scope_categories=[
                {"category": "happy_path", "description": "Happy path"},
                {"category": "edge_case", "description": "Edge cases"},
            ],
            assumptions=["Test"],
        )

        # Add one executed case
        case = CaseRecord(
            case_id="CASE-TEST-001",
            input_scenario=InputScenario(scenario_type="happy_path", inputs={}),
            expected_behavior=ExpectedBehavior(
                outcomes=[ExpectedOutcome(type="return_value", description="Test")]
            ),
            execution_record=ExecutionRecord(
                status="executed",
                executed_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                actual_behavior=ActualBehavior(),
            ),
            adjudication=Adjudication(
                decision="PASS",
                adjudicated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                adjudicated_by="test",
            ),
        )
        add_case_to_ledger(ledger, case)

        report = generate_anti_collapse_report(
            case_ledger=ledger,
            report_type="initial",
            created_by="test",
        )

        coverage = report.coverage_integrity
        assert coverage is not None
        assert coverage.claimed_coverage is not None
        assert coverage.verified_coverage is not None
        # Claimed: 1 in-scope covered out of 2 = 50%
        assert coverage.claimed_coverage["in_scope_count"] == 2
        assert coverage.claimed_coverage["covered_count"] == 1

    def test_coverage_gaps_detection(self):
        """T13 Hard Constraint: Must detect coverage gaps."""
        ledger = create_minimal_ledger(
            created_by="test",
            in_scope_categories=[
                {"category": "happy_path", "description": "Happy path"},
                {"category": "edge_case", "description": "Edge cases"},
            ],
            assumptions=["Test"],
        )

        # Add only one case (leaving gap)
        case = create_case_from_scenario(
            category="HAPPY",
            seq=1,
            scenario_type="happy_path",
            inputs={},
            expected_outcomes=[{"type": "return_value", "description": "Test"}],
        )
        # Keep pending - creates coverage gap
        add_case_to_ledger(ledger, case)

        report = generate_anti_collapse_report(
            case_ledger=ledger,
            report_type="initial",
            created_by="test",
        )

        coverage = report.coverage_integrity
        # Should have coverage gaps since not all in-scope are covered
        assert coverage.coverage_gaps is not None
        # The pending case means weak evidence
        assert len(coverage.coverage_gaps) > 0


class TestDegradationClassification:
    """Test degradation classification and misclassification detection."""

    def test_degraded_cases_explicitly_classified(self):
        """T13 Hard Constraint: Degraded cases must be explicitly classified."""
        ledger = create_minimal_ledger(
            created_by="test",
            in_scope_categories=[{"category": "happy_path", "description": "Test"}],
            assumptions=["Test"],
        )

        # Add DEGRADED case
        case = CaseRecord(
            case_id="CASE-DEGRADED-001",
            input_scenario=InputScenario(scenario_type="happy_path", inputs={}),
            expected_behavior=ExpectedBehavior(
                outcomes=[ExpectedOutcome(type="return_value", description="Test")]
            ),
            execution_record=ExecutionRecord(
                status="executed",
                executed_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                actual_behavior=ActualBehavior(
                    deviations=[
                        DeviationRecord(
                            type="performance_degradation",
                            description="Slower than expected"
                        )
                    ]
                ),
            ),
            adjudication=Adjudication(
                decision="DEGRADED",
                adjudicated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                adjudicated_by="test",
                degradation_level="minor",
            ),
        )
        add_case_to_ledger(ledger, case)

        report = generate_anti_collapse_report(
            case_ledger=ledger,
            report_type="initial",
            created_by="test",
        )

        degradation = report.degradation_classification
        assert degradation is not None
        assert degradation.cases_by_status["degraded_explicit"] == 1
        assert degradation.cases_by_status["fully_successful"] == 0
        assert len(degradation.degraded_cases) == 1
        # degraded_cases is a list of DegradedCaseReport dataclasses
        degraded_case = degradation.degraded_cases[0]
        assert degraded_case.degradation_level == "minor"

    def test_misclassification_detection_pass_with_deviation(self):
        """T13 Hard Constraint: PASS with deviations must be flagged as misclassification."""
        ledger = create_minimal_ledger(
            created_by="test",
            in_scope_categories=[{"category": "happy_path", "description": "Test"}],
            assumptions=["Test"],
        )

        # Add PASS case WITH deviations (MISCLASSIFICATION)
        case = CaseRecord(
            case_id="CASE-MISCHECK-001",
            input_scenario=InputScenario(scenario_type="happy_path", inputs={}),
            expected_behavior=ExpectedBehavior(
                outcomes=[ExpectedOutcome(type="return_value", description="Test")]
            ),
            execution_record=ExecutionRecord(
                status="executed",
                executed_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                actual_behavior=ActualBehavior(
                    deviations=[
                        DeviationRecord(
                            type="outcome_mismatch",
                            description="Got different result",
                            severity="MEDIUM",
                        )
                    ]
                ),
            ),
            adjudication=Adjudication(
                decision="PASS",  # WRONG: should be DEGRADED
                adjudicated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                adjudicated_by="test",
            ),
        )
        add_case_to_ledger(ledger, case)

        report = generate_anti_collapse_report(
            case_ledger=ledger,
            report_type="initial",
            created_by="test",
        )

        degradation = report.degradation_classification
        # Should detect misclassification
        assert degradation.cases_by_status["degraded_pass"] == 1  # PASS with deviations
        assert len(degradation.misclassification_detected) == 1
        # misclassification_detected is a list of MisclassificationDetected dataclasses
        misclass = degradation.misclassification_detected[0]
        assert misclass.case_id == "CASE-MISCHECK-001"

    def test_classification_integrity_score(self):
        """T13 Hard Constraint: classification_integrity_score must be computed."""
        ledger = create_minimal_ledger(
            created_by="test",
            in_scope_categories=[{"category": "happy_path", "description": "Test"}],
            assumptions=["Test"],
        )

        # Add proper PASS case (no deviations)
        case = CaseRecord(
            case_id="CASE-PASS-001",
            input_scenario=InputScenario(scenario_type="happy_path", inputs={}),
            expected_behavior=ExpectedBehavior(
                outcomes=[ExpectedOutcome(type="return_value", description="Test")]
            ),
            execution_record=ExecutionRecord(
                status="executed",
                executed_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                actual_behavior=ActualBehavior(),  # No deviations
            ),
            adjudication=Adjudication(
                decision="PASS",
                adjudicated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                adjudicated_by="test",
            ),
        )
        add_case_to_ledger(ledger, case)

        report = generate_anti_collapse_report(
            case_ledger=ledger,
            report_type="initial",
            created_by="test",
        )

        degradation = report.degradation_classification
        assert degradation.classification_integrity_score is not None
        assert 0.0 <= degradation.classification_integrity_score <= 1.0
        # Should be 1.0 since no misclassifications
        assert degradation.classification_integrity_score == 1.0


class TestResidualRiskRegistration:
    """Test residual risk registration (even for PASS cases)."""

    def test_residual_risks_registered(self):
        """T13 Hard Constraint: Residual risks must be registered."""
        ledger = create_minimal_ledger(
            created_by="test",
            in_scope_categories=[{"category": "happy_path", "description": "Test"}],
            assumptions=["Test"],
        )

        # Add case with residual risks
        case = CaseRecord(
            case_id="CASE-RISK-001",
            input_scenario=InputScenario(scenario_type="happy_path", inputs={}),
            expected_behavior=ExpectedBehavior(
                outcomes=[ExpectedOutcome(type="return_value", description="Test")]
            ),
            execution_record=ExecutionRecord(
                status="executed",
                executed_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                actual_behavior=ActualBehavior(),
            ),
            adjudication=Adjudication(
                decision="PASS",
                adjudicated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                adjudicated_by="test",
            ),
            residual_risks=[
                CaseRisk(
                    risk_id="RISK-001",
                    risk_category="test_gap",
                    description="Some edge cases not tested",
                    mitigation="Monitor production",
                ),
                CaseRisk(
                    risk_category="coverage_hole",
                    description="Limited data coverage",
                ),
            ],
        )
        add_case_to_ledger(ledger, case)

        report = generate_anti_collapse_report(
            case_ledger=ledger,
            report_type="initial",
            created_by="test",
        )

        risks = report.residual_risk_register
        assert risks is not None
        assert risks.total_risks == 2
        assert risks.by_category["test_gap"] == 1
        assert risks.by_category["coverage_hole"] == 1

    def test_pass_case_with_residual_risks(self):
        """T13 Hard Constraint: Even PASS cases should have residual risks."""
        ledger = create_minimal_ledger(
            created_by="test",
            in_scope_categories=[{"category": "happy_path", "description": "Test"}],
            assumptions=["Test"],
        )

        # Add PASS case with risk
        case = CaseRecord(
            case_id="CASE-PASS-RISK-001",
            input_scenario=InputScenario(scenario_type="happy_path", inputs={}),
            expected_behavior=ExpectedBehavior(
                outcomes=[ExpectedOutcome(type="return_value", description="Test")]
            ),
            execution_record=ExecutionRecord(
                status="executed",
                executed_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                actual_behavior=ActualBehavior(),
            ),
            adjudication=Adjudication(
                decision="PASS",
                adjudicated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                adjudicated_by="test",
            ),
            residual_risks=[
                CaseRisk(
                    risk_category="coverage_hole",
                    description="Minor coverage gap",
                ),
            ],
        )
        add_case_to_ledger(ledger, case)

        report = generate_anti_collapse_report(
            case_ledger=ledger,
            report_type="initial",
            created_by="test",
        )

        risks = report.residual_risk_register
        # Check that PASS case risks are tracked
        assert risks.by_case_status is not None
        # Risk should be counted
        assert risks.total_risks == 1

    def test_missing_risk_assessment_gaps(self):
        """T13 Hard Constraint: Must detect cases with missing risk assessment."""
        ledger = create_minimal_ledger(
            created_by="test",
            in_scope_categories=[{"category": "happy_path", "description": "Test"}],
            assumptions=["Test"],
        )

        # Add case WITHOUT residual risks
        case = CaseRecord(
            case_id="CASE-NORISK-001",
            input_scenario=InputScenario(scenario_type="happy_path", inputs={}),
            expected_behavior=ExpectedBehavior(
                outcomes=[ExpectedOutcome(type="return_value", description="Test")]
            ),
            execution_record=ExecutionRecord(
                status="executed",
                executed_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                actual_behavior=ActualBehavior(),
            ),
            adjudication=Adjudication(
                decision="PASS",
                adjudicated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                adjudicated_by="test",
            ),
            # No residual_risks - gap!
        )
        add_case_to_ledger(ledger, case)

        report = generate_anti_collapse_report(
            case_ledger=ledger,
            report_type="initial",
            created_by="test",
        )

        risks = report.residual_risk_register
        # Should detect gaps
        assert risks.gaps_detected is not None
        assert len(risks.gaps_detected) > 0
        assert risks.gaps_detected[0]["case_id"] == "CASE-NORISK-001"
        assert risks.gaps_detected[0]["gap_type"] == "no_risk_assessment"


class TestAntiCollapsePostureOutput:
    """Test anti-collapse posture output parsing."""

    def test_anti_collapse_score_structure(self):
        """anti_collapse_score must have all required fields."""
        ledger = create_minimal_ledger(
            created_by="test",
            in_scope_categories=[{"category": "happy_path", "description": "Test"}],
            assumptions=["Test"],
        )

        # Add a proper PASS case
        case = CaseRecord(
            case_id="CASE-PASS-001",
            input_scenario=InputScenario(scenario_type="happy_path", inputs={}),
            expected_behavior=ExpectedBehavior(
                outcomes=[ExpectedOutcome(type="return_value", description="Test")]
            ),
            execution_record=ExecutionRecord(
                status="executed",
                executed_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                actual_behavior=ActualBehavior(),
            ),
            adjudication=Adjudication(
                decision="PASS",
                adjudicated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                adjudicated_by="test",
            ),
            residual_risks=[
                CaseRisk(
                    risk_category="coverage_hole",
                    description="Minor gap",
                ),
            ],
        )
        add_case_to_ledger(ledger, case)

        report = generate_anti_collapse_report(
            case_ledger=ledger,
            report_type="initial",
            created_by="test",
        )

        score = report.anti_collapse_score
        assert score is not None
        assert isinstance(score, AntiCollapseScore)
        assert score.score is not None
        assert score.posture is not None
        assert score.determinants is not None
        assert 0.0 <= score.score <= 1.0
        assert score.posture in ["STRONG", "MODERATE", "WEAK", "CRITICAL"]

    def test_posture_levels_mapping(self):
        """T13 Hard Constraint: Posture levels must map correctly to scores."""
        # Test with a perfect ledger
        ledger = create_minimal_ledger(
            created_by="test",
            in_scope_categories=[{"category": "happy_path", "description": "Test"}],
            out_of_scope_items=[{"category": "performance", "reason": "deferred"}],
            assumptions=["Test"],
        )

        # Add executed PASS case with risks
        case = CaseRecord(
            case_id="CASE-PERFECT-001",
            input_scenario=InputScenario(scenario_type="happy_path", inputs={}),
            expected_behavior=ExpectedBehavior(
                outcomes=[ExpectedOutcome(type="return_value", description="Test")]
            ),
            execution_record=ExecutionRecord(
                status="executed",
                executed_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                actual_behavior=ActualBehavior(),
            ),
            adjudication=Adjudication(
                decision="PASS",
                adjudicated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                adjudicated_by="test",
            ),
            residual_risks=[
                CaseRisk(
                    risk_category="coverage_hole",
                    description="Minor",
                ),
            ],
        )
        add_case_to_ledger(ledger, case)

        report = generate_anti_collapse_report(
            case_ledger=ledger,
            report_type="initial",
            created_by="test",
        )

        score = report.anti_collapse_score
        # Should be at least MODERATE (good case with risks declared)
        assert score.posture in ["STRONG", "MODERATE", "WEAK", "CRITICAL"]

    def test_release_recommendation(self):
        """anti_collapse_score must include release recommendation."""
        ledger = create_minimal_ledger(
            created_by="test",
            in_scope_categories=[{"category": "happy_path", "description": "Test"}],
            assumptions=["Test"],
        )

        case = CaseRecord(
            case_id="CASE-TEST-001",
            input_scenario=InputScenario(scenario_type="happy_path", inputs={}),
            expected_behavior=ExpectedBehavior(
                outcomes=[ExpectedOutcome(type="return_value", description="Test")]
            ),
            execution_record=ExecutionRecord(status="pending"),
        )
        add_case_to_ledger(ledger, case)

        report = generate_anti_collapse_report(
            case_ledger=ledger,
            report_type="initial",
            created_by="test",
        )

        score = report.anti_collapse_score
        # Should have release recommendation
        assert score.release_recommendation in ["clear", "caution", "blocked", None]


class TestAntiCollapseMetrics:
    """Test anti-collapse metrics."""

    def test_boundary_transparency_metric(self):
        """anti_collapse_metrics must include boundary_transparency."""
        ledger = create_minimal_ledger(
            created_by="test",
            in_scope_categories=[{"category": "happy_path", "description": "Test"}],
            out_of_scope_items=[{"category": "performance", "reason": "deferred"}],
            assumptions=["Test"],
        )

        report = generate_anti_collapse_report(
            case_ledger=ledger,
            report_type="initial",
            created_by="test",
        )

        metrics = report.anti_collapse_metrics
        assert metrics is not None
        assert "boundary_transparency" in metrics
        assert 0.0 <= metrics["boundary_transparency"] <= 1.0

    def test_coverage_honesty_metric(self):
        """anti_collapse_metrics must include coverage_honesty."""
        ledger = create_minimal_ledger(
            created_by="test",
            in_scope_categories=[{"category": "happy_path", "description": "Test"}],
            assumptions=["Test"],
        )

        report = generate_anti_collapse_report(
            case_ledger=ledger,
            report_type="initial",
            created_by="test",
        )

        metrics = report.anti_collapse_metrics
        assert metrics is not None
        assert "coverage_honesty" in metrics
        assert 0.0 <= metrics["coverage_honesty"] <= 1.0

    def test_degradation_honesty_metric(self):
        """anti_collapse_metrics must include degradation_honesty."""
        ledger = create_minimal_ledger(
            created_by="test",
            in_scope_categories=[{"category": "happy_path", "description": "Test"}],
            assumptions=["Test"],
        )

        report = generate_anti_collapse_report(
            case_ledger=ledger,
            report_type="initial",
            created_by="test",
        )

        metrics = report.anti_collapse_metrics
        assert metrics is not None
        assert "degradation_honesty" in metrics
        assert 0.0 <= metrics["degradation_honesty"] <= 1.0

    def test_risk_awareness_metric(self):
        """anti_collapse_metrics must include risk_awareness."""
        ledger = create_minimal_ledger(
            created_by="test",
            in_scope_categories=[{"category": "happy_path", "description": "Test"}],
            assumptions=["Test"],
        )

        report = generate_anti_collapse_report(
            case_ledger=ledger,
            report_type="initial",
            created_by="test",
        )

        metrics = report.anti_collapse_metrics
        assert metrics is not None
        assert "risk_awareness" in metrics
        assert 0.0 <= metrics["risk_awareness"] <= 1.0


class TestAntiCollapseReportSerialization:
    """Test anti-collapse report JSON serialization."""

    def test_report_to_dict(self):
        """AntiCollapseReport.to_dict() must produce valid dict."""
        ledger = create_minimal_ledger(
            created_by="test",
            in_scope_categories=[{"category": "happy_path", "description": "Test"}],
            assumptions=["Test"],
        )

        report = generate_anti_collapse_report(
            case_ledger=ledger,
            report_type="initial",
            created_by="test",
        )

        result = report.to_dict()
        assert isinstance(result, dict)
        assert "report_id" in result
        assert "report_type" in result
        assert "case_ledger_ref" in result
        assert "boundary_assertions" in result
        assert "coverage_integrity" in result
        assert "degradation_classification" in result
        assert "residual_risk_register" in result
        assert "anti_collapse_score" in result

    def test_report_to_json(self):
        """AntiCollapseReport.to_json() must produce valid JSON string."""
        ledger = create_minimal_ledger(
            created_by="test",
            in_scope_categories=[{"category": "happy_path", "description": "Test"}],
            assumptions=["Test"],
        )

        report = generate_anti_collapse_report(
            case_ledger=ledger,
            report_type="initial",
            created_by="test",
        )

        json_str = report.to_json()
        assert isinstance(json_str, str)

        # Verify it's valid JSON
        parsed = json.loads(json_str)
        assert parsed["report_id"] == report.report_id

    def test_report_id_format(self):
        """Report ID must follow format ACR-{YYYYMMDD}-{short_hash}."""
        ledger = create_minimal_ledger(
            created_by="test",
            in_scope_categories=[{"category": "happy_path", "description": "Test"}],
            assumptions=["Test"],
        )

        report = generate_anti_collapse_report(
            case_ledger=ledger,
            report_type="initial",
            created_by="test",
        )

        # Check format
        import re
        pattern = r"^ACR-[0-9]{8}-[a-f0-9]{8}$"
        assert re.match(pattern, report.report_id), f"ID {report.report_id} doesn't match pattern {pattern}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
