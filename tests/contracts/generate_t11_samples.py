"""
T11 Owner Review - Sample Generator (Simplified)

Generates sample owner_review.json and owner_review.md files.
"""
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, "skillforge/src")

from skillforge.src.contracts.finding_builder import (
    EvidenceRef,
    Finding,
    FindingCategory,
    FindingSeverity,
    FindingSourceType,
    FindingsReport,
)
from skillforge.src.contracts.owner_review import (
    BusinessImpact,
    DecisionSummary,
    NextSteps,
    OwnerCard,
    OwnerOutcome,
    OwnerReview,
    OwnerReviewBuilder,
    RiskAssessment,
    save_owner_review,
)
from skillforge.src.contracts.release_decision import (
    ConditionType,
    DecisionRationale,
    RationaleCode,
    ReleaseCondition,
    ReleaseDecision,
    ReleaseOutcome,
)


def create_sample_findings_report():
    """Create a sample findings report."""
    findings = [
        # CRITICAL - subprocess with shell=True
        Finding(
            finding_id="F-rule_scan_E405_abc12345",
            source_type=FindingSourceType.RULE_SCAN,
            source_code="E405_SUBPROCESS_SHELL",
            title="subprocess.run with shell=True",
            description="Using subprocess.run with shell=True can lead to command injection",
            category=FindingCategory.DANGEROUS_PATTERN,
            severity=FindingSeverity.CRITICAL,
            confidence=1.0,
            file_path="skillforge/src/skills/quant/execute.py",
            line_number=42,
            snippet="subprocess.run(cmd, shell=True)",
            suggested_fix="Use subprocess.run without shell=True",
            cwe_id="CWE-78",
            owasp_id="A03:2021",
            evidence_refs=[
                EvidenceRef(
                    kind="FILE",
                    locator="skillforge/src/skills/quant/execute.py:42",
                )
            ],
        ),
        # HIGH - external action without stop rule
        Finding(
            finding_id="F-pattern_match_E501_def67890",
            source_type=FindingSourceType.PATTERN_MATCH,
            source_code="E501_EXTERNAL_WITHOUT_STOP_RULE",
            title="external action without stop rule",
            description="External HTTP call made without timeout or retry limit",
            category=FindingCategory.GOVERNANCE_GAP,
            severity=FindingSeverity.HIGH,
            confidence=0.85,
            file_path="skillforge/src/skills/quant/api_client.py",
            line_number=15,
            snippet="requests.get(url)",
            missing_control="Timeout and retry limit",
            recommended_control="Add timeout and max_retries parameters",
            evidence_refs=[
                EvidenceRef(
                    kind="FILE",
                    locator="skillforge/src/skills/quant/api_client.py:15",
                )
            ],
        ),
        # MEDIUM - missing audit event
        Finding(
            finding_id="F-pattern_match_E504_ghi12345",
            source_type=FindingSourceType.PATTERN_MATCH,
            source_code="E504_MISSING_AUDITABLE_EXIT",
            title="missing auditable exit",
            description="Function execute_market_order performs critical action without audit logging",
            category=FindingCategory.GOVERNANCE_GAP,
            severity=FindingSeverity.MEDIUM,
            confidence=0.85,
            file_path="skillforge/src/skills/quant/trading.py",
            line_number=88,
            function_name="execute_market_order",
            snippet="def execute_market_order(symbol, quantity):",
            missing_control="Audit logging for critical trading actions",
            recommended_control="Log all order executions with timestamp and parameters",
            evidence_refs=[
                EvidenceRef(
                    kind="FILE",
                    locator="skillforge/src/skills/quant/trading.py:88",
                )
            ],
        ),
    ]

    report = FindingsReport(
        skill_id="quant-skill-1.0.0-abc123",
        skill_name="quant",
        generated_at="2026-03-16T12:00:00Z",
        run_id="20260316_120000",
        findings=findings,
    )

    return report


def create_sample_adjudication_report():
    """Create a sample adjudication report."""
    return {
        "meta": {
            "skill_id": "quant-skill-1.0.0-abc123",
            "skill_name": "quant",
            "generated_at": "2026-03-16T12:00:00Z",
            "t8_version": "1.0.0-t8",
            "run_id": "20260316_120000",
        },
        "rule_decisions": [
            {
                "finding_id": "F-rule_scan_E405_abc12345",
                "decision": "FAIL",
                "truth_assessment": "CONFIRMED",
                "impact_level": "CRITICAL",
                "evidence_strength": "CONCLUSIVE",
                "primary_basis": "SECURITY_RULE",
                "largest_uncertainty": "NONE",
                "recommended_action": "MUST_FIX",
                "adjudicated_at": "2026-03-16T12:00:00Z",
            },
            {
                "finding_id": "F-pattern_match_E501_def67890",
                "decision": "PASS",
                "truth_assessment": "LIKELY_TRUE",
                "impact_level": "HIGH",
                "evidence_strength": "STRONG",
                "primary_basis": "GOVERNANCE_GAP",
                "largest_uncertainty": "CONTEXT_DEPENDENT",
                "recommended_action": "SHOULD_FIX",
                "adjudicated_at": "2026-03-16T12:00:00Z",
            },
            {
                "finding_id": "F-pattern_match_E504_ghi12345",
                "decision": "PASS",
                "truth_assessment": "LIKELY_TRUE",
                "impact_level": "MEDIUM",
                "evidence_strength": "MODERATE",
                "primary_basis": "GOVERNANCE_GAP",
                "largest_uncertainty": "CONTEXT_DEPENDENT",
                "recommended_action": "CONSIDER_FIX",
                "adjudicated_at": "2026-03-16T12:00:00Z",
            },
        ],
        "summary": {
            "total_decisions": 3,
            "by_decision": {
                "PASS": 2,
                "FAIL": 1,
                "WAIVE": 0,
                "DEFER": 0,
            },
            "by_truth_assessment": {
                "CONFIRMED": 1,
                "LIKELY_TRUE": 2,
                "UNCERTAIN": 0,
                "LIKELY_FALSE": 0,
                "FALSE_POSITIVE": 0,
            },
            "by_impact_level": {
                "CRITICAL": 1,
                "HIGH": 1,
                "MEDIUM": 1,
                "LOW": 0,
                "NEGLIGIBLE": 0,
            },
            "by_evidence_strength": {
                "CONCLUSIVE": 1,
                "STRONG": 1,
                "MODERATE": 1,
                "WEAK": 0,
                "INSUFFICIENT": 0,
            },
            "findings_requiring_attention": ["F-rule_scan_E405_abc12345"],
            "evidence_coverage": {
                "findings_with_evidence": 3,
                "findings_without_evidence": 0,
                "coverage_percentage": 100.0,
            },
        },
    }


def create_sample_release_decision():
    """Create a sample release decision."""
    return ReleaseDecision(
        run_id="20260316_120000",
        skill_id="quant-skill-1.0.0-abc123",
        decision_timestamp="2026-03-16T12:00:00Z",
        skill_name="quant",
        outcome=ReleaseOutcome.CONDITIONAL_RELEASE,
        rationale=DecisionRationale(
            code=RationaleCode.CONDITIONAL_ACCEPTANCE,
            blocking_findings_count=1,
            overrides_count=0,
        ),
        is_final=True,
        conditions=[
            ReleaseCondition(
                type=ConditionType.REMEDIATION_DEADLINE,
                description="Fix CRITICAL security finding before production deployment",
            )
        ],
        total_findings=3,
        by_severity={
            "CRITICAL": 1,
            "HIGH": 1,
            "MEDIUM": 1,
            "LOW": 0,
            "INFO": 0,
        },
        blocking_findings=["F-rule_scan_E405_abc12345"],
        overrides_applied=[],
        residual_risks={
            "total_risks": 0,
            "risk_ids": [],
            "by_level": {
                "CRITICAL": 0,
                "HIGH": 0,
                "MEDIUM": 0,
                "LOW": 0,
            },
        },
    )


def main():
    """Generate sample owner review files."""
    print("=" * 70)
    print("T11 Owner Review - Sample Generator")
    print("=" * 70)
    print()

    # Create sample inputs
    print("Creating sample inputs...")
    findings_report = create_sample_findings_report()
    adjudication_report = create_sample_adjudication_report()
    release_decision = create_sample_release_decision()

    # Build owner review
    print("Building owner review...")
    builder = OwnerReviewBuilder()
    owner_review = builder.build(
        findings_report,
        adjudication_report,
        release_decision,
    )

    # Save to files
    output_dir = Path("run/T11_evidence")
    print(f"Saving to {output_dir}...")

    paths = save_owner_review(owner_review, output_dir, "sample")

    print()
    print("✅ Sample owner review generated successfully!")
    print()
    print(f"JSON output: {paths['json']}")
    print(f"Markdown output: {paths['markdown']}")
    print()
    print("Summary:")
    print(f"  Outcome: {owner_review.decision_summary.outcome.value}")
    print(f"  Can Release: {owner_review.decision_summary.can_release}")
    print(f"  Risk Level: {owner_review.decision_summary.risk_assessment.value}")
    print(f"  Blocking Issues: {owner_review.decision_summary.blocking_issues}")
    print(f"  Owner Cards: {len(owner_review.owner_cards)}")
    print(f"  Action Items: {len(owner_review.action_items)}")
    print()

    # Print markdown preview
    print("=" * 70)
    print("Markdown Preview:")
    print("=" * 70)
    print()
    print(owner_review.to_markdown())
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
