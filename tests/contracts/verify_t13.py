#!/usr/bin/env python3
"""
T13 Verification Script

Verifies T13 deliverables:
- Schema files exist and are parseable
- Python modules are importable
- Minimal samples can run through
- Anti-collapse report can be generated
- Key hard constraints are enforced
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def verify_schema_files_exist() -> bool:
    """Verify T13 schema files exist."""
    print("Verifying T13 schema files...")

    base_path = Path(__file__).parent.parent.parent / "skillforge" / "src" / "contracts"
    schemas = [
        base_path / "case_ledger.schema.json",
        base_path / "anti_collapse_report.schema.json",
    ]

    all_exist = True
    for schema_path in schemas:
        if schema_path.exists():
            print(f"  [OK] {schema_path.name}")
        else:
            print(f"  [FAIL] {schema_path.name} - file not found")
            all_exist = False

    return all_exist


def verify_schemas_parseable() -> bool:
    """Verify schema files are valid JSON."""
    print("\nVerifying schemas are parseable...")

    base_path = Path(__file__).parent.parent.parent / "skillforge" / "src" / "contracts"

    # Verify case_ledger.schema.json
    schema_path = base_path / "case_ledger.schema.json"
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
            assert schema["$schema"].startswith("http://json-schema.org/")
            assert schema["title"] == "CaseLedger"
            print("  [OK] case_ledger.schema.json is valid JSON Schema")
    except Exception as e:
        print(f"  [FAIL] case_ledger.schema.json: {e}")
        return False

    # Verify anti_collapse_report.schema.json
    schema_path = base_path / "anti_collapse_report.schema.json"
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
            assert schema["$schema"].startswith("http://json-schema.org/")
            assert schema["title"] == "AntiCollapseReport"
            print("  [OK] anti_collapse_report.schema.json is valid JSON Schema")
    except Exception as e:
        print(f"  [FAIL] anti_collapse_report.schema.json: {e}")
        return False

    return True


def verify_python_modules_importable() -> bool:
    """Verify T13 Python modules can be imported."""
    print("\nVerifying Python modules are importable...")

    try:
        from skillforge.src.contracts import case_ledger
        print("  [OK] case_ledger module imported")
    except Exception as e:
        print(f"  [FAIL] case_ledger module: {e}")
        return False

    try:
        from skillforge.src.contracts import anti_collapse_report
        print("  [OK] anti_collapse_report module imported")
    except Exception as e:
        print(f"  [FAIL] anti_collapse_report module: {e}")
        return False

    return True


def verify_minimal_sample_works() -> bool:
    """Verify minimal case ledger sample can be created and run."""
    print("\nVerifying minimal sample can run...")

    try:
        from skillforge.src.contracts.case_ledger import (
            create_minimal_ledger,
            create_case_from_scenario,
            add_case_to_ledger,
        )

        # Create minimal ledger
        ledger = create_minimal_ledger(
            created_by="verify_t13",
            in_scope_categories=[
                {"category": "happy_path", "description": "Happy path scenarios"}
            ],
            out_of_scope_items=[
                {"category": "performance", "reason": "deferred"}
            ],
            assumptions=["Test environment available"],
        )

        # Add a case
        case = create_case_from_scenario(
            category="HAPPY",
            seq=1,
            scenario_type="happy_path",
            inputs={"test": "value"},
            expected_outcomes=[
                {"type": "return_value", "description": "Returns True"}
            ],
        )
        add_case_to_ledger(ledger, case)

        # Verify it has required fields
        assert ledger.ledger_id is not None
        assert ledger.boundary_declaration is not None
        assert len(ledger.boundary_declaration.in_scope) == 1
        assert len(ledger.boundary_declaration.out_of_scope) == 1
        assert len(ledger.cases) == 1

        print("  [OK] Minimal sample created successfully")
        return True

    except Exception as e:
        print(f"  [FAIL] Minimal sample: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_anti_collapse_report_generates() -> bool:
    """Verify anti-collapse report can be generated."""
    print("\nVerifying anti-collapse report generation...")

    try:
        from skillforge.src.contracts.case_ledger import (
            create_minimal_ledger,
            add_case_to_ledger,
        )
        from skillforge.src.contracts.case_ledger import (
            CaseRecord,
            InputScenario,
            ExpectedBehavior,
            ExpectedOutcome,
            ExecutionRecord,
            ActualBehavior,
            Adjudication,
            CaseRisk,
        )
        from skillforge.src.contracts.anti_collapse_report import (
            generate_anti_collapse_report,
        )

        # Create ledger with executed case
        ledger = create_minimal_ledger(
            created_by="verify_t13",
            in_scope_categories=[{"category": "happy_path", "description": "Test"}],
            out_of_scope_items=[{"category": "performance", "reason": "deferred"}],
            assumptions=["Test env available"],
        )

        # Add executed PASS case with residual risks
        case = CaseRecord(
            case_id="CASE-VERIFY-001",
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
                adjudicated_by="verify_t13",
            ),
            residual_risks=[
                CaseRisk(
                    risk_category="coverage_hole",
                    description="Minor coverage gap",
                )
            ],
        )
        add_case_to_ledger(ledger, case)

        # Generate report
        report = generate_anti_collapse_report(
            case_ledger=ledger,
            report_type="initial",
            created_by="verify_t13",
        )

        # Verify report structure
        assert report.report_id is not None
        assert report.boundary_assertions is not None
        assert report.coverage_integrity is not None
        assert report.degradation_classification is not None
        assert report.residual_risk_register is not None
        assert report.anti_collapse_score is not None

        print("  [OK] Anti-collapse report generated successfully")
        print(f"        Report ID: {report.report_id}")
        print(f"        Posture: {report.anti_collapse_score.posture}")
        print(f"        Score: {report.anti_collapse_score.score:.2f}")

        return True

    except Exception as e:
        print(f"  [FAIL] Anti-collapse report generation: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_hard_constraint_max_100_cases() -> bool:
    """Verify hard constraint: max 100 cases enforced."""
    print("\nVerifying hard constraint: max 100 cases...")

    try:
        from skillforge.src.contracts.case_ledger import (
            create_minimal_ledger,
            create_case_from_scenario,
            add_case_to_ledger,
        )

        ledger = create_minimal_ledger(
            created_by="verify_t13",
            in_scope_categories=[{"category": "happy_path", "description": "Test"}],
            assumptions=["Test"],
        )

        # Add 100 cases
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

        # Try to add 101st - should fail
        case_101 = create_case_from_scenario(
            category="HAPPY",
            seq=101,
            scenario_type="happy_path",
            inputs={"idx": 100},
            expected_outcomes=[{"type": "return_value", "description": "Test"}],
        )

        try:
            add_case_to_ledger(ledger, case_101)
            print("  [FAIL] 101st case was allowed (should have been blocked)")
            return False
        except ValueError as e:
            if "E1304" in str(e) or "100" in str(e):
                print("  [OK] Max 100 cases constraint enforced")
                return True
            else:
                print(f"  [FAIL] Wrong error: {e}")
                return False

    except Exception as e:
        print(f"  [FAIL] Max 100 cases verification: {e}")
        return False


def verify_hard_constraint_degraded_requires_level() -> bool:
    """Verify hard constraint: DEGRADED requires degradation_level."""
    print("\nVerifying hard constraint: DEGRADED requires degradation_level...")

    try:
        from skillforge.src.contracts.case_ledger import Adjudication

        # DEGRADED without level should fail
        try:
            Adjudication(
                decision="DEGRADED",
                adjudicated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                adjudicated_by="test",
                # degradation_level missing
            )
            print("  [FAIL] DEGRADED without level was allowed")
            return False
        except ValueError as e:
            if "E1306" in str(e) or "degradation_level" in str(e):
                print("  [OK] DEGRADED requires degradation_level")
            else:
                print(f"  [FAIL] Wrong error: {e}")
                return False

        # DEGRADED with level should succeed
        adj = Adjudication(
            decision="DEGRADED",
            adjudicated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            adjudicated_by="test",
            degradation_level="minor",
        )
        assert adj.degradation_level == "minor"
        print("  [OK] DEGRADED with valid degradation_level works")

        return True

    except Exception as e:
        print(f"  [FAIL] DEGRADED level verification: {e}")
        return False


def verify_hard_constraint_uncovered_not_completed() -> bool:
    """Verify hard constraint: uncovered (pending) cases not counted as completed."""
    print("\nVerifying hard constraint: uncovered not counted as completed...")

    try:
        from skillforge.src.contracts.case_ledger import (
            create_minimal_ledger,
            create_case_from_scenario,
            add_case_to_ledger,
        )

        ledger = create_minimal_ledger(
            created_by="verify_t13",
            in_scope_categories=[
                {"category": "happy_path", "description": "Happy path"},
                {"category": "edge_case", "description": "Edge cases"},
            ],
            assumptions=["Test"],
        )

        # Add pending case
        case = create_case_from_scenario(
            category="HAPPY",
            seq=1,
            scenario_type="happy_path",
            inputs={},
            expected_outcomes=[{"type": "return_value", "description": "Test"}],
        )
        # Keep it pending (status="pending" by default)
        add_case_to_ledger(ledger, case)

        # Check summary
        summary = ledger.summary
        # Pending case should NOT count as covered
        if summary["coverage_completeness"]["in_scope_covered"] != 0:
            print(f"  [FAIL] Pending case counted as covered: {summary['coverage_completeness']}")
            return False
        if summary["by_status"]["pending"] != 1:
            print(f"  [FAIL] Pending case not counted as pending: {summary['by_status']}")
            return False

        print("  [OK] Pending cases not counted as covered")
        return True

    except Exception as e:
        print(f"  [FAIL] Uncovered constraint verification: {e}")
        return False


def verify_hard_constraint_degradable_not_fully_successful() -> bool:
    """Verify hard constraint: degraded not treated as fully successful."""
    print("\nVerifying hard constraint: degraded not fully successful...")

    try:
        from skillforge.src.contracts.case_ledger import (
            create_minimal_ledger,
            add_case_to_ledger,
            CaseRecord,
            InputScenario,
            ExpectedBehavior,
            ExpectedOutcome,
            ExecutionRecord,
            ActualBehavior,
            DeviationRecord,
            Adjudication,
        )

        ledger = create_minimal_ledger(
            created_by="verify_t13",
            in_scope_categories=[{"category": "happy_path", "description": "Test"}],
            assumptions=["Test"],
        )

        # Add DEGRADED case
        case = CaseRecord(
            case_id="CASE-DEG-001",
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
                            description="Slower"
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
        if summary["by_degradation"]["fully_successful"] != 0:
            print(f"  [FAIL] DEGRADED counted as fully_successful: {summary['by_degradation']}")
            return False
        if summary["by_degradation"]["minor_degradation"] != 1:
            print(f"  [FAIL] DEGRADED not counted as minor_degradation: {summary['by_degradation']}")
            return False

        print("  [OK] DEGRADED not counted as fully_successful")
        return True

    except Exception as e:
        print(f"  [FAIL] Degradable constraint verification: {e}")
        return False


def verify_json_serialization() -> bool:
    """Verify JSON serialization works."""
    print("\nVerifying JSON serialization...")

    try:
        from skillforge.src.contracts.case_ledger import (
            create_minimal_ledger,
            create_case_from_scenario,
            add_case_to_ledger,
        )
        from skillforge.src.contracts.anti_collapse_report import (
            generate_anti_collapse_report,
        )

        ledger = create_minimal_ledger(
            created_by="verify_t13",
            in_scope_categories=[{"category": "happy_path", "description": "Test"}],
            assumptions=["Test"],
        )

        case = create_case_from_scenario(
            category="HAPPY",
            seq=1,
            scenario_type="happy_path",
            inputs={},
            expected_outcomes=[{"type": "return_value", "description": "Test"}],
        )
        add_case_to_ledger(ledger, case)

        # Test ledger JSON
        ledger_json = ledger.to_json()
        ledger_parsed = json.loads(ledger_json)
        assert ledger_parsed["ledger_id"] == ledger.ledger_id

        # Test report JSON
        report = generate_anti_collapse_report(
            case_ledger=ledger,
            report_type="initial",
            created_by="verify_t13",
        )
        report_json = report.to_json()
        report_parsed = json.loads(report_json)
        assert report_parsed["report_id"] == report.report_id

        print("  [OK] JSON serialization works")
        return True

    except Exception as e:
        print(f"  [FAIL] JSON serialization: {e}")
        return False


def main() -> int:
    """Run all T13 verification checks."""
    print("=" * 60)
    print("T13: Case Ledger & Anti-Collapse Report - Verification")
    print("=" * 60)

    checks = [
        ("Schema files exist", verify_schema_files_exist),
        ("Schemas parseable", verify_schemas_parseable),
        ("Python modules importable", verify_python_modules_importable),
        ("Minimal sample works", verify_minimal_sample_works),
        ("Anti-collapse report generates", verify_anti_collapse_report_generates),
        ("Hard constraint: max 100 cases", verify_hard_constraint_max_100_cases),
        ("Hard constraint: DEGRADED requires level", verify_hard_constraint_degraded_requires_level),
        ("Hard constraint: uncovered not completed", verify_hard_constraint_uncovered_not_completed),
        ("Hard constraint: degraded not fully successful", verify_hard_constraint_degradable_not_fully_successful),
        ("JSON serialization", verify_json_serialization),
    ]

    results = []
    for name, check_fn in checks:
        try:
            result = check_fn()
            results.append((name, result))
        except Exception as e:
            print(f"\n  [ERROR] {name}: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")

    print("\n" + "-" * 60)
    print(f"Total: {passed}/{total} checks passed")

    if passed == total:
        print("\n✅ T13 verification: ALL CHECKS PASSED")
        return 0
    else:
        print(f"\n❌ T13 verification: {total - passed} checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
