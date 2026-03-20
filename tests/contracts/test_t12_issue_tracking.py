"""
Tests for T12 contracts: IssueRecord and FixRecommendation.

These tests verify:
1. IssueRecord correctly derives from RuleDecision (PASS/FAIL only)
2. FixRecommendation correctly references issue_id
3. Finding -> IssueRecord -> FixRecommendation chain is complete
4. WAIVE/DEFER decisions do NOT create issues
5. Schema validation
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from skillforge.src.contracts.issue_record import (
    IssueRecord,
    create_issue_from_decision,
    create_issues_from_adjudication_report,
    generate_issue_id,
    IssueRecordErrorCode,
    RuleDecisionRef,
    EvidenceRef,
    WhereLocation,
    save_issue_records,
)
from skillforge.src.contracts.fix_recommendation import (
    FixRecommendation,
    FixOption,
    create_recommendation_for_issue,
    generate_recommendations_for_issues,
    generate_recommendation_id,
    FixRecommendationErrorCode,
    VerificationCriterion,
    Implementation,
    save_fix_recommendations,
)


# ============================================================================
# Schema Validation Tests
# ============================================================================
class TestIssueRecordSchema:
    """Tests for issue_record.schema.json structure."""

    def test_schema_exists(self):
        """Schema file should exist."""
        schema_path = Path("skillforge/src/contracts/issue_record.schema.json")
        assert schema_path.exists()

    def test_schema_is_valid_json(self):
        """Schema should be valid JSON."""
        schema_path = Path("skillforge/src/contracts/issue_record.schema.json")
        with open(schema_path) as f:
            data = json.load(f)
        assert data["$schema"] == "http://json-schema.org/draft-07/schema#"
        assert data["title"] == "IssueRecord"

    def test_schema_required_fields(self):
        """Schema should have correct required fields."""
        schema_path = Path("skillforge/src/contracts/issue_record.schema.json")
        with open(schema_path) as f:
            data = json.load(f)
        required = set(data["required"])
        expected = {
            "issue_id",
            "finding_id",
            "rule_decision_ref",
            "title",
            "description",
            "severity",
            "impact_level",
            "truth_assessment",
            "evidence_strength",
            "category",
            "status",
            "created_at",
            "created_by",
        }
        assert required == expected


class TestFixRecommendationSchema:
    """Tests for fix_recommendation.schema.json structure."""

    def test_schema_exists(self):
        """Schema file should exist."""
        schema_path = Path("skillforge/src/contracts/fix_recommendation.schema.json")
        assert schema_path.exists()

    def test_schema_is_valid_json(self):
        """Schema should be valid JSON."""
        schema_path = Path("skillforge/src/contracts/fix_recommendation.schema.json")
        with open(schema_path) as f:
            data = json.load(f)
        assert data["$schema"] == "http://json-schema.org/draft-07/schema#"
        assert data["title"] == "FixRecommendation"


# ============================================================================
# IssueRecord Tests
# ============================================================================
class TestIssueRecord:
    """Tests for IssueRecord class."""

    def test_generate_issue_id_format(self):
        """Issue ID should follow ISS-{task_id}-{short_hash} format."""
        issue_id = generate_issue_id("quant-1.0.0", "F-validation-E301-abc12345")
        assert issue_id.startswith("ISS-quant")
        assert len(issue_id.split("-")[-1]) == 8

    def test_create_issue_from_pass_decision(self):
        """Should create issue from PASS decision."""
        rule_decision = {
            "finding_id": "F-validation-E301-abc12345",
            "decision": "PASS",
            "truth_assessment": "CONFIRMED",
            "impact_level": "HIGH",
            "evidence_strength": "STRONG",
            "adjudicated_at": "2026-03-16T12:00:00Z",
        }
        finding = {
            "finding_id": "F-validation-E301-abc12345",
            "source": {"type": "validation", "code": "E301_SCHEMA_INVALID"},
            "what": {
                "title": "Invalid schema",
                "description": "Schema validation failed",
                "category": "schema_validation",
                "severity": "HIGH",
                "confidence": 0.9,
            },
            "where": {"file_path": "skill.json", "line_number": 42},
            "evidence_refs": [{"kind": "FILE", "locator": "skill.json"}],
        }

        issue = create_issue_from_decision(rule_decision, finding)

        assert issue.finding_id == "F-validation-E301-abc12345"
        assert issue.rule_decision_ref.decision == "PASS"
        assert issue.status == "OPEN"
        assert issue.priority == "P1"  # HIGH severity -> P1

    def test_create_issue_from_fail_decision(self):
        """Should create issue from FAIL decision."""
        rule_decision = {
            "finding_id": "F-rule_scan-E401-def45678",
            "decision": "FAIL",
            "truth_assessment": "UNCERTAIN",
            "impact_level": "MEDIUM",
            "evidence_strength": "WEAK",
            "adjudicated_at": "2026-03-16T12:00:00Z",
        }
        finding = {
            "finding_id": "F-rule_scan-E401-def45678",
            "source": {"type": "rule_scan", "code": "E401_DANGEROUS_FUNCTION"},
            "what": {
                "title": "Use of dangerous function",
                "description": "Uses eval() which is dangerous",
                "category": "dangerous_pattern",
                "severity": "MEDIUM",
                "confidence": 0.7,
            },
            "where": {"file_path": "skill.py", "line_number": 100},
            "security": {"cwe_id": "CWE-78"},
        }

        issue = create_issue_from_decision(rule_decision, finding)

        assert issue.finding_id == "F-rule_scan-E401-def45678"
        assert issue.rule_decision_ref.decision == "FAIL"
        assert issue.truth_assessment == "UNCERTAIN"

    def test_waive_decision_does_not_create_issue(self):
        """WAIVE decision should NOT create an issue."""
        rule_decision = {
            "finding_id": "F-validation-E302-xyz789",
            "decision": "WAIVE",
            "truth_assessment": "FALSE_POSITIVE",
            "impact_level": "LOW",
            "evidence_strength": "STRONG",
            "adjudicated_at": "2026-03-16T12:00:00Z",
        }
        finding = {
            "finding_id": "F-validation-E302-xyz789",
            "source": {"type": "validation", "code": "E302_FIELD_MISSING"},
            "what": {
                "title": "Optional field missing",
                "description": "Field is optional but flagged",
                "category": "schema_validation",
                "severity": "INFO",
                "confidence": 0.5,
            },
            "where": {"file_path": "spec.json"},
        }

        with pytest.raises(ValueError, match="E1201"):
            create_issue_from_decision(rule_decision, finding)

    def test_defer_decision_does_not_create_issue(self):
        """DEFER decision should NOT create an issue."""
        rule_decision = {
            "finding_id": "F-pattern-E501-abc111",
            "decision": "DEFER",
            "truth_assessment": "UNCERTAIN",
            "impact_level": "MEDIUM",
            "evidence_strength": "INSUFFICIENT",
            "adjudicated_at": "2026-03-16T12:00:00Z",
        }
        finding = {
            "finding_id": "F-pattern-E501-abc111",
            "source": {"type": "pattern_match", "code": "E501_MISSING_CONTROL"},
            "what": {
                "title": "Potentially missing control",
                "description": "May need additional control",
                "category": "governance_gap",
                "severity": "MEDIUM",
                "confidence": 0.6,
            },
            "where": {"file_path": "skill.py"},
        }

        with pytest.raises(ValueError, match="E1201"):
            create_issue_from_decision(rule_decision, finding)

    def test_status_transitions(self):
        """Status transitions should be validated."""
        rule_decision = {
            "finding_id": "F-test-E000-test123",
            "decision": "PASS",
            "truth_assessment": "CONFIRMED",
            "impact_level": "MEDIUM",
            "evidence_strength": "STRONG",
            "adjudicated_at": "2026-03-16T12:00:00Z",
        }
        finding = {
            "finding_id": "F-test-E000-test123",
            "source": {"type": "validation", "code": "E000_TEST"},
            "what": {
                "title": "Test issue",
                "description": "Test",
                "category": "schema_validation",
                "severity": "MEDIUM",
                "confidence": 0.8,
            },
            "where": {"file_path": "test.json"},
        }

        issue = create_issue_from_decision(rule_decision, finding)

        # Valid transition
        issue.update_status("IN_PROGRESS", "developer")
        assert issue.status == "IN_PROGRESS"

        # Invalid transition
        with pytest.raises(ValueError, match="E1205"):
            issue.update_status("CLOSED", "developer")  # Can't go from IN_PROGRESS to CLOSED


# ============================================================================
# FixRecommendation Tests
# ============================================================================
class TestFixRecommendation:
    """Tests for FixRecommendation class."""

    def test_generate_recommendation_id_format(self):
        """Recommendation ID should follow REC-{short_hash}-{count} format."""
        rec_id = generate_recommendation_id("ISS-quant-abc12345", 2)
        assert rec_id.startswith("REC-")
        assert rec_id.endswith("-2")

    def test_create_recommendation_for_issue(self):
        """Should create recommendation with valid issue_id reference."""
        issue = IssueRecord(
            issue_id="ISS-quant-abc12345",
            finding_id="F-test-E000-test",
            rule_decision_ref=RuleDecisionRef(decision="PASS", adjudicated_at="2026-03-16T12:00:00Z"),
            title="Test issue",
            description="Test",
            severity="MEDIUM",
            impact_level="MEDIUM",
            truth_assessment="CONFIRMED",
            evidence_strength="STRONG",
            category="schema_validation",
        )

        options = [
            FixOption(
                option_id="OPT-1",
                name="Fix schema",
                tier="RECOMMENDED",
                description="Update the schema",
            )
        ]

        rec = create_recommendation_for_issue(
            issue=issue,
            recommendation_type="SCHEMA_UPDATE",
            options=options,
        )

        assert rec.issue_id == "ISS-quant-abc12345"
        assert rec.recommendation_type == "SCHEMA_UPDATE"
        assert len(rec.options) == 1
        assert rec.priority == "MEDIUM"  # Derived from issue severity

    def test_recommendation_must_have_options(self):
        """Recommendation without options should raise error."""
        with pytest.raises(ValueError, match="E1212"):
            FixRecommendation(
                recommendation_id="REC-test123-0",
                issue_id="ISS-test-abc123",
                recommendation_type="CODE_FIX",
                priority="HIGH",
                options=[],  # Empty options
            )

    def test_recommendation_must_have_verification_criteria(self):
        """Verification criteria should be added if not provided."""
        issue = IssueRecord(
            issue_id="ISS-quant-abc12345",
            finding_id="F-test-E000-test",
            rule_decision_ref=RuleDecisionRef(decision="PASS", adjudicated_at="2026-03-16T12:00:00Z"),
            title="Test issue",
            description="Test",
            severity="MEDIUM",
            impact_level="MEDIUM",
            truth_assessment="CONFIRMED",
            evidence_strength="STRONG",
            category="schema_validation",
        )

        options = [
            FixOption(
                option_id="OPT-1",
                name="Fix",
                tier="RECOMMENDED",
                description="Fix it",
            )
        ]

        rec = create_recommendation_for_issue(
            issue=issue,
            recommendation_type="CODE_FIX",
            options=options,
        )

        # Should have default verification criteria
        assert len(rec.verification_criteria) >= 1
        assert any(vc.verification_method == "SCAN_RE-RUN" for vc in rec.verification_criteria)

    def test_generate_recommendations_for_issues(self):
        """Should generate recommendations for multiple issues."""
        issues = [
            IssueRecord(
                issue_id="ISS-test-abc123",
                finding_id="F-test-E001-test",
                rule_decision_ref=RuleDecisionRef(decision="PASS", adjudicated_at="2026-03-16T12:00:00Z"),
                title="Schema validation issue",
                description="Schema is wrong",
                severity="HIGH",
                impact_level="HIGH",
                truth_assessment="CONFIRMED",
                evidence_strength="STRONG",
                category="schema_validation",
                where=WhereLocation(file_path="schema.json", line_number=10),
            ),
            IssueRecord(
                issue_id="ISS-test-def456",
                finding_id="F-test-E002-test",
                rule_decision_ref=RuleDecisionRef(decision="PASS", adjudicated_at="2026-03-16T12:00:00Z"),
                title="Info issue",
                description="Low priority",
                severity="INFO",  # Should be skipped
                impact_level="NEGLIGIBLE",
                truth_assessment="LIKELY_TRUE",
                evidence_strength="WEAK",
                category="consistency_check",
            ),
        ]

        recommendations = generate_recommendations_for_issues(issues)

        # Should skip INFO severity
        assert len(recommendations) == 1
        assert recommendations[0].issue_id == "ISS-test-abc123"


# ============================================================================
# Chain Tests (Finding -> Issue -> Recommendation)
# ============================================================================
class TestFindingToIssueChain:
    """Tests for Finding -> IssueRecord chain."""

    def test_finding_to_issue_to_recommendation_chain(self):
        """Should create complete chain from finding to recommendation."""
        # Simulate finding
        finding = {
            "finding_id": "F-validation-E301-chain123",
            "source": {"type": "validation", "code": "E301_SCHEMA_INVALID"},
            "what": {
                "title": "Schema validation failed",
                "description": "Required field missing in schema",
                "category": "schema_validation",
                "severity": "HIGH",
                "confidence": 0.95,
            },
            "where": {"file_path": "contract.json", "line_number": 15},
            "evidence_refs": [{"kind": "FILE", "locator": "contract.json"}],
        }

        # Simulate rule decision (PASS = confirmed issue)
        rule_decision = {
            "finding_id": "F-validation-E301-chain123",
            "decision": "PASS",
            "truth_assessment": "CONFIRMED",
            "impact_level": "HIGH",
            "evidence_strength": "CONCLUSIVE",
            "adjudicated_at": "2026-03-16T12:00:00Z",
        }

        # Create issue
        issue = create_issue_from_decision(rule_decision, finding)

        # Verify issue
        assert issue.finding_id == "F-validation-E301-chain123"
        assert issue.issue_id.startswith("ISS-validation-")
        assert issue.rule_decision_ref.decision == "PASS"

        # Create recommendation
        options = [
            FixOption(
                option_id="OPT-1",
                name="Add missing field",
                tier="RECOMMENDED",
                description="Add the required field to the schema",
            )
        ]

        recommendation = create_recommendation_for_issue(
            issue=issue,
            recommendation_type="SCHEMA_UPDATE",
            options=options,
        )

        # Verify recommendation
        assert recommendation.issue_id == issue.issue_id
        assert recommendation.recommendation_type == "SCHEMA_UPDATE"
        assert recommendation.recommendation_id.startswith("REC-")

        # Verify chain integrity
        assert finding["finding_id"] == issue.finding_id
        assert issue.issue_id == recommendation.issue_id


# ============================================================================
# T12 Compliance Tests
# ============================================================================
class TestT12Compliance:
    """Tests for T12 compliance requirements."""

    def test_only_pass_fail_create_issues(self):
        """Only PASS and FAIL decisions should create issues."""
        decisions_and_expected = [
            ("PASS", True),
            ("FAIL", True),
            ("WAIVE", False),
            ("DEFER", False),
        ]

        finding = {
            "finding_id": "F-test-E000-compliance",
            "source": {"type": "validation", "code": "E000_TEST"},
            "what": {
                "title": "Test",
                "description": "Test",
                "category": "schema_validation",
                "severity": "MEDIUM",
                "confidence": 0.5,
            },
            "where": {"file_path": "test.json"},
        }

        for decision, should_create in decisions_and_expected:
            rule_decision = {
                "finding_id": "F-test-E000-compliance",
                "decision": decision,
                "truth_assessment": "CONFIRMED",
                "impact_level": "MEDIUM",
                "evidence_strength": "STRONG",
                "adjudicated_at": "2026-03-16T12:00:00Z",
            }

            if should_create:
                issue = create_issue_from_decision(rule_decision, finding)
                assert issue.rule_decision_ref.decision == decision
            else:
                with pytest.raises(ValueError, match="E1201"):
                    create_issue_from_decision(rule_decision, finding)

    def test_fix_recommendation_must_reference_issue_id(self):
        """Every FixRecommendation MUST have a valid issue_id reference."""
        # Use proper factory function to generate recommendation_id
        issue_id = "ISS-valid-abc12345"
        rec_id = generate_recommendation_id(issue_id, 1)

        rec = FixRecommendation(
            recommendation_id=rec_id,  # Generated from issue_id
            issue_id=issue_id,
            recommendation_type="CODE_FIX",
            priority="HIGH",
            options=[
                FixOption(
                    option_id="OPT-1",
                    name="Fix",
                    tier="RECOMMENDED",
                    description="Fix it",
                )
            ],
        )
        assert rec.issue_id == "ISS-valid-abc12345"

        # Test that recommendation_id contains derived issue reference
        assert "abc12345" in rec.recommendation_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
