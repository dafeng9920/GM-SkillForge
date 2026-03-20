"""
Rule Scanner and Boundary Checker - T4 Deliverable

This module provides static rule scanning and boundary gap detection for skill files.
It scans Python code for:
- Sensitive permissions (file I/O, network, system commands)
- External actions (HTTP requests, database access)
- Dangerous patterns (eval, exec, unsafe deserialization)
- Boundary gaps (missing permission checks, missing input validation)

Usage:
    from skillforge.src.contracts.rule_scanner import RuleScanner, RuleScanResult

    scanner = RuleScanner()
    result = scanner.scan_skill("skillforge/src/skills/quant/")
    result.save("run/T4_evidence/rule_scan_report.json")
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Optional


# ============================================================================
# Rule Definitions and Versioning
# ============================================================================
RULE_SET_VERSION = "1.0.0-t4"
RULE_SET_UPDATED_AT = "2026-03-15T00:00:00Z"


class RuleCode:
    """Standard rule codes for rule scanning (E4xx series)."""

    # Sensitive Permission Rules (E40x)
    E401_FILE_READ_without_CHECK = "E401_FILE_READ_without_CHECK"
    E402_FILE_WRITE_without_CHECK = "E402_FILE_WRITE_without_CHECK"
    E403_FILE_DELETE_without_CHECK = "E403_FILE_DELETE_without_CHECK"
    E404_NETWORK_ACCESS_without_CHECK = "E404_NETWORK_ACCESS_without_CHECK"
    E405_SYSTEM_COMMAND_without_SANITIZATION = "E405_SYSTEM_COMMAND_without_SANITIZATION"

    # External Action Rules (E41x)
    E411_HTTP_REQUEST_without_TIMEOUT = "E411_HTTP_REQUEST_without_TIMEOUT"
    E412_HTTP_REQUEST_without_ERROR_HANDLING = "E412_HTTP_REQUEST_without_ERROR_HANDLING"
    E413_DATABASE_QUERY_without_PARAMETERIZATION = "E413_DATABASE_QUERY_without_PARAMETERIZATION"
    E414_SHELL_COMMAND_with_USER_INPUT = "E414_SHELL_COMMAND_with_USER_INPUT"

    # Dangerous Pattern Rules (E42x)
    E421_EVAL_OR_EXEC_USED = "E421_EVAL_OR_EXEC_USED"
    E422_UNSAFE_DESERIALIZATION = "E422_UNSAFE_DESERIALIZATION"
    E423_HARDCODED_CREDENTIALS = "E423_HARDCODED_CREDENTIALS"
    E424_UNSAFE_RANDOM = "E424_UNSAFE_RANDOM"

    # Boundary Gap Rules (E43x)
    E431_MISSING_PERMISSION_CHECK = "E431_MISSING_PERMISSION_CHECK"
    E432_MISSING_INPUT_VALIDATION = "E432_MISSING_INPUT_VALIDATION"
    E433_MISSING_RATE_LIMITING = "E433_MISSING_RATE_LIMITING"
    E434_MISSING_AUDIT_LOG = "E434_MISSING_AUDIT_LOG"


# ============================================================================
# Rule Definition
# ============================================================================
@dataclass(frozen=True)
class Rule:
    """A single rule definition."""

    code: str
    name: str
    category: Literal["sensitive_permission", "external_action", "dangerous_pattern", "boundary_gap"]
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    description: str
    pattern: str  # Regex pattern to detect the rule
    file_patterns: list[str]  # File patterns to scan (e.g., ["*.py"])
    cwe_id: Optional[str] = None  # CWE ID if applicable
    owasp_id: Optional[str] = None  # OWASP ID if applicable
    remediation: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "code": self.code,
            "name": self.name,
            "category": self.category,
            "severity": self.severity,
            "description": self.description,
            "pattern": self.pattern,
            "file_patterns": self.file_patterns,
            "cwe_id": self.cwe_id,
            "owasp_id": self.owasp_id,
            "remediation": self.remediation,
        }


# ============================================================================
# Rule Hit
# ============================================================================
@dataclass(frozen=True)
class RuleHit:
    """A single rule hit found during scanning."""

    rule_code: str
    rule_name: str
    file_path: str  # Relative path from skill_dir
    line_number: int
    column_number: int
    snippet: str  # The matching code line
    category: str
    severity: str
    message: str
    suggested_fix: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rule_code": self.rule_code,
            "rule_name": self.rule_name,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column_number": self.column_number,
            "snippet": self.snippet,
            "category": self.category,
            "severity": self.severity,
            "message": self.message,
            "suggested_fix": self.suggested_fix,
        }


# ============================================================================
# Rule Scan Result
# ============================================================================
@dataclass
class RuleScanResult:
    """Result of a rule scan on a skill."""

    skill_name: str
    skill_dir: str
    scanned_at: str
    rule_set_version: str

    # Scan statistics
    files_scanned: int
    total_lines_scanned: int

    # Rule hits
    critical_hits: list[RuleHit] = field(default_factory=list)
    high_hits: list[RuleHit] = field(default_factory=list)
    medium_hits: list[RuleHit] = field(default_factory=list)
    low_hits: list[RuleHit] = field(default_factory=list)

    # Summary
    total_hits: int = 0
    by_category: dict[str, int] = field(default_factory=dict)
    by_severity: dict[str, int] = field(default_factory=dict)

    def add_hit(self, hit: RuleHit) -> None:
        """Add a rule hit to the appropriate severity bucket."""
        if hit.severity == "CRITICAL":
            self.critical_hits.append(hit)
        elif hit.severity == "HIGH":
            self.high_hits.append(hit)
        elif hit.severity == "MEDIUM":
            self.medium_hits.append(hit)
        else:
            self.low_hits.append(hit)

        self.total_hits += 1

        # Update by_category
        if hit.category not in self.by_category:
            self.by_category[hit.category] = 0
        self.by_category[hit.category] += 1

        # Update by_severity
        if hit.severity not in self.by_severity:
            self.by_severity[hit.severity] = 0
        self.by_severity[hit.severity] += 1

    def get_all_hits(self) -> list[RuleHit]:
        """Get all hits sorted by severity and line number."""
        all_hits = []
        all_hits.extend(self.critical_hits)
        all_hits.extend(self.high_hits)
        all_hits.extend(self.medium_hits)
        all_hits.extend(self.low_hits)
        return sorted(all_hits, key=lambda h: (h.severity, h.line_number))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "skill_name": self.skill_name,
            "skill_dir": self.skill_dir,
            "scanned_at": self.scanned_at,
            "rule_set_version": self.rule_set_version,
            "scan_statistics": {
                "files_scanned": self.files_scanned,
                "total_lines_scanned": self.total_lines_scanned,
                "total_hits": self.total_hits,
                "by_category": self.by_category,
                "by_severity": self.by_severity,
            },
            "findings": {
                "critical": [h.to_dict() for h in self.critical_hits],
                "high": [h.to_dict() for h in self.high_hits],
                "medium": [h.to_dict() for h in self.medium_hits],
                "low": [h.to_dict() for h in self.low_hits],
            },
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def save(self, output_path: str | Path) -> None:
        """Save the rule scan report to a JSON file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(self.to_json())


# ============================================================================
# Rule Scanner
# ============================================================================
class RuleScanner:
    """
    Scanner for detecting security and governance issues in skill code.

    T4 Scope:
    - Sensitive permission scanning (file I/O, network, system commands)
    - External action scanning (HTTP, database, shell)
    - Dangerous pattern scanning (eval, exec, unsafe deserialization)
    - Boundary gap scanning (missing checks, missing validation)
    - Rule version tracking

    T4 Hard Constraints:
    - Only static code analysis (no execution)
    - No adjudication or severity re-ranking
    - No owner summary or risk aggregation
    """

    # Rule definitions
    RULES: list[Rule] = [
        # Sensitive Permission Rules
        Rule(
            code=RuleCode.E401_FILE_READ_without_CHECK,
            name="File Read Without Permission Check",
            category="sensitive_permission",
            severity="HIGH",
            description="File read operation detected without explicit permission check",
            pattern=r'\b(open\(|read\(|Path\(.*read|readlines\()',
            file_patterns=["*.py"],
            cwe_id="CWE-732",
            remediation="Add explicit permission check before file read operation",
        ),
        Rule(
            code=RuleCode.E402_FILE_WRITE_without_CHECK,
            name="File Write Without Permission Check",
            category="sensitive_permission",
            severity="HIGH",
            description="File write operation detected without explicit permission check",
            pattern=r'\b(open\(.*[\'"]w[\'"\)]|write\(|\.write\()',
            file_patterns=["*.py"],
            cwe_id="CWE-732",
            remediation="Add explicit permission check before file write operation",
        ),
        Rule(
            code=RuleCode.E403_FILE_DELETE_without_CHECK,
            name="File Delete Without Permission Check",
            category="sensitive_permission",
            severity="CRITICAL",
            description="File delete operation detected without explicit permission check",
            pattern=r'\b(os\.remove|unlink|Path\(.*unlink|Path\(.*rmdir)',
            file_patterns=["*.py"],
            cwe_id="CWE-732",
            remediation="Add explicit permission check before file delete operation",
        ),
        Rule(
            code=RuleCode.E404_NETWORK_ACCESS_without_CHECK,
            name="Network Access Without Authorization Check",
            category="sensitive_permission",
            severity="HIGH",
            description="Network access detected without explicit authorization check",
            pattern=r'\b(socket\.|urllib\.|requests\.|http|connect\()',
            file_patterns=["*.py"],
            cwe_id="CWE-862",
            remediation="Add explicit authorization check before network access",
        ),
        Rule(
            code=RuleCode.E405_SYSTEM_COMMAND_without_SANITIZATION,
            name="System Command Without Sanitization",
            category="sensitive_permission",
            severity="CRITICAL",
            description="System command execution detected without input sanitization",
            pattern=r'\b(os\.system|subprocess\.call|subprocess\.run|Popen\()',
            file_patterns=["*.py"],
            cwe_id="CWE-78",
            owasp_id="A03:2021",
            remediation="Use subprocess.run with shell=False and sanitize all inputs",
        ),
        # External Action Rules
        Rule(
            code=RuleCode.E411_HTTP_REQUEST_without_TIMEOUT,
            name="HTTP Request Without Timeout",
            category="external_action",
            severity="MEDIUM",
            description="HTTP request detected without timeout parameter",
            pattern=r'\b(requests\.(get|post|put|delete|patch)\([^)]*\)(?!.*timeout)',
            file_patterns=["*.py"],
            remediation="Add timeout parameter to all HTTP requests",
        ),
        Rule(
            code=RuleCode.E412_HTTP_REQUEST_without_ERROR_HANDLING,
            name="HTTP Request Without Error Handling",
            category="external_action",
            severity="LOW",
            description="HTTP request without proper error handling",
            pattern=r'\brequests\.(get|post|put|delete|patch)\(',
            file_patterns=["*.py"],
            remediation="Wrap HTTP requests in try-except blocks",
        ),
        Rule(
            code=RuleCode.E413_DATABASE_QUERY_without_PARAMETERIZATION,
            name="Database Query Without Parameterization",
            category="external_action",
            severity="CRITICAL",
            description="Database query with string formatting (SQL injection risk)",
            pattern=r'(execute|executemany)\([^)]*%[^)]*\)|execute\([^)]*f["\'][^"\']*\{[^}]*\}[^"\']*["\']',
            file_patterns=["*.py"],
            cwe_id="CWE-89",
            owasp_id="A03:2021",
            remediation="Use parameterized queries with placeholders",
        ),
        Rule(
            code=RuleCode.E414_SHELL_COMMAND_with_USER_INPUT,
            name="Shell Command with User Input",
            category="external_action",
            severity="CRITICAL",
            description="Shell command constructed with user input",
            pattern=r'subprocess\.(call|run|Popen)\([^)]*\+\s*[^)]*\)|os\.system\([^)]*\+\s*',
            file_patterns=["*.py"],
            cwe_id="CWE-78",
            remediation="Never construct shell commands with user input",
        ),
        # Dangerous Pattern Rules
        Rule(
            code=RuleCode.E421_EVAL_OR_EXEC_USED,
            name="eval or exec Function Used",
            category="dangerous_pattern",
            severity="CRITICAL",
            description="Use of eval() or exec() functions detected",
            pattern=r'\b(eval\(|exec\()',
            file_patterns=["*.py"],
            cwe_id="CWE-95",
            remediation="Replace eval/exec with safer alternatives",
        ),
        Rule(
            code=RuleCode.E422_UNSAFE_DESERIALIZATION,
            name="Unsafe Deserialization",
            category="dangerous_pattern",
            severity="HIGH",
            description="Unsafe deserialization detected (pickle/shelve)",
            pattern=r'\b(pickle\.(loads|load)|shelve\.(open|dbmfile)|cPickle)',
            file_patterns=["*.py"],
            cwe_id="CWE-502",
            remediation="Use safe deserialization formats like JSON",
        ),
        Rule(
            code=RuleCode.E423_HARDCODED_CREDENTIALS,
            name="Hardcoded Credentials",
            category="dangerous_pattern",
            severity="HIGH",
            description="Potential hardcoded credentials detected",
            pattern=r'(password|api_key|secret|token)\s*=\s*["\'][^"\']{8,}["\']',
            file_patterns=["*.py"],
            cwe_id="CWE-798",
            remediation="Move credentials to environment variables or config files",
        ),
        Rule(
            code=RuleCode.E424_UNSAFE_RANDOM,
            name="Unsafe Random Number Generator",
            category="dangerous_pattern",
            severity="LOW",
            description="Use of random module for security-sensitive operations",
            pattern=r'\bimport random\b|random\.(random|randint|choice)\(',
            file_patterns=["*.py"],
            cwe_id="CWE-338",
            remediation="Use secrets module for cryptographic operations",
        ),
        # Boundary Gap Rules
        Rule(
            code=RuleCode.E431_MISSING_PERMISSION_CHECK,
            name="Missing Permission Check Before Sensitive Operation",
            category="boundary_gap",
            severity="HIGH",
            description="Sensitive operation without preceding permission check",
            pattern=r'(#\s*TODO:.*permission|#\s*FIXME:.*check)',
            file_patterns=["*.py"],
            cwe_id="CWE-862",
            remediation="Implement proper permission checks before sensitive operations",
        ),
        Rule(
            code=RuleCode.E432_MISSING_INPUT_VALIDATION,
            name="Missing Input Validation",
            category="boundary_gap",
            severity="MEDIUM",
            description="Function accepting user input without validation",
            pattern=r'def\s+\w+.*\([^)]*request[^)]*\):',
            file_patterns=["*.py"],
            remediation="Add input validation before processing user data",
        ),
        Rule(
            code=RuleCode.E433_MISSING_RATE_LIMITING,
            name="Missing Rate Limiting",
            category="boundary_gap",
            severity="MEDIUM",
            description="External API call without rate limiting",
            pattern=r'requests\.(get|post|put|delete)\(',
            file_patterns=["*.py"],
            remediation="Implement rate limiting for external API calls",
        ),
        Rule(
            code=RuleCode.E434_MISSING_AUDIT_LOG,
            name="Missing Audit Log",
            category="boundary_gap",
            severity="LOW",
            description="Sensitive operation without audit logging",
            pattern=r'(def\s+\w+.*delete|def\s+\w+.*admin|def\s+\w+.*root)',
            file_patterns=["*.py"],
            remediation="Add audit logging for sensitive operations",
        ),
    ]

    def __init__(self):
        """Initialize the rule scanner."""
        self.rules_by_code = {rule.code: rule for rule in self.RULES}

    def scan_skill(self, skill_dir: str | Path) -> RuleScanResult:
        """
        Scan a skill directory for rule violations.

        Args:
            skill_dir: Path to skill directory (e.g., "skillforge/src/skills/quant/")

        Returns:
            RuleScanResult with all detected rule hits.
        """
        skill_dir = Path(skill_dir).resolve()
        skill_name = skill_dir.name

        result = RuleScanResult(
            skill_name=skill_name,
            skill_dir=str(skill_dir),
            scanned_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            rule_set_version=RULE_SET_VERSION,
            files_scanned=0,
            total_lines_scanned=0,
        )

        # Find all Python files in skill directory
        python_files = list(skill_dir.rglob("*.py"))

        for file_path in python_files:
            self._scan_file(file_path, skill_dir, result)

        return result

    def _scan_file(self, file_path: Path, skill_dir: Path, result: RuleScanResult) -> None:
        """Scan a single file for rule violations."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except OSError:
            return

        result.files_scanned += 1
        rel_path = str(file_path.relative_to(skill_dir))

        for line_number, line in enumerate(lines, start=1):
            result.total_lines_scanned += 1
            self._scan_line(line, rel_path, line_number, result)

    def _scan_line(self, line: str, file_path: str, line_number: int, result: RuleScanResult) -> None:
        """Scan a single line for rule violations."""
        for rule in self.RULES:
            try:
                matches = re.finditer(rule.pattern, line, re.IGNORECASE)
                for match in matches:
                    hit = RuleHit(
                        rule_code=rule.code,
                        rule_name=rule.name,
                        file_path=file_path,
                        line_number=line_number,
                        column_number=match.start() + 1,
                        snippet=line.strip(),
                        category=rule.category,
                        severity=rule.severity,
                        message=rule.description,
                        suggested_fix=rule.remediation,
                    )
                    result.add_hit(hit)
            except re.error:
                # Skip invalid regex patterns
                continue


# ============================================================================
# Boundary Checker
# ============================================================================
class BoundaryChecker:
    """
    Checker for detecting governance boundary gaps in skills.

    Scans for:
    - Missing stop rules for external actions
    - Missing permission checks for sensitive operations
    - Missing input validation for user inputs
    - Missing audit logging for sensitive operations
    """

    def __init__(self):
        """Initialize the boundary checker."""
        self.stop_rule_patterns = [
            r"@require_permission",
            r"@check_authorization",
            r"if\s+not\s+.*permission",
            r"if\s+not\s+.*authorized",
            r"validate_permission",
            r"check_access",
        ]

        self.input_validation_patterns = [
            r"validate",
            r"sanitize",
            r"clean",
            r"check_input",
            r"verify",
        ]

    def check_boundaries(self, skill_dir: str | Path) -> list[dict[str, Any]]:
        """
        Check a skill directory for boundary gaps.

        Args:
            skill_dir: Path to skill directory

        Returns:
            List of boundary gap findings
        """
        skill_dir = Path(skill_dir).resolve()
        findings = []

        python_files = list(skill_dir.rglob("*.py"))

        for file_path in python_files:
            findings.extend(self._check_file_boundaries(file_path, skill_dir))

        return findings

    def _check_file_boundaries(self, file_path: Path, skill_dir: Path) -> list[dict[str, Any]]:
        """Check a single file for boundary gaps."""
        findings = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except OSError:
            return findings

        rel_path = str(file_path.relative_to(skill_dir))

        # Check for sensitive operations without stop rules
        for i, line in enumerate(lines):
            # Check for external actions (HTTP, file operations, etc.)
            if self._is_sensitive_operation(line):
                # Look backwards for stop rule
                has_stop_rule = False
                for prev_line in lines[max(0, i - 5):i]:
                    if any(re.search(pattern, prev_line) for pattern in self.stop_rule_patterns):
                        has_stop_rule = True
                        break

                if not has_stop_rule:
                    findings.append({
                        "type": "missing_stop_rule",
                        "file_path": rel_path,
                        "line_number": i + 1,
                        "severity": "HIGH",
                        "message": "Sensitive operation without stop rule",
                        "snippet": line.strip(),
                    })

        return findings

    def _is_sensitive_operation(self, line: str) -> bool:
        """Check if a line contains a sensitive operation."""
        sensitive_patterns = [
            r"requests\.(get|post|put|delete|patch)",
            r"subprocess\.",
            r"os\.system",
            r"open\(.*w",
            r"eval\(",
            r"exec\(",
        ]
        return any(re.search(pattern, line) for pattern in sensitive_patterns)


# ============================================================================
# CLI Entry Point
# ============================================================================
def main():
    """CLI entry point for rule scanning."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Scan skill directory for security and governance issues"
    )
    parser.add_argument(
        "skill_dir",
        help="Path to skill directory (e.g., skillforge/src/skills/quant/)",
    )
    parser.add_argument(
        "--output",
        default="run/T4_evidence/rule_scan_report.json",
        help="Output path for rule_scan_report.json",
    )
    args = parser.parse_args()

    # Scan skill
    scanner = RuleScanner()
    result = scanner.scan_skill(args.skill_dir)

    # Save report
    result.save(args.output)

    # Print summary
    print(f"Rule Scan Report saved to: {args.output}")
    print(f"  Files Scanned: {result.files_scanned}")
    print(f"  Lines Scanned: {result.total_lines_scanned}")
    print(f"  Total Hits: {result.total_hits}")
    print(f"  By Severity:")
    for severity, count in result.by_severity.items():
        print(f"    {severity}: {count}")


if __name__ == "__main__":
    main()
