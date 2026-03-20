#!/usr/bin/env python3
"""
T14 Unified Command - One Command to Rule Them All

This is the single command that runs the complete "发现 -> 裁决 -> 交付" pipeline:

    findings (T6) -> adjudication (T8) -> coverage/evidence (T9)
    -> release decision (T10) -> owner review (T11) -> issues/fixes (T12)
    -> audit pack (T14)

Usage:
    # From existing run directory
    python run_t14_pipeline.py --run-id 20260316_120000

    # Full pipeline from skill directory
    python run_t14_pipeline.py --skill-dir path/to/skill --run-id 20260316_120000

    # Validate only
    python run_t14_pipeline.py --run-id 20260316_120000 --validate-only

Output:
    run/<run_id>/audit_pack.json

@contact: vs--cc3
@task_id: T14
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="T14 Unified Command: Discovery -> Adjudication -> Delivery Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Build from existing run directory (most common)
  python run_t14_pipeline.py --run-id 20260316_120000

  # Validate existing audit pack
  python run_t14_pipeline.py --run-id 20260316_120000 --validate-only

  # Show summary without saving
  python run_t14_pipeline.py --run-id 20260316_120000 --summary-only
        """
    )

    parser.add_argument(
        "--run-id",
        help="Run identifier (e.g., 20260316_120000)",
    )
    parser.add_argument(
        "--run-dir",
        default="run",
        help="Base run directory (default: run)",
    )
    parser.add_argument(
        "--context",
        choices=["entry_gate", "exit_gate", "manual_audit", "regulatory_review"],
        default="exit_gate",
        help="Context for audit pack (default: exit_gate)",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate, don't create new pack",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Only show summary, don't save",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output",
    )
    parser.add_argument(
        "--output", "-o",
        help="Output path for audit_pack.json (default: run/<run_id>/audit_pack.json)",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if not args.run_id:
        parser.error("--run-id is required")

    try:
        # Direct import for standalone execution
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from audit_pack import (
            AuditPackBuilder,
            PackContext,
            build_audit_pack,
            validate_audit_pack,
        )

        # Build pack
        logger.info(f"Building audit pack for run_id: {args.run_id}")
        context = PackContext(args.context)

        run_dir = Path(args.run_dir) / args.run_id
        if not run_dir.exists():
            logger.error(f"Run directory not found: {run_dir}")
            logger.info("Available run directories:")
            base_dir = Path(args.run_dir)
            if base_dir.exists():
                for item in base_dir.iterdir():
                    if item.is_dir():
                        logger.info(f"  - {item.name}")
            sys.exit(1)

        builder = AuditPackBuilder(run_dir)
        pack = builder.build(context=context)

        # Validate
        is_valid, errors = validate_audit_pack(pack)

        # Print summary
        print("\n" + "=" * 70)
        print("T14 AUDIT PACK SUMMARY")
        print("=" * 70)
        print(f"Pack ID:      {pack.pack_id}")
        print(f"Run ID:       {pack.run_id}")
        print(f"Skill:        {pack.skill_name or 'N/A'} ({pack.skill_id or 'N/A'})")
        print(f"Created:      {pack.created_at}")
        print(f"Context:      {args.context}")
        print(f"\n📊 FINDINGS")
        print(f"  Total:              {pack.summary.total_findings}")
        print(f"  By Severity:")
        for sev, count in pack.summary.findings_by_severity.items():
            if count > 0:
                icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢", "INFO": "🔵"}.get(sev, "⚪")
                print(f"    {icon} {sev}: {count}")

        print(f"\n⚖️  ADJUDICATION")
        print(f"  Total Decisions:    {pack.summary.total_decisions}")
        print(f"  By Outcome:")
        for outcome, count in pack.summary.decisions_by_outcome.items():
            if count > 0:
                icon = {"PASS": "✅", "FAIL": "❌", "WAIVE": "⚠️", "DEFER": "⏳"}.get(outcome, "❓")
                print(f"    {icon} {outcome}: {count}")

        print(f"\n🚀 RELEASE DECISION")
        outcome = pack.summary.release_outcome
        icon = {"RELEASE": "✅", "CONDITIONAL_RELEASE": "⚠️", "LIMITED_RELEASE": "🔶",
                "ESCALATE": "📤", "REJECT": "🚫"}.get(outcome, "❓")
        print(f"  Outcome:            {icon} {outcome}")
        print(f"  Blocking Findings:  {pack.summary.blocking_findings_count}")

        print(f"\n📋 OVERRIDES & RISKS")
        print(f"  Overrides:          {pack.summary.override_count}")
        print(f"  Residual Risks:     {pack.summary.residual_risk_count}")
        if pack.summary.override_count > 0:
            print(f"  Has Overrides:       ✅ Yes")
        if pack.summary.residual_risk_count > 0:
            print(f"  Has Residual Risks:  ⚠️  Yes")

        print(f"\n📝 EVIDENCE")
        print(f"  Total Evidence Refs: {pack.evidence_manifest.total_evidence_refs}")
        print(f"  Findings with Evidence:     {pack.evidence_manifest.findings_with_evidence}")
        print(f"  Findings without Evidence:  {pack.evidence_manifest.findings_without_evidence}")
        if pack.evidence_manifest.total_evidence_refs > 0:
            print(f"  By Kind:")
            for kind, count in sorted(pack.evidence_manifest.by_kind.items()):
                print(f"    - {kind}: {count}")

        print(f"\n✅ COMPLIANCE")
        print(f"  Antigravity-1:      {'✅ Compliant' if pack.antigravity_compliant else '❌ Non-compliant'}")
        print(f"  Closed Loop:        {'✅ Complete' if pack.closed_loop_complete else '❌ Incomplete'}")
        print(f"  Evidence Refs:      {'✅ Complete' if pack.evidence_ref_complete else '❌ Incomplete'}")
        print(f"  Governance Gaps:    {pack.governance_gaps_identified}")
        print(f"  Security Findings:  {pack.security_findings_count}")

        if args.summary_only:
            sys.exit(0)

        if args.validate_only:
            print("\n" + "=" * 70)
            print("VALIDATION RESULT")
            print("=" * 70)
            if is_valid:
                print("✅ Audit pack is VALID")
                sys.exit(0)
            else:
                print("❌ Audit pack is INVALID:")
                for error in errors:
                    print(f"  - {error}")
                sys.exit(1)

        # Save pack
        if args.output:
            pack_path = Path(args.output)
            pack_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            pack_path = run_dir / "audit_pack.json"
        pack.save(pack_path)

        print("\n" + "=" * 70)
        print(f"✅ Audit pack saved to: {pack_path}")

        if not is_valid:
            print("\n⚠️  Validation Errors:")
            for error in errors:
                print(f"  - {error}")
            print("\nPack saved but validation failed. Review errors above.")

        sys.exit(0 if is_valid else 1)

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
