"""
T6 Finding Building Tests

Tests for unified Finding structure and FindingBuilder.
Tests conversion from T3 (ValidationFailure), T4 (RuleHit), and T5 (PatternMatch).

T6 Scope:
- Finding ID generation
- Severity initial assignment
- Confidence initial assignment
- Evidence refs binding
- Finding report generation
"""
from datetime import datetime, timezone

from skillforge.src.contracts.finding_builder import (
    EvidenceRef,
    FindingBuilder,
    FindingCategory,
    FindingSeverity,
    FindingSourceType,
    FindingsReport,
    FindingsReportBuilder,
    assign_initial_confidence,
    assign_initial_severity,
    generate_finding_id,
)
from skillforge.src.contracts.pattern_matcher import (
    GovernanceGap,
    PatternCode,
    PatternMatch,
)
from skillforge.src.contracts.rule_scanner import RuleHit, RuleCode
from skillforge.src.contracts.skill_contract_validator import (
    ValidationErrorCode,
    ValidationFailure,
)


class TestFindingIdGeneration:
    """Test Finding ID generation."""

    def test_finding_id_format(self):
        """Finding ID should follow format F-{source}-{code}-{hash}."""
        finding_id = generate_finding_id(
            FindingSourceType.VALIDATION,
            "E302_REQUIRED_FIELD_MISSING",
            "skill.py",
            42,
        )
        assert finding_id.startswith("F-validation-")
        assert len(finding_id.split("-")) == 4  # F, source, code, hash
        assert len(finding_id.split("-")[-1]) == 8  # 8-char hash

    def test_finding_id_deterministic(self):
        """Same input should generate same finding ID."""
        id1 = generate_finding_id(
            FindingSourceType.VALIDATION,
            "E302_REQUIRED_FIELD_MISSING",
            "skill.py",
            42,
        )
        id2 = generate_finding_id(
            FindingSourceType.VALIDATION,
            "E302_REQUIRED_FIELD_MISSING",
            "skill.py",
            42,
        )
        assert id1 == id2

    def test_finding_id_different_inputs(self):
        """Different inputs should generate different finding IDs."""
        id1 = generate_finding_id(
            FindingSourceType.VALIDATION,
            "E302_REQUIRED_FIELD_MISSING",
            "skill.py",
            42,
        )
        id2 = generate_finding_id(
            FindingSourceType.VALIDATION,
            "E302_REQUIRED_FIELD_MISSING",
            "skill.py",
            43,  # Different line
        )
        id3 = generate_finding_id(
            FindingSourceType.RULE_SCAN,  # Different source
            "E302_REQUIRED_FIELD_MISSING",
            "skill.py",
            42,
        )
        assert id1 != id2
        assert id1 != id3
        assert id2 != id3


class TestSeverityAssignment:
    """Test initial severity assignment."""

    def test_severity_from_t3_error(self):
        """T3 ERROR severity should map to HIGH."""
        severity = assign_initial_severity(FindingSourceType.VALIDATION, "ERROR")
        assert severity == FindingSeverity.HIGH

    def test_severity_from_t3_warning(self):
        """T3 WARNING severity should map to INFO."""
        severity = assign_initial_severity(FindingSourceType.VALIDATION, "WARNING")
        assert severity == FindingSeverity.INFO

    def test_severity_from_t4_critical(self):
        """T4 CRITICAL should be preserved."""
        severity = assign_initial_severity(FindingSourceType.RULE_SCAN, "CRITICAL")
        assert severity == FindingSeverity.CRITICAL

    def test_severity_from_t5_high(self):
        """T5 HIGH should be preserved."""
        severity = assign_initial_severity(FindingSourceType.PATTERN_MATCH, "HIGH")
        assert severity == FindingSeverity.HIGH

    def test_severity_unknown_falls_back_to_default(self):
        """Unknown severity falls back to source-specific default."""
        # For VALIDATION, unknown severity falls back to INFO (not ERROR)
        severity_validation = assign_initial_severity(FindingSourceType.VALIDATION, "UNKNOWN")
        assert severity_validation == FindingSeverity.INFO

        # For RULE_SCAN, unknown severity falls back to HIGH
        severity_rule = assign_initial_severity(FindingSourceType.RULE_SCAN, "UNKNOWN")
        assert severity_rule == FindingSeverity.HIGH

        # For PATTERN_MATCH, unknown severity falls back to HIGH
        severity_pattern = assign_initial_severity(FindingSourceType.PATTERN_MATCH, "UNKNOWN")
        assert severity_pattern == FindingSeverity.HIGH


class TestConfidenceAssignment:
    """Test initial confidence assignment."""

    def test_confidence_t3_schema_validation(self):
        """T3 schema validation (E30x) should have 1.0 confidence."""
        confidence = assign_initial_confidence(FindingSourceType.VALIDATION, "E301_SCHEMA_VALIDATION_FAILED")
        assert confidence == 1.0

    def test_confidence_t3_contract_validation(self):
        """T3 contract validation (E31x) should have 0.95 confidence."""
        confidence = assign_initial_confidence(FindingSourceType.VALIDATION, "E311_INPUT_CONTRACT_MISSING")
        assert confidence == 0.95

    def test_confidence_t4_dangerous_pattern(self):
        """T4 dangerous patterns (E42x) should have 1.0 confidence."""
        confidence = assign_initial_confidence(FindingSourceType.RULE_SCAN, "E421_EVAL_OR_EXEC_USED")
        assert confidence == 1.0

    def test_confidence_t4_external_action(self):
        """T4 external actions (E41x) should have 0.95 confidence."""
        confidence = assign_initial_confidence(FindingSourceType.RULE_SCAN, "E411_HTTP_REQUEST_without_TIMEOUT")
        assert confidence == 0.95

    def test_confidence_t5_pattern_match(self):
        """T5 pattern matching should have 0.85 confidence."""
        confidence = assign_initial_confidence(FindingSourceType.PATTERN_MATCH, "E501_EXTERNAL_WITHOUT_STOP_RULE")
        assert confidence == 0.85


class TestEvidenceRef:
    """Test EvidenceRef structure."""

    def test_evidence_ref_to_dict(self):
        """EvidenceRef should serialize correctly."""
        ref = EvidenceRef(
            kind="FILE",
            locator="run/T3_evidence/validation_report.json",
            note="T3 validation report",
        )
        d = ref.to_dict()
        assert d["kind"] == "FILE"
        assert d["locator"] == "run/T3_evidence/validation_report.json"
        assert d["note"] == "T3 validation report"

    def test_evidence_ref_optional_note(self):
        """EvidenceRef note is optional."""
        ref = EvidenceRef(kind="CODE_LOCATION", locator="skill.py:42")
        d = ref.to_dict()
        assert d["note"] is None


class TestFindingBuilder:
    """Test FindingBuilder conversion from T3/T4/T5."""

    def test_from_validation_failure(self):
        """Converting T3 ValidationFailure to Finding."""
        builder = FindingBuilder(run_id="test_run")

        failure = ValidationFailure(
            code=ValidationErrorCode.E302_REQUIRED_FIELD_MISSING,
            message="Required field 'skill_name' is missing",
            field_path="skill_name",
            severity="ERROR",
            suggested_fix="Add 'skill_name' to the skill spec",
        )

        finding = builder.from_validation_failure(failure, skill_id="test-skill-1.0.0-abc12345")

        # Verify core fields
        assert finding.finding_id.startswith("F-validation-")
        assert finding.source_type == FindingSourceType.VALIDATION
        assert finding.source_code == "E302_REQUIRED_FIELD_MISSING"
        assert finding.category == FindingCategory.SCHEMA_VALIDATION
        assert finding.severity == FindingSeverity.HIGH  # ERROR -> HIGH
        assert finding.confidence == 1.0  # Schema validation has max confidence

        # Verify evidence refs (T6 Hard Constraint)
        assert len(finding.evidence_refs) >= 1
        assert any(e.kind == "FILE" for e in finding.evidence_refs)
        assert any(e.kind == "CODE_LOCATION" for e in finding.evidence_refs)

    def test_from_rule_hit(self):
        """Converting T4 RuleHit to Finding."""
        builder = FindingBuilder(run_id="test_run")

        hit = RuleHit(
            rule_code=RuleCode.E421_EVAL_OR_EXEC_USED,
            rule_name="eval or exec Function Used",
            file_path="skill/dangerous.py",
            line_number=42,
            column_number=10,
            snippet="eval(user_input)",
            category="dangerous_pattern",
            severity="CRITICAL",
            message="Use of eval() or exec() functions detected",
            suggested_fix="Replace eval/exec with safer alternatives",
        )

        finding = builder.from_rule_hit(hit, skill_id="test-skill-1.0.0-abc12345")

        # Verify core fields
        assert finding.finding_id.startswith("F-rule_scan-")
        assert finding.source_type == FindingSourceType.RULE_SCAN
        assert finding.source_code == "E421_EVAL_OR_EXEC_USED"
        assert finding.category == FindingCategory.DANGEROUS_PATTERN
        assert finding.severity == FindingSeverity.CRITICAL
        assert finding.confidence == 1.0  # Dangerous patterns have max confidence

        # Verify location
        assert finding.file_path == "skill/dangerous.py"
        assert finding.line_number == 42
        assert finding.column_number == 10
        assert finding.snippet == "eval(user_input)"

        # Verify evidence refs
        assert len(finding.evidence_refs) >= 1
        assert any(e.kind == "CODE_LOCATION" for e in finding.evidence_refs)
        assert any("dangerous.py:42:10" in e.locator for e in finding.evidence_refs)

    def test_from_pattern_match(self):
        """Converting T5 PatternMatch to Finding."""
        builder = FindingBuilder(run_id="test_run")

        match = PatternMatch(
            pattern_code=PatternCode.E501_EXTERNAL_WITHOUT_STOP_RULE,
            pattern_name="External Action Without Stop Rule",
            file_path="skill/external.py",
            line_number=15,
            function_name="fetch_data",
            category="governance_gap",
            severity="CRITICAL",
            message="External action without preceding governance stop rule",
            snippet="requests.get(url)",
            context_lines=["def fetch_data(url):", "    requests.get(url)"],
            suggested_fix="Add @require_permission decorator or explicit permission check",
            evidence_source="run/T5_evidence/pattern_samples/e501_external_without_stop_rule/skill.py",
        )

        finding = builder.from_pattern_match(match, skill_id="test-skill-1.0.0-abc12345")

        # Verify core fields
        assert finding.finding_id.startswith("F-pattern_match-")
        assert finding.source_type == FindingSourceType.PATTERN_MATCH
        assert finding.source_code == "E501_EXTERNAL_WITHOUT_STOP_RULE"
        assert finding.category == FindingCategory.GOVERNANCE_GAP
        assert finding.severity == FindingSeverity.CRITICAL
        assert finding.confidence == 0.85  # Pattern matching has 0.85 confidence

        # Verify location
        assert finding.file_path == "skill/external.py"
        assert finding.line_number == 15
        assert finding.function_name == "fetch_data"

        # Verify evidence refs
        assert len(finding.evidence_refs) >= 2
        assert any(e.kind == "CODE_LOCATION" for e in finding.evidence_refs)
        assert any("external.py:15" in e.locator for e in finding.evidence_refs)
        # Verify evidence_source is included
        assert any("e501_external_without_stop_rule" in e.locator for e in finding.evidence_refs)

    def test_from_governance_gap(self):
        """Converting T5 GovernanceGap to Finding."""
        builder = FindingBuilder(run_id="test_run")

        gap = GovernanceGap(
            gap_code=PatternCode.E501_EXTERNAL_WITHOUT_STOP_RULE,
            gap_name="External Action Without Stop Rule",
            file_path="skill/external.py",
            line_number=20,
            function_name="write_file",
            description="External action without preceding governance stop rule",
            severity="CRITICAL",
            missing_control="Permission check or authorization",
            recommended_control="Add @require_permission or explicit permission check",
            snippet="open(filename, 'w')",
        )

        finding = builder.from_governance_gap(gap, skill_id="test-skill-1.0.0-abc12345")

        # Verify core fields
        assert finding.finding_id.startswith("F-pattern_match-")
        assert finding.source_type == FindingSourceType.PATTERN_MATCH
        assert finding.source_code == "E501_EXTERNAL_WITHOUT_STOP_RULE"
        assert finding.category == FindingCategory.GOVERNANCE_GAP
        assert finding.missing_control == "Permission check or authorization"
        assert finding.recommended_control == "Add @require_permission or explicit permission check"


class TestFindingsReportStructure:
    """Test FindingsReport structure and statistics."""

    def test_empty_report(self):
        """Empty report should have zero findings."""
        report = FindingsReport(
            skill_id="test-skill-1.0.0-abc12345",
            skill_name="test_skill",
            generated_at=datetime.now(timezone.utc).isoformat(),
            run_id="test_run",
        )

        assert report.summary["total_findings"] == 0
        assert report.get_critical_findings() == []

    def test_add_finding_updates_summary(self):
        """Adding a finding should update summary statistics."""
        report = FindingsReport(
            skill_id="test-skill-1.0.0-abc12345",
            skill_name="test_skill",
            generated_at=datetime.now(timezone.utc).isoformat(),
            run_id="test_run",
        )

        builder = FindingBuilder(run_id="test_run")
        failure = ValidationFailure(
            code=ValidationErrorCode.E302_REQUIRED_FIELD_MISSING,
            message="Test",
            field_path="test",
            severity="ERROR",
        )
        finding = builder.from_validation_failure(failure, skill_id="test")

        report.add_finding(finding)

        assert report.summary["total_findings"] == 1
        assert report.summary["by_source"]["validation"] == 1
        assert report.summary["by_severity"]["HIGH"] == 1

    def test_get_findings_by_severity(self):
        """Filter findings by severity should work."""
        report = FindingsReport(
            skill_id="test-skill-1.0.0-abc12345",
            skill_name="test_skill",
            generated_at=datetime.now(timezone.utc).isoformat(),
            run_id="test_run",
        )

        builder = FindingBuilder(run_id="test_run")

        # Add CRITICAL finding
        hit = RuleHit(
            rule_code=RuleCode.E421_EVAL_OR_EXEC_USED,
            rule_name="eval",
            file_path="test.py",
            line_number=1,
            column_number=1,
            snippet="eval(x)",
            category="dangerous_pattern",
            severity="CRITICAL",
            message="Test",
            suggested_fix="Fix",
        )
        critical_finding = builder.from_rule_hit(hit, skill_id="test")
        report.add_finding(critical_finding)

        # Add HIGH finding
        failure = ValidationFailure(
            code=ValidationErrorCode.E302_REQUIRED_FIELD_MISSING,
            message="Test",
            field_path="test",
            severity="ERROR",
        )
        high_finding = builder.from_validation_failure(failure, skill_id="test")
        report.add_finding(high_finding)

        critical_findings = report.get_critical_findings()
        assert len(critical_findings) == 1
        assert critical_findings[0].severity == FindingSeverity.CRITICAL

    def test_report_to_dict(self):
        """FindingsReport should serialize correctly."""
        report = FindingsReport(
            skill_id="test-skill-1.0.0-abc12345",
            skill_name="test_skill",
            generated_at="2026-03-15T12:00:00Z",
            run_id="test_run",
            validation_report_path="run/test/validation_report.json",
        )

        d = report.to_dict()

        assert d["meta"]["skill_id"] == "test-skill-1.0.0-abc12345"
        assert d["meta"]["skill_name"] == "test_skill"
        assert d["input_sources"]["validation_report"] == "run/test/validation_report.json"
        assert d["findings"] == []
        assert d["summary"]["total_findings"] == 0


class TestFindingsReportBuilder:
    """Test FindingsReportBuilder convenience methods."""

    def test_build_from_t3_only(self):
        """Build report from T3 validation result only."""
        # Create mock T3 result
        class MockValidationResult:
            def __init__(self):
                self.is_valid = False
                self.failures = [
                    ValidationFailure(
                        code=ValidationErrorCode.E302_REQUIRED_FIELD_MISSING,
                        message="Test failure",
                        field_path="test_field",
                        severity="ERROR",
                    )
                ]
                self.warnings = []

        validation_result = MockValidationResult()

        builder = FindingsReportBuilder(run_id="test_run")
        report = builder.build_from_reports(
            skill_id="test-skill-1.0.0-abc12345",
            skill_name="test_skill",
            validation_result=validation_result,
            validation_report_path="run/test/validation_report.json",
        )

        assert report.summary["total_findings"] == 1
        assert report.summary["by_source"]["validation"] == 1
        assert len(report.findings) == 1
        assert report.findings[0].source_type == FindingSourceType.VALIDATION

    def test_build_from_multiple_sources(self):
        """Build report from T3/T4/T5 results."""
        # Mock T3
        class MockValidationResult:
            def __init__(self):
                self.is_valid = False
                self.failures = [
                    ValidationFailure(
                        code=ValidationErrorCode.E302_REQUIRED_FIELD_MISSING,
                        message="Test",
                        field_path="test",
                        severity="ERROR",
                    )
                ]
                self.warnings = []

        # Mock T4
        class MockRuleResult:
            def get_all_hits(self):
                return [
                    RuleHit(
                        rule_code=RuleCode.E421_EVAL_OR_EXEC_USED,
                        rule_name="eval",
                        file_path="test.py",
                        line_number=1,
                        column_number=1,
                        snippet="eval(x)",
                        category="dangerous_pattern",
                        severity="CRITICAL",
                        message="Test",
                        suggested_fix="Fix",
                    )
                ]

        # Mock T5
        class MockPatternResult:
            def get_all_matches(self):
                return [
                    PatternMatch(
                        pattern_code=PatternCode.E501_EXTERNAL_WITHOUT_STOP_RULE,
                        pattern_name="External",
                        file_path="test.py",
                        line_number=1,
                        function_name="test",
                        category="governance_gap",
                        severity="CRITICAL",
                        message="Test",
                        snippet="requests.get()",
                        context_lines=[],
                        suggested_fix="Fix",
                        evidence_source="run/test/skill.py",
                    )
                ]
            @property
            def governance_gaps(self):
                return []

        validation_result = MockValidationResult()
        rule_result = MockRuleResult()
        pattern_result = MockPatternResult()

        builder = FindingsReportBuilder(run_id="test_run")
        report = builder.build_from_reports(
            skill_id="test-skill-1.0.0-abc12345",
            skill_name="test_skill",
            validation_result=validation_result,
            rule_result=rule_result,
            pattern_result=pattern_result,
        )

        # Should have findings from all three sources
        assert report.summary["total_findings"] == 3
        assert report.summary["by_source"]["validation"] == 1
        assert report.summary["by_source"]["rule_scan"] == 1
        assert report.summary["by_source"]["pattern_match"] == 1


class TestEvidenceRefsMandatory:
    """Test T6 Hard Constraint: EvidenceRef is mandatory."""

    def test_finding_from_t3_has_evidence_refs(self):
        """Finding from T3 must have evidence refs."""
        builder = FindingBuilder(run_id="test_run")
        failure = ValidationFailure(
            code=ValidationErrorCode.E302_REQUIRED_FIELD_MISSING,
            message="Test",
            field_path="test",
            severity="ERROR",
        )
        finding = builder.from_validation_failure(failure, skill_id="test")

        assert len(finding.evidence_refs) >= 1, "T6 Hard Constraint: EvidenceRef is mandatory"

    def test_finding_from_t4_has_evidence_refs(self):
        """Finding from T4 must have evidence refs."""
        builder = FindingBuilder(run_id="test_run")
        hit = RuleHit(
            rule_code=RuleCode.E421_EVAL_OR_EXEC_USED,
            rule_name="eval",
            file_path="test.py",
            line_number=1,
            column_number=1,
            snippet="eval(x)",
            category="dangerous_pattern",
            severity="CRITICAL",
            message="Test",
            suggested_fix="Fix",
        )
        finding = builder.from_rule_hit(hit, skill_id="test")

        assert len(finding.evidence_refs) >= 1, "T6 Hard Constraint: EvidenceRef is mandatory"

    def test_finding_from_t5_has_evidence_refs(self):
        """Finding from T5 must have evidence refs."""
        builder = FindingBuilder(run_id="test_run")
        match = PatternMatch(
            pattern_code=PatternCode.E501_EXTERNAL_WITHOUT_STOP_RULE,
            pattern_name="External",
            file_path="test.py",
            line_number=1,
            function_name="test",
            category="governance_gap",
            severity="CRITICAL",
            message="Test",
            snippet="requests.get()",
            context_lines=[],
            suggested_fix="Fix",
            evidence_source="run/test/skill.py",
        )
        finding = builder.from_pattern_match(match, skill_id="test")

        assert len(finding.evidence_refs) >= 1, "T6 Hard Constraint: EvidenceRef is mandatory"
