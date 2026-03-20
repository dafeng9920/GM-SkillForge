"""
T13 Case Ledger Tests

Test coverage for case_ledger.py enforcing hard constraints:
- CaseRecord field integrity
- boundary_declaration explicit in_scope / out_of_scope / assumptions / data_constraints
- uncovered NOT counted as completed
- degradable NOT treated as fully successful
- case count > 100 triggers error
- residual risks must exist
- CaseLedger max 100 cases enforcement
"""
from __future__ import annotations

import json
import pytest
from datetime import datetime, timezone
from pathlib import Path

from skillforge.src.contracts.case_ledger import (
    # Core classes
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
    FollowUpAction,
    DataRef,
    # Factory functions
    create_minimal_ledger,
    create_boundary_declaration,
    add_case_to_ledger,
    create_case_from_scenario,
    # Error codes
    CaseLedgerErrorCode,
    # Types
    ScenarioType,
    ExecutionStatus,
    AdjudicationDecision,
    DegradationLevel,
)


class TestCaseRecordFieldsIntegrity:
    """Test CaseRecord field integrity."""

    def test_case_record_has_all_required_fields(self):
        """CaseRecord must have all required fields."""
        case = CaseRecord(
            case_id="CASE-TEST-001",
            input_scenario=InputScenario(
                scenario_type="happy_path",
                inputs={"test": "value"}
            ),
            expected_behavior=ExpectedBehavior(
                outcomes=[ExpectedOutcome(
                    type="return_value",
                    description="Test outcome"
                )]
            ),
            execution_record=ExecutionRecord(status="pending"),
        )
        assert case.case_id == "CASE-TEST-001"
        assert case.input_scenario.scenario_type == "happy_path"
        assert case.expected_behavior.outcomes is not None
        assert len(case.expected_behavior.outcomes) == 1
        assert case.execution_record.status == "pending"

    def test_case_record_optional_fields(self):
        """CaseRecord optional fields should be None by default."""
        case = CaseRecord(
            case_id="CASE-TEST-002",
            input_scenario=InputScenario(
                scenario_type="edge_case",
                inputs={},
            ),
            expected_behavior=ExpectedBehavior(
                outcomes=[ExpectedOutcome(
                    type="state_change",
                    description="State change"
                )]
            ),
            execution_record=ExecutionRecord(status="pending"),
        )
        assert case.title is None
        assert case.description is None
        assert case.adjudication is None
        assert case.release_decision is None
        assert case.residual_risks is None
        assert case.follow_up_actions is None

    def test_case_record_to_dict_serialization(self):
        """CaseRecord.to_dict() must produce valid JSON-serializable dict."""
        case = CaseRecord(
            case_id="CASE-TEST-003",
            title="Test Case",
            description="A test case for serialization",
            input_scenario=InputScenario(
                scenario_type="happy_path",
                inputs={"key": "value"},
            ),
            expected_behavior=ExpectedBehavior(
                outcomes=[ExpectedOutcome(
                    type="return_value",
                    description="Returns True"
                )]
            ),
            execution_record=ExecutionRecord(status="executed"),
        )
        result = case.to_dict()
        assert isinstance(result, dict)
        assert result["case_id"] == "CASE-TEST-003"
        assert result["title"] == "Test Case"
        # Verify it's JSON serializable
        json_str = json.dumps(result)
        assert json_str is not None

    def test_case_record_created_at_auto_generation(self):
        """CaseRecord should auto-generate created_at if not provided."""
        before = datetime.now(timezone.utc)
        case = CaseRecord(
            case_id="CASE-TEST-004",
            input_scenario=InputScenario(
                scenario_type="happy_path",
                inputs={},
            ),
            expected_behavior=ExpectedBehavior(
                outcomes=[ExpectedOutcome(
                    type="return_value",
                    description="Test"
                )]
            ),
            execution_record=ExecutionRecord(status="pending"),
        )
        after = datetime.now(timezone.utc)
        assert case.created_at is not None
        # Parse and verify it's within expected range
        # Use time delta tolerance since created_at is second-precision but datetime.now has microseconds
        created = datetime.fromisoformat(case.created_at.replace("Z", "+00:00"))
        # Allow 1 second tolerance for precision difference
        assert (created - before).total_seconds() >= -1.0
        assert (after - created).total_seconds() >= -1.0


class TestBoundaryDeclarationExplicit:
    """Test boundary_declaration explicit requirements."""

    def test_boundary_declaration_has_in_scope(self):
        """boundary_declaration must have in_scope items."""
        boundary = BoundaryDeclaration(
            in_scope=[
                InScopeItem(
                    category="happy_path",
                    description="Basic happy path scenarios"
                ),
                InScopeItem(
                    category="edge_case",
                    description="Edge case scenarios"
                ),
            ],
            out_of_scope=[],
            assumptions=["Test environment available"],
        )
        assert len(boundary.in_scope) == 2
        assert boundary.in_scope[0].category == "happy_path"
        assert boundary.in_scope[1].category == "edge_case"

    def test_boundary_declaration_has_out_of_scope(self):
        """boundary_declaration must have out_of_scope items."""
        boundary = BoundaryDeclaration(
            in_scope=[],
            out_of_scope=[
                OutOfScopeItem(
                    category="performance",
                    reason="deferred"
                ),
                OutOfScopeItem(
                    category="security",
                    reason="out_of_project_scope"
                ),
            ],
            assumptions=[],
        )
        assert len(boundary.out_of_scope) == 2
        assert boundary.out_of_scope[0].category == "performance"
        assert boundary.out_of_scope[0].reason == "deferred"

    def test_boundary_declaration_has_assumptions(self):
        """boundary_declaration must have assumptions list."""
        boundary = BoundaryDeclaration(
            in_scope=[],
            out_of_scope=[],
            assumptions=[
                "Test data is available",
                "Environment is stable",
                "Dependencies are installed"
            ],
        )
        assert len(boundary.assumptions) == 3
        assert "Test data is available" in boundary.assumptions

    def test_boundary_declaration_has_data_constraints(self):
        """boundary_declaration may have data_constraints."""
        boundary = BoundaryDeclaration(
            in_scope=[],
            out_of_scope=[],
            assumptions=[],
            data_constraints=[
                {"constraint": "Limited market data", "impact": "limits_coverage"},
                {"constraint": "No offline mode testing", "impact": "requires_workaround"},
            ],
        )
        assert boundary.data_constraints is not None
        assert len(boundary.data_constraints) == 2
        assert boundary.data_constraints[0]["constraint"] == "Limited market data"

    def test_boundary_declaration_to_dict(self):
        """boundary_declaration.to_dict() must include all required fields."""
        boundary = BoundaryDeclaration(
            in_scope=[InScopeItem(category="happy_path", description="Test")],
            out_of_scope=[OutOfScopeItem(category="performance", reason="deferred")],
            assumptions=["Test assumption"],
            data_constraints=[{"constraint": "Test", "impact": "minimal_impact"}],
        )
        result = boundary.to_dict()
        assert "in_scope" in result
        assert "out_of_scope" in result
        assert "assumptions" in result
        assert "data_constraints" in result
        assert len(result["in_scope"]) == 1
        assert len(result["out_of_scope"]) == 1


class TestUncoveredNotCompleted:
    """Test that uncovered (pending) cases are NOT counted as completed."""

    def test_pending_case_not_counted_as_covered(self):
        """T13 Hard Constraint: Pending cases must NOT be counted as covered."""
        ledger = create_minimal_ledger(
            created_by="test",
            in_scope_categories=[
                {"category": "happy_path", "description": "Happy path"},
                {"category": "edge_case", "description": "Edge cases"},
            ],
            out_of_scope_items=[
                {"category": "performance", "reason": "deferred"}
            ],
            assumptions=["Test env available"],
        )

        # Add a pending case
        case = create_case_from_scenario(
            category="HAPPY",
            seq=1,
            scenario_type="happy_path",
            inputs={"test": "value"},
            expected_outcomes=[{"type": "return_value", "description": "Test"}],
        )
        # Keep it pending
        add_case_to_ledger(ledger, case)

        # Check summary
        summary = ledger.summary
        # Pending case should NOT count as covered
        assert summary["coverage_completeness"]["in_scope_covered"] == 0
        assert summary["by_status"]["pending"] == 1
        assert summary["by_status"]["passed"] == 0

    def test_only_executed_cases_count_as_covered(self):
        """T13 Hard Constraint: Only executed cases count as covered."""
        ledger = create_minimal_ledger(
            created_by="test",
            in_scope_categories=[{"category": "happy_path", "description": "Test"}],
            assumptions=["Test"],
        )

        # Add executed case with PASS adjudication
        from skillforge.src.contracts.case_ledger import (
            ActualBehavior, Adjudication
        )
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

        summary = ledger.summary
        # Executed case should count as covered
        assert summary["coverage_completeness"]["in_scope_covered"] == 1
        assert summary["by_status"]["passed"] == 1
        assert summary["by_status"]["pending"] == 0


class TestDegradableNotFullySuccessful:
    """Test that degraded cases are NOT treated as fully successful."""

    def test_degraded_with_level_not_fully_successful(self):
        """T13 Hard Constraint: DEGRADED cases must NOT count as fully_successful."""
        ledger = create_minimal_ledger(
            created_by="test",
            in_scope_categories=[{"category": "happy_path", "description": "Test"}],
            assumptions=["Test"],
        )

        # Add DEGRADED case
        from skillforge.src.contracts.case_ledger import (
            ActualBehavior, DeviationRecord, Adjudication
        )
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

        summary = ledger.summary
        # DEGRADED should NOT count as fully_successful
        assert summary["by_degradation"]["fully_successful"] == 0
        assert summary["by_degradation"]["minor_degradation"] == 1
        assert summary["by_status"]["degraded"] == 1

    def test_pass_with_deviations_is_misclassified(self):
        """T13 Hard Constraint: PASS with deviations is a misclassification."""
        ledger = create_minimal_ledger(
            created_by="test",
            in_scope_categories=[{"category": "happy_path", "description": "Test"}],
            assumptions=["Test"],
        )

        # Add PASS case WITH deviations (misclassification)
        from skillforge.src.contracts.case_ledger import (
            ActualBehavior, DeviationRecord, Adjudication
        )
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
                            description="Got different result"
                        )
                    ]
                ),
            ),
            adjudication=Adjudication(
                decision="PASS",  # MISCLASSIFIED: should be DEGRADED
                adjudicated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                adjudicated_by="test",
            ),
        )
        add_case_to_ledger(ledger, case)

        summary = ledger.summary
        # Should NOT count as passed OR fully_successful
        # Should count as unclassified (misclassification detected)
        assert summary["by_status"]["passed"] == 0
        assert summary["by_degradation"]["fully_successful"] == 0
        assert summary["by_degradation"]["unclassified"] == 1


class TestCaseCountOver100TriggersError:
    """Test that case count > 100 triggers error."""

    def test_max_100_cases_enforced(self):
        """T13 Hard Constraint: Maximum 100 cases enforced."""
        ledger = create_minimal_ledger(
            created_by="test",
            in_scope_categories=[{"category": "happy_path", "description": "Test"}],
            assumptions=["Test"],
        )

        # Add 100 cases - should work
        for i in range(100):
            case = create_case_from_scenario(
                category="HAPPY",
                seq=i + 1,
                scenario_type="happy_path",
                inputs={"idx": i},
                expected_outcomes=[{"type": "return_value", "description": "Test"}],
            )
            add_case_to_ledger(ledger, case)

        assert len(ledger.cases) == 100

        # Try to add 101st case - should fail
        case_101 = create_case_from_scenario(
            category="HAPPY",
            seq=101,
            scenario_type="happy_path",
            inputs={"idx": 100},
            expected_outcomes=[{"type": "return_value", "description": "Test"}],
        )

        with pytest.raises(ValueError) as exc_info:
            add_case_to_ledger(ledger, case_101)

        assert CaseLedgerErrorCode.CASE_LIBRARY_TOO_LARGE in str(exc_info.value)
        assert "100" in str(exc_info.value)

    def test_exactly_100_cases_allowed(self):
        """T13 Hard Constraint: Exactly 100 cases is the limit."""
        ledger = create_minimal_ledger(
            created_by="test",
            in_scope_categories=[{"category": "happy_path", "description": "Test"}],
            assumptions=["Test"],
        )

        # Add exactly 100 cases
        for i in range(100):
            case = create_case_from_scenario(
                category="HAPPY",
                seq=i + 1,
                scenario_type="happy_path",
                inputs={"idx": i},
                expected_outcomes=[{"type": "return_value", "description": "Test"}],
            )
            add_case_to_ledger(ledger, case)

        # Should succeed
        assert len(ledger.cases) == 100


class TestResidualRisksMustExist:
    """Test that residual risks must exist."""

    def test_residual_risks_can_be_added(self):
        """CaseRecord must support adding residual risks."""
        case = CaseRecord(
            case_id="CASE-RISK-001",
            input_scenario=InputScenario(scenario_type="happy_path", inputs={}),
            expected_behavior=ExpectedBehavior(
                outcomes=[ExpectedOutcome(type="return_value", description="Test")]
            ),
            execution_record=ExecutionRecord(status="pending"),
        )

        # Add residual risks
        risk1 = CaseRisk(
            risk_id="RISK-001",
            risk_category="test_gap",
            description="Limited test coverage",
            mitigation="Expand test suite",
            requires_monitoring=True,
        )
        case.add_residual_risk(risk1)

        assert case.residual_risks is not None
        assert len(case.residual_risks) == 1
        assert case.residual_risks[0].risk_category == "test_gap"

    def test_residual_risks_for_pass_case(self):
        """T13 Hard Constraint: Even PASS cases should have residual risks."""
        from skillforge.src.contracts.case_ledger import (
            ActualBehavior, Adjudication
        )
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
        )

        # Add residual risk even though it's PASS
        risk = CaseRisk(
            risk_category="coverage_hole",
            description="Some edge cases not tested",
            mitigation="Monitor production",
        )
        case.add_residual_risk(risk)

        assert case.residual_risks is not None
        assert len(case.residual_risks) == 1


class TestDegradedRequiresLevel:
    """Test that DEGRADED decisions require degradation_level."""

    def test_degraded_without_level_raises_error(self):
        """T13 Hard Constraint: DEGRADED decision MUST have degradation_level."""
        with pytest.raises(ValueError) as exc_info:
            Adjudication(
                decision="DEGRADED",
                adjudicated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                adjudicated_by="test",
                # degradation_level missing - should fail
            )

        assert CaseLedgerErrorCode.INVALID_DEGRADATION_LEVEL in str(exc_info.value)

    def test_degraded_with_minor_level_succeeds(self):
        """DEGRADED with 'minor' level should succeed."""
        adj = Adjudication(
            decision="DEGRADED",
            adjudicated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            adjudicated_by="test",
            degradation_level="minor",
        )
        assert adj.decision == "DEGRADED"
        assert adj.degradation_level == "minor"

    def test_degraded_with_partial_functionality_level_succeeds(self):
        """DEGRADED with 'partial_functionality' level should succeed."""
        adj = Adjudication(
            decision="DEGRADED",
            adjudicated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            adjudicated_by="test",
            degradation_level="partial_functionality",
        )
        assert adj.decision == "DEGRADED"
        assert adj.degradation_level == "partial_functionality"

    def test_degraded_with_major_level_succeeds(self):
        """DEGRADED with 'major' level should succeed."""
        adj = Adjudication(
            decision="DEGRADED",
            adjudicated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            adjudicated_by="test",
            degradation_level="major",
        )
        assert adj.decision == "DEGRADED"
        assert adj.degradation_level == "major"


class TestCaseLedgerJsonSerialization:
    """Test CaseLedger JSON serialization."""

    def test_ledger_to_json_valid_json(self):
        """CaseLedger.to_json() must produce valid JSON string."""
        ledger = create_minimal_ledger(
            created_by="test",
            in_scope_categories=[
                {"category": "happy_path", "description": "Happy path"}
            ],
            out_of_scope_items=[
                {"category": "performance", "reason": "deferred"}
            ],
            assumptions=["Test assumption"],
        )

        case = create_case_from_scenario(
            category="HAPPY",
            seq=1,
            scenario_type="happy_path",
            inputs={"test": "value"},
            expected_outcomes=[{"type": "return_value", "description": "Test"}],
        )
        add_case_to_ledger(ledger, case)

        json_str = ledger.to_json()
        assert isinstance(json_str, str)

        # Verify it's valid JSON
        parsed = json.loads(json_str)
        assert parsed["ledger_id"] == ledger.ledger_id
        assert parsed["ledger_version"] == ledger.ledger_version
        assert len(parsed["cases"]) == 1

    def test_ledger_save_creates_file(self):
        """CaseLedger.save() should create JSON file."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_ledger.json"
            ledger = create_minimal_ledger(
                created_by="test",
                in_scope_categories=[{"category": "happy_path", "description": "Test"}],
                assumptions=["Test"],
            )

            ledger.save(str(output_path))

            assert output_path.exists()
            with open(output_path, "r", encoding="utf-8") as f:
                content = json.load(f)
                assert content["ledger_id"] == ledger.ledger_id
                assert "boundary_declaration" in content


class TestCaseLedgerIdFormat:
    """Test CaseLedger ID format."""

    def test_ledger_id_format(self):
        """Ledger ID must follow format LEDGER-{YYYYMMDD}-{short_hash}."""
        ledger = create_minimal_ledger(
            created_by="test",
            in_scope_categories=[{"category": "happy_path", "description": "Test"}],
            assumptions=["Test"],
        )

        # Check format
        import re
        pattern = r"^LEDGER-[0-9]{8}-[a-f0-9]{8}$"
        assert re.match(pattern, ledger.ledger_id), f"ID {ledger.ledger_id} doesn't match pattern {pattern}"


class TestDeviationsRecording:
    """Test deviation recording functionality."""

    def test_add_deviation_to_case(self):
        """Deviations must be recordable on CaseRecord."""
        from skillforge.src.contracts.case_ledger import ActualBehavior
        case = CaseRecord(
            case_id="CASE-DEV-001",
            input_scenario=InputScenario(scenario_type="happy_path", inputs={}),
            expected_behavior=ExpectedBehavior(
                outcomes=[ExpectedOutcome(type="return_value", description="Test")]
            ),
            execution_record=ExecutionRecord(
                status="executed",
                executed_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                actual_behavior=ActualBehavior(),
            ),
        )

        deviation = DeviationRecord(
            type="outcome_mismatch",
            description="Expected True, got False",
            severity="HIGH",
            expected="True",
            actual="False",
            impact="Test fails",
        )
        case.add_deviation(deviation)

        assert case.execution_record.actual_behavior is not None
        assert case.execution_record.actual_behavior.deviations is not None
        assert len(case.execution_record.actual_behavior.deviations) == 1
        assert case.execution_record.actual_behavior.deviations[0].type == "outcome_mismatch"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
