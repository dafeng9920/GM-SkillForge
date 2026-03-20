"""
Finding Adjudicator - T8 Deliverable

This module provides RuleDecision structure and adjudication logic to convert
findings from "discovered objects" into "adjudicatable objects".

T8 Scope:
- Truth assessment for each finding
- Impact level evaluation
- Evidence strength determination
- Primary basis identification
- Uncertainty quantification
- Recommended action generation
- Deterministic RuleDecision

T8 Hard Constraints:
- No PASS decision without sufficient evidence
- No free-text decisions - all fields must be structured enums
- All decisions must be deterministic and reproducible
- No Owner Review (T9) scope overlap
- No ReleaseDecision (T10) scope overlap

Usage:
    from skillforge.src.contracts.adjudicator import Adjudicator, AdjudicationReport
    from skillforge.src.contracts.finding_builder import FindingsReport

    adjudicator = Adjudicator()
    report = adjudicator.adjudicate_findings_report(findings_report)
    report.save("run/T8_evidence/adjudication_report.json")
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Literal, Optional


# ============================================================================
# Decision Enums (T8 Structured Fields)
# ============================================================================

class Decision(Enum):
    """Final adjudication decision for a finding."""
    PASS = "PASS"       # Finding is confirmed and requires action
    FAIL = "FAIL"       # Finding cannot be verified or lacks evidence
    WAIVE = "WAIVE"     # Finding is waived (false positive, out of scope, etc.)
    DEFER = "DEFER"     # Finding requires manual review


class TruthAssessment(Enum):
    """Assessment of whether the finding represents a true issue."""
    CONFIRMED = "CONFIRMED"           # Definitely true, no doubt
    LIKELY_TRUE = "LIKELY_TRUE"       # Probably true, minor uncertainty
    UNCERTAIN = "UNCERTAIN"           # Cannot determine either way
    LIKELY_FALSE = "LIKELY_FALSE"     # Probably not a real issue
    FALSE_POSITIVE = "FALSE_POSITIVE" # Definitely not a real issue


class ImpactLevel(Enum):
    """Assessed impact level if the finding is true."""
    CRITICAL = "CRITICAL"   # System compromise, data loss, security breach
    HIGH = "HIGH"           # Significant impact, requires immediate attention
    MEDIUM = "MEDIUM"       # Moderate impact, should be addressed
    LOW = "LOW"             # Minor impact, can be deferred
    NEGLIGIBLE = "NEGLIGIBLE"  # Minimal impact, informational


class EvidenceStrength(Enum):
    """Strength of evidence supporting the finding."""
    CONCLUSIVE = "CONCLUSIVE"  # Multiple strong sources, direct confirmation
    STRONG = "STRONG"          # Multiple sources or single definitive source
    MODERATE = "MODERATE"      # Single source with some ambiguity
    WEAK = "WEAK"              # Indirect or circumstantial evidence
    INSUFFICIENT = "INSUFFICIENT"  # No evidence or unreliable


class PrimaryBasis(Enum):
    """Primary basis for the adjudication decision."""
    SCHEMA_VALIDATION = "SCHEMA_VALIDATION"  # Based on schema validation (T3)
    CODE_ANALYSIS = "CODE_ANALYSIS"         # Based on code analysis (T4)
    PATTERN_MATCH = "PATTERN_MATCH"         # Based on pattern detection (T5)
    SECURITY_RULE = "SECURITY_RULE"         # Based on security rule violation (T4)
    GOVERNANCE_GAP = "GOVERNANCE_GAP"       # Based on governance gap (T5)
    MANUAL_REVIEW = "MANUAL_REVIEW"         # Based on manual review
    HEURISTIC = "HEURISTIC"                 # Based on heuristic assessment


class LargestUncertainty(Enum):
    """The largest source of uncertainty in the decision."""
    NONE = "NONE"                        # No significant uncertainty
    CONTEXT_DEPENDENT = "CONTEXT_DEPENDENT"  # Depends on runtime context
    SCOPE_AMBIGUITY = "SCOPE_AMBIGUITY"      # Unclear if in scope
    FALSE_POSITIVE_RISK = "FALSE_POSITIVE_RISK"  # Might be false positive
    EVIDENCE_INCOMPLETE = "EVIDENCE_INCOMPLETE"  # Missing key evidence
    IMPACT_ASSESSMENT = "IMPACT_ASSESSMENT"  # Unclear impact level


class RecommendedAction(Enum):
    """Recommended action based on the adjudication."""
    MUST_FIX = "MUST_FIX"                   # Must be fixed before release
    SHOULD_FIX = "SHOULD_FIX"               # Should be fixed as soon as possible
    CONSIDER_FIX = "CONSIDER_FIX"           # Consider fixing
    DOCUMENT_ACCEPTANCE = "DOCUMENT_ACCEPTANCE"  # Document and accept risk
    ESCALATE_FOR_REVIEW = "ESCALATE_FOR_REVIEW"  # Escalate for manual review
    IGNORE_FALSE_POSITIVE = "IGNORE_FALSE_POSITIVE"  # Ignore as false positive
    DEFER_TO_OWNER = "DEFER_TO_OWNER"       # Defer to owner for decision
    NO_ACTION = "NO_ACTION"                  # No action required


class WaiverReason(Enum):
    """Reason for waiving a finding."""
    FALSE_POSITIVE_CONFIRMED = "FALSE_POSITIVE_CONFIRMED"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"
    ACCEPTABLE_RISK = "ACCEPTABLE_RISK"
    COMPENSATING_CONTROL = "COMPENSATING_CONTROL"
    LEGACY_CODE = "LEGACY_CODE"
    THIRD_PARTY_DEPENDENCY = "THIRD_PARTY_DEPENDENCY"


class DeferReason(Enum):
    """Reason for deferring a finding."""
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    CONTEXT_INCOMPLETE = "CONTEXT_INCOMPLETE"
    REQUIRES_DOMAIN_EXPERTISE = "REQUIRES_DOMAIN_EXPERTISE"
    REQUIRES_RUNTIME_VERIFICATION = "REQUIRES_RUNTIME_VERIFICATION"
    REQUIRES_SECURITY_REVIEW = "REQUIRES_SECURITY_REVIEW"


class SeverityAdjustment(Enum):
    """Adjustment to original severity."""
    UPGRADED = "UPGRADED"
    DOWNGRADED = "DOWNGRADED"
    UNCHANGED = "UNCHANGED"
    UNCHANGED_VIA_EVIDENCE = "UNCHANGED_VIA_EVIDENCE"


# ============================================================================
# Severity Mapping (FindingSeverity -> ImpactLevel)
# ============================================================================
SEVERITY_TO_IMPACT: dict[str, ImpactLevel] = {
    "CRITICAL": ImpactLevel.CRITICAL,
    "HIGH": ImpactLevel.HIGH,
    "MEDIUM": ImpactLevel.MEDIUM,
    "LOW": ImpactLevel.LOW,
    "INFO": ImpactLevel.NEGLIGIBLE,
}


# ============================================================================
# Evidence Strength Determination (Deterministic)
# ============================================================================
def determine_evidence_strength(
    evidence_count: int,
    evidence_kinds: list[str],
    source_type: str,
    confidence: float,
) -> EvidenceStrength:
    """
    Determine evidence strength deterministically.

    Rules (in priority order):
    1. No evidence -> INSUFFICIENT
    2. Only LOG evidence (no direct source) -> WEAK
    3. FILE or CODE_LOCATION with high confidence -> STRONG
    4. Multiple evidence kinds -> CONCLUSIVE
    5. Single FILE/CODE_LOCATION with medium confidence -> MODERATE
    6. Default -> WEAK

    T8 Hard Constraint: INSUFFICIENT evidence cannot result in PASS decision.
    """
    if evidence_count == 0:
        return EvidenceStrength.INSUFFICIENT

    # Check for strong evidence types
    has_strong_type = any(k in evidence_kinds for k in ["FILE", "CODE_LOCATION"])
    has_only_weak_type = all(k in ["LOG", "URL"] for k in evidence_kinds)

    # Rule 1: Only weak evidence types (LOG, URL only)
    if has_only_weak_type:
        return EvidenceStrength.WEAK

    # Rule 2: Multiple evidence kinds
    if len(evidence_kinds) >= 2:
        if has_strong_type:
            return EvidenceStrength.CONCLUSIVE
        return EvidenceStrength.MODERATE

    # Rule 3: High confidence with strong evidence
    if has_strong_type and confidence >= 0.95:
        return EvidenceStrength.STRONG

    # Rule 4: Medium confidence with strong evidence
    if has_strong_type and confidence >= 0.85:
        return EvidenceStrength.MODERATE

    # Default
    return EvidenceStrength.WEAK


# ============================================================================
# Truth Assessment (Deterministic)
# ============================================================================
def assess_truth(
    source_type: str,
    confidence: float,
    evidence_strength: EvidenceStrength,
    category: str,
) -> TruthAssessment:
    """
    Assess truth of finding deterministically.

    Rules:
    1. Schema validation (T3) with confidence >= 0.95 -> CONFIRMED
    2. Security rules (T4) with confidence >= 0.90 -> CONFIRMED
    3. INSUFFICIENT evidence -> UNCERTAIN
    4. WEAK evidence -> LIKELY_FALSE
    5. High confidence with STRONG+ evidence -> LIKELY_TRUE
    6. Default -> UNCERTAIN
    """
    # Rule: Schema validation is deterministic
    if source_type == "validation" and confidence >= 0.95:
        return TruthAssessment.CONFIRMED

    # Rule: Security rules are highly reliable
    if source_type == "rule_scan" and category == "dangerous_pattern":
        if confidence >= 0.95:
            return TruthAssessment.CONFIRMED
        elif confidence >= 0.85:
            return TruthAssessment.LIKELY_TRUE

    # Rule: No evidence -> uncertain
    if evidence_strength == EvidenceStrength.INSUFFICIENT:
        return TruthAssessment.UNCERTAIN

    # Rule: Weak evidence -> likely false
    if evidence_strength == EvidenceStrength.WEAK:
        return TruthAssessment.LIKELY_FALSE

    # Rule: High confidence with strong evidence
    if confidence >= 0.90 and evidence_strength in (EvidenceStrength.STRONG, EvidenceStrength.CONCLUSIVE):
        return TruthAssessment.LIKELY_TRUE

    # Rule: Pattern matching (T5) has some uncertainty
    if source_type == "pattern_match":
        if evidence_strength == EvidenceStrength.CONCLUSIVE:
            return TruthAssessment.LIKELY_TRUE
        return TruthAssessment.UNCERTAIN

    return TruthAssessment.UNCERTAIN


# ============================================================================
# Primary Basis (Deterministic)
# ============================================================================
def determine_primary_basis(
    source_type: str,
    category: str,
) -> PrimaryBasis:
    """Determine primary basis from source type and category."""
    if source_type == "validation":
        return PrimaryBasis.SCHEMA_VALIDATION
    elif source_type == "rule_scan":
        if category == "dangerous_pattern":
            return PrimaryBasis.SECURITY_RULE
        return PrimaryBasis.CODE_ANALYSIS
    elif source_type == "pattern_match":
        if category == "governance_gap":
            return PrimaryBasis.GOVERNANCE_GAP
        return PrimaryBasis.PATTERN_MATCH
    return PrimaryBasis.HEURISTIC


# ============================================================================
# Largest Uncertainty (Deterministic)
# ============================================================================
def determine_uncertainty(
    truth_assessment: TruthAssessment,
    evidence_strength: EvidenceStrength,
    source_type: str,
    category: str,
) -> LargestUncertainty:
    """Determine largest uncertainty deterministically."""
    # Confirmed findings have minimal uncertainty
    if truth_assessment == TruthAssessment.CONFIRMED:
        return LargestUncertainty.NONE

    # No evidence -> evidence incomplete
    if evidence_strength == EvidenceStrength.INSUFFICIENT:
        return LargestUncertainty.EVIDENCE_INCOMPLETE

    # Weak evidence -> false positive risk
    if evidence_strength == EvidenceStrength.WEAK:
        return LargestUncertainty.FALSE_POSITIVE_RISK

    # Pattern matching has context dependency
    if source_type == "pattern_match":
        if category == "governance_gap":
            return LargestUncertainty.SCOPE_AMBIGUITY
        return LargestUncertainty.CONTEXT_DEPENDENT

    # Security rules have some uncertainty
    if source_type == "rule_scan" and category == "dangerous_pattern":
        return LargestUncertainty.CONTEXT_DEPENDENT

    return LargestUncertainty.NONE


# ============================================================================
# Decision Logic (T8 Core)
# ============================================================================
def make_decision(
    truth_assessment: TruthAssessment,
    impact_level: ImpactLevel,
    evidence_strength: EvidenceStrength,
    uncertainty: LargestUncertainty,
    source_type: str,
) -> Decision:
    """
    Make final adjudication decision.

    T8 Hard Constraint: PASS decision requires:
    - Truth assessment is CONFIRMED or LIKELY_TRUE
    - Evidence strength is at least MODERATE
    - Not a false positive

    Decision Matrix:
    | Truth         | Evidence | Impact  | Decision |
    |---------------|----------|---------|----------|
    | CONFIRMED     | STRONG+  | HIGH+   | PASS     |
    | CONFIRMED     | MODERATE | MEDIUM+ | PASS     |
    | LIKELY_TRUE   | STRONG+  | HIGH+   | PASS     |
    | FALSE_POSITIVE| -        | -       | WAIVE    |
    | LIKELY_FALSE  | -        | -       | WAIVE    |
    | UNCERTAIN     | WEAK     | -       | FAIL     |
    | UNCERTAIN     | INSUFF   | -       | DEFER    |
    | -             | INSUFF   | -       | FAIL     |
    | CONFIRMED     | WEAK     | CRITICAL| DEFER    |
    """
    # Hard constraint: No evidence -> FAIL (unless UNCERTAIN, then DEFER)
    if evidence_strength == EvidenceStrength.INSUFFICIENT:
        if truth_assessment == TruthAssessment.UNCERTAIN:
            return Decision.DEFER
        return Decision.FAIL

    # False positive or likely false -> WAIVE
    if truth_assessment in (TruthAssessment.FALSE_POSITIVE, TruthAssessment.LIKELY_FALSE):
        return Decision.WAIVE

    # Strong confirmation with good evidence -> PASS
    if truth_assessment in (TruthAssessment.CONFIRMED, TruthAssessment.LIKELY_TRUE):
        if evidence_strength in (EvidenceStrength.STRONG, EvidenceStrength.CONCLUSIVE):
            return Decision.PASS
        if evidence_strength == EvidenceStrength.MODERATE and impact_level in (ImpactLevel.HIGH, ImpactLevel.MEDIUM):
            return Decision.PASS

    # Uncertain with weak evidence -> FAIL
    if truth_assessment == TruthAssessment.UNCERTAIN:
        if evidence_strength == EvidenceStrength.WEAK:
            return Decision.FAIL
        if evidence_strength == EvidenceStrength.INSUFFICIENT:
            return Decision.DEFER

    # Critical findings with weak evidence need review
    if impact_level == ImpactLevel.CRITICAL and evidence_strength == EvidenceStrength.WEAK:
        return Decision.DEFER

    # Default: defer uncertain findings for manual review
    return Decision.DEFER


# ============================================================================
# Recommended Action (Deterministic)
# ============================================================================
def recommend_action(
    decision: Decision,
    impact_level: ImpactLevel,
    truth_assessment: TruthAssessment,
) -> RecommendedAction:
    """Determine recommended action based on decision and impact."""
    if decision == Decision.WAIVE:
        return RecommendedAction.IGNORE_FALSE_POSITIVE

    if decision == Decision.DEFER:
        if impact_level == ImpactLevel.CRITICAL:
            return RecommendedAction.ESCALATE_FOR_REVIEW
        return RecommendedAction.DEFER_TO_OWNER

    if decision == Decision.FAIL:
        return RecommendedAction.ESCALATE_FOR_REVIEW

    # PASS decisions - consider both impact and truth_assessment
    if impact_level == ImpactLevel.CRITICAL:
        return RecommendedAction.MUST_FIX
    if impact_level == ImpactLevel.HIGH:
        # CONFIRMED HIGH -> MUST_FIX, otherwise -> SHOULD_FIX
        if truth_assessment == TruthAssessment.CONFIRMED:
            return RecommendedAction.MUST_FIX
        return RecommendedAction.SHOULD_FIX
    if impact_level == ImpactLevel.MEDIUM:
        return RecommendedAction.SHOULD_FIX
    if impact_level == ImpactLevel.LOW:
        return RecommendedAction.CONSIDER_FIX
    return RecommendedAction.NO_ACTION


# ============================================================================
# Confidence Calculation (Deterministic)
# ============================================================================
def calculate_adjudication_confidence(
    evidence_strength: EvidenceStrength,
    truth_assessment: TruthAssessment,
    source_confidence: float,
) -> float:
    """Calculate confidence in the adjudication decision."""
    # Base confidence from evidence strength
    evidence_confidence_map = {
        EvidenceStrength.CONCLUSIVE: 0.98,
        EvidenceStrength.STRONG: 0.90,
        EvidenceStrength.MODERATE: 0.75,
        EvidenceStrength.WEAK: 0.50,
        EvidenceStrength.INSUFFICIENT: 0.25,
    }

    # Base confidence from truth assessment
    truth_confidence_map = {
        TruthAssessment.CONFIRMED: 0.98,
        TruthAssessment.LIKELY_TRUE: 0.80,
        TruthAssessment.UNCERTAIN: 0.50,
        TruthAssessment.LIKELY_FALSE: 0.70,  # Confidence it's NOT true
        TruthAssessment.FALSE_POSITIVE: 0.95,  # Confidence it's false
    }

    ev_conf = evidence_confidence_map.get(evidence_strength, 0.5)
    truth_conf = truth_confidence_map.get(truth_assessment, 0.5)

    # Combine: average of evidence and truth confidence, weighted by source
    return (ev_conf * 0.4 + truth_conf * 0.4 + source_confidence * 0.2)


# ============================================================================
# Rule Decision
# ============================================================================
@dataclass(frozen=True)
class RuleDecision:
    """
    Adjudication decision for a single finding.

    T8 converts Findings from "discovered objects" to "adjudicatable objects"
    through structured, deterministic assessment.
    """
    finding_id: str
    decision: Decision
    truth_assessment: TruthAssessment
    impact_level: ImpactLevel
    evidence_strength: EvidenceStrength
    primary_basis: PrimaryBasis
    largest_uncertainty: LargestUncertainty
    recommended_action: RecommendedAction
    adjudicated_at: str

    # Optional fields
    confidence: float = 0.8
    evidence_count: int = 0
    evidence_kinds: list[str] = field(default_factory=list)
    has_strong_evidence: bool = False
    waiver_reason: Optional[WaiverReason] = None
    defer_reason: Optional[DeferReason] = None
    severity_adjustment: SeverityAdjustment = SeverityAdjustment.UNCHANGED
    adjudicator_notes: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "finding_id": self.finding_id,
            "decision": self.decision.value,
            "truth_assessment": self.truth_assessment.value,
            "impact_level": self.impact_level.value,
            "evidence_strength": self.evidence_strength.value,
            "primary_basis": self.primary_basis.value,
            "largest_uncertainty": self.largest_uncertainty.value,
            "recommended_action": self.recommended_action.value,
            "adjudicated_at": self.adjudicated_at,
            "confidence": self.confidence,
            "evidence_summary": {
                "evidence_count": self.evidence_count,
                "evidence_kinds": self.evidence_kinds,
                "has_strong_evidence": self.has_strong_evidence,
            },
            "severity_adjustment": self.severity_adjustment.value,
        }

        if self.waiver_reason:
            result["waiver_reason"] = self.waiver_reason.value
        if self.defer_reason:
            result["defer_reason"] = self.defer_reason.value
        if self.adjudicator_notes:
            result["adjudicator_notes"] = self.adjudicator_notes

        return result


# ============================================================================
# Adjudicator
# ============================================================================
class Adjudicator:
    """
    Finding Adjudicator - T8 Core Logic.

    Converts Findings into RuleDecisions through deterministic assessment.
    All decisions are reproducible and evidence-based.
    """

    def __init__(
        self,
        evidence_threshold: float = 0.6,  # Minimum evidence strength for PASS
        confidence_threshold: float = 0.7,  # Minimum finding confidence
    ):
        """
        Initialize Adjudicator.

        Args:
            evidence_threshold: Minimum evidence strength (0-1) for PASS decision
            confidence_threshold: Minimum finding confidence for adjudication
        """
        self.evidence_threshold = evidence_threshold
        self.confidence_threshold = confidence_threshold
        self.t8_version = "1.0.0-t8"

    def adjudicate_finding(
        self,
        finding: dict[str, Any],
    ) -> RuleDecision:
        """
        Adjudicate a single finding.

        Args:
            finding: Finding dictionary from FindingsReport

        Returns:
            RuleDecision with structured assessment
        """
        # Extract finding data
        finding_id = finding["finding_id"]
        source_type = finding["source"]["type"]
        category = finding["what"]["category"]
        severity = finding["what"]["severity"]
        confidence = finding["what"]["confidence"]

        # Extract evidence
        evidence_refs = finding.get("evidence_refs", [])
        evidence_count = len(evidence_refs)
        evidence_kinds = list(set(e["kind"] for e in evidence_refs))
        has_strong_evidence = any(
            k in evidence_kinds for k in ["FILE", "CODE_LOCATION"]
        )

        # Determine evidence strength
        evidence_strength = determine_evidence_strength(
            evidence_count,
            evidence_kinds,
            source_type,
            confidence,
        )

        # Determine impact level from severity
        impact_level = SEVERITY_TO_IMPACT.get(severity, ImpactLevel.MEDIUM)

        # Assess truth
        truth_assessment = assess_truth(
            source_type,
            confidence,
            evidence_strength,
            category,
        )

        # Determine primary basis
        primary_basis = determine_primary_basis(source_type, category)

        # Determine uncertainty
        largest_uncertainty = determine_uncertainty(
            truth_assessment,
            evidence_strength,
            source_type,
            category,
        )

        # Make decision
        decision = make_decision(
            truth_assessment,
            impact_level,
            evidence_strength,
            largest_uncertainty,
            source_type,
        )

        # Determine recommended action
        recommended_action = recommend_action(
            decision,
            impact_level,
            truth_assessment,
        )

        # Set waiver/defer reasons if needed
        waiver_reason = None
        defer_reason = None

        if decision == Decision.WAIVE:
            if truth_assessment == TruthAssessment.FALSE_POSITIVE:
                waiver_reason = WaiverReason.FALSE_POSITIVE_CONFIRMED
            elif truth_assessment == TruthAssessment.LIKELY_FALSE:
                waiver_reason = WaiverReason.FALSE_POSITIVE_CONFIRMED

        if decision == Decision.DEFER:
            if evidence_strength == EvidenceStrength.INSUFFICIENT:
                defer_reason = DeferReason.INSUFFICIENT_EVIDENCE
            elif largest_uncertainty == LargestUncertainty.CONTEXT_DEPENDENT:
                defer_reason = DeferReason.CONTEXT_INCOMPLETE
            elif largest_uncertainty == LargestUncertainty.SCOPE_AMBIGUITY:
                defer_reason = DeferReason.REQUIRES_DOMAIN_EXPERTISE
            else:
                defer_reason = DeferReason.REQUIRES_SECURITY_REVIEW

        # Calculate adjudication confidence
        adjudication_confidence = calculate_adjudication_confidence(
            evidence_strength,
            truth_assessment,
            confidence,
        )

        # Notes for traceability (structured, not free text)
        notes_template = (
            f"T8 Adjudication: source={source_type}, category={category}, "
            f"severity={severity}, confidence={confidence:.2f}, "
            f"evidence_count={evidence_count}, evidence_strength={evidence_strength.value}"
        )

        return RuleDecision(
            finding_id=finding_id,
            decision=decision,
            truth_assessment=truth_assessment,
            impact_level=impact_level,
            evidence_strength=evidence_strength,
            primary_basis=primary_basis,
            largest_uncertainty=largest_uncertainty,
            recommended_action=recommended_action,
            adjudicated_at=datetime.now(timezone.utc).isoformat(),
            confidence=adjudication_confidence,
            evidence_count=evidence_count,
            evidence_kinds=evidence_kinds,
            has_strong_evidence=has_strong_evidence,
            waiver_reason=waiver_reason,
            defer_reason=defer_reason,
            adjudicator_notes=notes_template,
        )


# ============================================================================
# Adjudication Report
# ============================================================================
@dataclass
class AdjudicationReport:
    """
    T8 Deliverable: Adjudication Report containing all RuleDecisions.

    This report converts findings from "discovered objects" to
    "adjudicatable objects" ready for Owner Review (T9).
    """
    skill_id: str
    skill_name: str
    generated_at: str
    t8_version: str = "1.0.0-t8"
    run_id: str = ""

    # Input references
    findings_report_path: Optional[str] = None
    validation_report_path: Optional[str] = None
    rule_scan_report_path: Optional[str] = None
    pattern_detection_report_path: Optional[str] = None

    # Decisions
    rule_decisions: list[RuleDecision] = field(default_factory=list)

    # Summary (computed)
    summary: dict[str, Any] = field(default_factory=dict)

    # Config
    adjudicator_config: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Compute summary on creation."""
        if not self.summary:
            self._update_summary()

    def _update_summary(self) -> None:
        """Update summary statistics."""
        total = len(self.rule_decisions)

        by_decision = {d.value: 0 for d in Decision}
        by_truth = {t.value: 0 for t in TruthAssessment}
        by_impact = {i.value: 0 for i in ImpactLevel}
        by_evidence = {e.value: 0 for e in EvidenceStrength}

        findings_requiring_attention = []

        with_evidence = 0
        without_evidence = 0

        for rd in self.rule_decisions:
            by_decision[rd.decision.value] += 1
            by_truth[rd.truth_assessment.value] += 1
            by_impact[rd.impact_level.value] += 1
            by_evidence[rd.evidence_strength.value] += 1

            # Track findings requiring attention
            if rd.decision == Decision.FAIL or rd.impact_level == ImpactLevel.CRITICAL:
                findings_requiring_attention.append(rd.finding_id)

            # Evidence coverage
            if rd.evidence_count > 0:
                with_evidence += 1
            else:
                without_evidence += 1

        coverage_pct = (with_evidence / total * 100) if total > 0 else 0

        self.summary = {
            "total_decisions": total,
            "by_decision": by_decision,
            "by_truth_assessment": by_truth,
            "by_impact_level": by_impact,
            "by_evidence_strength": by_evidence,
            "findings_requiring_attention": findings_requiring_attention,
            "evidence_coverage": {
                "findings_with_evidence": with_evidence,
                "findings_without_evidence": without_evidence,
                "coverage_percentage": round(coverage_pct, 2),
            },
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "meta": {
                "skill_id": self.skill_id,
                "skill_name": self.skill_name,
                "generated_at": self.generated_at,
                "t8_version": self.t8_version,
                "run_id": self.run_id,
                "adjudicator_config": self.adjudicator_config,
            },
            "input_sources": {
                "findings_report": self.findings_report_path,
                "validation_report": self.validation_report_path,
                "rule_scan_report": self.rule_scan_report_path,
                "pattern_detection_report": self.pattern_detection_report_path,
            },
            "rule_decisions": [rd.to_dict() for rd in self.rule_decisions],
            "summary": self.summary,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def save(self, output_path: str | Path) -> None:
        """Save adjudication report to JSON file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(self.to_json())


# ============================================================================
# Adjudicate Findings Report
# ============================================================================
def adjudicate_findings_report(
    findings_report: dict[str, Any],
    run_id: Optional[str] = None,
) -> AdjudicationReport:
    """
    Adjudicate an entire findings report.

    Args:
        findings_report: FindingsReport dictionary from T6
        run_id: Optional run identifier

    Returns:
        AdjudicationReport with all RuleDecisions
    """
    run_id = run_id or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    meta = findings_report.get("meta", {})
    input_sources = findings_report.get("input_sources", {})
    findings = findings_report.get("findings", [])

    adjudicator = Adjudicator()

    decisions = []
    for finding in findings:
        decision = adjudicator.adjudicate_finding(finding)
        decisions.append(decision)

    report = AdjudicationReport(
        skill_id=meta.get("skill_id", ""),
        skill_name=meta.get("skill_name", ""),
        generated_at=datetime.now(timezone.utc).isoformat(),
        run_id=run_id,
        findings_report_path=input_sources.get("findings_report"),
        validation_report_path=input_sources.get("validation_report"),
        rule_scan_report_path=input_sources.get("rule_scan_report"),
        pattern_detection_report_path=input_sources.get("pattern_detection_report"),
        rule_decisions=decisions,
        adjudicator_config={
            "evidence_threshold": adjudicator.evidence_threshold,
            "confidence_threshold": adjudicator.confidence_threshold,
            "severity_weights": {
                "CRITICAL": 5.0,
                "HIGH": 4.0,
                "MEDIUM": 3.0,
                "LOW": 2.0,
                "INFO": 1.0,
            },
        },
    )

    return report


# ============================================================================
# CLI Entry Point
# ============================================================================
def main():
    """CLI entry point for finding adjudication."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Adjudicate findings report (T8)"
    )
    parser.add_argument(
        "--findings-report",
        required=True,
        help="Path to T6 findings_report.json",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="run/T8_evidence/adjudication_report.json",
        help="Output path for adjudication_report.json",
    )
    parser.add_argument(
        "--run-id",
        help="Run identifier (default: timestamp)",
    )
    parser.add_argument(
        "--evidence-threshold",
        type=float,
        default=0.6,
        help="Minimum evidence strength for PASS (default: 0.6)",
    )

    args = parser.parse_args()

    # Load findings report
    with open(args.findings_report, "r", encoding="utf-8") as f:
        findings_report = json.load(f)

    # Adjudicate
    report = adjudicate_findings_report(findings_report, run_id=args.run_id)

    # Save report
    report.save(args.output)

    # Print summary
    print(f"Adjudication Report saved to: {args.output}")
    print(f"  Total Decisions: {report.summary['total_decisions']}")
    print(f"  By Decision:")
    for decision, count in report.summary['by_decision'].items():
        if count > 0:
            print(f"    {decision}: {count}")
    print(f"  By Truth Assessment:")
    for truth, count in report.summary['by_truth_assessment'].items():
        if count > 0:
            print(f"    {truth}: {count}")
    print(f"  Evidence Coverage: {report.summary['evidence_coverage']['coverage_percentage']:.1f}%")

    findings_requiring_attention = report.summary['findings_requiring_attention']
    if findings_requiring_attention:
        print(f"  Findings Requiring Attention: {len(findings_requiring_attention)}")
        for fid in findings_requiring_attention[:5]:
            print(f"    - {fid}")
        if len(findings_requiring_attention) > 5:
            print(f"    ... and {len(findings_requiring_attention) - 5} more")


if __name__ == "__main__":
    main()
