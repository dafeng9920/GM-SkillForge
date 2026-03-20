"""
Pattern Matcher - T5 Deliverable

This module provides pattern matching for detecting anti-patterns and governance gaps
in skill code. It identifies high-value patterns based on actual code analysis.

T5 Scope:
- External action without stop rule (E501)
- Retry without idempotency protection (E502)
- High-privilege call without boundary (E503)
- Missing auditable exit (E504)

T5 Hard Constraints:
- Only 4 fixed high-value patterns
- No fabricating pattern findings
- All patterns must have source evidence
- Each pattern must have sample code

Usage:
    from skillforge.src.contracts.pattern_matcher import PatternMatcher, PatternMatchResult

    matcher = PatternMatcher()
    result = matcher.match_patterns("skillforge/src/skills/quant/")
    result.save("run/T5_evidence/pattern_detection_report.json")
"""
from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Optional


# ============================================================================
# Pattern Definitions and Versioning
# ============================================================================
PATTERN_SET_VERSION = "1.0.0-t5"
PATTERN_SET_UPDATED_AT = "2026-03-15T00:00:00Z"


class PatternCode:
    """Pattern codes for anti-pattern detection (E5xx series)."""

    # E501: External action without stop rule
    E501_EXTERNAL_WITHOUT_STOP_RULE = "E501_EXTERNAL_WITHOUT_STOP_RULE"

    # E502: Retry without idempotency protection
    E502_RETRY_WITHOUT_IDEMPOTENCY = "E502_RETRY_WITHOUT_IDEMPOTENCY"

    # E503: High-privilege call without boundary
    E503_HIGH_PRIV_WITHOUT_BOUNDARY = "E503_HIGH_PRIV_WITHOUT_BOUNDARY"

    # E504: Missing auditable exit
    E504_MISSING_AUDITABLE_EXIT = "E504_MISSING_AUDITABLE_EXIT"


# ============================================================================
# Anti-Pattern Definition
# ============================================================================
@dataclass(frozen=True)
class AntiPattern:
    """Definition of an anti-pattern."""

    code: str
    name: str
    category: Literal["governance_gap", "anti_pattern"]
    severity: Literal["CRITICAL", "HIGH", "MEDIUM"]
    description: str
    risk_impact: str
    detection_criteria: str
    remediation: str
    evidence_source: str  # Source file where pattern was found

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "code": self.code,
            "name": self.name,
            "category": self.category,
            "severity": self.severity,
            "description": self.description,
            "risk_impact": self.risk_impact,
            "detection_criteria": self.detection_criteria,
            "remediation": self.remediation,
            "evidence_source": self.evidence_source,
        }


# ============================================================================
# Anti-Pattern Library (Fixed 4 patterns)
# ============================================================================
ANTI_PATTERN_LIBRARY: list[AntiPattern] = [
    AntiPattern(
        code=PatternCode.E501_EXTERNAL_WITHOUT_STOP_RULE,
        name="External Action Without Stop Rule",
        category="governance_gap",
        severity="CRITICAL",
        description="External action (HTTP request, file write, subprocess) executed without "
                    "preceding governance stop rule (permission check, authorization, permit validation)",
        risk_impact="External actions can bypass governance controls, leading to unauthorized "
                    "system modifications, data exfiltration, or resource consumption",
        detection_criteria="Function containing external action keywords (requests., subprocess., "
                          "open(.*w) without preceding stop rule patterns "
                          "(@require_permission, @check_authorization, if not.*permission, validate_permission)",
        remediation="Add stop rule before external action: "
                  "@require_permission decorator or explicit permission check",
        evidence_source="run/T5_evidence/pattern_samples/e501_external_without_stop_rule/skill.py",
    ),
    AntiPattern(
        code=PatternCode.E502_RETRY_WITHOUT_IDEMPOTENCY,
        name="Retry Without Idempotency Protection",
        category="anti_pattern",
        severity="HIGH",
        description="Retry loop detected without idempotency protection mechanism "
                    "(idempotency key, deduplication check, transaction guard)",
        risk_impact="Retry without idempotency can cause duplicate operations, "
                    "double-charging, data corruption, or inconsistent state",
        detection_criteria="Loop or function with 'retry' in name containing external action "
                          "without idempotency patterns (idempotency_key, dedup, is_duplicate, already_processed)",
        remediation="Add idempotency key check before executing operation in retry loop",
        evidence_source="run/T5_evidence/pattern_samples/e502_retry_without_idempotency/skill.py",
    ),
    AntiPattern(
        code=PatternCode.E503_HIGH_PRIV_WITHOUT_BOUNDARY,
        name="High-Privilege Call Without Boundary",
        category="governance_gap",
        severity="CRITICAL",
        description="High-privilege operation (file delete, database write, system command) "
                    "executed without boundary limits (rate limit, resource cap, scope restriction)",
        risk_impact="Unbounded high-privilege operations can cause resource exhaustion, "
                    "system instability, or unlimited data modification",
        detection_criteria="High-privilege function call (os.remove, db.execute/write, subprocess.run) "
                          "without boundary patterns (rate_limit, max_count, resource_limit, check_quota)",
        remediation="Add boundary limits: rate limiter, resource cap, or scope restriction",
        evidence_source="run/T5_evidence/pattern_samples/e503_high_priv_without_boundary/skill.py",
    ),
    AntiPattern(
        code=PatternCode.E504_MISSING_AUDITABLE_EXIT,
        name="Missing Auditable Exit",
        category="governance_gap",
        severity="HIGH",
        description="Function performing sensitive action without writing auditable exit record "
                    "(audit log, evidence file, gate decision record)",
        risk_impact="Missing audit trail prevents post-mortem analysis, "
                    "compliance verification, and incident investigation",
        detection_criteria="Function with sensitive keywords (delete, execute, approve, transfer) "
                          "without audit patterns (write_audit, log_event, save_evidence, capture_gate_event)",
        remediation="Add audit event writing before returning from sensitive operation",
        evidence_source="run/T5_evidence/pattern_samples/e504_missing_auditable_exit/skill.py",
    ),
]


def get_pattern_by_code(code: str) -> Optional[AntiPattern]:
    """Get pattern definition by code."""
    for pattern in ANTI_PATTERN_LIBRARY:
        if pattern.code == code:
            return pattern
    return None


# ============================================================================
# Pattern Match
# ============================================================================
@dataclass(frozen=True)
class PatternMatch:
    """A single pattern match found during analysis."""

    pattern_code: str
    pattern_name: str
    file_path: str  # Relative path from skill_dir
    line_number: int
    function_name: str
    category: str
    severity: str
    message: str
    snippet: str  # The matching code line
    context_lines: list[str]  # Surrounding lines for context
    suggested_fix: str
    evidence_source: str  # Original source file where pattern was defined

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "pattern_code": self.pattern_code,
            "pattern_name": self.pattern_name,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "function_name": self.function_name,
            "category": self.category,
            "severity": self.severity,
            "message": self.message,
            "snippet": self.snippet,
            "context_lines": self.context_lines,
            "suggested_fix": self.suggested_fix,
            "evidence_source": self.evidence_source,
        }


# ============================================================================
# Governance Gap Finding
# ============================================================================
@dataclass(frozen=True)
class GovernanceGap:
    """A governance gap found during analysis."""

    gap_code: str
    gap_name: str
    file_path: str
    line_number: int
    function_name: str
    description: str
    severity: str
    missing_control: str
    recommended_control: str
    snippet: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "gap_code": self.gap_code,
            "gap_name": self.gap_name,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "function_name": self.function_name,
            "description": self.description,
            "severity": self.severity,
            "missing_control": self.missing_control,
            "recommended_control": self.recommended_control,
            "snippet": self.snippet,
        }


# ============================================================================
# Pattern Match Result
# ============================================================================
@dataclass
class PatternMatchResult:
    """Result of pattern matching on a skill."""

    skill_name: str
    skill_dir: str
    analyzed_at: str
    pattern_set_version: str

    # Analysis statistics
    files_analyzed: int
    functions_analyzed: int

    # Pattern matches
    critical_matches: list[PatternMatch] = field(default_factory=list)
    high_matches: list[PatternMatch] = field(default_factory=list)
    medium_matches: list[PatternMatch] = field(default_factory=list)

    # Governance gaps
    governance_gaps: list[GovernanceGap] = field(default_factory=list)

    # Summary
    total_matches: int = 0
    by_pattern: dict[str, int] = field(default_factory=dict)
    by_category: dict[str, int] = field(default_factory=dict)

    def add_match(self, match: PatternMatch) -> None:
        """Add a pattern match to the appropriate severity bucket."""
        if match.severity == "CRITICAL":
            self.critical_matches.append(match)
        elif match.severity == "HIGH":
            self.high_matches.append(match)
        else:
            self.medium_matches.append(match)

        self.total_matches += 1

        # Update by_pattern
        if match.pattern_code not in self.by_pattern:
            self.by_pattern[match.pattern_code] = 0
        self.by_pattern[match.pattern_code] += 1

        # Update by_category
        if match.category not in self.by_category:
            self.by_category[match.category] = 0
        self.by_category[match.category] += 1

    def add_governance_gap(self, gap: GovernanceGap) -> None:
        """Add a governance gap finding."""
        self.governance_gaps.append(gap)

    def get_all_matches(self) -> list[PatternMatch]:
        """Get all matches sorted by severity and line number."""
        all_matches = []
        all_matches.extend(self.critical_matches)
        all_matches.extend(self.high_matches)
        all_matches.extend(self.medium_matches)
        return sorted(all_matches, key=lambda m: (m.severity, m.line_number))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "skill_name": self.skill_name,
            "skill_dir": self.skill_dir,
            "analyzed_at": self.analyzed_at,
            "pattern_set_version": self.pattern_set_version,
            "analysis_statistics": {
                "files_analyzed": self.files_analyzed,
                "functions_analyzed": self.functions_analyzed,
                "total_matches": self.total_matches,
                "by_pattern": self.by_pattern,
                "by_category": self.by_category,
            },
            "pattern_matches": {
                "critical": [m.to_dict() for m in self.critical_matches],
                "high": [m.to_dict() for m in self.high_matches],
                "medium": [m.to_dict() for m in self.medium_matches],
            },
            "governance_gaps": [g.to_dict() for g in self.governance_gaps],
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def save(self, output_path: str | Path) -> None:
        """Save the pattern detection report to a JSON file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(self.to_json())


# ============================================================================
# Pattern Matcher - Main Detection Engine
# ============================================================================
class PatternMatcher:
    """
    Pattern matcher for detecting anti-patterns and governance gaps.

    T5 Scope:
    - External action without stop rule (E501)
    - Retry without idempotency protection (E502)
    - High-privilege call without boundary (E503)
    - Missing auditable exit (E504)

    T5 Hard Constraints:
    - Only 4 fixed patterns
    - No fabricating findings
    - All patterns must have source evidence
    """

    # Stop rule patterns (governance checks)
    STOP_RULE_PATTERNS = [
        r"@require_permission",
        r"@check_authorization",
        r"if\s+not\s+.*permission",
        r"if\s+not\s+.*authorized",
        r"validate_permission",
        r"check_access",
        r"permit\.",
        r"has_permission",
    ]

    # Idempotency protection patterns
    IDEMPOTENCY_PATTERNS = [
        r"idempotency_key",
        r"dedup",
        r"is_duplicate",
        r"already_processed",
        r"seen_keys",
        r"transaction_guard",
        r"prevent_duplicate",
    ]

    # Boundary limit patterns
    BOUNDARY_PATTERNS = [
        r"rate_limit",
        r"max_count",
        r"resource_limit",
        r"check_quota",
        r"throttle",
        r"circuit_breaker",
        r"semaphore",
    ]

    # Audit exit patterns
    AUDIT_PATTERNS = [
        r"write_audit",
        r"log_event",
        r"save_evidence",
        r"capture_gate_event",
        r"audit_log",
        r"record_decision",
        r"emit_audit",
    ]

    # External action patterns
    EXTERNAL_ACTION_PATTERNS = [
        r"requests\.(get|post|put|delete|patch)",
        r"subprocess\.",
        r"os\.system",
        r"open\(.*[\"']w[\"']",
        r"Path\(.*write",
    ]

    # High-privilege patterns
    HIGH_PRIV_PATTERNS = [
        r"os\.remove",
        r"os\.unlink",
        r"shutil\.rmtree",
        r"\.execute\(",
        r"\.execute\(.*\b(WRITE|DELETE|DROP|ALTER)",
        r"\.write\(",
        r"\.delete\(",
        r"subprocess\.run",
        r"Popen\(",
    ]

    # Sensitive operation patterns
    SENSITIVE_OPERATION_PATTERNS = [
        r"\.delete\(",
        r"\.remove\(",
        r"\.execute\(",
        r"\.transfer\(",
        r"\.approve\(",
    ]

    # Retry patterns
    RETRY_PATTERNS = [
        r"for\s+.*\s+in\s+range\(?.*retry",
        r"while\s+.*retry",
        r"def\s+.*retry",
    ]

    def __init__(self):
        """Initialize the pattern matcher."""
        self.patterns = {p.code: p for p in ANTI_PATTERN_LIBRARY}

    def match_patterns(self, skill_dir: str | Path) -> PatternMatchResult:
        """
        Match patterns in a skill directory.

        Args:
            skill_dir: Path to skill directory (e.g., "skillforge/src/skills/quant/")

        Returns:
            PatternMatchResult with all detected pattern matches.
        """
        skill_dir = Path(skill_dir).resolve()
        skill_name = skill_dir.name

        result = PatternMatchResult(
            skill_name=skill_name,
            skill_dir=str(skill_dir),
            analyzed_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            pattern_set_version=PATTERN_SET_VERSION,
            files_analyzed=0,
            functions_analyzed=0,
        )

        # Find all Python files in skill directory
        python_files = list(skill_dir.rglob("*.py"))

        for file_path in python_files:
            self._analyze_file(file_path, skill_dir, result)

        return result

    def _analyze_file(self, file_path: Path, skill_dir: Path, result: PatternMatchResult) -> None:
        """Analyze a single file for pattern matches."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.splitlines()
        except OSError:
            return

        result.files_analyzed += 1
        rel_path = str(file_path.relative_to(skill_dir))

        try:
            tree = ast.parse(content)
            analyzer = PatternAnalyzer(lines, rel_path, self)
            analyzer.visit(tree)
            result.functions_analyzed += analyzer.function_count

            for match in analyzer.matches:
                result.add_match(match)

            for gap in analyzer.gaps:
                result.add_governance_gap(gap)

        except SyntaxError:
            # Skip files with syntax errors
            pass


# ============================================================================
# AST Analyzer for Pattern Detection
# ============================================================================
class PatternAnalyzer(ast.NodeVisitor):
    """AST visitor for pattern detection."""

    def __init__(self, lines: list[str], file_path: str, matcher: PatternMatcher):
        self.lines = lines
        self.file_path = file_path
        self.matcher = matcher
        self.matches: list[PatternMatch] = []
        self.gaps: list[GovernanceGap] = []
        self.function_count = 0
        self.current_function: Optional[ast.FunctionDef] = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Analyze a function definition."""
        self.function_count += 1
        self.current_function = node

        # Get function content lines
        start_line = node.lineno - 1
        end_line = node.end_lineno if node.end_lineno else start_line + 1
        func_lines = self.lines[start_line:end_line]

        # Check for each pattern
        self._check_e501_external_without_stop(node, func_lines)
        self._check_e502_retry_without_idempotency(node, func_lines)
        self._check_e503_high_priv_without_boundary(node, func_lines)
        self._check_e504_missing_auditable_exit(node, func_lines)

        # Visit nested functions
        self.generic_visit(node)
        self.current_function = None

    def _get_context_lines(self, line_number: int, context_size: int = 3) -> list[str]:
        """Get surrounding lines for context."""
        start = max(0, line_number - context_size - 1)
        end = min(len(self.lines), line_number + context_size)
        return self.lines[start:end]

    def _extract_code_without_comments(self, node: ast.FunctionDef) -> list[str]:
        """
        Extract actual code lines from function, excluding comments and docstrings.

        Uses AST to find actual statement nodes, excluding:
        - Comments (not represented in AST)
        - Docstrings (first expression if it's a string constant)
        """
        code_lines = []

        # Get the function body nodes
        for child in node.body:
            # Skip docstrings (first Expr node with a Str/Constant)
            if isinstance(child, ast.Expr):
                if isinstance(child.value, (ast.Str, ast.Constant)):
                    if isinstance(child.value, ast.Constant) and isinstance(child.value.value, str):
                        # This is likely a docstring
                        if child == node.body[0] and child.lineno == node.lineno + 1:
                            continue
                    elif isinstance(child.value, ast.Str):
                        if child == node.body[0]:
                            continue

            # Get the line range for this statement
            start = child.lineno - 1
            end = child.end_lineno - 1 if child.end_lineno else start

            # Add lines from this statement
            for line_no in range(start, end + 1):
                if 0 <= line_no < len(self.lines):
                    line = self.lines[line_no].strip()
                    # Skip empty lines and comment-only lines
                    if line and not line.startswith("#"):
                        code_lines.append(line)

        return code_lines

    def _has_function_call(self, node: ast.FunctionDef, call_patterns: list[str]) -> bool:
        """
        Check if function contains specific call patterns using AST only.

        This excludes comments and docstrings by only looking at actual Call nodes.
        Uses substring matching for pattern matching (not full regex).
        """
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                # Get the full function call name
                func_name = self._get_full_call_name(child.func)
                if func_name:
                    for pattern in call_patterns:
                        # Use simple substring matching (pattern is already a clean string like "requests.get")
                        if pattern.lower() in func_name.lower():
                            return True

        return False

    def _get_full_call_name(self, func_node: ast.expr) -> str:
        """Extract full call name from AST node (e.g., 'requests.get')."""
        parts = []
        current = func_node

        while current:
            if isinstance(current, ast.Name):
                parts.append(current.id)
                break
            elif isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            else:
                # For more complex expressions, return empty string
                break

        if parts:
            parts.reverse()
            return ".".join(parts)
        return ""

    def _check_e501_external_without_stop(self, node: ast.FunctionDef, func_lines: list[str]) -> None:
        """
        Check for E501: External action without stop rule.

        Uses AST to detect external action calls (requests, subprocess, etc.)
        and stop rules in decorators or function calls.
        """
        func_name = node.name

        # Check if function contains external action using AST
        external_call_patterns = ["requests.get", "requests.post", "requests.put", "requests.delete",
                                   "requests.patch", "subprocess.call", "subprocess.run", "subprocess.Popen",
                                   "os.system", "os.remove", "os.unlink", "open"]
        has_external = self._has_function_call(node, external_call_patterns)

        if not has_external:
            return

        # Check decorators first (decorator_list comes before function body)
        has_stop_rule = False

        # Check decorators for stop rule patterns
        if node.decorator_list:
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Call):
                    if isinstance(decorator.func, ast.Name):
                        decorator_name = decorator.func.id
                    elif isinstance(decorator.func, ast.Attribute):
                        decorator_name = decorator.func.attr
                    else:
                        continue
                elif isinstance(decorator, ast.Name):
                    decorator_name = decorator.id
                elif isinstance(decorator, ast.Attribute):
                    decorator_name = decorator.attr
                else:
                    continue

                # Check if decorator name contains stop rule keywords
                if any(keyword in decorator_name.lower() for keyword in ["permission", "authorization", "permit", "check_access"]):
                    has_stop_rule = True
                    break

        # If not found in decorators, check function body for stop rule calls using AST
        if not has_stop_rule:
            stop_rule_patterns = ["validate_permission", "check_authorization", "has_permission",
                                  "require_permission", "check_access"]
            has_stop_rule = self._has_function_call(node, stop_rule_patterns)

        if not has_stop_rule:
            # No stop rule found - report the finding
            pattern = get_pattern_by_code(PatternCode.E501_EXTERNAL_WITHOUT_STOP_RULE)
            if pattern:
                match = PatternMatch(
                    pattern_code=pattern.code,
                    pattern_name=pattern.name,
                    file_path=self.file_path,
                    line_number=node.lineno,
                    function_name=func_name,
                    category=pattern.category,
                    severity=pattern.severity,
                    message=pattern.description,
                    snippet=func_lines[0].strip() if func_lines else "",
                    context_lines=self._get_context_lines(node.lineno),
                    suggested_fix=pattern.remediation,
                    evidence_source=pattern.evidence_source,
                )
                self.matches.append(match)

    def _check_e502_retry_without_idempotency(self, node: ast.FunctionDef, func_lines: list[str]) -> None:
        """
        Check for E502: Retry without idempotency protection.

        Uses AST to detect retry loops and idempotency protection.
        Excludes comments from detection.
        """
        func_name = node.name

        # Check if function name contains "retry"
        is_retry_function = "retry" in func_name.lower()

        # Also check for retry loop patterns in function body (for/while with retry logic)
        has_retry_loop = False
        for child in node.body:
            if isinstance(child, (ast.For, ast.While)):
                has_retry_loop = True
                break

        if not (is_retry_function or has_retry_loop):
            return

        # Check for external action in retry function using AST
        external_call_patterns = ["requests.get", "requests.post", "requests.put", "requests.delete",
                                   "requests.patch", "subprocess.call", "subprocess.run", "subprocess.Popen",
                                   "os.system"]
        has_external = self._has_function_call(node, external_call_patterns)

        if not has_external:
            return

        # Check for idempotency protection using AST (not text regex)
        # Need to check if idempotency check happens BEFORE the external action
        idempotency_patterns = ["idempotency_key", "dedup", "is_duplicate", "already_processed",
                                 "seen_keys", "transaction_guard", "prevent_duplicate"]

        # Look for idempotency checks in if statements or comparisons
        has_idempotency_check = False
        for child in ast.walk(node):
            if isinstance(child, ast.If):
                # Check if the test condition uses idempotency
                test_str = ast.unparse(child.test) if hasattr(ast, 'unparse') else ""
                for pattern in idempotency_patterns:
                    if pattern in test_str.lower():
                        has_idempotency_check = True
                        break
            if has_idempotency_check:
                break

        if not has_idempotency_check:
            pattern = get_pattern_by_code(PatternCode.E502_RETRY_WITHOUT_IDEMPOTENCY)
            if pattern:
                match = PatternMatch(
                    pattern_code=pattern.code,
                    pattern_name=pattern.name,
                    file_path=self.file_path,
                    line_number=node.lineno,
                    function_name=func_name,
                    category=pattern.category,
                    severity=pattern.severity,
                    message=pattern.description,
                    snippet=func_lines[0].strip() if func_lines else "",
                    context_lines=self._get_context_lines(node.lineno),
                    suggested_fix=pattern.remediation,
                    evidence_source=pattern.evidence_source,
                )
                self.matches.append(match)

    def _check_e503_high_priv_without_boundary(self, node: ast.FunctionDef, func_lines: list[str]) -> None:
        """
        Check for E503: High-privilege call without boundary.

        Uses AST to detect high-privilege operations and boundary limits.
        Excludes comments from detection.
        """
        func_name = node.name

        # Check if function contains high-privilege operation using AST
        high_priv_patterns = ["os.remove", "os.unlink", "shutil.rmtree", "execute",
                               "write", "delete", "subprocess.run", "Popen"]
        has_high_priv = self._has_function_call(node, high_priv_patterns)

        if not has_high_priv:
            return

        # Check for boundary limits using AST (not text regex)
        boundary_patterns = ["rate_limit", "max_count", "resource_limit", "check_quota",
                              "throttle", "circuit_breaker", "semaphore", "limit"]
        has_boundary = self._has_function_call(node, boundary_patterns)

        if not has_boundary:
            pattern = get_pattern_by_code(PatternCode.E503_HIGH_PRIV_WITHOUT_BOUNDARY)
            if pattern:
                match = PatternMatch(
                    pattern_code=pattern.code,
                    pattern_name=pattern.name,
                    file_path=self.file_path,
                    line_number=node.lineno,
                    function_name=func_name,
                    category=pattern.category,
                    severity=pattern.severity,
                    message=pattern.description,
                    snippet=func_lines[0].strip() if func_lines else "",
                    context_lines=self._get_context_lines(node.lineno),
                    suggested_fix=pattern.remediation,
                    evidence_source=pattern.evidence_source,
                )
                self.matches.append(match)

    def _check_e504_missing_auditable_exit(self, node: ast.FunctionDef, func_lines: list[str]) -> None:
        """
        Check for E504: Missing auditable exit.

        Uses AST to check for actual audit function calls, not comments.
        This prevents false positives when comments mention audit functions.
        """
        func_name = node.name

        # Check if function performs sensitive operation (by function name keywords)
        sensitive_keywords = ["delete", "execute", "approve", "transfer", "write"]
        has_sensitive_keyword = any(keyword in func_name.lower() for keyword in sensitive_keywords)

        if not has_sensitive_keyword:
            return

        # Check for audit exit using AST (not text regex)
        # This prevents matching comments like "# Missing: write_audit_event"
        audit_call_patterns = ["write_audit", "log_event", "save_evidence", "capture_gate_event",
                               "audit_log", "record_decision", "emit_audit", "write_audit_log"]
        has_audit = self._has_function_call(node, audit_call_patterns)

        if not has_audit:
            pattern = get_pattern_by_code(PatternCode.E504_MISSING_AUDITABLE_EXIT)
            if pattern:
                match = PatternMatch(
                    pattern_code=pattern.code,
                    pattern_name=pattern.name,
                    file_path=self.file_path,
                    line_number=node.lineno,
                    function_name=func_name,
                    category=pattern.category,
                    severity=pattern.severity,
                    message=pattern.description,
                    snippet=func_lines[0].strip() if func_lines else "",
                    context_lines=self._get_context_lines(node.lineno),
                    suggested_fix=pattern.remediation,
                    evidence_source=pattern.evidence_source,
                )
                self.matches.append(match)


# ============================================================================
# Governance Gap Detector
# ============================================================================
class GovernanceGapDetector:
    """
    Detector for governance gaps in skill code.

    Scans for:
    - Missing stop rules before external actions
    - Missing permission checks before sensitive operations
    - Missing audit logging for sensitive operations
    """

    def __init__(self):
        """Initialize the governance gap detector."""
        self.stop_rule_patterns = PatternMatcher.STOP_RULE_PATTERNS
        self.audit_patterns = PatternMatcher.AUDIT_PATTERNS

    def detect_gaps(self, skill_dir: str | Path) -> list[GovernanceGap]:
        """
        Detect governance gaps in a skill directory.

        Args:
            skill_dir: Path to skill directory

        Returns:
            List of governance gap findings
        """
        skill_dir = Path(skill_dir).resolve()
        gaps = []

        python_files = list(skill_dir.rglob("*.py"))

        for file_path in python_files:
            gaps.extend(self._check_file_gaps(file_path, skill_dir))

        return gaps

    def _check_file_gaps(self, file_path: Path, skill_dir: Path) -> list[GovernanceGap]:
        """Check a single file for governance gaps."""
        gaps = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.splitlines()
        except OSError:
            return gaps

        rel_path = str(file_path.relative_to(skill_dir))

        # Check for external actions without preceding stop rule
        for i, line in enumerate(lines):
            if any(re.search(pattern, line, re.IGNORECASE) for pattern in PatternMatcher.EXTERNAL_ACTION_PATTERNS):
                # Look backwards for stop rule
                has_stop_rule = False
                for prev_line in lines[max(0, i - 5):i]:
                    if any(re.search(pattern, prev_line, re.IGNORECASE) for pattern in self.stop_rule_patterns):
                        has_stop_rule = True
                        break

                if not has_stop_rule:
                    gaps.append(GovernanceGap(
                        gap_code=PatternCode.E501_EXTERNAL_WITHOUT_STOP_RULE,
                        gap_name="External Action Without Stop Rule",
                        file_path=rel_path,
                        line_number=i + 1,
                        function_name="<module>",
                        description="External action without preceding governance stop rule",
                        severity="CRITICAL",
                        missing_control="Permission check or authorization",
                        recommended_control="Add @require_permission or explicit permission check",
                        snippet=line.strip(),
                    ))

        return gaps


# ============================================================================
# CLI Entry Point
# ============================================================================
def main():
    """CLI entry point for pattern matching."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Match patterns in skill directory"
    )
    parser.add_argument(
        "skill_dir",
        help="Path to skill directory (e.g., skillforge/src/skills/quant/)",
    )
    parser.add_argument(
        "--output",
        default="run/T5_evidence/pattern_detection_report.json",
        help="Output path for pattern_detection_report.json",
    )
    args = parser.parse_args()

    # Match patterns
    matcher = PatternMatcher()
    result = matcher.match_patterns(args.skill_dir)

    # Also detect governance gaps
    gap_detector = GovernanceGapDetector()
    gaps = gap_detector.detect_gaps(args.skill_dir)
    for gap in gaps:
        result.add_governance_gap(gap)

    # Save report
    result.save(args.output)

    # Print summary
    print(f"Pattern Detection Report saved to: {args.output}")
    print(f"  Files Analyzed: {result.files_analyzed}")
    print(f"  Functions Analyzed: {result.functions_analyzed}")
    print(f"  Total Matches: {result.total_matches}")
    print(f"  By Severity:")
    for severity in ["CRITICAL", "HIGH", "MEDIUM"]:
        count = len(getattr(result, f"{severity.lower()}_matches"))
        if count > 0:
            print(f"    {severity}: {count}")
    print(f"  Governance Gaps: {len(result.governance_gaps)}")


if __name__ == "__main__":
    main()
