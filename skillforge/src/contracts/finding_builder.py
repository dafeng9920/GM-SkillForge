"""
Finding Builder - T6 Deliverable

This module provides unified Finding structure for consolidating validation/rule/pattern results.
It converts heterogeneous findings from T3 (ValidationFailure), T4 (RuleHit), and T5 (PatternMatch)
into a consistent Finding format with evidence refs binding.

T6 Scope:
- Unified Finding schema
- Severity initial assignment
- Confidence initial assignment
- Evidence refs binding
- Finding ID generation

T6 Hard Constraints:
- No adjudication logic
- No bare findings without evidence
- Every finding must have source traceability
- EvidenceRef is mandatory

Usage:
    from skillforge.src.contracts.finding_builder import FindingBuilder, Finding, FindingSource
    from skillforge.src.contracts.skill_contract_validator import ValidationResult
    from skillforge.src.contracts.rule_scanner import RuleScanResult
    from skillforge.src.contracts.pattern_matcher import PatternMatchResult

    builder = FindingBuilder()

    # Convert T3 validation result
    for failure in validation_result.failures:
        finding = builder.from_validation_failure(failure, skill_id)
        findings.append(finding)

    # Convert T4 rule scan result
    for hit in rule_result.get_all_hits():
        finding = builder.from_rule_hit(hit, skill_id)
        findings.append(finding)

    # Convert T5 pattern match result
    for match in pattern_result.get_all_matches():
        finding = builder.from_pattern_match(match, skill_id)
        findings.append(finding)

    # Build findings.json
    findings_report = builder.build_findings_report(skill_id, findings)
    findings_report.save("run/T6_evidence/findings.json")
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Literal, Optional


# ============================================================================
# Finding Source Type (T6)
# ============================================================================
class FindingSourceType(Enum):
    """Source of the finding - which task detected it."""
    VALIDATION = "validation"  # T3: ValidationFailure
    RULE_SCAN = "rule_scan"    # T4: RuleHit
    PATTERN_MATCH = "pattern_match"  # T5: PatternMatch


# ============================================================================
# Finding Category (Unified)
# ============================================================================
class FindingCategory(Enum):
    """Unified finding categories across T3/T4/T5."""
    # T3 categories
    SCHEMA_VALIDATION = "schema_validation"
    CONTRACT_VALIDATION = "contract_validation"
    CONSISTENCY_CHECK = "consistency_check"

    # T4 categories
    SENSITIVE_PERMISSION = "sensitive_permission"
    EXTERNAL_ACTION = "external_action"
    DANGEROUS_PATTERN = "dangerous_pattern"
    BOUNDARY_GAP = "boundary_gap"

    # T5 categories
    GOVERNANCE_GAP = "governance_gap"
    ANTI_PATTERN = "anti_pattern"


# ============================================================================
# Severity Levels (Unified)
# ============================================================================
class FindingSeverity(Enum):
    """Unified severity levels across T3/T4/T5."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"  # For informational findings


# ============================================================================
# Evidence Reference (Mandatory)
# ============================================================================
@dataclass(frozen=True)
class EvidenceRef:
    """
    Reference to evidence that supports this finding.

    T6 Hard Constraint: Every finding MUST have at least one EvidenceRef.
    """
    kind: Literal["FILE", "LOG", "DIFF", "SNIPPET", "URL", "CODE_LOCATION"]
    locator: str  # Path or URL to evidence (e.g., "skill.py:42" or "run/T3_evidence/validation_report.json")
    note: Optional[str] = None  # Additional context

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "locator": self.locator,
            "note": self.note,
        }


# ============================================================================
# Finding ID Generator
# ============================================================================
def generate_finding_id(
    source_type: FindingSourceType,
    code: str,
    file_path: str,
    line_number: Optional[int],
) -> str:
    """
    Generate a deterministic finding ID.

    Format: F-{source_type}-{code}-{hash}
    Example: F-validation-E302_SCHEMA_VALIDATION_FAILED-a1b2c3d4

    The hash is derived from: code + file_path + line_number
    This ensures same finding in same location has same ID.
    """
    # Create hash input
    hash_input = f"{code}:{file_path}:{line_number or 0}"
    hash_suffix = hashlib.sha256(hash_input.encode()).hexdigest()[:8]

    # Shorten code for ID (take first part before underscore)
    code_short = code.split("_")[0] if "_" in code else code

    return f"F-{source_type.value}-{code_short}-{hash_suffix}"


# ============================================================================
# Unified Finding
# ============================================================================
@dataclass(frozen=True)
class Finding:
    """
    Unified Finding structure for T3/T4/T5 results.

    T6 Hard Constraints:
    - finding_id: Must be deterministic and unique
    - source_type: Must trace back to T3/T4/T5
    - source_code: Original error/rule/pattern code
    - evidence_refs: Must have at least one reference
    """
    # Core identification
    finding_id: str
    source_type: FindingSourceType
    source_code: str  # Original code (E3xx, E4xx, E5xx)

    # What was found
    title: str  # Short human-readable title
    description: str  # Detailed description
    category: FindingCategory
    severity: FindingSeverity
    confidence: float  # 0.0 to 1.0, initial assignment

    # Where it was found
    file_path: str  # Relative path from skill root
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    function_name: Optional[str] = None  # For T5 pattern matches

    # Code context
    snippet: Optional[str] = None  # Relevant code line
    context_lines: Optional[list[str]] = None  # Surrounding context (T5)

    # Fix information
    suggested_fix: Optional[str] = None
    remediation: Optional[str] = None  # More detailed remediation steps

    # Additional context (T3/T4/T5 specific)
    field_path: Optional[str] = None  # For T3: JSON path
    actual_value: Optional[str] = None  # For T3
    expected_value: Optional[str] = None  # For T3
    missing_control: Optional[str] = None  # For T5 governance gaps
    recommended_control: Optional[str] = None  # For T5 governance gaps
    cwe_id: Optional[str] = None  # For T4 security rules
    owasp_id: Optional[str] = None  # For T4 security rules

    # Evidence (T6 Hard Constraint: Mandatory)
    evidence_refs: list[EvidenceRef] = field(default_factory=list)

    # Timestamp
    detected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "finding_id": self.finding_id,
            "source": {
                "type": self.source_type.value,
                "code": self.source_code,
            },
            "what": {
                "title": self.title,
                "description": self.description,
                "category": self.category.value,
                "severity": self.severity.value,
                "confidence": self.confidence,
            },
            "where": {
                "file_path": self.file_path,
                "line_number": self.line_number,
                "column_number": self.column_number,
                "function_name": self.function_name,
            },
            "context": {
                "snippet": self.snippet,
                "context_lines": self.context_lines,
                "field_path": self.field_path,
                "actual_value": self.actual_value,
                "expected_value": self.expected_value,
            },
            "fix": {
                "suggested_fix": self.suggested_fix,
                "remediation": self.remediation,
            },
            "security": {
                "cwe_id": self.cwe_id,
                "owasp_id": self.owasp_id,
            },
            "governance": {
                "missing_control": self.missing_control,
                "recommended_control": self.recommended_control,
            },
            "evidence_refs": [e.to_dict() for e in self.evidence_refs],
            "detected_at": self.detected_at,
        }


# ============================================================================
# Severity Initial Assignment
# ============================================================================
def assign_initial_severity(
    source_type: FindingSourceType,
    original_severity: Optional[str],
) -> FindingSeverity:
    """
    Assign initial FindingSeverity from source.

    T6 Scope: Initial assignment only, no re-ranking or adjudication.
    """
    if original_severity:
        try:
            return FindingSeverity(original_severity)
        except ValueError:
            pass

    # Default mapping by source type
    if source_type == FindingSourceType.VALIDATION:
        # T3: ERROR -> HIGH, WARNING -> INFO
        if original_severity == "ERROR":
            return FindingSeverity.HIGH
        return FindingSeverity.INFO

    elif source_type == FindingSourceType.RULE_SCAN:
        # T4: Trust the rule's severity
        return FindingSeverity.HIGH  # Default if unknown

    elif source_type == FindingSourceType.PATTERN_MATCH:
        # T5: Trust the pattern's severity
        return FindingSeverity.HIGH  # Default if unknown

    return FindingSeverity.MEDIUM


# ============================================================================
# Confidence Initial Assignment
# ============================================================================
def assign_initial_confidence(
    source_type: FindingSourceType,
    source_code: str,
) -> float:
    """
    Assign initial confidence score (0.0 to 1.0).

    T6 Scope: Initial assignment based on detection method, not adjudication.
    """
    # T3: Schema validation has highest confidence (deterministic)
    if source_type == FindingSourceType.VALIDATION:
        if source_code.startswith("E30"):  # Schema validation
            return 1.0
        elif source_code.startswith("E31"):  # Contract validation
            return 0.95
        elif source_code.startswith("E32"):  # Consistency check
            return 0.95
        return 0.9

    # T4: Rule scanning has high confidence (static analysis)
    elif source_type == FindingSourceType.RULE_SCAN:
        if source_code.startswith("E42"):  # Dangerous patterns (eval, etc.)
            return 1.0  # Certain detection
        elif source_code.startswith("E41"):  # External actions
            return 0.95
        return 0.9  # General rules

    # T5: Pattern matching has moderate confidence (AST-based)
    elif source_type == FindingSourceType.PATTERN_MATCH:
        return 0.85  # AST-based detection is reliable

    return 0.8  # Default


# ============================================================================
# Finding Builder
# ============================================================================
class FindingBuilder:
    """
    Builder for converting T3/T4/T5 results to unified Findings.

    T6 Deliverable: Unified Finding structure with evidence binding.
    """

    def __init__(self, run_id: Optional[str] = None):
        """
        Initialize FindingBuilder.

        Args:
            run_id: Optional run identifier for evidence paths
        """
        self.run_id = run_id or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    # ------------------------------------------------------------------------
    # Convert T3 ValidationFailure
    # ------------------------------------------------------------------------
    def from_validation_failure(
        self,
        failure: Any,  # ValidationFailure from T3
        skill_id: str,
        evidence_path: Optional[str] = None,
    ) -> Finding:
        """
        Convert T3 ValidationFailure to unified Finding.

        Evidence binding: Points to T3 validation report.
        """
        from skillforge.src.contracts.skill_contract_validator import ValidationErrorCode

        # Map T3 category
        category_map = {
            "E30": FindingCategory.SCHEMA_VALIDATION,
            "E31": FindingCategory.CONTRACT_VALIDATION,
            "E32": FindingCategory.CONSISTENCY_CHECK,
        }
        code_prefix = failure.code[:3]
        category = category_map.get(code_prefix, FindingCategory.SCHEMA_VALIDATION)

        # Severity mapping
        severity = assign_initial_severity(
            FindingSourceType.VALIDATION,
            failure.severity,
        )

        # Confidence
        confidence = assign_initial_confidence(FindingSourceType.VALIDATION, failure.code)

        # Generate ID
        finding_id = generate_finding_id(
            FindingSourceType.VALIDATION,
            failure.code,
            failure.field_path,
            None,  # No line number for T3
        )

        # Evidence refs
        evidence_refs = [
            EvidenceRef(
                kind="FILE",
                locator=evidence_path or f"run/{self.run_id}/validation_report.json",
                note="T3 validation report containing this failure",
            ),
            EvidenceRef(
                kind="CODE_LOCATION",
                locator=failure.field_path,
                note="JSON path to invalid field",
            ),
        ]

        return Finding(
            finding_id=finding_id,
            source_type=FindingSourceType.VALIDATION,
            source_code=failure.code,
            title=failure.code.replace("_", " ").title(),
            description=failure.message,
            category=category,
            severity=severity,
            confidence=confidence,
            file_path="<schema>",  # T3 is schema-level
            line_number=None,
            field_path=failure.field_path,
            suggested_fix=failure.suggested_fix,
            actual_value=failure.actual_value,
            expected_value=failure.expected_value,
            evidence_refs=evidence_refs,
        )

    # ------------------------------------------------------------------------
    # Convert T4 RuleHit
    # ------------------------------------------------------------------------
    def from_rule_hit(
        self,
        hit: Any,  # RuleHit from T4
        skill_id: str,
        evidence_path: Optional[str] = None,
        rule_set_version: str = "1.0.0-t4",
    ) -> Finding:
        """
        Convert T4 RuleHit to unified Finding.

        Evidence binding: Points to T4 rule scan report and source file.
        """
        # Map T4 category
        category_map = {
            "sensitive_permission": FindingCategory.SENSITIVE_PERMISSION,
            "external_action": FindingCategory.EXTERNAL_ACTION,
            "dangerous_pattern": FindingCategory.DANGEROUS_PATTERN,
            "boundary_gap": FindingCategory.BOUNDARY_GAP,
        }
        category = category_map.get(hit.category, FindingCategory.BOUNDARY_GAP)

        # Severity
        severity = assign_initial_severity(
            FindingSourceType.RULE_SCAN,
            hit.severity,
        )

        # Confidence
        confidence = assign_initial_confidence(FindingSourceType.RULE_SCAN, hit.rule_code)

        # Generate ID
        finding_id = generate_finding_id(
            FindingSourceType.RULE_SCAN,
            hit.rule_code,
            hit.file_path,
            hit.line_number,
        )

        # Evidence refs
        evidence_refs = [
            EvidenceRef(
                kind="FILE",
                locator=evidence_path or f"run/{self.run_id}/rule_scan_report.json",
                note=f"T4 rule scan report (rule set v{rule_set_version})",
            ),
            EvidenceRef(
                kind="CODE_LOCATION",
                locator=f"{hit.file_path}:{hit.line_number}:{hit.column_number}",
                note="Source location of rule violation",
            ),
        ]

        return Finding(
            finding_id=finding_id,
            source_type=FindingSourceType.RULE_SCAN,
            source_code=hit.rule_code,
            title=hit.rule_name,
            description=hit.message,
            category=category,
            severity=severity,
            confidence=confidence,
            file_path=hit.file_path,
            line_number=hit.line_number,
            column_number=hit.column_number,
            snippet=hit.snippet,
            suggested_fix=hit.suggested_fix,
            remediation=hit.suggested_fix,
            evidence_refs=evidence_refs,
        )

    # ------------------------------------------------------------------------
    # Convert T5 PatternMatch
    # ------------------------------------------------------------------------
    def from_pattern_match(
        self,
        match: Any,  # PatternMatch from T5
        skill_id: str,
        evidence_path: Optional[str] = None,
        pattern_set_version: str = "1.0.0-t5",
    ) -> Finding:
        """
        Convert T5 PatternMatch to unified Finding.

        Evidence binding: Points to T5 pattern report and evidence source file.
        """
        # Map T5 category
        category_map = {
            "governance_gap": FindingCategory.GOVERNANCE_GAP,
            "anti_pattern": FindingCategory.ANTI_PATTERN,
        }
        category = category_map.get(match.category, FindingCategory.GOVERNANCE_GAP)

        # Severity
        severity = assign_initial_severity(
            FindingSourceType.PATTERN_MATCH,
            match.severity,
        )

        # Confidence
        confidence = assign_initial_confidence(FindingSourceType.PATTERN_MATCH, match.pattern_code)

        # Generate ID
        finding_id = generate_finding_id(
            FindingSourceType.PATTERN_MATCH,
            match.pattern_code,
            match.file_path,
            match.line_number,
        )

        # Evidence refs
        evidence_refs = [
            EvidenceRef(
                kind="FILE",
                locator=evidence_path or f"run/{self.run_id}/pattern_detection_report.json",
                note=f"T5 pattern detection report (pattern set v{pattern_set_version})",
            ),
            EvidenceRef(
                kind="CODE_LOCATION",
                locator=f"{match.file_path}:{match.line_number}",
                note=f"Pattern detected in function: {match.function_name}",
            ),
        ]

        # Add evidence_source if available (T5 pattern definition source)
        if hasattr(match, 'evidence_source') and match.evidence_source:
            evidence_refs.append(
                EvidenceRef(
                    kind="FILE",
                    locator=match.evidence_source,
                    note="Pattern definition source (sample code where pattern was identified)",
                )
            )

        return Finding(
            finding_id=finding_id,
            source_type=FindingSourceType.PATTERN_MATCH,
            source_code=match.pattern_code,
            title=match.pattern_name,
            description=match.message,
            category=category,
            severity=severity,
            confidence=confidence,
            file_path=match.file_path,
            line_number=match.line_number,
            function_name=match.function_name,
            snippet=match.snippet,
            context_lines=match.context_lines,
            suggested_fix=match.suggested_fix,
            remediation=match.suggested_fix,
            evidence_refs=evidence_refs,
        )

    # ------------------------------------------------------------------------
    # Convert T5 GovernanceGap
    # ------------------------------------------------------------------------
    def from_governance_gap(
        self,
        gap: Any,  # GovernanceGap from T5
        skill_id: str,
        evidence_path: Optional[str] = None,
    ) -> Finding:
        """
        Convert T5 GovernanceGap to unified Finding.

        Evidence binding: Points to T5 pattern report.
        """
        # Severity
        severity = assign_initial_severity(
            FindingSourceType.PATTERN_MATCH,
            gap.severity,
        )

        # Confidence (governance gaps have slightly lower confidence)
        confidence = assign_initial_confidence(FindingSourceType.PATTERN_MATCH, gap.gap_code) * 0.95

        # Generate ID
        finding_id = generate_finding_id(
            FindingSourceType.PATTERN_MATCH,
            gap.gap_code,
            gap.file_path,
            gap.line_number,
        )

        # Evidence refs
        evidence_refs = [
            EvidenceRef(
                kind="FILE",
                locator=evidence_path or f"run/{self.run_id}/pattern_detection_report.json",
                note="T5 pattern detection report (governance_gaps section)",
            ),
            EvidenceRef(
                kind="CODE_LOCATION",
                locator=f"{gap.file_path}:{gap.line_number}",
                note=f"Governance gap in function: {gap.function_name}",
            ),
        ]

        return Finding(
            finding_id=finding_id,
            source_type=FindingSourceType.PATTERN_MATCH,
            source_code=gap.gap_code,
            title=gap.gap_name,
            description=gap.description,
            category=FindingCategory.GOVERNANCE_GAP,
            severity=severity,
            confidence=confidence,
            file_path=gap.file_path,
            line_number=gap.line_number,
            function_name=gap.function_name,
            snippet=gap.snippet,
            missing_control=gap.missing_control,
            recommended_control=gap.recommended_control,
            suggested_fix=gap.recommended_control,
            remediation=gap.recommended_control,
            evidence_refs=evidence_refs,
        )


# ============================================================================
# Findings Report
# ============================================================================
@dataclass
class FindingsReport:
    """
    Unified findings report containing all findings from T3/T4/T5.

    T6 Deliverable: Consolidated findings.json with evidence binding.
    """
    skill_id: str
    skill_name: str
    generated_at: str
    t6_version: str = "1.0.0-t6"
    run_id: str = ""

    # Input references (traceability)
    validation_report_path: Optional[str] = None
    rule_scan_report_path: Optional[str] = None
    pattern_detection_report_path: Optional[str] = None

    # Findings
    findings: list[Finding] = field(default_factory=list)

    # Summary statistics
    summary: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize summary on creation."""
        if not self.summary:
            self._update_summary()

    def add_finding(self, finding: Finding) -> None:
        """Add a finding to the report."""
        self.findings.append(finding)
        self._update_summary()

    def _update_summary(self) -> None:
        """Update summary statistics."""
        self.summary = {
            "total_findings": len(self.findings),
            "by_severity": self._count_by_severity(),
            "by_category": self._count_by_category(),
            "by_source": self._count_by_source(),
            "by_confidence": self._count_by_confidence(),
        }

    def _count_by_severity(self) -> dict[str, int]:
        counts = {s.value: 0 for s in FindingSeverity}
        for f in self.findings:
            counts[f.severity.value] += 1
        return counts

    def _count_by_category(self) -> dict[str, int]:
        counts = {}
        for f in self.findings:
            cat = f.category.value
            counts[cat] = counts.get(cat, 0) + 1
        return counts

    def _count_by_source(self) -> dict[str, int]:
        counts = {st.value: 0 for st in FindingSourceType}
        for f in self.findings:
            counts[f.source_type.value] += 1
        return counts

    def _count_by_confidence(self) -> dict[str, int]:
        """Count findings by confidence ranges."""
        counts = {
            "very_high (0.95-1.0)": 0,
            "high (0.85-0.95)": 0,
            "medium (0.70-0.85)": 0,
            "low (<0.70)": 0,
        }
        for f in self.findings:
            if f.confidence >= 0.95:
                counts["very_high (0.95-1.0)"] += 1
            elif f.confidence >= 0.85:
                counts["high (0.85-0.95)"] += 1
            elif f.confidence >= 0.70:
                counts["medium (0.70-0.85)"] += 1
            else:
                counts["low (<0.70)"] += 1
        return counts

    def get_findings_by_severity(self, severity: FindingSeverity) -> list[Finding]:
        """Get all findings of a specific severity."""
        return [f for f in self.findings if f.severity == severity]

    def get_findings_by_source(self, source: FindingSourceType) -> list[Finding]:
        """Get all findings from a specific source."""
        return [f for f in self.findings if f.source_type == source]

    def get_critical_findings(self) -> list[Finding]:
        """Get all CRITICAL findings."""
        return self.get_findings_by_severity(FindingSeverity.CRITICAL)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "meta": {
                "skill_id": self.skill_id,
                "skill_name": self.skill_name,
                "generated_at": self.generated_at,
                "t6_version": self.t6_version,
                "run_id": self.run_id,
            },
            "input_sources": {
                "validation_report": self.validation_report_path,
                "rule_scan_report": self.rule_scan_report_path,
                "pattern_detection_report": self.pattern_detection_report_path,
            },
            "findings": [f.to_dict() for f in self.findings],
            "summary": self.summary,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def save(self, output_path: str | Path) -> None:
        """Save findings report to JSON file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(self.to_json())


# ============================================================================
# Findings Report Builder (Convenience)
# ============================================================================
class FindingsReportBuilder:
    """
    Convenience builder for creating FindingsReport from T3/T4/T5 results.

    Usage:
        builder = FindingsReportBuilder(run_id="20260315_120000")
        report = builder.build_from_reports(
            skill_id="skill-1.0.0-abc12345",
            skill_name="my_skill",
            validation_result=validation_result,
            rule_result=rule_result,
            pattern_result=pattern_result,
        )
        report.save("run/T6_evidence/findings.json")
    """

    def __init__(self, run_id: Optional[str] = None):
        self.run_id = run_id or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.finding_builder = FindingBuilder(run_id=self.run_id)

    def build_from_reports(
        self,
        skill_id: str,
        skill_name: str,
        validation_result: Optional[Any] = None,
        rule_result: Optional[Any] = None,
        pattern_result: Optional[Any] = None,
        validation_report_path: Optional[str] = None,
        rule_scan_report_path: Optional[str] = None,
        pattern_detection_report_path: Optional[str] = None,
    ) -> FindingsReport:
        """
        Build FindingsReport from T3/T4/T5 results.

        Args:
            skill_id: Skill identifier
            skill_name: Skill name
            validation_result: T3 ValidationResult (optional)
            rule_result: T4 RuleScanResult (optional)
            pattern_result: T5 PatternMatchResult (optional)
            validation_report_path: Path to T3 report (for evidence ref)
            rule_scan_report_path: Path to T4 report (for evidence ref)
            pattern_detection_report_path: Path to T5 report (for evidence ref)

        Returns:
            FindingsReport with all findings from T3/T4/T5
        """
        report = FindingsReport(
            skill_id=skill_id,
            skill_name=skill_name,
            generated_at=datetime.now(timezone.utc).isoformat(),
            run_id=self.run_id,
            validation_report_path=validation_report_path,
            rule_scan_report_path=rule_scan_report_path,
            pattern_detection_report_path=pattern_detection_report_path,
        )

        # Process T3 validation failures
        if validation_result and hasattr(validation_result, 'failures'):
            for failure in validation_result.failures:
                finding = self.finding_builder.from_validation_failure(
                    failure,
                    skill_id,
                    evidence_path=validation_report_path,
                )
                report.add_finding(finding)

        # Process T4 rule hits
        if rule_result and hasattr(rule_result, 'get_all_hits'):
            for hit in rule_result.get_all_hits():
                finding = self.finding_builder.from_rule_hit(
                    hit,
                    skill_id,
                    evidence_path=rule_scan_report_path,
                )
                report.add_finding(finding)

        # Process T5 pattern matches
        if pattern_result and hasattr(pattern_result, 'get_all_matches'):
            for match in pattern_result.get_all_matches():
                finding = self.finding_builder.from_pattern_match(
                    match,
                    skill_id,
                    evidence_path=pattern_detection_report_path,
                )
                report.add_finding(finding)

        # Process T5 governance gaps
        if pattern_result and hasattr(pattern_result, 'governance_gaps'):
            for gap in pattern_result.governance_gaps:
                finding = self.finding_builder.from_governance_gap(
                    gap,
                    skill_id,
                    evidence_path=pattern_detection_report_path,
                )
                report.add_finding(finding)

        return report


# ============================================================================
# CLI Entry Point
# ============================================================================
def main():
    """CLI entry point for finding building."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Build unified findings report from T3/T4/T5 results (T6)"
    )
    parser.add_argument(
        "--skill-id",
        required=True,
        help="Skill identifier (e.g., quant-1.0.0-abc12345)",
    )
    parser.add_argument(
        "--skill-name",
        required=True,
        help="Skill name (e.g., quant)",
    )
    parser.add_argument(
        "--validation-report",
        help="Path to T3 validation_report.json",
    )
    parser.add_argument(
        "--rule-scan-report",
        help="Path to T4 rule_scan_report.json",
    )
    parser.add_argument(
        "--pattern-detection-report",
        help="Path to T5 pattern_detection_report.json",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="run/T6_evidence/findings.json",
        help="Output path for findings.json",
    )
    parser.add_argument(
        "--run-id",
        help="Run identifier for evidence paths (default: timestamp)",
    )

    args = parser.parse_args()

    # Load T3 result
    validation_result = None
    if args.validation_report:
        from skillforge.src.contracts.skill_contract_validator import ValidationResult

        with open(args.validation_report, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Reconstruct ValidationResult (simplified)
            validation_result = type('obj', (object,), {
                'is_valid': data.get('is_valid', False),
                'failures': [
                    type('obj', (object,), {**f, 'severity': 'ERROR'})()
                    for f in data.get('failures', [])
                ],
                'warnings': [
                    type('obj', (object,), {**w, 'severity': 'WARNING'})()
                    for w in data.get('warnings', [])
                ],
            })()

    # Load T4 result
    rule_result = None
    if args.rule_scan_report:
        with open(args.rule_scan_report, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Reconstruct RuleScanResult (simplified)
            all_hits = []
            for severity in ['critical', 'high', 'medium', 'low']:
                for hit in data.get('findings', {}).get(severity, []):
                    all_hits.append(type('obj', (object,), hit)())
            rule_result = type('obj', (object,), {
                'get_all_hits': lambda: all_hits,
            })()

    # Load T5 result
    pattern_result = None
    if args.pattern_detection_report:
        with open(args.pattern_detection_report, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Reconstruct PatternMatchResult (simplified)
            all_matches = []
            for severity in ['critical', 'high', 'medium']:
                for match in data.get('pattern_matches', {}).get(severity, []):
                    all_matches.append(type('obj', (object,), match)())
            pattern_result = type('obj', (object,), {
                'get_all_matches': lambda: all_matches,
                'governance_gaps': [
                    type('obj', (object,), g)()
                    for g in data.get('governance_gaps', [])
                ],
            })()

    # Build report
    builder = FindingsReportBuilder(run_id=args.run_id)
    report = builder.build_from_reports(
        skill_id=args.skill_id,
        skill_name=args.skill_name,
        validation_result=validation_result,
        rule_result=rule_result,
        pattern_result=pattern_result,
        validation_report_path=args.validation_report,
        rule_scan_report_path=args.rule_scan_report,
        pattern_detection_report_path=args.pattern_detection_report,
    )

    # Save report
    report.save(args.output)

    # Print summary
    print(f"Findings Report saved to: {args.output}")
    print(f"  Total Findings: {report.summary['total_findings']}")
    print(f"  By Severity:")
    for severity, count in report.summary['by_severity'].items():
        if count > 0:
            print(f"    {severity}: {count}")
    print(f"  By Source:")
    for source, count in report.summary['by_source'].items():
        if count > 0:
            print(f"    {source}: {count}")


if __name__ == "__main__":
    main()
