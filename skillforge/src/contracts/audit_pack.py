"""
Audit Pack - T14 Deliverable: Discovery -> Adjudication -> Delivery Pipeline

This module implements the complete "发现 -> 裁决 -> 交付" (Discovery -> Adjudication -> Delivery)
pipeline, consolidating all batch 2 contracts into a unified audit pack.

Pipeline:
    findings (T6) -> adjudication (T8) -> coverage/evidence (T9) -> release decision (T10)
    -> owner review (T11) -> issues/fixes (T12) -> audit pack (T14)

T14 Hard Constraints:
- No manual stitching required
- No batch 3 runtime capabilities
- No completion claim without EvidenceRef
- Fixed output directory structure
- At least 3 regression samples provided

Usage:
    from skillforge.src.contracts.audit_pack import (
        AuditPackBuilder,
        build_audit_pack,
        run_audit_pipeline
    )

    # Build from existing run directory
    pack = build_audit_pack(run_id="20260316_120000")
    pack.save("run/20260316_120000/audit_pack.json")

    # Or run full pipeline
    pack = run_audit_pipeline(
        skill_dir="path/to/skill",
        run_id="20260316_120000"
    )

Output Directory Structure (FIXED):
run/<run_id>/
├── intake_request.json           # T1
├── normalized_skill_spec.json    # T2
├── validation_report.json        # T3
├── rule_scan_report.json         # T4
├── pattern_detection_report.json # T5
├── findings.json                 # T6 (REQUIRED)
├── adjudication_report.json      # T8 (REQUIRED)
├── coverage_statement.json       # T9 (optional)
├── judgment_overrides.json       # T10 (optional)
├── residual_risks.json           # T10 (optional)
├── release_decision.json         # T10 (REQUIRED)
├── owner_review.json             # T11 (optional)
├── issue_records.json            # T12 (optional)
├── fix_recommendations.json      # T12 (optional)
└── audit_pack.json               # T14 (OUTPUT)

@contact: 执行者 vs--cc3
@task_id: T14
@date: 2026-03-16
"""

from __future__ import annotations

import hashlib
import json
import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Literal, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================
class PackContext(Enum):
    """Context for the audit pack."""
    ENTRY_GATE = "entry_gate"
    EXIT_GATE = "exit_gate"
    MANUAL_AUDIT = "manual_audit"
    REGULATORY_REVIEW = "regulatory_review"


class PackType(Enum):
    """Type of audit pack based on artifact inclusion."""
    MINIMAL = "MINIMAL"       # Only required artifacts (findings, adjudication, release)
    STANDARD = "STANDARD"     # Required + overrides + residual risks
    COMPREHENSIVE = "COMPREHENSIVE"  # All artifacts


class ComplianceStatus(Enum):
    """Compliance status for audit pack."""
    COMPLIANT = "COMPLIANT"
    PARTIAL = "PARTIAL"
    NON_COMPLIANT = "NON_COMPLIANT"


# =============================================================================
# Data Structures
# =============================================================================
@dataclass
class EvidenceManifest:
    """Manifest of all evidence references."""
    total_evidence_refs: int = 0
    by_kind: dict[str, int] = field(default_factory=dict)
    evidence_digest: str = ""
    findings_with_evidence: int = 0
    findings_without_evidence: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_evidence_refs": self.total_evidence_refs,
            "by_kind": self.by_kind,
            "evidence_digest": self.evidence_digest,
            "findings_with_evidence": self.findings_with_evidence,
            "findings_without_evidence": self.findings_without_evidence,
        }


@dataclass
class AuditPackSummary:
    """Summary statistics across all artifacts."""
    total_findings: int = 0
    findings_by_severity: dict[str, int] = field(default_factory=dict)
    total_decisions: int = 0
    decisions_by_outcome: dict[str, int] = field(default_factory=dict)
    release_outcome: str = "REJECT"
    has_overrides: bool = False
    override_count: int = 0
    has_residual_risks: bool = False
    residual_risk_count: int = 0
    blocking_findings_count: int = 0
    issues_created: int = 0
    fix_recommendations: int = 0
    coverage_percentage: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_findings": self.total_findings,
            "findings_by_severity": self.findings_by_severity,
            "total_decisions": self.total_decisions,
            "decisions_by_outcome": self.decisions_by_outcome,
            "release_outcome": self.release_outcome,
            "has_overrides": self.has_overrides,
            "override_count": self.override_count,
            "has_residual_risks": self.has_residual_risks,
            "residual_risk_count": self.residual_risk_count,
            "blocking_findings_count": self.blocking_findings_count,
            "issues_created": self.issues_created,
            "fix_recommendations": self.fix_recommendations,
            "coverage_percentage": self.coverage_percentage,
        }


@dataclass
class ChainOfCustodyEntry:
    """Entry in chain of custody."""
    timestamp: str
    event: str
    actor: str
    note: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        result = {
            "timestamp": self.timestamp,
            "event": self.event,
            "actor": self.actor,
        }
        if self.note:
            result["note"] = self.note
        return result


# =============================================================================
# Main Audit Pack
# =============================================================================
@dataclass
class AuditPack:
    """
    Final audit pack consolidating all discovery, adjudication, and delivery artifacts.

    T14 Deliverable: Complete traceability from findings to release decision.
    """
    pack_id: str
    run_id: str
    created_at: str
    t14_version: str = "1.0.0-t14"

    # Metadata
    skill_id: str = ""
    skill_name: str = ""
    pack_context: PackContext = PackContext.EXIT_GATE
    pack_type: PackType = PackType.STANDARD

    # Artifact paths
    intake_request: Optional[str] = None
    normalized_skill_spec: Optional[str] = None
    validation_report: Optional[str] = None
    rule_scan_report: Optional[str] = None
    pattern_detection_report: Optional[str] = None
    findings_report: str = ""
    adjudication_report: str = ""
    coverage_statement: Optional[str] = None
    judgment_overrides: Optional[str] = None
    residual_risks: Optional[str] = None
    release_decision: str = ""
    owner_review: Optional[str] = None
    issue_records: Optional[str] = None
    fix_recommendations: Optional[str] = None

    # Computed data
    evidence_manifest: EvidenceManifest = field(default_factory=EvidenceManifest)
    summary: AuditPackSummary = field(default_factory=AuditPackSummary)
    chain_of_custody: list[ChainOfCustodyEntry] = field(default_factory=list)

    # Compliance
    antigravity_compliant: bool = False
    closed_loop_complete: bool = False
    evidence_ref_complete: bool = False
    governance_gaps_identified: int = 0
    security_findings_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        artifacts = {
            "discovery": {
                "intake_request": self.intake_request,
                "normalized_skill_spec": self.normalized_skill_spec,
                "validation_report": self.validation_report,
                "rule_scan_report": self.rule_scan_report,
                "pattern_detection_report": self.pattern_detection_report,
                "findings_report": self.findings_report,
            },
            "adjudication": {
                "adjudication_report": self.adjudication_report,
                "coverage_statement": self.coverage_statement,
            },
            "delivery": {
                "judgment_overrides": self.judgment_overrides,
                "residual_risks": self.residual_risks,
                "release_decision": self.release_decision,
                "owner_review": self.owner_review,
                "issue_records": self.issue_records,
                "fix_recommendations": self.fix_recommendations,
            },
        }

        return {
            "meta": {
                "pack_id": self.pack_id,
                "run_id": self.run_id,
                "created_at": self.created_at,
                "t14_version": self.t14_version,
                "skill_id": self.skill_id,
                "skill_name": self.skill_name,
                "pack_context": self.pack_context.value,
            },
            "pack_type": self.pack_type.value,
            "artifacts": artifacts,
            "evidence_manifest": self.evidence_manifest.to_dict(),
            "summary": self.summary.to_dict(),
            "compliance": {
                "antigravity_compliant": self.antigravity_compliant,
                "closed_loop_complete": self.closed_loop_complete,
                "evidence_ref_complete": self.evidence_ref_complete,
                "governance_gaps_identified": self.governance_gaps_identified,
                "security_findings_count": self.security_findings_count,
            },
            "chain_of_custody": [e.to_dict() for e in self.chain_of_custody],
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def save(self, output_path: str | Path) -> None:
        """Save audit pack to JSON file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(self.to_json())

        logger.info(f"Audit pack saved to: {output_path}")

    def validate(self) -> list[str]:
        """
        Validate audit pack completeness.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Required artifacts
        if not self.findings_report:
            errors.append("Missing required artifact: findings_report")
        if not self.adjudication_report:
            errors.append("Missing required artifact: adjudication_report")
        if not self.release_decision:
            errors.append("Missing required artifact: release_decision")

        # T14 Hard Constraint: All findings must have evidence
        if self.evidence_manifest.findings_without_evidence > 0:
            errors.append(
                f"T14 Hard Constraint Violation: {self.evidence_manifest.findings_without_evidence} "
                "findings without evidence refs"
            )

        # Evidence refs must exist
        if self.evidence_manifest.total_evidence_refs == 0:
            errors.append("T14 Hard Constraint Violation: No evidence refs found")

        return errors


# =============================================================================
# Audit Pack Builder
# =============================================================================
class AuditPackBuilder:
    """
    Builder for creating AuditPack from run directory.

    Automatically discovers and validates all artifacts.
    """

    def __init__(self, run_dir: str | Path):
        """
        Initialize builder with run directory.

        Args:
            run_dir: Path to run directory containing all artifacts
        """
        self.run_dir = Path(run_dir)
        if not self.run_dir.exists():
            raise FileNotFoundError(f"Run directory not found: {run_dir}")

        # Extract run_id from directory name
        self.run_id = self.run_dir.name

    def build(self, context: PackContext = PackContext.EXIT_GATE) -> AuditPack:
        """
        Build audit pack from run directory.

        Args:
            context: Context for this audit pack

        Returns:
            Complete AuditPack with all discovered artifacts
        """
        logger.info(f"Building audit pack for run_id: {self.run_id}")

        now = datetime.now(timezone.utc)
        pack_id = self._generate_pack_id()

        # Initialize pack
        pack = AuditPack(
            pack_id=pack_id,
            run_id=self.run_id,
            created_at=now.isoformat(),
            pack_context=context,
        )

        # Discover artifacts
        self._discover_artifacts(pack)
        self._load_and_summarize(pack)
        self._compute_evidence_manifest(pack)
        self._validate_compliance(pack)
        self._add_chain_of_custody_entry(pack, "PACK_CREATED")

        return pack

    def _generate_pack_id(self) -> str:
        """Generate unique pack ID."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        hash_input = f"{self.run_id}:{timestamp}"
        hash_suffix = hashlib.sha256(hash_input.encode()).hexdigest()[:12]
        return f"PACK-{hash_suffix}"

    def _discover_artifacts(self, pack: AuditPack) -> None:
        """Discover all artifacts in run directory."""
        artifact_map = {
            "intake_request.json": "intake_request",
            "normalized_skill_spec.json": "normalized_skill_spec",
            "validation_report.json": "validation_report",
            "rule_scan_report.json": "rule_scan_report",
            "pattern_detection_report.json": "pattern_detection_report",
            "findings.json": "findings_report",
            "adjudication_report.json": "adjudication_report",
            "coverage_statement.json": "coverage_statement",
            "judgment_overrides.json": "judgment_overrides",
            "residual_risks.json": "residual_risks",
            "release_decision.json": "release_decision",
            "owner_review.json": "owner_review",
            "issue_records.json": "issue_records",
            "fix_recommendations.json": "fix_recommendations",
        }

        for filename, attr_name in artifact_map.items():
            path = self.run_dir / filename
            if path.exists():
                setattr(pack, attr_name, str(path))
                logger.debug(f"Discovered artifact: {filename}")

    def _load_and_summarize(self, pack: AuditPack) -> None:
        """Load artifacts and compute summary statistics."""
        # Load findings report
        if pack.findings_report:
            findings_data = self._load_json(pack.findings_report)
            if findings_data:
                pack.skill_id = findings_data.get("meta", {}).get("skill_id", "")
                pack.skill_name = findings_data.get("meta", {}).get("skill_name", "")
                pack.summary.total_findings = findings_data.get("summary", {}).get("total_findings", 0)
                pack.summary.findings_by_severity = findings_data.get("summary", {}).get("by_severity", {})

        # Load adjudication report
        if pack.adjudication_report:
            adj_data = self._load_json(pack.adjudication_report)
            if adj_data:
                pack.summary.total_decisions = adj_data.get("summary", {}).get("total_decisions", 0)
                pack.summary.decisions_by_outcome = adj_data.get("summary", {}).get("by_decision", {})

        # Load release decision
        if pack.release_decision:
            rd_data = self._load_json(pack.release_decision)
            if rd_data:
                pack.summary.release_outcome = rd_data.get("decision", {}).get("outcome", "REJECT")
                pack.summary.blocking_findings_count = len(
                    rd_data.get("findings_summary", {}).get("blocking_findings", [])
                )

        # Load overrides
        if pack.judgment_overrides:
            jo_data = self._load_json(pack.judgment_overrides)
            if jo_data:
                pack.summary.has_overrides = True
                pack.summary.override_count = jo_data.get("summary", {}).get("total_overrides", 0)

        # Load residual risks
        if pack.residual_risks:
            rr_data = self._load_json(pack.residual_risks)
            if rr_data:
                pack.summary.has_residual_risks = True
                pack.summary.residual_risk_count = rr_data.get("summary", {}).get("total_risks", 0)

        # Load coverage
        if pack.coverage_statement:
            cs_data = self._load_json(pack.coverage_statement)
            if cs_data:
                pack.summary.coverage_percentage = cs_data.get("coverage_summary", {}).get("coverage_percent", 0.0)

        # Load issues
        if pack.issue_records:
            ir_data = self._load_json(pack.issue_records)
            if ir_data:
                pack.summary.issues_created = len(ir_data.get("issues", []))

        # Load fixes
        if pack.fix_recommendations:
            fr_data = self._load_json(pack.fix_recommendations)
            if fr_data:
                pack.summary.fix_recommendations = len(fr_data.get("recommendations", []))

    def _compute_evidence_manifest(self, pack: AuditPack) -> None:
        """Compute evidence manifest from all artifacts."""
        all_evidence_refs = []
        findings_without_evidence = 0

        # Collect evidence from findings
        if pack.findings_report:
            findings_data = self._load_json(pack.findings_report)
            if findings_data:
                for finding in findings_data.get("findings", []):
                    refs = finding.get("evidence_refs", [])
                    if refs:
                        all_evidence_refs.extend(refs)
                    else:
                        findings_without_evidence += 1

                    # Count governance gaps
                    if finding.get("what", {}).get("category") == "governance_gap":
                        pack.governance_gaps_identified += 1

                    # Count security findings
                    if finding.get("what", {}).get("category") in ["sensitive_permission", "dangerous_pattern"]:
                        pack.security_findings_count += 1

        # Count by kind
        by_kind: dict[str, int] = {}
        for ref in all_evidence_refs:
            kind = ref.get("kind", "UNKNOWN")
            by_kind[kind] = by_kind.get(kind, 0) + 1

        # Compute digest
        locator_strings = sorted(ref.get("locator", "") for ref in all_evidence_refs)
        digest_input = "\n".join(locator_strings)
        evidence_digest = hashlib.sha256(digest_input.encode()).hexdigest()

        pack.evidence_manifest = EvidenceManifest(
            total_evidence_refs=len(all_evidence_refs),
            by_kind=by_kind,
            evidence_digest=evidence_digest,
            findings_with_evidence=len(all_evidence_refs),
            findings_without_evidence=findings_without_evidence,
        )

    def _validate_compliance(self, pack: AuditPack) -> None:
        """Validate compliance status."""
        # Evidence ref completeness (T14 hard constraint)
        pack.evidence_ref_complete = pack.evidence_manifest.findings_without_evidence == 0

        # Antigravity-1 compliance
        pack.antigravity_compliant = (
            pack.evidence_ref_complete
            and pack.evidence_manifest.total_evidence_refs > 0
            and pack.governance_gaps_identified >= 0
        )

        # Closed-loop completeness
        pack.closed_loop_complete = (
            pack.findings_report is not None
            and pack.adjudication_report is not None
            and pack.release_decision is not None
        )

    def _add_chain_of_custody_entry(
        self, pack: AuditPack, event: str, note: Optional[str] = None
    ) -> None:
        """Add entry to chain of custody."""
        entry = ChainOfCustodyEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            event=event,
            actor="T14-AuditPackBuilder",
            note=note,
        )
        pack.chain_of_custody.append(entry)

    def _load_json(self, path: str) -> Optional[dict[str, Any]]:
        """Load JSON file safely."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load {path}: {e}")
            return None


# =============================================================================
# Convenience Functions
# =============================================================================
def build_audit_pack(
    run_id: str,
    run_base_dir: str = "run",
    context: PackContext = PackContext.EXIT_GATE,
) -> AuditPack:
    """
    Build audit pack from run directory.

    Args:
        run_id: Run identifier
        run_base_dir: Base directory for runs
        context: Context for this audit pack

    Returns:
        Complete AuditPack
    """
    run_dir = Path(run_base_dir) / run_id
    builder = AuditPackBuilder(run_dir)
    return builder.build(context=context)


def validate_audit_pack(pack: AuditPack) -> tuple[bool, list[str]]:
    """
    Validate audit pack.

    Args:
        pack: AuditPack to validate

    Returns:
        Tuple of (is_valid, error_list)
    """
    errors = pack.validate()
    return (len(errors) == 0, errors)


def run_audit_pipeline(
    skill_dir: str,
    intent_id: str,
    repo_url: str,
    commit_sha: str,
    run_base_dir: str = "run",
    run_id: Optional[str] = None,
    at_time: Optional[str] = None,
    issue_key: Optional[str] = None,
    context: PackContext = PackContext.EXIT_GATE,
) -> AuditPack:
    """
    Run full audit pipeline and generate audit pack.

    This is the ONE command to rule them all. Runs the complete pipeline:
    T1-T6 (Discovery) → T8 (Adjudication) → T10 (Release Decision) → T14 (Audit Pack)

    Args:
        skill_dir: Path to skill directory to audit
        intent_id: Audit intent ID (T1 whitelist)
        repo_url: Repository URL
        commit_sha: Commit SHA (7-40 hex characters)
        run_base_dir: Base directory for runs
        run_id: Optional run ID (auto-generated if not provided)
        at_time: Audit time (ISO-8601)
        issue_key: Optional issue ticket number
        context: Context for this audit pack

    Returns:
        Complete AuditPack

    Raises:
        RuntimeError: If pipeline fails
    """
    from skillforge.src.contracts.discovery_pipeline import DiscoveryPipeline
    from skillforge.src.contracts.adjudicator import adjudicate_findings_report
    from skillforge.src.contracts.release_decision import make_release_decision, ReleaseDecision, EvidenceRef

    # Generate run_id if not provided
    if run_id is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        run_id = timestamp

    logger.info(f"Running T14 audit pipeline for run_id: {run_id}")
    logger.info(f"Skill directory: {skill_dir}")

    # Step 1: Run discovery pipeline (T1-T6)
    logger.info("=" * 60)
    logger.info("Step 1: Discovery Pipeline (T1-T6)")
    logger.info("=" * 60)
    discovery = DiscoveryPipeline(output_base_dir=run_base_dir)
    discovery_result = discovery.run(
        intent_id=intent_id,
        repo_url=repo_url,
        commit_sha=commit_sha,
        skill_dir=skill_dir,
        at_time=at_time,
        issue_key=issue_key,
        run_id=run_id,
    )

    if discovery_result.status != "success":
        raise RuntimeError(
            f"Discovery pipeline failed: {discovery_result.error_summary}"
        )

    logger.info(f"Discovery complete: {discovery_result.total_findings} findings")

    # Step 2: Run adjudication (T8)
    logger.info("=" * 60)
    logger.info("Step 2: Adjudication (T8)")
    logger.info("=" * 60)

    # Load findings report
    findings_path = Path(run_base_dir) / run_id / "findings.json"
    with open(findings_path, "r", encoding="utf-8") as f:
        findings_report = json.load(f)

    # Run adjudication
    adjudication_report = adjudicate_findings_report(
        findings_report=findings_report,
        run_id=run_id,
    )

    # Save adjudication report
    adjudication_path = Path(run_base_dir) / run_id / "adjudication_report.json"
    adjudication_report.save(str(adjudication_path))
    logger.info(f"Adjudication complete: {adjudication_report.summary['total_decisions']} decisions")

    # Step 3: Make release decision (T10)
    logger.info("=" * 60)
    logger.info("Step 3: Release Decision (T10)")
    logger.info("=" * 60)

    # Prepare evidence refs
    evidence_refs = [
        EvidenceRef(
            kind="FILE",
            locator=str(findings_path.relative_to(Path(run_base_dir))),
            note="T6 findings report",
        ),
        EvidenceRef(
            kind="FILE",
            locator=str(adjudication_path.relative_to(Path(run_base_dir))),
            note="T8 adjudication report",
        ),
    ]

    # Make release decision
    findings = findings_report.get("findings", [])
    release_decision_obj = make_release_decision(
        findings=findings,
        overrides=[],  # No overrides for automated pipeline
        residual_risks=[],
        evidence_refs=evidence_refs,
        run_id=run_id,
        skill_id=findings_report.get("meta", {}).get("skill_id", ""),
    )

    # Save release decision
    rd_path = Path(run_base_dir) / run_id / "release_decision.json"
    release_decision_obj.save(str(rd_path))
    logger.info(f"Release decision: {release_decision_obj.outcome.value}")

    # Step 4: Build audit pack
    logger.info("=" * 60)
    logger.info("Step 4: Building Audit Pack (T14)")
    logger.info("=" * 60)
    pack = build_audit_pack(run_id=run_id, run_base_dir=run_base_dir, context=context)

    # Step 5: Validate
    is_valid, errors = validate_audit_pack(pack)
    if not is_valid:
        logger.error(f"Audit pack validation failed: {errors}")
        raise RuntimeError(f"Audit pack validation failed: {errors}")

    # Step 6: Save
    pack_path = Path(run_base_dir) / run_id / "audit_pack.json"
    pack.save(pack_path)

    logger.info("=" * 60)
    logger.info(f"T14 audit pipeline complete: {pack_path}")
    logger.info(f"Release outcome: {pack.summary.release_outcome}")
    logger.info("=" * 60)

    return pack


# =============================================================================
# CLI Entry Point
# =============================================================================
def main():
    """CLI entry point for audit pack operations."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Audit Pack Builder - T14: Discovery -> Adjudication -> Delivery"
    )
    parser.add_argument(
        "--run-id",
        required=True,
        help="Run identifier (e.g., 20260316_120000)",
    )
    parser.add_argument(
        "--run-dir",
        default="run",
        help="Base run directory",
    )
    parser.add_argument(
        "--context",
        choices=["entry_gate", "exit_gate", "manual_audit", "regulatory_review"],
        default="exit_gate",
        help="Context for audit pack",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate, don't create new pack",
    )

    args = parser.parse_args()

    context = PackContext(args.context)

    try:
        pack = build_audit_pack(
            run_id=args.run_id,
            run_base_dir=args.run_dir,
            context=context,
        )

        is_valid, errors = validate_audit_pack(pack)

        if args.validate_only:
            if is_valid:
                print("✅ Audit pack is VALID")
                sys.exit(0)
            else:
                print("❌ Audit pack is INVALID:")
                for error in errors:
                    print(f"  - {error}")
                sys.exit(1)

        # Save pack
        pack_path = Path(args.run_dir) / args.run_id / "audit_pack.json"
        pack.save(pack_path)

        # Print summary
        print("\n" + "=" * 60)
        print("Audit Pack Summary")
        print("=" * 60)
        print(f"Pack ID: {pack.pack_id}")
        print(f"Run ID: {pack.run_id}")
        print(f"Skill: {pack.skill_name} ({pack.skill_id})")
        print(f"\nSummary:")
        print(f"  Total Findings: {pack.summary.total_findings}")
        print(f"  Release Outcome: {pack.summary.release_outcome}")
        print(f"  Overrides: {pack.summary.override_count}")
        print(f"  Residual Risks: {pack.summary.residual_risk_count}")
        print(f"\nEvidence:")
        print(f"  Total Evidence Refs: {pack.evidence_manifest.total_evidence_refs}")
        print(f"  Findings with Evidence: {pack.evidence_manifest.findings_with_evidence}")
        print(f"  Findings without Evidence: {pack.evidence_manifest.findings_without_evidence}")
        print(f"\nCompliance:")
        print(f"  Antigravity-1: {'✅' if pack.antigravity_compliant else '❌'}")
        print(f"  Closed Loop: {'✅' if pack.closed_loop_complete else '❌'}")
        print(f"  Evidence Refs Complete: {'✅' if pack.evidence_ref_complete else '❌'}")
        print(f"\nOutput: {pack_path}")

        if not is_valid:
            print("\n⚠️  Validation Errors:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)

        sys.exit(0)

    except Exception as e:
        logger.error(f"Audit pack creation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
