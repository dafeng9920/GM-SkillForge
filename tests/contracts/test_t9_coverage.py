"""
Tests for T9 contracts: CoverageStatement and EvidenceLevel.

These tests verify:
1. CoverageStatement correctly represents covered/uncovered items
2. EvidenceLevel definitions are stable and valid
3. No default full coverage (silence = not covered)
4. No default evidence strength (must be explicitly declared)
5. Evidence refs are complete and traceable
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from skillforge.src.contracts.coverage_statement import (
    CoverageStatement,
    CoveredItem,
    UncoveredItem,
    ExcludedItem,
    EvidenceRef,
    validate_coverage_statement,
    create_coverage_statement,
    CoverageErrorCode,
)
from skillforge.src.contracts.evidence_level import (
    get_evidence_level,
    validate_evidence_level,
    get_all_evidence_levels,
    compare_levels,
    validate_evidence_refs,
    EVIDENCE_LEVEL_DEFINITIONS,
)


# ============================================================================
# Schema Validation Tests
# ============================================================================
class TestCoverageStatementSchema:
    """Tests for coverage_statement.schema.json structure."""

    def test_schema_exists(self):
        """Schema file should exist."""
        schema_path = Path("skillforge/src/contracts/coverage_statement.schema.json")
        assert schema_path.exists()

    def test_schema_is_valid_json(self):
        """Schema should be valid JSON."""
        schema_path = Path("skillforge/src/contracts/coverage_statement.schema.json")
        with open(schema_path) as f:
            data = json.load(f)
        assert data["$schema"] == "http://json-schema.org/draft-07/schema#"
        assert data["title"] == "CoverageStatement"

    def test_schema_required_fields(self):
        """Schema should have correct required fields."""
        schema_path = Path("skillforge/src/contracts/coverage_statement.schema.json")
        with open(schema_path) as f:
            data = json.load(f)
        required = set(data["required"])
        expected = {
            "statement_id",
            "artifact_id",
            "artifact_type",
            "declared_at",
            "declared_by",
            "covered_items",
            "uncovered_items",
            "exclusions",
            "coverage_summary",
        }
        assert required == expected


class TestEvidenceLevelSchema:
    """Tests for evidence_level.schema.json structure."""

    def test_schema_exists(self):
        """Schema file should exist."""
        schema_path = Path("skillforge/src/contracts/evidence_level.schema.json")
        assert schema_path.exists()

    def test_schema_is_valid_json(self):
        """Schema should be valid JSON."""
        schema_path = Path("skillforge/src/contracts/evidence_level.schema.json")
        with open(schema_path) as f:
            data = json.load(f)
        assert data["$schema"] == "http://json-schema.org/draft-07/schema#"
        assert data["title"] == "EvidenceLevel"


# ============================================================================
# CoverageStatement Tests
# ============================================================================
class TestCoverageStatement:
    """Tests for CoverageStatement class."""

    def test_create_empty_statement(self):
        """Should create empty coverage statement."""
        statement = create_coverage_statement(
            artifact_id="test_task",
            artifact_type="task",
            declared_by="test_runner",
        )
        assert statement.artifact_id == "test_task"
        assert statement.artifact_type == "task"
        assert len(statement.covered_items) == 0
        assert len(statement.uncovered_items) == 0

    def test_statement_id_format(self):
        """Statement ID should follow COV-{artifact}-{hash} format."""
        statement = create_coverage_statement(
            artifact_id="T3_validation",
            artifact_type="task",
            declared_by="vs--cc1",
        )
        assert statement.statement_id.startswith("COV-T3_validation-")
        assert len(statement.statement_id) == len("COV-T3_validation-") + 8

    def test_add_covered_item(self):
        """Should add covered item with evidence."""
        statement = create_coverage_statement(
            artifact_id="test",
            artifact_type="task",
            declared_by="test",
        )
        statement.add_covered(
            item_id="test_func",
            item_type="function",
            evidence_level="E4",
            evidence_refs=[
                EvidenceRef(kind="TEST_FILE", locator="tests/test.py::test_func")
            ],
        )
        assert len(statement.covered_items) == 1
        assert statement.covered_items[0].item_id == "test_func"
        assert statement.covered_items[0].evidence_level == "E4"

    def test_add_covered_item_requires_evidence(self):
        """Should raise error if no evidence refs provided."""
        statement = create_coverage_statement(
            artifact_id="test",
            artifact_type="task",
            declared_by="test",
        )
        with pytest.raises(ValueError, match="E904"):
            statement.add_covered(
                item_id="test_func",
                item_type="function",
                evidence_level="E4",
                evidence_refs=[],
            )

    def test_add_covered_item_invalid_level(self):
        """Should raise error for invalid evidence level."""
        statement = create_coverage_statement(
            artifact_id="test",
            artifact_type="task",
            declared_by="test",
        )
        with pytest.raises(ValueError, match="E903"):
            statement.add_covered(
                item_id="test_func",
                item_type="function",
                evidence_level="E6",  # Invalid
                evidence_refs=[
                    EvidenceRef(kind="TEST_FILE", locator="tests/test.py::test_func")
                ],
            )

    def test_add_uncovered_item(self):
        """Should add uncovered item with reason."""
        statement = create_coverage_statement(
            artifact_id="test",
            artifact_type="task",
            declared_by="test",
        )
        statement.add_uncovered(
            item_id="untested_func",
            item_type="function",
            reason="not_implemented",
            planned=True,
        )
        assert len(statement.uncovered_items) == 1
        assert statement.uncovered_items[0].item_id == "untested_func"
        assert statement.uncovered_items[0].reason == "not_implemented"

    def test_compute_summary(self):
        """Should compute coverage summary correctly."""
        statement = create_coverage_statement(
            artifact_id="test",
            artifact_type="task",
            declared_by="test",
        )
        statement.add_covered(
            item_id="func1",
            item_type="function",
            evidence_level="E4",
            evidence_refs=[EvidenceRef(kind="TEST_FILE", locator="tests/test.py")],
        )
        statement.add_covered(
            item_id="func2",
            item_type="function",
            evidence_level="E3",
            evidence_refs=[EvidenceRef(kind="LOG", locator="run/test.log")],
        )
        statement.add_uncovered(
            item_id="func3",
            item_type="function",
            reason="deferred",
        )
        statement.add_uncovered(
            item_id="func4",
            item_type="function",
            reason="not_implemented",
        )

        summary = statement.compute_summary()
        assert summary.total_items == 4
        assert summary.covered_count == 2
        assert summary.uncovered_count == 2
        assert summary.coverage_percent == 50.0

    def test_exclusions_not_counted_in_total(self):
        """Exclusions should NOT be counted in total items."""
        statement = create_coverage_statement(
            artifact_id="test",
            artifact_type="task",
            declared_by="test",
        )
        statement.add_covered(
            item_id="func1",
            item_type="function",
            evidence_level="E4",
            evidence_refs=[EvidenceRef(kind="TEST_FILE", locator="tests/test.py")],
        )
        statement.add_excluded(
            item_id="internal_func",
            exclusion_reason="internal_only",
        )

        summary = statement.compute_summary()
        assert summary.total_items == 1  # Only covered item
        assert summary.covered_count == 1
        assert summary.uncovered_count == 0

    def test_to_dict_serialization(self):
        """Should serialize to dict correctly."""
        statement = create_coverage_statement(
            artifact_id="test",
            artifact_type="task",
            declared_by="test",
        )
        statement.add_covered(
            item_id="func1",
            item_type="function",
            evidence_level="E4",
            evidence_refs=[EvidenceRef(kind="TEST_FILE", locator="tests/test.py")],
        )

        data = statement.to_dict()
        assert "statement_id" in data
        assert data["artifact_id"] == "test"
        assert len(data["covered_items"]) == 1
        assert "coverage_summary" in data


# ============================================================================
# EvidenceLevel Tests
# ============================================================================
class TestEvidenceLevelDefinitions:
    """Tests for EvidenceLevel definitions."""

    def test_all_levels_defined(self):
        """Should have exactly E1-E5 defined."""
        assert set(EVIDENCE_LEVEL_DEFINITIONS.keys()) == {"E1", "E2", "E3", "E4", "E5"}

    def test_levels_ordered_by_strength(self):
        """Levels should be ordered 1-5 by strength."""
        all_levels = get_all_evidence_levels()
        strengths = [level["strength"] for level in all_levels]
        assert strengths == [1, 2, 3, 4, 5]

    def test_level_names_unique(self):
        """Level names should be unique."""
        all_levels = get_all_evidence_levels()
        names = [level["level_name"] for level in all_levels]
        assert len(names) == len(set(names))

    def test_get_evidence_level_valid(self):
        """Should get level definition for valid ID."""
        level = get_evidence_level("E4")
        assert level["level_id"] == "E4"
        assert level["strength"] == 4
        assert "Replayable" in level["level_name"]

    def test_get_evidence_level_invalid(self):
        """Should raise error for invalid level ID."""
        with pytest.raises(ValueError, match="E911"):
            get_evidence_level("E6")

    def test_validate_evidence_level(self):
        """Should validate evidence level IDs."""
        assert validate_evidence_level("E1") is True
        assert validate_evidence_level("E5") is True
        assert validate_evidence_level("E0") is False
        assert validate_evidence_level("E6") is False

    def test_compare_levels(self):
        """Should compare levels by strength."""
        assert compare_levels("E1", "E5") == -1  # E1 < E5
        assert compare_levels("E5", "E1") == 1   # E5 > E1
        assert compare_levels("E3", "E3") == 0   # E3 == E3

    def test_e5_has_highest_strength(self):
        """E5 should have strength 5 (highest)."""
        level = get_evidence_level("E5")
        assert level["strength"] == 5
        assert level["requirements"]["gate_required"] is True

    def test_e1_has_lowest_strength(self):
        """E1 should have strength 1 (lowest)."""
        level = get_evidence_level("E1")
        assert level["strength"] == 1
        assert level["requirements"]["replayable"] is False


class TestEvidenceLevelValidation:
    """Tests for evidence validation."""

    def test_validate_evidence_refs_e5_complete_dual_gate(self):
        """E5 should pass with complete dual-gate + receipt evidence."""
        # Valid E5 refs with entry/exit gates and receipt
        valid_refs = [
            {"kind": "GATE_DECISION", "locator": "run/20260316_120000/entry_gate_decision.json"},
            {"kind": "GATE_DECISION", "locator": "run/20260316_120000/exit_gate_decision.json"},
            {"kind": "RUN_ID", "locator": "run/20260316_120000"},  # Receipt via RUN_ID
        ]
        result = validate_evidence_refs("E5", valid_refs)
        assert result["valid"] is True, f"Expected valid, got errors: {result['errors']}"

    def test_validate_evidence_refs_e5_missing_entry_gate(self):
        """E5 should fail without entry_gate_decision."""
        # Missing entry gate
        invalid_refs = [
            {"kind": "GATE_DECISION", "locator": "run/20260316_120000/exit_gate_decision.json"},
            {"kind": "RUN_ID", "locator": "run/20260316_120000"},
        ]
        result = validate_evidence_refs("E5", invalid_refs)
        assert result["valid"] is False
        assert any("E915_ENTRY_GATE_MISSING" in e or "entry_gate" in e.lower() for e in result["errors"])

    def test_validate_evidence_refs_e5_missing_exit_gate(self):
        """E5 should fail without exit_gate_decision."""
        # Missing exit gate
        invalid_refs = [
            {"kind": "GATE_DECISION", "locator": "run/20260316_120000/entry_gate_decision.json"},
            {"kind": "RUN_ID", "locator": "run/20260316_120000"},
        ]
        result = validate_evidence_refs("E5", invalid_refs)
        assert result["valid"] is False
        assert any("E916_EXIT_GATE_MISSING" in e or "exit_gate" in e.lower() for e in result["errors"])

    def test_validate_evidence_refs_e5_missing_receipt(self):
        """E5 should fail without receipt evidence."""
        # Missing receipt
        invalid_refs = [
            {"kind": "GATE_DECISION", "locator": "run/20260316_120000/entry_gate_decision.json"},
            {"kind": "GATE_DECISION", "locator": "run/20260316_120000/exit_gate_decision.json"},
        ]
        result = validate_evidence_refs("E5", invalid_refs)
        assert result["valid"] is False
        assert any("E917_RECEIPT_MISSING" in e or "receipt" in e.lower() for e in result["errors"])

    def test_validate_evidence_refs_e5_missing_all_three(self):
        """E5 should fail when all three components are missing."""
        # No gate evidence at all
        invalid_refs = [
            {"kind": "LOG", "locator": "run/test.log"},
        ]
        result = validate_evidence_refs("E5", invalid_refs)
        assert result["valid"] is False
        # Should have all three errors
        error_msgs = " ".join(result["errors"])
        assert "entry_gate" in error_msgs.lower() or "E915" in error_msgs
        assert "exit_gate" in error_msgs.lower() or "E916" in error_msgs
        assert "receipt" in error_msgs.lower() or "E917" in error_msgs

    def test_validate_evidence_refs_kind_mismatch(self):
        """Should reject evidence kinds not acceptable for level."""
        # E1 only accepts SNIPPET/CODE_LOCATION
        refs = [{"kind": "GATE_DECISION", "locator": "run/gate.json"}]
        result = validate_evidence_refs("E1", refs)
        assert result["valid"] is False
        assert any("E913" in e for e in result["errors"])


# ============================================================================
# Sample File Tests
# ============================================================================
class TestSampleFiles:
    """Tests for sample JSON files."""

    def test_coverage_statement_sample_exists(self):
        """Sample coverage_statement.json should exist."""
        sample_path = Path("tests/contracts/T9/coverage_statement.sample.json")
        assert sample_path.exists()

    def test_coverage_statement_sample_valid_json(self):
        """Sample should be valid JSON."""
        sample_path = Path("tests/contracts/T9/coverage_statement.sample.json")
        with open(sample_path) as f:
            data = json.load(f)
        assert "statement_id" in data
        assert "covered_items" in data
        assert "uncovered_items" in data

    def test_evidence_level_json_exists(self):
        """evidence_level.json should exist."""
        level_path = Path("tests/contracts/T9/evidence_level.json")
        assert level_path.exists()

    def test_evidence_level_json_has_all_levels(self):
        """evidence_level.json should have E1-E5."""
        level_path = Path("tests/contracts/T9/evidence_level.json")
        with open(level_path) as f:
            data = json.load(f)
        level_ids = {level["level_id"] for level in data["levels"]}
        assert level_ids == {"E1", "E2", "E3", "E4", "E5"}


# ============================================================================
# Compliance Tests (Antigravity-1)
# ============================================================================
class TestT9Compliance:
    """Tests for T9 compliance with Antigravity-1 standards."""

    def test_no_default_full_coverage(self):
        """Coverage should NOT default to full coverage."""
        # Empty statement should have 0% coverage, not 100%
        statement = create_coverage_statement(
            artifact_id="test",
            artifact_type="task",
            declared_by="test",
        )
        summary = statement.compute_summary()
        assert summary.coverage_percent == 0.0  # Silence = not covered

    def test_no_default_evidence_strength(self):
        """Evidence level must be explicitly declared (no default value)."""
        statement = create_coverage_statement(
            artifact_id="test",
            artifact_type="task",
            declared_by="test",
        )
        # Verify that evidence_level must be one of E1-E5 (no auto-default)
        # This tests that the system enforces explicit declaration
        with pytest.raises(ValueError, match="E903"):
            statement.add_covered(
                item_id="func",
                item_type="function",
                evidence_level="INVALID",  # Not a valid level
                evidence_refs=[EvidenceRef(kind="TEST_FILE", locator="tests/test.py")],
            )

    def test_evidence_ref_required(self):
        """Covered items MUST have at least one evidence ref."""
        statement = create_coverage_statement(
            artifact_id="test",
            artifact_type="task",
            declared_by="test",
        )
        with pytest.raises(ValueError, match="E904"):
            statement.add_covered(
                item_id="func",
                item_type="function",
                evidence_level="E4",
                evidence_refs=[],  # Empty refs
            )

    def test_uncovered_must_be_explicit(self):
        """Silence means not covered - uncovered items must be explicitly declared."""
        statement = create_coverage_statement(
            artifact_id="test",
            artifact_type="task",
            declared_by="test",
        )
        statement.add_covered(
            item_id="covered_func",
            item_type="function",
            evidence_level="E4",
            evidence_refs=[EvidenceRef(kind="TEST_FILE", locator="tests/test.py")],
        )
        # If we don't explicitly declare "uncovered_func", it's not in the list
        # The summary only counts explicitly declared items
        summary = statement.compute_summary()
        assert summary.total_items == 1  # Only covered item
        assert summary.uncovered_count == 0  # No explicit uncovered items


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
