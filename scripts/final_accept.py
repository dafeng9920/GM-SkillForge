#!/usr/bin/env python3
"""
Final Accept - Local Main Chain Final Unified Entry

本地主链的 Final Accept 统一入口脚本。

此脚本在 Local Accept 完成后执行，负责：
1. 聚合 Local Accept Decision、Gate Decision、Compliance Attestation
2. 验证三权分立记录完整性
3. 执行最终裁决：ALLOW / REQUIRES_CHANGES / DENY
4. 生成 Final Accept Decision
5. 输出到 docs/{date}/verification/{task_id}_final_accept_decision.json

此脚本不修改任何业务逻辑，只做验证和决策输出。
与现有 antigravity_final_gate.py 和 gate_final_decision.py 保持兼容。

Usage:
    python scripts/final_accept.py --task-id <task_id>
    python scripts/final_accept.py --task-id <task_id> --date <YYYY-MM-DD>
    python scripts/final_accept.py --task-id <task_id> --verification-dir <path>
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from datetime import datetime, timezone
from typing import Any


# =============================================================================
# Configuration
# =============================================================================
FINAL_ACCEPT_VERSION = "1.0.0"
ALLOWED_DECISIONS = ["ALLOW", "REQUIRES_CHANGES", "DENY"]


# =============================================================================
# Utility Functions
# =============================================================================
def utc_now_iso() -> str:
    """Get current UTC time in ISO format with Z suffix."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: pathlib.Path) -> dict[str, Any] | None:
    """Read JSON file, return None if not exists."""
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: pathlib.Path, obj: dict[str, Any]) -> None:
    """Write JSON file with UTF-8 encoding."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# =============================================================================
# Final Accept Adjudicator
# =============================================================================
class FinalAcceptAdjudicator:
    """
    Final Accept Adjudicator for Local Main Chain

    Aggregates all triad records (Execution, Review, Compliance) and
    performs final gate adjudication.
    """

    def __init__(self, task_id: str, verification_dir: pathlib.Path):
        self.task_id = task_id
        self.verification_dir = verification_dir
        self.adjudicated_at = utc_now_iso()

        # Decision state
        self.blockers: list[str] = []
        self.warnings: list[str] = []
        self.required_changes: list[dict[str, str]] = []
        self.next_steps: list[str] = []

        # Evidence paths
        self.execution_report_path = verification_dir / f"{task_id}_execution_report.yaml"
        self.local_accept_path = verification_dir / f"{task_id}_local_accept_decision.json"
        self.gate_decision_path = verification_dir / f"{task_id}_gate_decision.json"
        self.compliance_attestation_path = verification_dir / f"{task_id}_compliance_attestation.json"

        # Load evidence
        self.execution_report = self._load_yaml_or_json(self.execution_report_path)
        self.local_accept = read_json(self.local_accept_path)
        self.gate_decision = read_json(self.gate_decision_path)
        self.compliance_attestation = read_json(self.compliance_attestation_path)

    def _load_yaml_or_json(self, path: pathlib.Path) -> dict[str, Any] | None:
        """Load file as YAML or JSON."""
        if not path.exists():
            return None
        try:
            import yaml
            return yaml.safe_load(path.read_text(encoding="utf-8"))
        except ImportError:
            return read_json(path)

    def check_triad_completeness(self) -> bool:
        """Check triad records completeness (Execution, Review, Compliance)."""
        missing = []
        if not self.execution_report:
            missing.append("execution_report")
        if not self.gate_decision:
            missing.append("gate_decision (Review)")
        if not self.compliance_attestation:
            missing.append("compliance_attestation")

        if missing:
            self.blockers.append(f"Missing triad records: {missing}")
            return False

        return True

    def check_compliance_precedence(self) -> bool:
        """Check compliance preceded execution (hard rule)."""
        if not self.compliance_attestation or not self.execution_report:
            return True  # Already checked in completeness

        # Get compliance decision
        compliance_decision = (
            self.compliance_attestation.get("decision") or
            self.compliance_attestation.get("attestation", {}).get("decision")
        )

        # Get compliance time
        compliance_time = (
            self.compliance_attestation.get("reviewed_at") or
            self.compliance_attestation.get("attestation", {}).get("reviewed_at") or
            self.compliance_attestation.get("signed_at")
        )

        # Get execution time
        execution_time = (
            self.execution_report.get("execution_date") or
            self.execution_report.get("started_at") or
            self.execution_report.get("created_at")
        )

        if compliance_decision and compliance_decision != "PASS":
            self.blockers.append(f"Compliance decision is {compliance_decision}, not PASS")
            return False

        # If we have timestamps, check precedence
        if compliance_time and execution_time:
            try:
                comp_dt = datetime.fromisoformat(compliance_time.replace("Z", "+00:00"))
                exec_dt = datetime.fromisoformat(execution_time.replace("Z", "+00:00"))
                if comp_dt > exec_dt:
                    self.blockers.append("Compliance attestation after execution (violates precedence)")
                    return False
            except ValueError:
                self.warnings.append("Could not parse timestamps for precedence check")

        return True

    def check_local_accept(self) -> bool:
        """Check local accept decision (if exists)."""
        if not self.local_accept:
            self.warnings.append("Local accept decision not found (non-blocking)")
            return True  # Non-blocking for backwards compatibility

        # Check decision
        local_decision = self.local_accept.get("decision")
        if local_decision == "DENY":
            self.blockers.append("Local accept decision is DENY")
            return False

        if local_decision == "REQUIRES_CHANGES":
            self.warnings.append("Local accept has REQUIRES_CHANGES")

        return True

    def check_gate_decision(self) -> bool:
        """Check gate decision."""
        if not self.gate_decision:
            return True  # Already checked in completeness

        # Get decision
        gate_decision = (
            self.gate_decision.get("decision") or
            self.gate_decision.get("gate_decision", {}).get("decision")
        )

        if gate_decision and gate_decision not in ["ALLOW", "PASS"]:
            self.blockers.append(f"Gate decision is {gate_decision}, not ALLOW/PASS")
            return False

        return True

    def check_evidence_refs(self) -> bool:
        """Check evidence refs exist and point to valid files."""
        evidence_refs = self.execution_report.get("evidence_refs", []) if self.execution_report else []

        if not evidence_refs:
            self.warnings.append("No evidence refs in execution report")
            return True  # Non-blocking

        valid_count = 0
        for ref in evidence_refs:
            locator = ref.get("locator")
            if locator:
                path = pathlib.Path(locator)
                if path.exists():
                    valid_count += 1

        if valid_count == 0:
            self.warnings.append("No evidence refs point to existing files")

        return True

    def adjudicate(self) -> dict[str, Any]:
        """Perform final gate adjudication."""
        # Run all checks
        triad_ok = self.check_triad_completeness()
        precedence_ok = self.check_compliance_precedence()
        local_ok = self.check_local_accept()
        gate_ok = self.check_gate_decision()
        evidence_ok = self.check_evidence_refs()

        # Determine decision
        if self.blockers:
            decision = "DENY"
            self.next_steps.append("Resolve all blockers before final accept")
        elif self.warnings:
            decision = "REQUIRES_CHANGES"
            self.next_steps.append("Review warnings and address if necessary")
        else:
            decision = "ALLOW"
            self.next_steps.append("Final accept passed, task complete")

        # Build required changes from warnings
        for warning in self.warnings:
            self.required_changes.append({
                "issue_key": f"FA-{self.task_id}-{len(self.required_changes) + 1}",
                "reason": warning,
                "next_action": "Review and resolve warning"
            })

        # Build final decision
        final_decision = {
            "schema_version": "final_accept_v1",
            "version": FINAL_ACCEPT_VERSION,
            "adjudicated_at_utc": self.adjudicated_at,
            "task_id": self.task_id,
            "decision": decision,
            "summary": self._build_summary(decision, triad_ok, precedence_ok, local_ok, gate_ok, evidence_ok),
            "verification_results": {
                "triad_completeness": triad_ok,
                "compliance_precedence": precedence_ok,
                "local_accept": local_ok,
                "gate_decision": gate_ok,
                "evidence_refs": evidence_ok,
            },
            "blocking_evidence": {
                "blockers": self.blockers,
                "warnings": self.warnings,
            },
            "required_changes": self.required_changes,
            "next_steps": self.next_steps,
            "triad_records": {
                "execution_report": str(self.execution_report_path) if self.execution_report else None,
                "gate_decision": str(self.gate_decision_path) if self.gate_decision else None,
                "compliance_attestation": str(self.compliance_attestation_path) if self.compliance_attestation else None,
            },
            "local_accept_record": str(self.local_accept_path) if self.local_accept else None,
        }

        return final_decision

    def _build_summary(
        self,
        decision: str,
        triad_ok: bool,
        precedence_ok: bool,
        local_ok: bool,
        gate_ok: bool,
        evidence_ok: bool
    ) -> str:
        """Build human-readable summary."""
        parts = [
            f"Final Accept Decision: {decision}",
            f"",
            f"Task ID: {self.task_id}",
            f"Adjudicated At: {self.adjudicated_at}",
            f"",
            f"Verification Results:",
            f"  - Triad Completeness: {'PASS' if triad_ok else 'FAIL'}",
            f"  - Compliance Precedence: {'PASS' if precedence_ok else 'FAIL'}",
            f"  - Local Accept: {'PASS' if local_ok else 'FAIL'}",
            f"  - Gate Decision: {'PASS' if gate_ok else 'FAIL'}",
            f"  - Evidence Refs: {'PASS' if evidence_ok else 'WARN'}",
        ]

        if self.blockers:
            parts.extend([
                f"",
                f"Blockers ({len(self.blockers)}):"
            ])
            for blocker in self.blockers:
                parts.append(f"  - {blocker}")

        if self.warnings:
            parts.extend([
                f"",
                f"Warnings ({len(self.warnings)}):"
            ])
            for warning in self.warnings:
                parts.append(f"  - {warning}")

        return "\n".join(parts)


# =============================================================================
# Main Entry Point
# =============================================================================
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Final Accept - Local Main Chain Final Unified Entry"
    )
    parser.add_argument("--task-id", required=True, help="Task ID to adjudicate")
    parser.add_argument(
        "--date",
        default=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        help="Date for verification directory (default: today)"
    )
    parser.add_argument(
        "--verification-dir",
        default=None,
        help="Override verification directory (default: docs/{date}/verification)"
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Output path (default: docs/{date}/verification/{task_id}_final_accept_decision.json)"
    )
    args = parser.parse_args()

    verification_dir = pathlib.Path(args.verification_dir) if args.verification_dir else pathlib.Path(f"docs/{args.date}/verification")
    output_path = pathlib.Path(args.out) if args.out else verification_dir / f"{args.task_id}_final_accept_decision.json"

    print("=" * 60)
    print("FINAL ACCEPT - Local Main Chain Final Gate")
    print("=" * 60)
    print(f"Task ID: {args.task_id}")
    print(f"Verification Dir: {verification_dir}")
    print(f"Output: {output_path}")
    print("=" * 60)

    # Create adjudicator
    adjudicator = FinalAcceptAdjudicator(args.task_id, verification_dir)

    # Perform adjudication
    decision = adjudicator.adjudicate()

    # Write output
    write_json(output_path, decision)

    # Print result
    print(f"\n[Decision] {decision['decision']}")
    print()

    if decision["blocking_evidence"]["blockers"]:
        print("[Blockers]")
        for blocker in decision["blocking_evidence"]["blockers"]:
            print(f"  - {blocker}")
        print()

    if decision["blocking_evidence"]["warnings"]:
        print("[Warnings]")
        for warning in decision["blocking_evidence"]["warnings"]:
            print(f"  - {warning}")
        print()

    print(f"[Output] {output_path}")
    print()
    print(decision["summary"])

    return 0 if decision["decision"] == "ALLOW" else 1


if __name__ == "__main__":
    sys.exit(main())
