"""
T8 Finding Adjudication Tests

Tests for RuleDecision structure and Adjudicator.
Tests conversion of Findings into RuleDecisions through deterministic assessment.

T8 Scope:
- Truth assessment
- Impact level evaluation
- Evidence strength determination
- Primary basis identification
- Uncertainty quantification
- Recommended action generation
- Deterministic RuleDecision
- Hard constraint: No PASS without evidence

T8 Hard Constraints:
- No PASS decision without sufficient evidence
- No free-text decisions - all fields must be structured enums
- All decisions must be deterministic and reproducible
- No Owner Review (T9) scope overlap
- No ReleaseDecision (T10) scope overlap
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from skillforge.src.contracts.adjudicator import (
    AdjudicationReport,
    Adjudicator,
    Decision,
    DeferReason,
    EvidenceStrength,
    ImpactLevel,
    LargestUncertainty,
    PrimaryBasis,
    RecommendedAction,
    RuleDecision,
    SeverityAdjustment,
    TruthAssessment,
    WaiverReason,
    adjudicate_findings_report,
    assess_truth,
    calculate_adjudication_confidence,
    determine_evidence_strength,
    determine_primary_basis,
    determine_uncertainty,
    make_decision,
    recommend_action,
)


# ============================================================================
# Sample Finding Data
# ============================================================================
def make_sample_finding(
    finding_id: str,
    source_type: str = "validation",
    category: str = "schema_validation",
    severity: str = "HIGH",
    confidence: float = 0.95,
    evidence_refs: list[dict] | None = None,
) -> dict:
    """Create a sample finding for testing."""
    if evidence_refs is None:
        evidence_refs = [
            {"kind": "FILE", "locator": "run/validation_report.json", "note": "T3 report"},
            {"kind": "CODE_LOCATION", "locator": "skill.py:42", "note": "Source location"},
        ]

    return {
        "finding_id": finding_id,
        "source": {"type": source_type, "code": "E302_SCHEMA_VALIDATION_FAILED"},
        "what": {
            "title": "Schema Validation Failed",
            "description": "Required field missing",
            "category": category,
            "severity": severity,
            "confidence": confidence,
        },
        "where": {
            "file_path": "skill.py",
            "line_number": 42,
            "column_number": None,
            "function_name": None,
        },
        "evidence_refs": evidence_refs,
        "detected_at": datetime.now(timezone.utc).isoformat(),
    }


# ============================================================================
# Test Evidence Strength Determination
# ============================================================================
class TestEvidenceStrengthDetermination:
    """Test evidence strength determination logic."""

    def test_no_evidence_insufficient(self):
        """No evidence should result in INSUFFICIENT strength."""
        strength = determine_evidence_strength(0, [], "validation", 0.9)
        assert strength == EvidenceStrength.INSUFFICIENT

    def test_strong_evidence_types(self):
        """FILE and CODE_LOCATION are strong evidence types."""
        strength = determine_evidence_strength(
            2,
            ["FILE", "CODE_LOCATION"],
            "validation",
            0.95,
        )
        assert strength == EvidenceStrength.CONCLUSIVE

    def test_single_file_with_high_confidence(self):
        """Single FILE evidence with high confidence should be STRONG."""
        strength = determine_evidence_strength(
            1,
            ["FILE"],
            "validation",
            0.95,
        )
        assert strength == EvidenceStrength.STRONG

    def test_single_file_with_medium_confidence(self):
        """Single FILE evidence with medium confidence should be MODERATE."""
        strength = determine_evidence_strength(
            1,
            ["FILE"],
            "validation",
            0.85,
        )
        assert strength == EvidenceStrength.MODERATE

    def test_only_log_evidence_weak(self):
        """Only LOG evidence should be WEAK."""
        strength = determine_evidence_strength(
            2,
            ["LOG", "LOG"],
            "validation",
            0.9,
        )
        assert strength == EvidenceStrength.WEAK

    def test_multiple_evidence_kinds(self):
        """Multiple different evidence kinds should be CONCLUSIVE."""
        strength = determine_evidence_strength(
            3,
            ["FILE", "CODE_LOCATION", "LOG"],
            "validation",
            0.9,
        )
        assert strength == EvidenceStrength.CONCLUSIVE


# ============================================================================
# Test Truth Assessment
# ============================================================================
class TestTruthAssessment:
    """Test truth assessment logic."""

    def test_schema_validation_confirmed(self):
        """Schema validation with high confidence should be CONFIRMED."""
        truth = assess_truth(
            "validation",
            0.98,
            EvidenceStrength.CONCLUSIVE,
            "schema_validation",
        )
        assert truth == TruthAssessment.CONFIRMED

    def test_security_rule_confirmed(self):
        """Security rule (dangerous_pattern) with high confidence should be CONFIRMED."""
        truth = assess_truth(
            "rule_scan",
            0.95,
            EvidenceStrength.STRONG,
            "dangerous_pattern",
        )
        assert truth == TruthAssessment.CONFIRMED

    def test_insufficient_evidence_uncertain(self):
        """INSUFFICIENT evidence should result in UNCERTAIN."""
        truth = assess_truth(
            "validation",
            0.9,
            EvidenceStrength.INSUFFICIENT,
            "schema_validation",
        )
        assert truth == TruthAssessment.UNCERTAIN

    def test_weak_evidence_likely_false(self):
        """WEAK evidence should result in LIKELY_FALSE."""
        truth = assess_truth(
            "validation",
            0.8,
            EvidenceStrength.WEAK,
            "schema_validation",
        )
        assert truth == TruthAssessment.LIKELY_FALSE

    def test_pattern_match_uncertain(self):
        """Pattern match should have some uncertainty."""
        truth = assess_truth(
            "pattern_match",
            0.85,
            EvidenceStrength.MODERATE,
            "governance_gap",
        )
        assert truth == TruthAssessment.UNCERTAIN


# ============================================================================
# Test Primary Basis
# ============================================================================
class TestPrimaryBasis:
    """Test primary basis determination."""

    def test_validation_source_schema_validation(self):
        """Validation source should map to SCHEMA_VALIDATION basis."""
        basis = determine_primary_basis("validation", "schema_validation")
        assert basis == PrimaryBasis.SCHEMA_VALIDATION

    def test_rule_scan_dangerous_pattern_security_rule(self):
        """Rule scan with dangerous_pattern should map to SECURITY_RULE."""
        basis = determine_primary_basis("rule_scan", "dangerous_pattern")
        assert basis == PrimaryBasis.SECURITY_RULE

    def test_rule_scan_other_code_analysis(self):
        """Rule scan with other category should map to CODE_ANALYSIS."""
        basis = determine_primary_basis("rule_scan", "external_action")
        assert basis == PrimaryBasis.CODE_ANALYSIS

    def test_pattern_match_governance_gap(self):
        """Pattern match with governance_gap should map to GOVERNANCE_GAP."""
        basis = determine_primary_basis("pattern_match", "governance_gap")
        assert basis == PrimaryBasis.GOVERNANCE_GAP

    def test_pattern_match_other_pattern_match(self):
        """Pattern match with other category should map to PATTERN_MATCH."""
        basis = determine_primary_basis("pattern_match", "anti_pattern")
        assert basis == PrimaryBasis.PATTERN_MATCH


# ============================================================================
# Test Uncertainty Determination
# ============================================================================
class TestUncertaintyDetermination:
    """Test uncertainty determination logic."""

    def test_confirmed_no_uncertainty(self):
        """CONFIRMED truth should have NONE uncertainty."""
        uncertainty = determine_uncertainty(
            TruthAssessment.CONFIRMED,
            EvidenceStrength.STRONG,
            "validation",
            "schema_validation",
        )
        assert uncertainty == LargestUncertainty.NONE

    def test_insufficient_evidence_evidence_incomplete(self):
        """INSUFFICIENT evidence should result in EVIDENCE_INCOMPLETE."""
        uncertainty = determine_uncertainty(
            TruthAssessment.UNCERTAIN,
            EvidenceStrength.INSUFFICIENT,
            "validation",
            "schema_validation",
        )
        assert uncertainty == LargestUncertainty.EVIDENCE_INCOMPLETE

    def test_weak_evidence_false_positive_risk(self):
        """WEAK evidence should result in FALSE_POSITIVE_RISK."""
        uncertainty = determine_uncertainty(
            TruthAssessment.LIKELY_FALSE,
            EvidenceStrength.WEAK,
            "validation",
            "schema_validation",
        )
        assert uncertainty == LargestUncertainty.FALSE_POSITIVE_RISK

    def test_pattern_match_context_dependent(self):
        """Pattern match should result in CONTEXT_DEPENDENT."""
        uncertainty = determine_uncertainty(
            TruthAssessment.LIKELY_TRUE,
            EvidenceStrength.MODERATE,
            "pattern_match",
            "anti_pattern",
        )
        assert uncertainty == LargestUncertainty.CONTEXT_DEPENDENT

    def test_governance_gap_scope_ambiguity(self):
        """Governance gap should result in SCOPE_AMBIGUITY."""
        uncertainty = determine_uncertainty(
            TruthAssessment.UNCERTAIN,
            EvidenceStrength.MODERATE,
            "pattern_match",
            "governance_gap",
        )
        assert uncertainty == LargestUncertainty.SCOPE_AMBIGUITY


# ============================================================================
# Test Decision Logic (T8 Core)
# ============================================================================
class TestDecisionLogic:
    """Test the core decision logic."""

    def test_insufficient_evidence_fail(self):
        """T8 Hard Constraint: INSUFFICIENT evidence must result in FAIL."""
        decision = make_decision(
            TruthAssessment.CONFIRMED,
            ImpactLevel.HIGH,
            EvidenceStrength.INSUFFICIENT,
            LargestUncertainty.EVIDENCE_INCOMPLETE,
            "validation",
        )
        assert decision == Decision.FAIL

    def test_confirmed_strong_evidence_pass(self):
        """CONFIRMED with STRONG evidence should PASS."""
        decision = make_decision(
            TruthAssessment.CONFIRMED,
            ImpactLevel.HIGH,
            EvidenceStrength.STRONG,
            LargestUncertainty.NONE,
            "validation",
        )
        assert decision == Decision.PASS

    def test_confirmed_conclusive_evidence_pass(self):
        """CONFIRMED with CONCLUSIVE evidence should PASS."""
        decision = make_decision(
            TruthAssessment.CONFIRMED,
            ImpactLevel.CRITICAL,
            EvidenceStrength.CONCLUSIVE,
            LargestUncertainty.NONE,
            "rule_scan",
        )
        assert decision == Decision.PASS

    def test_likely_true_moderate_evidence_high_impact_pass(self):
        """LIKELY_TRUE with MODERATE evidence and HIGH+ impact should PASS."""
        decision = make_decision(
            TruthAssessment.LIKELY_TRUE,
            ImpactLevel.HIGH,
            EvidenceStrength.MODERATE,
            LargestUncertainty.NONE,
            "validation",
        )
        assert decision == Decision.PASS

    def test_false_positive_waive(self):
        """FALSE_POSITIVE should WAIVE."""
        decision = make_decision(
            TruthAssessment.FALSE_POSITIVE,
            ImpactLevel.HIGH,
            EvidenceStrength.STRONG,
            LargestUncertainty.NONE,
            "validation",
        )
        assert decision == Decision.WAIVE

    def test_likely_false_waive(self):
        """LIKELY_FALSE should WAIVE."""
        decision = make_decision(
            TruthAssessment.LIKELY_FALSE,
            ImpactLevel.MEDIUM,
            EvidenceStrength.WEAK,
            LargestUncertainty.FALSE_POSITIVE_RISK,
            "validation",
        )
        assert decision == Decision.WAIVE

    def test_uncertain_weak_evidence_fail(self):
        """UNCERTAIN with WEAK evidence should FAIL."""
        decision = make_decision(
            TruthAssessment.UNCERTAIN,
            ImpactLevel.MEDIUM,
            EvidenceStrength.WEAK,
            LargestUncertainty.FALSE_POSITIVE_RISK,
            "validation",
        )
        assert decision == Decision.FAIL

    def test_critical_weak_evidence_defer(self):
        """CRITICAL with WEAK evidence should DEFER for review."""
        decision = make_decision(
            TruthAssessment.CONFIRMED,
            ImpactLevel.CRITICAL,
            EvidenceStrength.WEAK,
            LargestUncertainty.NONE,
            "validation",
        )
        assert decision == Decision.DEFER

    def test_uncertain_insufficient_evidence_defer(self):
        """UNCERTAIN with INSUFFICIENT evidence should DEFER."""
        decision = make_decision(
            TruthAssessment.UNCERTAIN,
            ImpactLevel.HIGH,
            EvidenceStrength.INSUFFICIENT,
            LargestUncertainty.EVIDENCE_INCOMPLETE,
            "validation",
        )
        assert decision == Decision.DEFER


# ============================================================================
# Test Recommended Action
# ============================================================================
class TestRecommendedAction:
    """Test recommended action determination."""

    def test_waive_ignore_false_positive(self):
        """WAIVE decision should result in IGNORE_FALSE_POSITIVE."""
        action = recommend_action(Decision.WAIVE, ImpactLevel.HIGH, TruthAssessment.FALSE_POSITIVE)
        assert action == RecommendedAction.IGNORE_FALSE_POSITIVE

    def test_defer_critical_escalate(self):
        """DEFER with CRITICAL impact should ESCALATE_FOR_REVIEW."""
        action = recommend_action(Decision.DEFER, ImpactLevel.CRITICAL, TruthAssessment.UNCERTAIN)
        assert action == RecommendedAction.ESCALATE_FOR_REVIEW

    def test_defer_non_critical_defer_to_owner(self):
        """DEFER with non-CRITICAL impact should DEFER_TO_OWNER."""
        action = recommend_action(Decision.DEFER, ImpactLevel.MEDIUM, TruthAssessment.UNCERTAIN)
        assert action == RecommendedAction.DEFER_TO_OWNER

    def test_fail_escalate(self):
        """FAIL decision should ESCALATE_FOR_REVIEW."""
        action = recommend_action(Decision.FAIL, ImpactLevel.HIGH, TruthAssessment.UNCERTAIN)
        assert action == RecommendedAction.ESCALATE_FOR_REVIEW

    def test_pass_critical_must_fix(self):
        """PASS with CRITICAL impact should MUST_FIX."""
        action = recommend_action(Decision.PASS, ImpactLevel.CRITICAL, TruthAssessment.CONFIRMED)
        assert action == RecommendedAction.MUST_FIX

    def test_pass_high_should_fix(self):
        """PASS with HIGH impact and LIKELY_TRUE should SHOULD_FIX."""
        action = recommend_action(Decision.PASS, ImpactLevel.HIGH, TruthAssessment.LIKELY_TRUE)
        assert action == RecommendedAction.SHOULD_FIX

    def test_pass_medium_should_fix(self):
        """PASS with MEDIUM impact should SHOULD_FIX."""
        action = recommend_action(Decision.PASS, ImpactLevel.MEDIUM, TruthAssessment.CONFIRMED)
        assert action == RecommendedAction.SHOULD_FIX

    def test_pass_low_consider_fix(self):
        """PASS with LOW impact should CONSIDER_FIX."""
        action = recommend_action(Decision.PASS, ImpactLevel.LOW, TruthAssessment.CONFIRMED)
        assert action == RecommendedAction.CONSIDER_FIX

    def test_pass_negligible_no_action(self):
        """PASS with NEGLIGIBLE impact should NO_ACTION."""
        action = recommend_action(Decision.PASS, ImpactLevel.NEGLIGIBLE, TruthAssessment.CONFIRMED)
        assert action == RecommendedAction.NO_ACTION


# ============================================================================
# Test Confidence Calculation
# ============================================================================
class TestConfidenceCalculation:
    """Test adjudication confidence calculation."""

    def test_conclusive_confirmed_high_confidence(self):
        """CONCLUSIVE evidence + CONFIRMED truth should have high confidence."""
        confidence = calculate_adjudication_confidence(
            EvidenceStrength.CONCLUSIVE,
            TruthAssessment.CONFIRMED,
            0.95,
        )
        assert confidence >= 0.90

    def test_insufficient_uncertain_low_confidence(self):
        """INSUFFICIENT evidence + UNCERTAIN truth should have low confidence."""
        confidence = calculate_adjudication_confidence(
            EvidenceStrength.INSUFFICIENT,
            TruthAssessment.UNCERTAIN,
            0.7,
        )
        assert confidence <= 0.50

    def test_weak_likely_false_moderate_confidence(self):
        """WEAK evidence + LIKELY_FALSE should have moderate confidence."""
        confidence = calculate_adjudication_confidence(
            EvidenceStrength.WEAK,
            TruthAssessment.LIKELY_FALSE,
            0.8,
        )
        assert 0.50 <= confidence <= 0.80


# ============================================================================
# Test Rule Decision Data Structure
# ============================================================================
class TestRuleDecision:
    """Test RuleDecision data structure."""

    def test_rule_decision_to_dict(self):
        """RuleDecision should convert to dict correctly."""
        decision = RuleDecision(
            finding_id="F-validation-E302-a1b2c3d4",
            decision=Decision.PASS,
            truth_assessment=TruthAssessment.CONFIRMED,
            impact_level=ImpactLevel.HIGH,
            evidence_strength=EvidenceStrength.STRONG,
            primary_basis=PrimaryBasis.SCHEMA_VALIDATION,
            largest_uncertainty=LargestUncertainty.NONE,
            recommended_action=RecommendedAction.MUST_FIX,
            adjudicated_at="2026-03-16T12:00:00Z",
            confidence=0.95,
            evidence_count=2,
            evidence_kinds=["FILE", "CODE_LOCATION"],
            has_strong_evidence=True,
        )

        result = decision.to_dict()

        assert result["finding_id"] == "F-validation-E302-a1b2c3d4"
        assert result["decision"] == "PASS"
        assert result["truth_assessment"] == "CONFIRMED"
        assert result["impact_level"] == "HIGH"
        assert result["evidence_strength"] == "STRONG"
        assert result["primary_basis"] == "SCHEMA_VALIDATION"
        assert result["largest_uncertainty"] == "NONE"
        assert result["recommended_action"] == "MUST_FIX"
        assert result["confidence"] == 0.95
        assert result["evidence_summary"]["evidence_count"] == 2
        assert result["evidence_summary"]["has_strong_evidence"] is True

    def test_rule_decision_with_waiver_reason(self):
        """RuleDecision with WAIVE should include waiver_reason."""
        decision = RuleDecision(
            finding_id="F-validation-E302-a1b2c3d4",
            decision=Decision.WAIVE,
            truth_assessment=TruthAssessment.FALSE_POSITIVE,
            impact_level=ImpactLevel.LOW,
            evidence_strength=EvidenceStrength.STRONG,
            primary_basis=PrimaryBasis.SCHEMA_VALIDATION,
            largest_uncertainty=LargestUncertainty.FALSE_POSITIVE_RISK,
            recommended_action=RecommendedAction.IGNORE_FALSE_POSITIVE,
            adjudicated_at="2026-03-16T12:00:00Z",
            waiver_reason=WaiverReason.FALSE_POSITIVE_CONFIRMED,
        )

        result = decision.to_dict()
        assert result["waiver_reason"] == "FALSE_POSITIVE_CONFIRMED"

    def test_rule_decision_with_defer_reason(self):
        """RuleDecision with DEFER should include defer_reason."""
        decision = RuleDecision(
            finding_id="F-validation-E302-a1b2c3d4",
            decision=Decision.DEFER,
            truth_assessment=TruthAssessment.UNCERTAIN,
            impact_level=ImpactLevel.MEDIUM,
            evidence_strength=EvidenceStrength.MODERATE,
            primary_basis=PrimaryBasis.PATTERN_MATCH,
            largest_uncertainty=LargestUncertainty.CONTEXT_DEPENDENT,
            recommended_action=RecommendedAction.DEFER_TO_OWNER,
            adjudicated_at="2026-03-16T12:00:00Z",
            defer_reason=DeferReason.CONTEXT_INCOMPLETE,
        )

        result = decision.to_dict()
        assert result["defer_reason"] == "CONTEXT_INCOMPLETE"


# ============================================================================
# Test Adjudicator
# ============================================================================
class TestAdjudicator:
    """Test Adjudicator class."""

    def test_adjudicator_initialization(self):
        """Adjudicator should initialize with config."""
        adjudicator = Adjudicator(evidence_threshold=0.7, confidence_threshold=0.8)
        assert adjudicator.evidence_threshold == 0.7
        assert adjudicator.confidence_threshold == 0.8
        assert adjudicator.t8_version == "1.0.0-t8"

    def test_adjudicate_finding_pass(self):
        """Adjudicator should produce PASS decision for confirmed finding with strong evidence."""
        finding = make_sample_finding(
            "F-validation-E302-a1b2c3d4",
            source_type="validation",
            category="schema_validation",
            severity="HIGH",
            confidence=0.98,
            evidence_refs=[
                {"kind": "FILE", "locator": "run/validation_report.json", "note": "T3 report"},
                {"kind": "CODE_LOCATION", "locator": "skill.py:42", "note": "Source location"},
            ],
        )

        adjudicator = Adjudicator()
        decision = adjudicator.adjudicate_finding(finding)

        assert decision.decision == Decision.PASS
        assert decision.truth_assessment == TruthAssessment.CONFIRMED
        assert decision.evidence_strength == EvidenceStrength.CONCLUSIVE
        assert decision.recommended_action == RecommendedAction.MUST_FIX

    def test_adjudicate_finding_fail_no_evidence(self):
        """T8 Hard Constraint: Finding without evidence should FAIL."""
        finding = make_sample_finding(
            "F-rule_scan-E420-1a2b3c4d",
            source_type="rule_scan",
            category="dangerous_pattern",
            severity="CRITICAL",
            confidence=0.9,
            evidence_refs=[],  # No evidence
        )

        adjudicator = Adjudicator()
        decision = adjudicator.adjudicate_finding(finding)

        assert decision.decision == Decision.FAIL
        assert decision.evidence_strength == EvidenceStrength.INSUFFICIENT
        assert decision.evidence_count == 0

    def test_adjudicate_finding_waive_false_positive(self):
        """Adjudicator should WAIVE likely false positive."""
        finding = make_sample_finding(
            "F-validation-E301-3c4d5e6f",
            source_type="validation",
            category="schema_validation",
            severity="LOW",
            confidence=0.7,
            evidence_refs=[
                {"kind": "LOG", "locator": "run/validation.log", "note": "Log entry"},
            ],
        )

        adjudicator = Adjudicator()
        decision = adjudicator.adjudicate_finding(finding)

        # WEAK evidence results in LIKELY_FALSE, which results in WAIVE
        assert decision.decision == Decision.WAIVE
        assert decision.truth_assessment in (TruthAssessment.LIKELY_FALSE, TruthAssessment.FALSE_POSITIVE)

    def test_adjudicate_finding_defer_uncertain(self):
        """Adjudicator should DEFER uncertain findings."""
        finding = make_sample_finding(
            "F-pattern_match-E500-2b3c4d5e",
            source_type="pattern_match",
            category="governance_gap",
            severity="MEDIUM",
            confidence=0.85,
            evidence_refs=[
                {"kind": "FILE", "locator": "run/pattern_report.json", "note": "T5 report"},
            ],
        )

        adjudicator = Adjudicator()
        decision = adjudicator.adjudicate_finding(finding)

        # Pattern match with single evidence is DEFER
        assert decision.decision == Decision.DEFER
        assert decision.defer_reason is not None


# ============================================================================
# Test Adjudication Report
# ============================================================================
class TestAdjudicationReport:
    """Test AdjudicationReport structure."""

    def test_report_to_dict(self):
        """AdjudicationReport should convert to dict correctly."""
        decisions = [
            RuleDecision(
                finding_id="F-validation-E302-a1b2c3d4",
                decision=Decision.PASS,
                truth_assessment=TruthAssessment.CONFIRMED,
                impact_level=ImpactLevel.HIGH,
                evidence_strength=EvidenceStrength.STRONG,
                primary_basis=PrimaryBasis.SCHEMA_VALIDATION,
                largest_uncertainty=LargestUncertainty.NONE,
                recommended_action=RecommendedAction.MUST_FIX,
                adjudicated_at="2026-03-16T12:00:00Z",
            ),
            RuleDecision(
                finding_id="F-rule_scan-E420-1a2b3c4d",
                decision=Decision.FAIL,
                truth_assessment=TruthAssessment.UNCERTAIN,
                impact_level=ImpactLevel.HIGH,
                evidence_strength=EvidenceStrength.INSUFFICIENT,
                primary_basis=PrimaryBasis.CODE_ANALYSIS,
                largest_uncertainty=LargestUncertainty.EVIDENCE_INCOMPLETE,
                recommended_action=RecommendedAction.ESCALATE_FOR_REVIEW,
                adjudicated_at="2026-03-16T12:00:00Z",
                evidence_count=0,
            ),
        ]

        report = AdjudicationReport(
            skill_id="skill-1.0.0-abc12345",
            skill_name="test_skill",
            generated_at="2026-03-16T12:00:00Z",
            run_id="20260316_120000",
            rule_decisions=decisions,
        )

        result = report.to_dict()

        assert result["meta"]["skill_id"] == "skill-1.0.0-abc12345"
        assert result["meta"]["t8_version"] == "1.0.0-t8"
        assert len(result["rule_decisions"]) == 2
        assert result["summary"]["total_decisions"] == 2
        assert result["summary"]["by_decision"]["PASS"] == 1
        assert result["summary"]["by_decision"]["FAIL"] == 1

    def test_report_summary_evidence_coverage(self):
        """Report summary should calculate evidence coverage correctly."""
        decisions = [
            RuleDecision(
                finding_id=f"F-test-E30{i}-hash",
                decision=Decision.PASS,
                truth_assessment=TruthAssessment.CONFIRMED,
                impact_level=ImpactLevel.HIGH,
                evidence_strength=EvidenceStrength.STRONG,
                primary_basis=PrimaryBasis.SCHEMA_VALIDATION,
                largest_uncertainty=LargestUncertainty.NONE,
                recommended_action=RecommendedAction.MUST_FIX,
                adjudicated_at="2026-03-16T12:00:00Z",
                evidence_count=2,
            )
            for i in range(8)  # 8 findings with evidence
        ] + [
            RuleDecision(
                finding_id="F-test-E308-noevidence",
                decision=Decision.FAIL,
                truth_assessment=TruthAssessment.UNCERTAIN,
                impact_level=ImpactLevel.HIGH,
                evidence_strength=EvidenceStrength.INSUFFICIENT,
                primary_basis=PrimaryBasis.SCHEMA_VALIDATION,
                largest_uncertainty=LargestUncertainty.EVIDENCE_INCOMPLETE,
                recommended_action=RecommendedAction.ESCALATE_FOR_REVIEW,
                adjudicated_at="2026-03-16T12:00:00Z",
                evidence_count=0,
            )
        ]

        report = AdjudicationReport(
            skill_id="skill-1.0.0-abc12345",
            skill_name="test_skill",
            generated_at="2026-03-16T12:00:00Z",
            run_id="20260316_120000",
            rule_decisions=decisions,
        )

        assert report.summary["evidence_coverage"]["findings_with_evidence"] == 8
        assert report.summary["evidence_coverage"]["findings_without_evidence"] == 1
        assert report.summary["evidence_coverage"]["coverage_percentage"] == 88.89

    def test_report_findings_requiring_attention(self):
        """Report should identify findings requiring attention."""
        decisions = [
            RuleDecision(
                finding_id="F-test-E301-pass",
                decision=Decision.PASS,
                truth_assessment=TruthAssessment.CONFIRMED,
                impact_level=ImpactLevel.MEDIUM,
                evidence_strength=EvidenceStrength.STRONG,
                primary_basis=PrimaryBasis.SCHEMA_VALIDATION,
                largest_uncertainty=LargestUncertainty.NONE,
                recommended_action=RecommendedAction.SHOULD_FIX,
                adjudicated_at="2026-03-16T12:00:00Z",
            ),
            RuleDecision(
                finding_id="F-test-E302-fail",
                decision=Decision.FAIL,
                truth_assessment=TruthAssessment.UNCERTAIN,
                impact_level=ImpactLevel.HIGH,
                evidence_strength=EvidenceStrength.INSUFFICIENT,
                primary_basis=PrimaryBasis.SCHEMA_VALIDATION,
                largest_uncertainty=LargestUncertainty.EVIDENCE_INCOMPLETE,
                recommended_action=RecommendedAction.ESCALATE_FOR_REVIEW,
                adjudicated_at="2026-03-16T12:00:00Z",
            ),
            RuleDecision(
                finding_id="F-test-E303-critical",
                decision=Decision.PASS,
                truth_assessment=TruthAssessment.CONFIRMED,
                impact_level=ImpactLevel.CRITICAL,
                evidence_strength=EvidenceStrength.STRONG,
                primary_basis=PrimaryBasis.SCHEMA_VALIDATION,
                largest_uncertainty=LargestUncertainty.NONE,
                recommended_action=RecommendedAction.MUST_FIX,
                adjudicated_at="2026-03-16T12:00:00Z",
            ),
        ]

        report = AdjudicationReport(
            skill_id="skill-1.0.0-abc12345",
            skill_name="test_skill",
            generated_at="2026-03-16T12:00:00Z",
            run_id="20260316_120000",
            rule_decisions=decisions,
        )

        attention_list = report.summary["findings_requiring_attention"]
        assert "F-test-E302-fail" in attention_list  # FAIL decision
        assert "F-test-E303-critical" in attention_list  # CRITICAL impact
        assert "F-test-E301-pass" not in attention_list


# ============================================================================
# Test Integration: adjudicate_findings_report
# ============================================================================
class TestAdjudicateFindingsReport:
    """Test the integration function."""

    def test_adjudicate_full_report(self):
        """Should adjudicate a full findings report."""
        findings_report = {
            "meta": {
                "skill_id": "skill-1.0.0-abc12345",
                "skill_name": "test_skill",
                "generated_at": "2026-03-16T12:00:00Z",
                "t6_version": "1.0.0-t6",
                "run_id": "20260316_120000",
            },
            "input_sources": {
                "validation_report": "run/T3_evidence/validation_report.json",
                "rule_scan_report": "run/T4_evidence/rule_scan_report.json",
                "pattern_detection_report": "run/T5_evidence/pattern_detection_report.json",
            },
            "findings": [
                make_sample_finding("F-validation-E302-a1b2c3d4"),
                make_sample_finding(
                    "F-rule_scan-E420-1a2b3c4d",
                    source_type="rule_scan",
                    category="dangerous_pattern",
                    severity="CRITICAL",
                    evidence_refs=[],
                ),
            ],
            "summary": {
                "total_findings": 2,
                "by_severity": {"CRITICAL": 1, "HIGH": 1, "MEDIUM": 0, "LOW": 0, "INFO": 0},
                "by_category": {"schema_validation": 1, "dangerous_pattern": 1},
                "by_source": {"validation": 1, "rule_scan": 1, "pattern_match": 0},
                "by_confidence": {"very_high (0.95-1.0)": 1, "high (0.85-0.95)": 1},
            },
        }

        report = adjudicate_findings_report(findings_report, run_id="20260316_120000")

        assert report.skill_id == "skill-1.0.0-abc12345"
        assert len(report.rule_decisions) == 2
        assert report.summary["total_decisions"] == 2

    def test_schema_validation_sample(self):
        """Load and validate the sample adjudication report."""
        sample_path = Path(__file__).parent / "t8_samples" / "sample_adjudication_report.json"

        if sample_path.exists():
            with open(sample_path, "r", encoding="utf-8") as f:
                sample = json.load(f)

            # Validate structure
            assert "meta" in sample
            assert "rule_decisions" in sample
            assert "summary" in sample
            assert sample["meta"]["t8_version"] == "1.0.0-t8"
            assert len(sample["rule_decisions"]) == 6


# ============================================================================
# Schema Validation Tests
# ============================================================================
class TestSchemaValidation:
    """Test that adjudication reports conform to schema."""

    def test_rule_decision_conforms_to_schema(self):
        """RuleDecision should produce output matching schema structure."""
        decision = RuleDecision(
            finding_id="F-validation-E302-a1b2c3d4",
            decision=Decision.PASS,
            truth_assessment=TruthAssessment.CONFIRMED,
            impact_level=ImpactLevel.HIGH,
            evidence_strength=EvidenceStrength.STRONG,
            primary_basis=PrimaryBasis.SCHEMA_VALIDATION,
            largest_uncertainty=LargestUncertainty.NONE,
            recommended_action=RecommendedAction.MUST_FIX,
            adjudicated_at="2026-03-16T12:00:00Z",
        )

        result = decision.to_dict()

        # Check required fields exist
        required_fields = [
            "finding_id",
            "decision",
            "truth_assessment",
            "impact_level",
            "evidence_strength",
            "primary_basis",
            "largest_uncertainty",
            "recommended_action",
            "adjudicated_at",
        ]
        for field in required_fields:
            assert field in result

        # Check enum values are valid
        assert result["decision"] in ["PASS", "FAIL", "WAIVE", "DEFER"]
        assert result["truth_assessment"] in [
            "CONFIRMED",
            "LIKELY_TRUE",
            "UNCERTAIN",
            "LIKELY_FALSE",
            "FALSE_POSITIVE",
        ]
        assert result["impact_level"] in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "NEGLIGIBLE"]
        assert result["evidence_strength"] in [
            "CONCLUSIVE",
            "STRONG",
            "MODERATE",
            "WEAK",
            "INSUFFICIENT",
        ]


# ============================================================================
# T8 Hard Constraint Tests
# ============================================================================
class TestT8HardConstraints:
    """Test T8 hard constraints."""

    def test_no_pass_without_evidence(self):
        """T8 Hard Constraint: No PASS decision without at least MODERATE evidence."""
        adjudicator = Adjudicator()

        # Finding with INSUFFICIENT evidence
        finding = make_sample_finding(
            "F-test-E301-noevidence",
            evidence_refs=[],
        )

        decision = adjudicator.adjudicate_finding(finding)
        assert decision.decision != Decision.PASS

        # Finding with WEAK evidence
        finding = make_sample_finding(
            "F-test-E302-weak",
            evidence_refs=[{"kind": "LOG", "locator": "log.txt", "note": "Log"}],
        )

        decision = adjudicator.adjudicate_finding(finding)
        assert decision.decision != Decision.PASS

    def test_all_structured_no_free_text(self):
        """T8 Hard Constraint: All decision fields must be structured enums."""
        decision = RuleDecision(
            finding_id="F-test-E301-test",
            decision=Decision.PASS,
            truth_assessment=TruthAssessment.CONFIRMED,
            impact_level=ImpactLevel.HIGH,
            evidence_strength=EvidenceStrength.STRONG,
            primary_basis=PrimaryBasis.SCHEMA_VALIDATION,
            largest_uncertainty=LargestUncertainty.NONE,
            recommended_action=RecommendedAction.MUST_FIX,
            adjudicated_at="2026-03-16T12:00:00Z",
        )

        result = decision.to_dict()

        # All key fields should be enum values, not free text
        assert isinstance(result["decision"], str)
        assert isinstance(result["truth_assessment"], str)
        assert isinstance(result["impact_level"], str)
        assert isinstance(result["evidence_strength"], str)
        assert isinstance(result["primary_basis"], str)
        assert isinstance(result["largest_uncertainty"], str)
        assert isinstance(result["recommended_action"], str)

    def test_deterministic_decisions(self):
        """T8 Hard Constraint: Same input should produce same decision."""
        adjudicator = Adjudicator()
        finding = make_sample_finding("F-test-E301-deterministic")

        decision1 = adjudicator.adjudicate_finding(finding)
        decision2 = adjudicator.adjudicate_finding(finding)

        assert decision1.decision == decision2.decision
        assert decision1.truth_assessment == decision2.truth_assessment
        assert decision1.evidence_strength == decision2.evidence_strength


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
