"""
T5 Pattern Detection Tests

Tests for T5 anti-pattern and governance gap detection.

T5 Scope:
- E501: External action without stop rule
- E502: Retry without idempotency protection
- E503: High-privilege call without boundary
- E504: Missing auditable exit

Test Categories:
1. Pattern matcher basic functionality
2. Anti-pattern library validation
3. Pattern detection on sample code
4. Governance gap detection
5. Report generation and schema validation
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

# Add project root to path
import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "skillforge" / "src"))

from skillforge.src.contracts.pattern_matcher import (
    PatternMatcher,
    PatternCode,
    ANTI_PATTERN_LIBRARY,
    GovernanceGapDetector,
)


# ============================================================================
# Anti-Pattern Library Tests
# ============================================================================
class TestAntiPatternLibrary:
    """Tests for the anti-pattern library."""

    def test_only_four_patterns_defined(self):
        """T5 Constraint: Only 4 fixed patterns allowed."""
        assert len(ANTI_PATTERN_LIBRARY) == 4, (
            "T5 hard constraint: exactly 4 patterns required. "
            "Do not expand into comprehensive pattern library."
        )

    def test_pattern_codes(self):
        """Verify all 4 required pattern codes exist."""
        expected_codes = {
            PatternCode.E501_EXTERNAL_WITHOUT_STOP_RULE,
            PatternCode.E502_RETRY_WITHOUT_IDEMPOTENCY,
            PatternCode.E503_HIGH_PRIV_WITHOUT_BOUNDARY,
            PatternCode.E504_MISSING_AUDITABLE_EXIT,
        }
        actual_codes = {p.code for p in ANTI_PATTERN_LIBRARY}
        assert actual_codes == expected_codes, (
            f"Expected pattern codes: {expected_codes}, got: {actual_codes}"
        )

    def test_pattern_has_evidence_source(self):
        """T5 Constraint: All patterns must have evidence_source."""
        for pattern in ANTI_PATTERN_LIBRARY:
            assert pattern.evidence_source, (
                f"Pattern {pattern.code} missing evidence_source. "
                "T5 requires all patterns to have source file evidence."
            )
            # Verify evidence_source is a valid file path format
            assert "skillforge/src/" in pattern.evidence_source or ".py" in pattern.evidence_source, (
                f"Pattern {pattern.code} has invalid evidence_source: {pattern.evidence_source}"
            )

    def test_pattern_structure(self):
        """Verify all required fields exist in pattern definitions."""
        for pattern in ANTI_PATTERN_LIBRARY:
            assert pattern.code, f"Pattern missing code"
            assert pattern.name, f"Pattern {pattern.code} missing name"
            assert pattern.category in ["governance_gap", "anti_pattern"], (
                f"Pattern {pattern.code} has invalid category: {pattern.category}"
            )
            assert pattern.severity in ["CRITICAL", "HIGH", "MEDIUM"], (
                f"Pattern {pattern.code} has invalid severity: {pattern.severity}"
            )
            assert pattern.description, f"Pattern {pattern.code} missing description"
            assert pattern.risk_impact, f"Pattern {pattern.code} missing risk_impact"
            assert pattern.detection_criteria, f"Pattern {pattern.code} missing detection_criteria"
            assert pattern.remediation, f"Pattern {pattern.code} missing remediation"


# ============================================================================
# Pattern Matcher Basic Tests
# ============================================================================
class TestPatternMatcher:
    """Tests for PatternMatcher basic functionality."""

    def test_matcher_initialization(self):
        """PatternMatcher should initialize with all 4 patterns."""
        matcher = PatternMatcher()
        assert len(matcher.patterns) == 4
        assert PatternCode.E501_EXTERNAL_WITHOUT_STOP_RULE in matcher.patterns
        assert PatternCode.E502_RETRY_WITHOUT_IDEMPOTENCY in matcher.patterns
        assert PatternCode.E503_HIGH_PRIV_WITHOUT_BOUNDARY in matcher.patterns
        assert PatternCode.E504_MISSING_AUDITABLE_EXIT in matcher.patterns

    def test_match_empty_directory(self):
        """Matcher should handle empty directory gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            matcher = PatternMatcher()
            result = matcher.match_patterns(tmpdir)

            assert result.files_analyzed == 0
            assert result.functions_analyzed == 0
            assert result.total_matches == 0
            assert len(result.critical_matches) == 0
            assert len(result.high_matches) == 0
            assert len(result.medium_matches) == 0


# ============================================================================
# E501: External Action Without Stop Rule Tests
# ============================================================================
class TestE501ExternalWithoutStopRule:
    """Tests for E501 pattern detection."""

    def test_requests_without_permission_check(self):
        """HTTP request without preceding permission check should trigger E501."""
        code = '''
def execute_external_call():
    """This function makes HTTP request without permission check."""
    import requests
    response = requests.get("https://api.example.com/data")
    return response.json()
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test_skill.py"
            test_file.write_text(code)

            matcher = PatternMatcher()
            result = matcher.match_patterns(tmpdir)

            # Should detect E501
            e501_matches = [m for m in result.get_all_matches()
                           if m.pattern_code == PatternCode.E501_EXTERNAL_WITHOUT_STOP_RULE]
            assert len(e501_matches) >= 1, "E501 should detect requests.get without permission check"

    def test_requests_with_permission_check_passes(self):
        """HTTP request WITH permission check should NOT trigger E501."""
        code = '''
@require_permission("api_call")
def execute_external_call():
    """This function has permission check decorator."""
    import requests
    response = requests.get("https://api.example.com/data")
    return response.json()
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test_skill.py"
            test_file.write_text(code)

            matcher = PatternMatcher()
            result = matcher.match_patterns(tmpdir)

            # Should NOT detect E501
            e501_matches = [m for m in result.get_all_matches()
                           if m.pattern_code == PatternCode.E501_EXTERNAL_WITHOUT_STOP_RULE]
            assert len(e501_matches) == 0, "E501 should NOT fire when @require_permission is present"

    def test_subprocess_without_stop_rule(self):
        """Subprocess call without stop rule should trigger E501."""
        code = '''
def run_system_command(command):
    """Run system command without authorization check."""
    import subprocess
    result = subprocess.run(command, shell=True)
    return result
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test_skill.py"
            test_file.write_text(code)

            matcher = PatternMatcher()
            result = matcher.match_patterns(tmpdir)

            e501_matches = [m for m in result.get_all_matches()
                           if m.pattern_code == PatternCode.E501_EXTERNAL_WITHOUT_STOP_RULE]
            assert len(e501_matches) >= 1, "E501 should detect subprocess.run without stop rule"


# ============================================================================
# E502: Retry Without Idempotency Tests
# ============================================================================
class TestE502RetryWithoutIdempotency:
    """Tests for E502 pattern detection."""

    def test_retry_without_idempotency_key(self):
        """Retry function without idempotency key should trigger E502."""
        code = '''
def retry_api_call():
    """Retry API call without idempotency protection."""
    import requests
    for attempt in range(3):
        try:
            response = requests.post("https://api.example.com/execute", json={"action": "transfer"})
            return response.json()
        except requests.Timeout:
            continue
    return None
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test_skill.py"
            test_file.write_text(code)

            matcher = PatternMatcher()
            result = matcher.match_patterns(tmpdir)

            e502_matches = [m for m in result.get_all_matches()
                           if m.pattern_code == PatternCode.E502_RETRY_WITHOUT_IDEMPOTENCY]
            assert len(e502_matches) >= 1, "E502 should detect retry loop without idempotency protection"

    def test_retry_with_idempotency_key_passes(self):
        """Retry function WITH idempotency key should NOT trigger E502."""
        code = '''
def retry_api_call_with_idempotency(idempotency_key):
    """Retry API call with idempotency protection."""
    import requests
    for attempt in range(3):
        # Check if already processed
        if idempotency_key in seen_keys:
            return get_cached_result(idempotency_key)
        try:
            response = requests.post("https://api.example.com/execute",
                                    json={"idempotency_key": idempotency_key, "action": "transfer"})
            return response.json()
        except requests.Timeout:
            continue
    return None
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test_skill.py"
            test_file.write_text(code)

            matcher = PatternMatcher()
            result = matcher.match_patterns(tmpdir)

            e502_matches = [m for m in result.get_all_matches()
                           if m.pattern_code == PatternCode.E502_RETRY_WITHOUT_IDEMPOTENCY]
            assert len(e502_matches) == 0, "E502 should NOT fire when idempotency_key is present"


# ============================================================================
# E503: High-Privilege Call Without Boundary Tests
# ============================================================================
class TestE503HighPrivWithoutBoundary:
    """Tests for E503 pattern detection."""

    def test_file_delete_without_limit(self):
        """File delete operation without boundary limit should trigger E503."""
        code = '''
def cleanup_old_files():
    """Delete files without any limit or quota check."""
    import os
    for file_path in old_files:
        os.remove(file_path)
    return "deleted"
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test_skill.py"
            test_file.write_text(code)

            matcher = PatternMatcher()
            result = matcher.match_patterns(tmpdir)

            e503_matches = [m for m in result.get_all_matches()
                           if m.pattern_code == PatternCode.E503_HIGH_PRIV_WITHOUT_BOUNDARY]
            assert len(e503_matches) >= 1, "E503 should detect os.remove without boundary limit"

    def test_db_write_without_limit(self):
        """Database write without resource limit should trigger E503."""
        code = '''
def batch_write_records(records):
    """Write records without any limit check."""
    for record in records:
        db.execute("INSERT INTO transactions VALUES (?)", record)
    return "written"
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test_skill.py"
            test_file.write_text(code)

            matcher = PatternMatcher()
            result = matcher.match_patterns(tmpdir)

            e503_matches = [m for m in result.get_all_matches()
                           if m.pattern_code == PatternCode.E503_HIGH_PRIV_WITHOUT_BOUNDARY]
            assert len(e503_matches) >= 1, "E503 should detect db.execute without boundary"

    def test_high_priv_with_rate_limit_passes(self):
        """High-privilege operation WITH rate limit should NOT trigger E503."""
        code = '''
def delete_files_with_limit(files):
    """Delete files with rate limiting."""
    import os
    for file_path in files:
        if rate_limit.check("delete_operation"):
            os.remove(file_path)
    return "deleted"
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test_skill.py"
            test_file.write_text(code)

            matcher = PatternMatcher()
            result = matcher.match_patterns(tmpdir)

            e503_matches = [m for m in result.get_all_matches()
                           if m.pattern_code == PatternCode.E503_HIGH_PRIV_WITHOUT_BOUNDARY]
            assert len(e503_matches) == 0, "E503 should NOT fire when rate_limit is present"


# ============================================================================
# E504: Missing Auditable Exit Tests
# ============================================================================
class TestE504MissingAuditableExit:
    """Tests for E504 pattern detection."""

    def test_execute_without_audit(self):
        """Execute function without audit logging should trigger E504."""
        code = '''
def execute_trade(symbol, quantity):
    """Execute trade without audit log."""
    order = broker.place_order(symbol, quantity)
    return {"order_id": order.id, "status": "FILLED"}
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test_skill.py"
            test_file.write_text(code)

            matcher = PatternMatcher()
            result = matcher.match_patterns(tmpdir)

            e504_matches = [m for m in result.get_all_matches()
                           if m.pattern_code == PatternCode.E504_MISSING_AUDITABLE_EXIT]
            # Note: E504 checks for function name OR sensitive keywords
            # "execute" in function name should trigger it
            assert len(e504_matches) >= 1, "E504 should detect execute function without audit"

    def test_delete_with_audit_passes(self):
        """Delete function WITH audit logging should NOT trigger E504."""
        code = '''
def delete_record(record_id):
    """Delete record with audit logging."""
    db.delete(record_id)
    write_audit_event("DELETE", record_id=record_id, user=current_user)
    return {"status": "deleted"}
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test_skill.py"
            test_file.write_text(code)

            matcher = PatternMatcher()
            result = matcher.match_patterns(tmpdir)

            e504_matches = [m for m in result.get_all_matches()
                           if m.pattern_code == PatternCode.E504_MISSING_AUDITABLE_EXIT]
            assert len(e504_matches) == 0, "E504 should NOT fire when write_audit_event is present"


# ============================================================================
# Governance Gap Detector Tests
# ============================================================================
class TestGovernanceGapDetector:
    """Tests for GovernanceGapDetector."""

    def test_detector_initialization(self):
        """GovernanceGapDetector should initialize."""
        detector = GovernanceGapDetector()
        assert detector.stop_rule_patterns
        assert detector.audit_patterns

    def test_detect_gaps_empty_directory(self):
        """Detector should handle empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            detector = GovernanceGapDetector()
            gaps = detector.detect_gaps(tmpdir)
            assert gaps == []


# ============================================================================
# Report Generation Tests
# ============================================================================
class TestReportGeneration:
    """Tests for report generation and schema validation."""

    def test_report_to_dict(self):
        """PatternMatchResult should convert to dict correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "skill.py"
            test_file.write_text("def foo(): pass")

            matcher = PatternMatcher()
            result = matcher.match_patterns(tmpdir)

            report_dict = result.to_dict()
            assert "skill_name" in report_dict
            assert "analyzed_at" in report_dict
            assert "pattern_set_version" in report_dict
            assert "analysis_statistics" in report_dict
            assert "pattern_matches" in report_dict
            assert "governance_gaps" in report_dict

    def test_report_save_and_load(self):
        """Report should save to JSON and be loadable."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "skill.py"
            test_file.write_text("def foo(): pass")

            report_path = Path(tmpdir) / "report.json"

            matcher = PatternMatcher()
            result = matcher.match_patterns(tmpdir)
            result.save(report_path)

            assert report_path.exists()

            with open(report_path) as f:
                loaded = json.load(f)

            assert loaded["skill_name"] == result.skill_name
            assert loaded["pattern_set_version"] == result.pattern_set_version

    def test_schema_validation_positive(self):
        """Valid report should pass schema validation."""
        schema_path = project_root / "skillforge" / "src" / "contracts" / "pattern_detection_report.schema.json"

        if not schema_path.exists():
            pytest.skip("Schema file not found")

        with open(schema_path) as f:
            schema = json.load(f)

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "skill.py"
            test_file.write_text("def foo(): pass")

            matcher = PatternMatcher()
            result = matcher.match_patterns(tmpdir)
            report_dict = result.to_dict()

            # Basic validation - check required fields
            required = schema.get("required", [])
            for field in required:
                assert field in report_dict, f"Missing required field: {field}"

            # Check analysis_statistics structure
            stats = report_dict["analysis_statistics"]
            assert "files_analyzed" in stats
            assert "total_matches" in stats


# ============================================================================
# Integration Tests
# ============================================================================
class TestIntegration:
    """Integration tests for pattern detection."""

    def test_full_workflow(self):
        """Test complete pattern detection workflow."""
        code = '''
# This file contains multiple anti-patterns for testing

def risky_operation():
    """E501: External action without stop rule."""
    import requests
    return requests.get("https://api.example.com/data")

def retry_transfer(amount):
    """E502: Retry without idempotency."""
    import requests
    for i in range(3):
        response = requests.post("https://api.bank.com/transfer",
                                json={"amount": amount})
        if response.ok:
            break
    return response

def cleanup_files():
    """E503: High-privilege without boundary."""
    import os
    for f in files:
        os.remove(f)

def execute_trade():
    """E504: Missing auditable exit."""
    broker.place_order("AAPL", 100)
    return "done"
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "risky_skill.py"
            test_file.write_text(code)

            matcher = PatternMatcher()
            result = matcher.match_patterns(tmpdir)

            # Should detect multiple patterns
            assert result.files_analyzed == 1
            assert result.total_matches > 0

            # Check that we found our expected patterns
            pattern_codes_found = {m.pattern_code for m in result.get_all_matches()}
            # At least some of E501-E504 should be detected
            assert len(pattern_codes_found) > 0


# ============================================================================
# Evidence Source Tests (T5 Requirement)
# ============================================================================
class TestEvidenceSource:
    """Tests for evidence_source requirement."""

    def test_all_patterns_have_evidence_source(self):
        """T5 Constraint: All patterns must have evidence_source."""
        for pattern in ANTI_PATTERN_LIBRARY:
            assert pattern.evidence_source, (
                f"Pattern {pattern.code} missing evidence_source. "
                "T5 requires traceability to source code."
            )

    def test_evidence_source_is_valid_path(self):
        """Evidence source should be a valid file path."""
        for pattern in ANTI_PATTERN_LIBRARY:
            # Should be a valid-looking file path
            assert ".py" in pattern.evidence_source or "src/" in pattern.evidence_source, (
                f"Pattern {pattern.code} has invalid evidence_source format: {pattern.evidence_source}"
            )

    def test_match_includes_evidence_source(self):
        """PatternMatch should include evidence_source for traceability."""
        code = '''
def risky_call():
    import requests
    return requests.get("https://api.example.com")
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text(code)

            matcher = PatternMatcher()
            result = matcher.match_patterns(tmpdir)

            for match in result.get_all_matches():
                assert match.evidence_source, (
                    f"Match {match.pattern_code} missing evidence_source. "
                    "T5 requires all matches to reference source file."
                )


# ============================================================================
# Comment Insulation Tests (T5 Fix Validation)
# ============================================================================
class TestCommentInsulation:
    """
    Tests to verify that comments do not affect pattern detection.

    This validates the fix for the CRITICAL violations:
    - Comments like '# Missing: write_audit_event' should NOT be treated as actual audit code
    - Only actual code (AST nodes) should drive pattern detection
    """

    def test_e504_comment_with_missing_audit_does_not_prevent_detection(self):
        """
        E504 should be detected even when comments mention 'Missing: write_audit_event'.

        This was the CRITICAL bug: comments were being matched by AUDIT_PATTERNS,
        causing real violations to be missed.
        """
        code = '''
def execute_trade():
    """
    Execute trade without audit log.

    CRITICAL FIX: The comment below should NOT prevent E504 detection.
    """
    broker.place_order("AAPL", 100)

    # Missing: write_audit_event("ORDER_EXECUTED", ...)
    # Missing: capture_gate_event(...)

    return "done"
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "skill.py"
            test_file.write_text(code)

            matcher = PatternMatcher()
            result = matcher.match_patterns(tmpdir)

            # Should detect E504 because there's no actual audit call in the code
            e504_matches = [m for m in result.get_all_matches()
                           if m.pattern_code == PatternCode.E504_MISSING_AUDITABLE_EXIT]
            assert len(e504_matches) >= 1, (
                "E504 should be detected. Comments mentioning 'Missing: write_audit_event' "
                "should NOT count as actual audit code."
            )

    def test_e504_actual_audit_call_prevents_detection(self):
        """
        E504 should NOT be detected when there's an actual audit call.

        This validates that real audit function calls ARE detected.
        """
        code = '''
def execute_trade():
    """Execute trade with proper audit log."""
    broker.place_order("AAPL", 100)

    # Actual audit call - this should prevent E504
    write_audit_event("ORDER_EXECUTED", symbol="AAPL", quantity=100)

    return "done"
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "skill.py"
            test_file.write_text(code)

            matcher = PatternMatcher()
            result = matcher.match_patterns(tmpdir)

            # Should NOT detect E504 because there's actual audit code
            e504_matches = [m for m in result.get_all_matches()
                           if m.pattern_code == PatternCode.E504_MISSING_AUDITABLE_EXIT]
            assert len(e504_matches) == 0, (
                "E504 should NOT be detected when actual write_audit_event() call exists."
            )

    def test_e501_comment_does_not_count_as_stop_rule(self):
        """
        E501 should be detected even when comments mention permission checks.

        Comments should NOT substitute for actual permission checks.
        """
        code = '''
def risky_api_call():
    """
    Make external API call.

    CRITICAL FIX: Comments should NOT count as stop rules.
    """
    import requests

    # TODO: check_permission before calling API
    # FIXME: add authorization here

    # Actual external action without stop rule
    return requests.get("https://api.example.com/data")
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "skill.py"
            test_file.write_text(code)

            matcher = PatternMatcher()
            result = matcher.match_patterns(tmpdir)

            # Should detect E501 because comments don't count as stop rules
            e501_matches = [m for m in result.get_all_matches()
                           if m.pattern_code == PatternCode.E501_EXTERNAL_WITHOUT_STOP_RULE]
            assert len(e501_matches) >= 1, (
                "E501 should be detected. Comments mentioning 'check_permission' "
                "should NOT count as actual stop rules."
            )

    def test_e502_idempotency_check_in_code_prevents_detection(self):
        """
        E502 should NOT be detected when there's actual idempotency check.

        This validates that real idempotency checks ARE detected.
        """
        code = '''
def retry_transfer_safe(idempotency_key):
    """Retry with idempotency protection."""
    import requests

    # Actual idempotency check in if statement
    if idempotency_key in seen_keys:
        return {"cached": True}

    for attempt in range(3):
        response = requests.post("https://api.bank.com/transfer",
                                json={"idempotency_key": idempotency_key})
        if response.ok:
            break
    return response
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "skill.py"
            test_file.write_text(code)

            matcher = PatternMatcher()
            result = matcher.match_patterns(tmpdir)

            # Should NOT detect E502 because there's actual idempotency check
            e502_matches = [m for m in result.get_all_matches()
                           if m.pattern_code == PatternCode.E502_RETRY_WITHOUT_IDEMPOTENCY]
            assert len(e502_matches) == 0, (
                "E502 should NOT be detected when actual idempotency check exists."
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
