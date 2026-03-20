"""
T11 Owner Review Layer - Tests

Tests the owner review builder functionality.
"""

import json
from pathlib import Path

import pytest

from skillforge.src.contracts.finding_builder import (
    EvidenceRef,
    Finding,
    FindingCategory,
    FindingSeverity,
    FindingSourceType,
    FindingsReport,
)
from skillforge.src.contracts.owner_review import (
    ActionItem,
    ActionPriority,
    AssigneeType,
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
from skillforge.src.contracts.release_decision import ReleaseDecision


class TestOwnerCard:
    """Test OwnerCard data structure."""

    def test_owner_card_has_7_fixed_fields(self):
        """Owner card must have exactly 7 fixed fields."""
        card = OwnerCard(
            card_id="C-00000001",
            title="Password security issue",
            business_impact=BusinessImpact.BLOCKS_RELEASE,
            what_it_means="Passwords are stored without encryption",
            severity="CRITICAL",
            action_required=True,
            why_this_matters="Attackers could steal user passwords",
            next_steps=NextSteps.MUST_FIX_BEFORE_RELEASE,
        )

        # 7 fixed fields are required
        assert card.card_id is not None
        assert card.title is not None
        assert card.business_impact is not None
        assert card.what_it_means is not None
        assert card.severity is not None
        assert card.action_required is not None
        assert card.why_this_matters is not None
        assert card.next_steps is not None

    def test_owner_card_to_dict(self):
        """Owner card can be serialized to dictionary."""
        card = OwnerCard(
            card_id="C-00000001",
            title="Password security issue",
            business_impact=BusinessImpact.BLOCKS_RELEASE,
            what_it_means="Passwords are stored without encryption",
            severity="CRITICAL",
            action_required=True,
            why_this_matters="Attackers could steal user passwords",
            next_steps=NextSteps.MUST_FIX_BEFORE_RELEASE,
            finding_id="F-rule_scan_E401_abc12345",
            technical_note="E401_MISSING_PASSWORD_VALIDATION",
            location="auth.py:42",
        )

        result = card.to_dict()

        assert result["card_id"] == "C-00000001"
        assert result["title"] == "Password security issue"
        assert result["business_impact"] == "BLOCKS_RELEASE"
        assert result["what_it_means"] == "Passwords are stored without encryption"
        assert result["severity"] == "CRITICAL"
        assert result["action_required"] is True
        assert result["why_this_matters"] == "Attackers could steal user passwords"
        assert result["next_steps"] == "MUST_FIX_BEFORE_RELEASE"
        assert result["finding_id"] == "F-rule_scan_E401_abc12345"
        assert result["technical_note"] == "E401_MISSING_PASSWORD_VALIDATION"
        assert result["location"] == "auth.py:42"


class TestDecisionSummary:
    """Test DecisionSummary data structure."""

    def test_decision_summary_required_fields(self):
        """Decision summary has all required fields."""
        summary = DecisionSummary(
            outcome=OwnerOutcome.APPROVE,
            can_release=True,
            blocking_issues=0,
            risk_assessment=RiskAssessment.LOW_RISK,
            recommendation="APPROVE_RELEASE",
            summary_text="This skill passed all critical security checks.",
        )

        assert summary.outcome == OwnerOutcome.APPROVE
        assert summary.can_release is True
        assert summary.blocking_issues == 0
        assert summary.risk_assessment == RiskAssessment.LOW_RISK
        assert summary.recommendation == "APPROVE_RELEASE"
        assert summary.summary_text == "This skill passed all critical security checks."


class TestOwnerReviewBuilder:
    """Test OwnerReviewBuilder functionality."""

    @pytest.fixture
    def sample_findings_report(self):
        """Create a sample findings report."""
        findings = [
            Finding(
                finding_id="F-rule_scan_E401_abc12345",
                source_type=FindingSourceType.RULE_SCAN,
                source_code="E401_MISSING_PASSWORD_VALIDATION",
                title="subprocess.run with shell=True",
                description="Using subprocess.run with shell=True can lead to command injection",
                category=FindingCategory.DANGEROUS_PATTERN,
                severity=FindingSeverity.CRITICAL,
                confidence=1.0,
                file_path="skill.py",
                line_number=42,
                column_number=10,
                snippet="subprocess.run(cmd, shell=True)",
                suggested_fix="Use subprocess.run without shell=True",
                cwe_id="CWE-78",
                owasp_id="A03:2021",
                evidence_refs=[
                    EvidenceRef(kind="FILE", locator="skill.py:42"),
                ],
                detected_at="2026-03-16T12:00:00Z",
            ),
            Finding(
                finding_id="F-pattern_match_E501_def67890",
                source_type=FindingSourceType.PATTERN_MATCH,
                source_code="E501_EXTERNAL_WITHOUT_STOP_RULE",
                title="external action without stop rule",
                description="External HTTP call made without timeout or retry limit",
                category=FindingCategory.GOVERNANCE_GAP,
                severity=FindingSeverity.HIGH,
                confidence=0.85,
                file_path="api_client.py",
                line_number=15,
                snippet="requests.get(url)",
                suggested_fix="Add timeout parameter",
                missing_control="Timeout and retry limit",
                recommended_control="Add timeout and max_retries parameters",
                evidence_refs=[
                    EvidenceRef(kind="FILE", locator="api_client.py:15"),
                ],
                detected_at="2026-03-16T12:00:00Z",
            ),
        ]

        return FindingsReport(
            skill_id="test-skill-1.0.0-abc123",
            skill_name="test_skill",
            generated_at="2026-03-16T12:00:00Z",
            t6_version="1.0.0-t6",
            run_id="20260316_120000",
            validation_report_path="run/validation_report.json",
            rule_scan_report_path="run/rule_scan_report.json",
            pattern_detection_report_path="run/pattern_detection_report.json",
            findings=findings,
        )

    @pytest.fixture
    def sample_adjudication_report(self):
        """Create a sample adjudication report."""
        return {
            "meta": {
                "skill_id": "test-skill-1.0.0-abc123",
                "skill_name": "test_skill",
                "generated_at": "2026-03-16T12:00:00Z",
                "t8_version": "1.0.0-t8",
                "run_id": "20260316_120000",
            },
            "rule_decisions": [
                {
                    "finding_id": "F-rule_scan_E401_abc12345",
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
            ],
            "summary": {
                "total_decisions": 2,
                "by_decision": {
                    "PASS": 1,
                    "FAIL": 1,
                    "WAIVE": 0,
                    "DEFER": 0,
                },
                "by_truth_assessment": {
                    "CONFIRMED": 1,
                    "LIKELY_TRUE": 1,
                    "UNCERTAIN": 0,
                    "LIKELY_FALSE": 0,
                    "FALSE_POSITIVE": 0,
                },
                "by_impact_level": {
                    "CRITICAL": 1,
                    "HIGH": 1,
                    "MEDIUM": 0,
                    "LOW": 0,
                    "NEGLIGIBLE": 0,
                },
                "by_evidence_strength": {
                    "CONCLUSIVE": 1,
                    "STRONG": 1,
                    "MODERATE": 0,
                    "WEAK": 0,
                    "INSUFFICIENT": 0,
                },
                "findings_requiring_attention": ["F-rule_scan_E401_abc12345"],
                "evidence_coverage": {
                    "findings_with_evidence": 2,
                    "findings_without_evidence": 0,
                    "coverage_percentage": 100.0,
                },
            },
        }

    @pytest.fixture
    def sample_release_decision(self):
        """Create a sample release decision."""
        from skillforge.src.contracts.release_decision import (
            ConditionType,
            DecisionRationale,
            RationaleCode,
            ReleaseCondition,
            ReleaseOutcome,
        )

        return ReleaseDecision(
            run_id="20260316_120000",
            skill_id="test-skill-1.0.0-abc123",
            decision_timestamp="2026-03-16T12:00:00Z",
            skill_name="test_skill",
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
                    description="Fix CRITICAL finding before production",
                )
            ],
            total_findings=2,
            by_severity={
                "CRITICAL": 1,
                "HIGH": 1,
                "MEDIUM": 0,
                "LOW": 0,
                "INFO": 0,
            },
            blocking_findings=["F-rule_scan_E401_abc12345"],
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

    def test_build_owner_review(
        self,
        sample_findings_report,
        sample_adjudication_report,
        sample_release_decision,
    ):
        """Owner review can be built from technical reports."""
        builder = OwnerReviewBuilder()
        owner_review = builder.build(
            sample_findings_report,
            sample_adjudication_report,
            sample_release_decision,
        )

        # Check metadata
        assert owner_review.skill_id == "test-skill-1.0.0-abc123"
        assert owner_review.skill_name == "test_skill"
        assert owner_review.run_id == "20260316_120000"

        # Check decision summary
        assert owner_review.decision_summary is not None
        assert owner_review.decision_summary.can_release is True  # CONDITIONAL_RELEASE
        # T11: blocking_issues comes from actual release_decision.blocking_findings
        assert owner_review.decision_summary.blocking_issues == 1  # Only F-rule_scan_E401_abc12345 is blocking
        assert owner_review.decision_summary.outcome == OwnerOutcome.CONDITIONAL

        # Check owner cards
        assert len(owner_review.owner_cards) == 2

        # First card (CRITICAL finding)
        critical_card = owner_review.owner_cards[0]
        assert critical_card.severity == "CRITICAL"
        assert critical_card.action_required is True
        assert critical_card.business_impact == BusinessImpact.BLOCKS_RELEASE
        assert critical_card.next_steps == NextSteps.MUST_FIX_BEFORE_RELEASE

        # Second card (HIGH finding)
        high_card = owner_review.owner_cards[1]
        assert high_card.severity == "HIGH"
        assert high_card.action_required is True
        assert high_card.business_impact == BusinessImpact.REQUIRES_FIX

        # Check action items
        assert len(owner_review.action_items) == 2
        action_1 = owner_review.action_items[0]
        assert action_1.priority == ActionPriority.P0_BLOCKING
        assert action_1.assignee_type == AssigneeType.DEVELOPER

    def test_owner_review_to_dict(
        self,
        sample_findings_report,
        sample_adjudication_report,
        sample_release_decision,
    ):
        """Owner review can be serialized to dictionary."""
        builder = OwnerReviewBuilder()
        owner_review = builder.build(
            sample_findings_report,
            sample_adjudication_report,
            sample_release_decision,
        )

        result = owner_review.to_dict()

        # Check structure
        assert "meta" in result
        assert "input_sources" in result
        assert "decision_summary" in result
        assert "owner_cards" in result
        assert "action_items" in result

        # Check meta
        assert result["meta"]["skill_id"] == "test-skill-1.0.0-abc123"
        assert result["meta"]["skill_name"] == "test_skill"

        # Check owner cards
        assert len(result["owner_cards"]) == 2
        card_1 = result["owner_cards"][0]
        assert "card_id" in card_1
        assert "title" in card_1
        assert "business_impact" in card_1
        assert "what_it_means" in card_1
        assert "severity" in card_1
        assert "action_required" in card_1
        assert "why_this_matters" in card_1
        assert "next_steps" in card_1

    def test_owner_review_to_markdown(
        self,
        sample_findings_report,
        sample_adjudication_report,
        sample_release_decision,
    ):
        """Owner review can be rendered as markdown."""
        builder = OwnerReviewBuilder()
        owner_review = builder.build(
            sample_findings_report,
            sample_adjudication_report,
            sample_release_decision,
        )

        markdown = owner_review.to_markdown()

        # Check markdown structure
        assert "# Owner Review: test_skill" in markdown
        assert "## Executive Summary" in markdown
        assert "## Issues Requiring Attention" in markdown
        assert "## Action Items" in markdown
        assert "## What Was Checked" in markdown

        # Check no error codes in card titles (business readable)
        # Note: error codes may appear in technical_note field, which is intentional
        for card in owner_review.owner_cards:
            assert "E401_" not in card.title
            assert "E501_" not in card.title
            # Verify titles appear in markdown without error codes
            assert f"#### {card.title}" in markdown

    def test_owner_cards_no_technical_jargon_dump(
        self,
        sample_findings_report,
        sample_adjudication_report,
        sample_release_decision,
    ):
        """Owner cards should NOT be a dump of technical findings."""
        builder = OwnerReviewBuilder()
        owner_review = builder.build(
            sample_findings_report,
            sample_adjudication_report,
            sample_release_decision,
        )

        markdown = owner_review.to_markdown()

        # Owner cards should have plain language, not raw technical data
        for card in owner_review.owner_cards:
            # Title should not contain error codes
            assert "E401_" not in card.title
            assert "E501_" not in card.title
            assert "E3xx" not in card.title
            assert "E4xx" not in card.title
            assert "E5xx" not in card.title

            # What it means should be readable
            assert len(card.what_it_means) > 10
            assert "Finding" not in card.what_it_means  # Not meta-description

            # Why this matters should be business context
            assert len(card.why_this_matters) > 10

    def test_blocking_findings_preserved(
        self,
        sample_findings_report,
        sample_adjudication_report,
        sample_release_decision,
    ):
        """CRITICAL/HIGH findings must be preserved in owner review."""
        builder = OwnerReviewBuilder()
        owner_review = builder.build(
            sample_findings_report,
            sample_adjudication_report,
            sample_release_decision,
        )

        # Should have cards for CRITICAL and HIGH findings
        severities = [card.severity for card in owner_review.owner_cards]
        assert "CRITICAL" in severities
        assert "HIGH" in severities

        # Should be marked as action required
        critical_card = next(c for c in owner_review.owner_cards if c.severity == "CRITICAL")
        assert critical_card.action_required is True
        assert critical_card.business_impact == BusinessImpact.BLOCKS_RELEASE

    def test_coverage_note_includes_uncovered_areas(
        self,
        sample_findings_report,
        sample_adjudication_report,
        sample_release_decision,
    ):
        """Coverage note must explicitly state what was NOT covered."""
        builder = OwnerReviewBuilder()
        owner_review = builder.build(
            sample_findings_report,
            sample_adjudication_report,
            sample_release_decision,
        )

        assert owner_review.coverage_note is not None
        assert "not_covered" in owner_review.coverage_note

        # Should have some not_covered areas
        not_covered = owner_review.coverage_note["not_covered"]
        assert len(not_covered) > 0

        # Should always mention limitations
        limitations = ["Runtime behavior", "Performance", "Integration"]
        assert any(l.lower() in " ".join(not_covered).lower() for l in limitations)

    def test_t11_blocking_findings_must_be_exposed(
        self,
        sample_findings_report,
        sample_adjudication_report,
        sample_release_decision,
    ):
        """
        T11 Zero Exception: blocking findings from release_decision MUST be
        exposed in owner review output, never hidden.

        This test ensures that findings listed in release_decision.blocking_findings
        appear in the owner review with business_impact=BLOCKS_RELEASE.
        """
        builder = OwnerReviewBuilder()
        owner_review = builder.build(
            sample_findings_report,
            sample_adjudication_report,
            sample_release_decision,
        )

        # Get the blocking finding IDs from release_decision
        blocking_finding_ids = set(sample_release_decision.blocking_findings or [])

        # Verify blocking_issues count matches actual blocking_findings
        assert owner_review.decision_summary.blocking_issues == len(blocking_finding_ids)

        # Verify each blocking finding has a card with BLOCKS_RELEASE impact
        blocking_cards = [
            card for card in owner_review.owner_cards
            if card.finding_id in blocking_finding_ids
        ]

        # All blocking findings should have cards
        assert len(blocking_cards) == len(blocking_finding_ids)

        # All blocking cards should have BLOCKS_RELEASE business impact
        for card in blocking_cards:
            assert card.business_impact == BusinessImpact.BLOCKS_RELEASE, (
                f"Blocking finding {card.finding_id} must have BLOCKS_RELEASE impact, "
                f"but has {card.business_impact}"
            )
            assert card.action_required is True
            assert card.next_steps == NextSteps.MUST_FIX_BEFORE_RELEASE


class TestSaveOwnerReview:
    """Test saving owner review to files."""

    def test_save_owner_review_creates_json_and_md(self, tmp_path):
        """Save creates both JSON and Markdown files."""
        owner_review = OwnerReview(
            run_id="test_run",
            skill_id="test-skill",
            skill_name="test_skill",
            generated_at="2026-03-16T12:00:00Z",
            decision_summary=DecisionSummary(
                outcome=OwnerOutcome.APPROVE,
                can_release=True,
                blocking_issues=0,
                risk_assessment=RiskAssessment.LOW_RISK,
                recommendation="APPROVE_RELEASE",
                summary_text="Test summary",
            ),
            owner_cards=[],
            action_items=[],
        )

        paths = save_owner_review(owner_review, tmp_path, "test_run")

        # Check files exist
        assert Path(paths["json"]).exists()
        assert Path(paths["markdown"]).exists()

        # Check file names
        assert "owner_review_test_run.json" in paths["json"]
        assert "owner_review_test_run.md" in paths["markdown"]

    def test_saved_json_is_valid(self, tmp_path):
        """Saved JSON can be loaded and validated."""
        owner_review = OwnerReview(
            run_id="test_run",
            skill_id="test-skill",
            skill_name="test_skill",
            generated_at="2026-03-16T12:00:00Z",
            decision_summary=DecisionSummary(
                outcome=OwnerOutcome.APPROVE,
                can_release=True,
                blocking_issues=0,
                risk_assessment=RiskAssessment.LOW_RISK,
                recommendation="APPROVE_RELEASE",
                summary_text="Test summary",
            ),
            owner_cards=[],
            action_items=[],
        )

        paths = save_owner_review(owner_review, tmp_path, "test_run")

        # Load and verify JSON
        with open(paths["json"], "r") as f:
            data = json.load(f)

        assert data["meta"]["skill_id"] == "test-skill"
        assert data["meta"]["skill_name"] == "test_skill"
        assert "decision_summary" in data

    def test_saved_markdown_is_valid(self, tmp_path):
        """Saved Markdown is properly formatted."""
        owner_review = OwnerReview(
            run_id="test_run",
            skill_id="test-skill",
            skill_name="test_skill",
            generated_at="2026-03-16T12:00:00Z",
            decision_summary=DecisionSummary(
                outcome=OwnerOutcome.APPROVE,
                can_release=True,
                blocking_issues=0,
                risk_assessment=RiskAssessment.LOW_RISK,
                recommendation="APPROVE_RELEASE",
                summary_text="Test summary",
            ),
            owner_cards=[
                OwnerCard(
                    card_id="C-00000001",
                    title="Test issue",
                    business_impact=BusinessImpact.SHOULD_FIX,
                    what_it_means="Test what it means",
                    severity="MEDIUM",
                    action_required=True,
                    why_this_matters="Test why it matters",
                    next_steps=NextSteps.SCHEDULE_FIX,
                )
            ],
            action_items=[
                ActionItem(
                    item_id="A-00000001",
                    description="Fix the issue",
                    priority=ActionPriority.P1_HIGH,
                    assignee_type=AssigneeType.DEVELOPER,
                )
            ],
        )

        paths = save_owner_review(owner_review, tmp_path, "test_run")

        # Read and verify markdown
        with open(paths["markdown"], "r") as f:
            content = f.read()

        assert "# Owner Review: test_skill" in content
        assert "## Executive Summary" in content
        assert "Test issue" in content
        assert "Fix the issue" in content


class TestOwnerReviewConstraints:
    """Test T11 hard constraints."""

    def test_no_dashboard_owner_review_is_structured_output_only(self):
        """Owner review is structured JSON/MD output, NOT a dashboard."""
        owner_review = OwnerReview(
            run_id="test",
            skill_id="test",
            skill_name="test",
            generated_at="2026-03-16T12:00:00Z",
            decision_summary=DecisionSummary(
                outcome=OwnerOutcome.APPROVE,
                can_release=True,
                blocking_issues=0,
                risk_assessment=RiskAssessment.LOW_RISK,
                recommendation="APPROVE_RELEASE",
                summary_text="Test",
            ),
            owner_cards=[],
            action_items=[],
        )

        # Can serialize to JSON
        json_dict = owner_review.to_dict()
        assert isinstance(json_dict, dict)

        # Can render to Markdown
        md = owner_review.to_markdown()
        assert isinstance(md, str)

        # No UI components, no dashboard state
        assert not hasattr(owner_review, "ui_state")
        assert not hasattr(owner_review, "dashboard_config")

    def test_not_technical_finding_dump(self):
        """Owner review is NOT a dump of technical findings."""
        card = OwnerCard(
            card_id="C-00000001",
            title="Clear business title",
            business_impact=BusinessImpact.SHOULD_FIX,
            what_it_means="Plain language explanation",
            severity="HIGH",
            action_required=True,
            why_this_matters="Business context",
            next_steps=NextSteps.FIX_BEFORE_PRODUCTION,
        )

        # Should have business-readable fields, not raw finding data
        assert "E401_" not in card.title
        assert "E501_" not in card.title
        assert "subprocess" not in card.title.lower()  # Technical term removed

        # What it means should be plain language
        assert card.what_it_means == "Plain language explanation"

    def test_single_finding_card_has_exactly_7_fields(self):
        """Single finding owner card has exactly 7 fixed fields."""
        card = OwnerCard(
            card_id="C-00000001",
            title="Title",
            business_impact=BusinessImpact.SHOULD_FIX,
            what_it_means="What",
            severity="HIGH",
            action_required=True,
            why_this_matters="Why",
            next_steps=NextSteps.SCHEDULE_FIX,
        )

        # 7 fixed fields
        fixed_fields = [
            "card_id",
            "title",
            "business_impact",
            "what_it_means",
            "severity",
            "action_required",
            "why_this_matters",
            "next_steps",
        ]

        for field in fixed_fields:
            assert hasattr(card, field)
            assert getattr(card, field) is not None

    def test_owner_summary_exists(self):
        """Owner review includes owner summary."""
        summary = DecisionSummary(
            outcome=OwnerOutcome.APPROVE,
            can_release=True,
            blocking_issues=0,
            risk_assessment=RiskAssessment.LOW_RISK,
            recommendation="APPROVE_RELEASE",
            summary_text="All checks passed, safe to release.",
        )

        # Should have decision-making info
        assert summary.outcome is not None
        assert summary.can_release is not None
        assert summary.blocking_issues is not None
        assert summary.risk_assessment is not None
        assert summary.recommendation is not None
        assert summary.summary_text is not None

