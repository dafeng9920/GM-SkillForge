"""
Owner Review Builder - T11 Deliverable

Converts technical findings and adjudication into business-readable owner review.
Two-layer report: JSON structure + Markdown rendering.

Key Design:
- Single finding owner card with 7 fixed fields
- Owner summary for decision-making
- NO technical jargon dump
- NO dashboard (structured output only)

T11 硬约束:
- 不做大 dashboard
- 不把 owner review 写成技术原始日志堆叠
- owner review 不得丢失 blocking findings
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from skillforge.src.contracts.finding_builder import (
    Finding,
    FindingCategory,
    FindingsReport,
    FindingSeverity,
    FindingSourceType,
)
from skillforge.src.contracts.release_decision import ReleaseDecision


class BusinessImpact(str, Enum):
    """Business impact category for owner cards."""
    BLOCKS_RELEASE = "BLOCKS_RELEASE"
    REQUIRES_FIX = "REQUIRES_FIX"
    SHOULD_FIX = "SHOULD_FIX"
    NICE_TO_HAVE = "NICE_TO_HAVE"
    ACKNOWLEDGE_ONLY = "ACKNOWLEDGE_ONLY"


class OwnerOutcome(str, Enum):
    """Simplified outcome for owner consumption."""
    APPROVE = "APPROVE"
    CONDITIONAL = "CONDITIONAL"
    ESCALATE = "ESCALATE"
    REJECT = "REJECT"


class RiskAssessment(str, Enum):
    """Overall risk assessment."""
    LOW_RISK = "LOW_RISK"
    MEDIUM_RISK = "MEDIUM_RISK"
    HIGH_RISK = "HIGH_RISK"
    CRITICAL_RISK = "CRITICAL_RISK"


class NextSteps(str, Enum):
    """Clear next steps for owner/team."""
    MUST_FIX_BEFORE_RELEASE = "MUST_FIX_BEFORE_RELEASE"
    FIX_BEFORE_PRODUCTION = "FIX_BEFORE_PRODUCTION"
    DOCUMENT_AND_MONITOR = "DOCUMENT_AND_MONITOR"
    SCHEDULE_FIX = "SCHEDULE_FIX"
    ACCEPT_RISK = "ACCEPT_RISK"
    ESCALATE_FOR_DECISION = "ESCALATE_FOR_DECISION"


class ActionPriority(str, Enum):
    """Action item priority."""
    P0_BLOCKING = "P0_BLOCKING"
    P1_HIGH = "P1_HIGH"
    P2_MEDIUM = "P2_MEDIUM"
    P3_LOW = "P3_LOW"


class AssigneeType(str, Enum):
    """Type of assignee for action items."""
    DEVELOPER = "DEVELOPER"
    SECURITY_TEAM = "SECURITY_TEAM"
    OWNER = "OWNER"
    ARCHITECT = "ARCHITECT"
    EXTERNAL = "EXTERNAL"


@dataclass
class OwnerCard:
    """Owner Card - 7 fixed fields. Business-readable format."""

    card_id: str
    title: str
    business_impact: BusinessImpact
    what_it_means: str
    severity: str
    action_required: bool
    why_this_matters: str
    next_steps: NextSteps

    # Optional fields for traceability
    finding_id: Optional[str] = None
    technical_note: Optional[str] = None
    location: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "card_id": self.card_id,
            "finding_id": self.finding_id,
            "title": self.title,
            "business_impact": self.business_impact.value,
            "what_it_means": self.what_it_means,
            "severity": self.severity,
            "action_required": self.action_required,
            "why_this_matters": self.why_this_matters,
            "next_steps": self.next_steps.value,
            "technical_note": self.technical_note,
            "location": self.location,
        }


@dataclass
class ActionItem:
    """Actionable item derived from findings."""

    item_id: str
    description: str
    priority: ActionPriority
    assignee_type: AssigneeType
    linked_cards: list[str] = field(default_factory=list)
    deadline: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "item_id": self.item_id,
            "description": self.description,
            "priority": self.priority.value,
            "assignee_type": self.assignee_type.value,
            "linked_cards": self.linked_cards,
            "deadline": self.deadline,
        }


@dataclass
class DecisionSummary:
    """High-level summary for owner decision-making."""

    outcome: OwnerOutcome
    can_release: bool
    blocking_issues: int
    risk_assessment: RiskAssessment
    recommendation: str
    summary_text: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "outcome": self.outcome.value,
            "can_release": self.can_release,
            "blocking_issues": self.blocking_issues,
            "risk_assessment": self.risk_assessment.value,
            "recommendation": self.recommendation,
            "summary_text": self.summary_text,
        }


@dataclass
class OwnerReview:
    """Owner Review - T11 main deliverable."""

    # Metadata
    run_id: str
    skill_id: str
    skill_name: str
    generated_at: str
    t11_version: str = "1.0.0-t11"
    reviewer: str = "Tech Lead"

    # Input source references
    findings_report_path: Optional[str] = None
    adjudication_report_path: Optional[str] = None
    release_decision_path: Optional[str] = None
    coverage_statement_path: Optional[str] = None

    # Owner review content
    decision_summary: Optional[DecisionSummary] = None
    owner_cards: list[OwnerCard] = field(default_factory=list)
    coverage_note: Optional[dict[str, Any]] = None
    action_items: list[ActionItem] = field(default_factory=list)
    overrides_summary: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "meta": {
                "run_id": self.run_id,
                "skill_id": self.skill_id,
                "skill_name": self.skill_name,
                "generated_at": self.generated_at,
                "t11_version": self.t11_version,
                "reviewer": self.reviewer,
            },
            "input_sources": {
                "findings_report": self.findings_report_path,
                "adjudication_report": self.adjudication_report_path,
                "release_decision": self.release_decision_path,
                "coverage_statement": self.coverage_statement_path,
            },
            "decision_summary": self.decision_summary.to_dict() if self.decision_summary else None,
            "owner_cards": [card.to_dict() for card in self.owner_cards],
            "action_items": [item.to_dict() for item in self.action_items],
        }

        if self.coverage_note:
            result["coverage_note"] = self.coverage_note
        if self.overrides_summary:
            result["overrides_summary"] = self.overrides_summary

        return result

    def to_markdown(self) -> str:
        """Generate owner review as markdown document."""
        lines = []

        # Title
        lines.append(f"# Owner Review: {self.skill_name}")
        lines.append(f"**Generated**: {self.generated_at}")
        lines.append(f"**Run ID**: {self.run_id}")
        lines.append("")

        # Decision Summary
        if self.decision_summary:
            ds = self.decision_summary
            lines.append("## Executive Summary")
            lines.append(f"**Outcome**: {ds.outcome.value}")
            lines.append(f"**Can Release**: {'Yes' if ds.can_release else 'No'}")
            lines.append(f"**Risk Level**: {ds.risk_assessment.value}")
            lines.append(f"**Blocking Issues**: {ds.blocking_issues}")
            lines.append("")
            lines.append(f"**Summary**: {ds.summary_text}")
            lines.append("")

        # Owner Cards
        if self.owner_cards:
            lines.append("## Issues Requiring Attention")
            lines.append("")

            # Group by business impact
            blocking = [c for c in self.owner_cards if c.business_impact == BusinessImpact.BLOCKS_RELEASE]
            requires_fix = [c for c in self.owner_cards if c.business_impact == BusinessImpact.REQUIRES_FIX]
            should_fix = [c for c in self.owner_cards if c.business_impact == BusinessImpact.SHOULD_FIX]

            if blocking:
                lines.append("### 🔴 Blocking Release")
                for card in blocking:
                    lines.extend(self._card_to_markdown(card))
                    lines.append("")

            if requires_fix:
                lines.append("### 🟠 Requires Fix")
                for card in requires_fix:
                    lines.extend(self._card_to_markdown(card))
                    lines.append("")

            if should_fix:
                lines.append("### 🟡 Should Fix")
                for card in should_fix:
                    lines.extend(self._card_to_markdown(card))
                    lines.append("")

        # Action Items
        if self.action_items:
            lines.append("## Action Items")
            lines.append("")

            for item in sorted(self.action_items, key=lambda x: x.priority.value):
                lines.append(f"- **[{item.priority.value}]** {item.description}")
                if item.deadline:
                    lines.append(f"  - Deadline: {item.deadline}")
                if item.assignee_type:
                    lines.append(f"  - Assignee: {item.assignee_type.value}")
            lines.append("")

        # Coverage Note
        if self.coverage_note:
            lines.append("## What Was Checked")
            lines.append("")

            covered = self.coverage_note.get("covered_areas", [])
            if covered:
                lines.append("**Covered Areas**:")
                for area in covered:
                    lines.append(f"- ✅ {area}")
                lines.append("")

            not_covered = self.coverage_note.get("not_covered", [])
            if not_covered:
                lines.append("**NOT Covered**:")
                for area in not_covered:
                    lines.append(f"- ❌ {area}")
                lines.append("")

            confidence = self.coverage_note.get("confidence_level")
            if confidence:
                lines.append(f"**Confidence Level**: {confidence}")
                lines.append("")

        # Overrides Summary
        if self.overrides_summary:
            lines.append("## Overrides Applied")
            lines.append("")
            total = self.overrides_summary.get("total_overrides", 0)
            lines.append(f"**Total Overrides**: {total}")
            lines.append("")

            reasons = self.overrides_summary.get("override_reasons", [])
            if reasons:
                lines.append("**Reasons**:")
                for reason in reasons:
                    lines.append(f"- {reason}")
                lines.append("")

        return "\n".join(lines)

    def _card_to_markdown(self, card: OwnerCard) -> list[str]:
        """Convert an owner card to markdown format."""
        lines = []
        lines.append(f"#### {card.title}")
        lines.append("")
        lines.append(f"**Severity**: {card.severity} | **Action Required**: {'Yes' if card.action_required else 'No'}")
        lines.append("")
        lines.append(f"**What it means**: {card.what_it_means}")
        lines.append("")
        lines.append(f"**Why this matters**: {card.why_this_matters}")
        lines.append("")
        lines.append(f"**Next steps**: {card.next_steps.value}")

        if card.location:
            lines.append(f"**Location**: `{card.location}`")

        if card.technical_note:
            lines.append(f"**Technical note**: {card.technical_note}")

        return lines


class OwnerReviewBuilder:
    """Builds owner review from technical findings and adjudication."""

    def __init__(self, t11_version: str = "1.0.0-t11"):
        self.t11_version = t11_version
        self._card_counter = 0
        self._action_counter = 0

    def build(
        self,
        findings_report: FindingsReport,
        adjudication_report: dict[str, Any],
        release_decision: ReleaseDecision,
        coverage_statement: Optional[dict[str, Any]] = None,
    ) -> OwnerReview:
        """Build owner review from technical reports.

        Args:
            findings_report: T6 findings report
            adjudication_report: T8 adjudication report
            release_decision: T10 release decision
            coverage_statement: T9 coverage statement (optional)

        Returns:
            OwnerReview with owner cards and summary

        T11 Zero Exception: blocking_findings from release_decision MUST be
        explicitly exposed in owner review output.
        """
        skill_id = findings_report.skill_id
        skill_name = findings_report.skill_name
        run_id = findings_report.run_id

        # Build decision summary from release decision
        decision_summary = self._build_decision_summary(
            findings_report, adjudication_report, release_decision
        )

        # Build owner cards from significant findings
        # T11: Must include release_decision to check blocking_findings
        owner_cards = self._build_owner_cards(
            findings_report, adjudication_report, release_decision
        )

        # Build coverage note
        coverage_note = self._build_coverage_note(
            findings_report, coverage_statement
        )

        # Build action items
        action_items = self._build_action_items(owner_cards)

        # Build overrides summary
        overrides_summary = self._build_overrides_summary(release_decision)

        return OwnerReview(
            run_id=run_id,
            skill_id=skill_id,
            skill_name=skill_name,
            generated_at=datetime.now().isoformat(),
            t11_version=self.t11_version,
            findings_report_path="findings.json",
            adjudication_report_path="adjudication_report.json",
            release_decision_path="release_decision.json",
            coverage_statement_path="coverage_statement.json",
            decision_summary=decision_summary,
            owner_cards=owner_cards,
            coverage_note=coverage_note,
            action_items=action_items,
            overrides_summary=overrides_summary,
        )

    def _build_decision_summary(
        self,
        findings_report: FindingsReport,
        adjudication_report: dict[str, Any],
        release_decision: ReleaseDecision,
    ) -> DecisionSummary:
        """Build high-level decision summary for owner.

        T11 Zero Exception: blocking_issues MUST come from actual
        release_decision.blocking_findings list, not a severity approximation.
        """

        # Determine outcome from release decision
        outcome_map = {
            "RELEASE": OwnerOutcome.APPROVE,
            "CONDITIONAL_RELEASE": OwnerOutcome.CONDITIONAL,
            "LIMITED_RELEASE": OwnerOutcome.CONDITIONAL,
            "ESCALATE": OwnerOutcome.ESCALATE,
            "REJECT": OwnerOutcome.REJECT,
        }

        decision_outcome = release_decision.outcome.value
        outcome = outcome_map.get(decision_outcome, OwnerOutcome.ESCALATE)

        # T11 Critical: blocking_issues from actual release_decision.blocking_findings
        # NOT a severity-based approximation
        blocking_issues = len(release_decision.blocking_findings or [])

        # Determine risk assessment
        adjudication_summary = adjudication_report.get("summary", {})
        critical_impact = adjudication_summary.get("by_impact_level", {}).get("CRITICAL", 0)
        high_impact = adjudication_summary.get("by_impact_level", {}).get("HIGH", 0)

        if critical_impact > 0:
            risk_assessment = RiskAssessment.CRITICAL_RISK
        elif high_impact > 2:
            risk_assessment = RiskAssessment.HIGH_RISK
        elif high_impact > 0 or blocking_issues > 0:
            risk_assessment = RiskAssessment.MEDIUM_RISK
        else:
            risk_assessment = RiskAssessment.LOW_RISK

        # Build recommendation
        if outcome == OwnerOutcome.APPROVE:
            recommendation = "APPROVE_RELEASE"
        elif outcome == OwnerOutcome.CONDITIONAL:
            recommendation = "APPROVE_WITH_MONITORING"
        elif blocking_issues > 0:
            recommendation = "REQUEST_CHANGES"
        elif critical_impact > 0:
            recommendation = "ESCALATE_TO_SECURITY"
        else:
            recommendation = "REJECT"

        # Build summary text (plain language, no jargon)
        total_findings = findings_report.summary.get("total_findings", 0)
        if blocking_issues == 0:
            summary_text = (
                f"This skill passed all critical security checks. "
                f"{total_findings} minor issues found."
            )
        else:
            summary_text = (
                f"This skill has {blocking_issues} issues that need attention "
                f"before it can be released safely."
            )

        can_release = outcome in [OwnerOutcome.APPROVE, OwnerOutcome.CONDITIONAL]

        return DecisionSummary(
            outcome=outcome,
            can_release=can_release,
            blocking_issues=blocking_issues,
            risk_assessment=risk_assessment,
            recommendation=recommendation,
            summary_text=summary_text,
        )

    def _build_owner_cards(
        self,
        findings_report: FindingsReport,
        adjudication_report: dict[str, Any],
        release_decision: ReleaseDecision,
    ) -> list[OwnerCard]:
        """Build owner cards from significant findings.

        Only create cards for findings that matter to owners:
        - CRITICAL/HIGH severity
        - FAIL decision from adjudication
        - Significant governance gaps

        T11 Zero Exception: blocking_findings from release_decision MUST be
        explicitly exposed in owner cards, never hidden.
        """
        cards = []

        # Get rule decisions for reference
        rule_decisions = adjudication_report.get("rule_decisions", [])
        decision_map = {
            d["finding_id"]: d
            for d in rule_decisions
        }

        # T11 Critical: Get blocking findings from release_decision
        # These MUST be exposed in owner review - Zero Exception
        blocking_finding_ids = set(release_decision.blocking_findings or [])

        # Track which findings have been added as cards
        added_finding_ids = set()

        for finding in findings_report.findings:
            # T11 Zero Exception: blocking findings ALWAYS get a card
            # regardless of severity or decision outcome
            is_blocking = finding.finding_id in blocking_finding_ids

            # Skip INFO/LOW severity findings for owner review
            # (unless they have FAIL decision or are blocking)
            severity = finding.severity.value
            decision = decision_map.get(finding.finding_id, {})
            decision_outcome = decision.get("decision", "PASS")

            if not is_blocking:
                if severity == "INFO":
                    continue
                if severity == "LOW" and decision_outcome != "FAIL":
                    continue

            card = self._finding_to_owner_card(finding, decision, is_blocking)
            if card:
                cards.append(card)
                added_finding_ids.add(finding.finding_id)

        # T11 Verification: Ensure all blocking findings have cards
        missing_blocking = blocking_finding_ids - added_finding_ids
        if missing_blocking:
            # Find the findings data for missing blocking ones
            for finding in findings_report.findings:
                if finding.finding_id in missing_blocking:
                    # Create card for blocking finding even if it would normally be skipped
                    decision = decision_map.get(finding.finding_id, {})
                    card = self._finding_to_owner_card(finding, decision, is_blocking=True)
                    if card:
                        cards.append(card)

        return cards

    def _finding_to_owner_card(
        self,
        finding: Finding,
        decision: dict[str, Any],
        is_blocking: bool = False,
    ) -> Optional[OwnerCard]:
        """Convert a technical finding to an owner card.

        Args:
            finding: The technical finding
            decision: Adjudication decision for this finding
            is_blocking: Whether this finding is in release_decision.blocking_findings
                         (T11: overrides normal business impact calculation)

        Returns:
            OwnerCard or None if no card should be created
        """

        # Generate card ID
        self._card_counter += 1
        card_id = f"C-{self._card_counter:08d}"

        # Build plain-language title (no error codes)
        title = self._plain_language_title(finding)

        # Determine business impact (T11: is_blocking takes precedence)
        business_impact = self._determine_business_impact(finding, decision, is_blocking)

        # Build plain-language "what it means"
        what_it_means = self._plain_language_description(finding)

        # Determine action required
        action_required = business_impact in [
            BusinessImpact.BLOCKS_RELEASE,
            BusinessImpact.REQUIRES_FIX,
        ]

        # Build "why this matters"
        why_this_matters = self._build_business_context(finding)

        # Determine next steps
        next_steps = self._determine_next_steps(finding, decision)

        # Technical note (optional)
        technical_note = None
        if finding.source_type == FindingSourceType.RULE_SCAN:
            technical_note = f"Rule: {finding.source_code}"
        elif finding.source_type == FindingSourceType.VALIDATION:
            technical_note = f"Field: {finding.field_path}"

        # Location
        location = None
        if finding.file_path and finding.file_path != "<schema>":
            location = finding.file_path
            if finding.line_number:
                location += f":{finding.line_number}"

        return OwnerCard(
            card_id=card_id,
            finding_id=finding.finding_id,
            title=title,
            business_impact=business_impact,
            what_it_means=what_it_means,
            severity=finding.severity.value,
            action_required=action_required,
            why_this_matters=why_this_matters,
            next_steps=next_steps,
            technical_note=technical_note,
            location=location,
        )

    def _plain_language_title(self, finding: Finding) -> str:
        """Convert finding title to plain language (no error codes)."""

        # Remove error codes like "E401_" or "E501_"
        original_title = finding.title

        # Common technical terms to plain language mapping
        replacements = {
            "subprocess": "system command",
            "eval": "dynamic code execution",
            "pickle": "data deserialization",
            "shell=True": "shell command",
            "stop rule": "safety limit",
            "audit event": "security log",
            "external action": "external system call",
        }

        title = original_title
        for tech, plain in replacements.items():
            title = title.replace(tech, plain)

        # Remove underscore_casing
        title = title.replace("_", " ").strip()

        return title.capitalize()

    def _determine_business_impact(
        self,
        finding: Finding,
        decision: dict[str, Any],
        is_blocking: bool = False,
    ) -> BusinessImpact:
        """Determine business impact category.

        T11 Zero Exception: If is_blocking=True (from release_decision.blocking_findings),
        this finding MUST have BusinessImpact.BLOCKS_RELEASE, regardless of other factors.
        """

        # T11 Zero Exception: blocking findings ALWAYS block release
        if is_blocking:
            return BusinessImpact.BLOCKS_RELEASE

        severity = finding.severity.value
        decision_outcome = decision.get("decision", "PASS")
        impact_level = decision.get("impact_level", severity)

        # CRITICAL findings with FAIL decision block release
        if severity == "CRITICAL" and decision_outcome == "FAIL":
            return BusinessImpact.BLOCKS_RELEASE

        # HIGH findings usually require fix
        if severity == "HIGH":
            if impact_level in ["CRITICAL", "HIGH"]:
                return BusinessImpact.REQUIRES_FIX
            return BusinessImpact.SHOULD_FIX

        # MEDIUM findings
        if severity == "MEDIUM":
            if decision_outcome == "FAIL":
                return BusinessImpact.SHOULD_FIX
            return BusinessImpact.NICE_TO_HAVE

        # LOW severity or WAIVE decision
        if decision_outcome == "WAIVE":
            return BusinessImpact.ACKNOWLEDGE_ONLY

        return BusinessImpact.NICE_TO_HAVE

    def _plain_language_description(self, finding: Finding) -> str:
        """Build plain-language "what it means" description."""

        # Start with finding description
        description = finding.description

        # Remove technical jargon
        jargon_map = {
            "subprocess.run": "running system commands",
            "eval()": "executing unknown code",
            "pickle.loads": "loading data unsafely",
            "stop rule": "safety boundary",
            "governance gap": "missing safety control",
            "anti-pattern": "problematic code pattern",
        }

        for jargon, plain in jargon_map.items():
            description = description.replace(jargon, plain)

        return description

    def _build_business_context(self, finding: Finding) -> str:
        """Build business context: why should the owner care?"""

        category = finding.category

        context_map = {
            FindingCategory.SENSITIVE_PERMISSION: "This could allow unauthorized access to system resources.",
            FindingCategory.EXTERNAL_ACTION: "This makes external calls that could be exploited or fail unexpectedly.",
            FindingCategory.DANGEROUS_PATTERN: "This could allow attackers to execute malicious code.",
            FindingCategory.BOUNDARY_GAP: "This lacks important safety checks, which could lead to unexpected behavior.",
            FindingCategory.GOVERNANCE_GAP: "This is missing required security or safety controls.",
            FindingCategory.ANTI_PATTERN: "This pattern is known to cause problems in production systems.",
            FindingCategory.SCHEMA_VALIDATION: "This could cause the skill to fail when processing certain inputs.",
            FindingCategory.CONTRACT_VALIDATION: "This could break compatibility with other systems.",
        }

        return context_map.get(category, "This could affect system security or reliability.")

    def _determine_next_steps(
        self,
        finding: Finding,
        decision: dict[str, Any],
    ) -> NextSteps:
        """Determine clear next steps for owner/team."""

        severity = finding.severity.value
        decision_outcome = decision.get("decision", "PASS")

        # CRITICAL + FAIL = must fix before release
        if severity == "CRITICAL" and decision_outcome == "FAIL":
            return NextSteps.MUST_FIX_BEFORE_RELEASE

        # HIGH severity = fix before production
        if severity == "HIGH":
            return NextSteps.FIX_BEFORE_PRODUCTION

        # MEDIUM = schedule fix
        if severity == "MEDIUM":
            return NextSteps.SCHEDULE_FIX

        # WAIVE = accept risk
        if decision_outcome == "WAIVE":
            return NextSteps.ACCEPT_RISK

        # DEFER = escalate
        if decision_outcome == "DEFER":
            return NextSteps.ESCALATE_FOR_DECISION

        return NextSteps.DOCUMENT_AND_MONITOR

    def _build_coverage_note(
        self,
        findings_report: FindingsReport,
        coverage_statement: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Build owner-readable coverage note."""

        covered = []
        not_covered = []

        # Determine what was checked based on finding sources
        sources = findings_report.summary.get("by_source", {})

        if sources.get("validation", 0) > 0:
            covered.append("Skill structure and contracts")
        else:
            not_covered.append("Skill structure and contracts")

        if sources.get("rule_scan", 0) > 0:
            covered.append("Security rules and dangerous patterns")
        else:
            not_covered.append("Security rules and dangerous patterns")

        if sources.get("pattern_match", 0) > 0:
            covered.append("Governance and safety patterns")
        else:
            not_covered.append("Governance and safety patterns")

        # Always note limitations
        not_covered.extend([
            "Runtime behavior analysis",
            "Performance under load",
            "Integration testing with other systems",
        ])

        # Determine confidence level
        total_findings = findings_report.summary.get("total_findings", 0)
        high_severity = (
            findings_report.summary.get("by_severity", {}).get("CRITICAL", 0) +
            findings_report.summary.get("by_severity", {}).get("HIGH", 0)
        )

        if high_severity == 0:
            confidence = "HIGH"
        elif high_severity <= 2:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        return {
            "covered_areas": covered,
            "not_covered": not_covered,
            "confidence_level": confidence,
        }

    def _build_action_items(self, owner_cards: list[OwnerCard]) -> list[ActionItem]:
        """Build actionable items from owner cards."""

        actions = []

        for card in owner_cards:
            # Only create action items for cards requiring action
            if not card.action_required:
                continue

            if card.business_impact == BusinessImpact.BLOCKS_RELEASE:
                priority = ActionPriority.P0_BLOCKING
                assignee = AssigneeType.DEVELOPER
            elif card.business_impact == BusinessImpact.REQUIRES_FIX:
                priority = ActionPriority.P1_HIGH
                assignee = AssigneeType.DEVELOPER
            elif card.business_impact == BusinessImpact.SHOULD_FIX:
                priority = ActionPriority.P2_MEDIUM
                assignee = AssigneeType.DEVELOPER
            else:
                continue

            self._action_counter += 1
            action = ActionItem(
                item_id=f"A-{self._action_counter:08d}",
                description=card.what_it_means,
                priority=priority,
                assignee_type=assignee,
                linked_cards=[card.card_id],
            )
            actions.append(action)

        return actions

    def _build_overrides_summary(
        self,
        release_decision: ReleaseDecision,
    ) -> Optional[dict[str, Any]]:
        """Build summary of judgment overrides applied."""

        overrides = release_decision.overrides_applied
        if not overrides:
            return None

        # Count overrides by reason
        reason_codes = {}
        for override in overrides:
            reason = override.get("justification_code", "UNKNOWN")
            reason_codes[reason] = reason_codes.get(reason, 0) + 1

        # Map reason codes to business language
        reason_map = {
            "FALSE_POSITIVE_CONFIRMED": "FALSE_POSITIVE_CONFIRMED",
            "OUT_OF_SCOPE": "OUT_OF_SCOPE",
            "ACCEPTABLE_RISK": "ACCEPTABLE_BUSINESS_RISK",
            "COMPENSATING_CONTROL": "COMPENSATING_CONTROLS_EXIST",
            "BUSINESS_REQUIREMENT": "ACCEPTABLE_BUSINESS_RISK",
        }

        override_reasons = []
        for code, count in reason_codes.items():
            reason = reason_map.get(code, code)
            override_reasons.append(reason)

        return {
            "total_overrides": len(overrides),
            "override_reasons": override_reasons,
        }


def save_owner_review(
    owner_review: OwnerReview,
    output_dir: Path,
    run_id: str,
) -> dict[str, str]:
    """Save owner review to JSON and Markdown files.

    Args:
        owner_review: The owner review to save
        output_dir: Output directory path
        run_id: Run identifier for filename

    Returns:
        Dictionary with paths to saved files
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save JSON
    json_path = output_dir / f"owner_review_{run_id}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(owner_review.to_dict(), f, indent=2, default=str)

    # Save Markdown
    md_path = output_dir / f"owner_review_{run_id}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(owner_review.to_markdown())

    return {
        "json": str(json_path),
        "markdown": str(md_path),
    }
