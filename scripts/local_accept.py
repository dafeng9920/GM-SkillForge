#!/usr/bin/env python3
"""
Local Accept - Local Main Chain Back-End Unified Entry

本地主链后半段的 Local Accept 统一入口脚本。

此脚本在 absorb 完成后执行，负责：
1. 检查 Execution Report 是否存在且完整
2. 检查 Deliverables 是否齐全
3. 检查 Evidence Refs 是否有效
4. 生成 Local Accept Decision
5. 输出到 docs/{date}/verification/{task_id}_local_accept_decision.json

此脚本不修改任何业务逻辑，只做验证和决策输出。
保持与现有 pre_absorb_check.sh 和 absorb.sh 的兼容性。

Usage:
    python scripts/local_accept.py --task-id <task_id>
    python scripts/local_accept.py --task-id <task_id> --date <YYYY-MM-DD>
    python scripts/local_accept.py --task-id <task_id> --verification-dir <path>
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
LOCAL_ACCEPT_VERSION = "1.0.0"
DEFAULT_VERIFICATION_DIR = "docs/{date}/verification"
ALLOWED_DECISIONS = ["ALLOW", "REQUIRES_CHANGES", "DENY"]


# =============================================================================
# Utility Functions
# =============================================================================
def utc_now_iso() -> str:
    """Get current UTC time in ISO format with Z suffix."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: pathlib.Path) -> dict[str, Any]:
    """Read JSON file, return empty dict if not exists."""
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: pathlib.Path, obj: dict[str, Any]) -> None:
    """Write JSON file with UTF-8 encoding."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_yaml(path: pathlib.Path) -> dict[str, Any] | None:
    """Read YAML file."""
    try:
        import yaml
        if not path.exists():
            return None
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except ImportError:
        return None


# =============================================================================
# Local Accept Checker
# =============================================================================
class LocalAcceptChecker:
    """
    Local Accept Checker for Local Main Chain Back-End

    Checks execution completeness and generates local accept decision.
    Does NOT modify any existing logic or files.
    """

    def __init__(self, task_id: str, verification_dir: pathlib.Path):
        self.task_id = task_id
        self.verification_dir = verification_dir
        self.checked_at = utc_now_iso()

        # Decision state
        self.blockers: list[str] = []
        self.warnings: list[str] = []
        self.required_changes: list[dict[str, str]] = []
        self.next_steps: list[str] = []

        # Evidence collection
        self.execution_report_path = verification_dir / f"{task_id}_execution_report.yaml"
        self.gate_decision_path = verification_dir / f"{task_id}_gate_decision.json"
        self.compliance_attestation_path = verification_dir / f"{task_id}_compliance_attestation.json"

        # Loaded data
        self.execution_report = read_yaml(self.execution_report_path) or read_json(self.execution_report_path)
        self.gate_decision = read_json(self.gate_decision_path)
        self.compliance_attestation = read_json(self.compliance_attestation_path)

    def check_execution_report(self) -> bool:
        """Check execution report exists and has required fields."""
        if not self.execution_report:
            self.blockers.append(f"Execution report not found: {self.execution_report_path}")
            return False

        # Check required fields
        required_fields = ["task_id", "status", "deliverables", "evidence_refs"]
        missing_fields = [f for f in required_fields if f not in self.execution_report]

        if missing_fields:
            self.blockers.append(f"Execution report missing fields: {missing_fields}")
            return False

        # Check task_id match
        if self.execution_report.get("task_id") != self.task_id:
            self.blockers.append(f"Task ID mismatch in execution report: {self.execution_report.get('task_id')}")
            return False

        # Check status is completed (at least not failed)
        status = self.execution_report.get("status", "").upper()
        if status in ["FAILED", "BLOCKED"]:
            self.blockers.append(f"Execution status is {status}, cannot accept")
            return False

        if status not in ["COMPLETED", "PARTIALLY_COMPLETED"]:
            self.warnings.append(f"Unexpected execution status: {status}")

        return True

    def check_deliverables(self) -> bool:
        """Check all deliverables exist."""
        deliverables = self.execution_report.get("deliverables", [])
        if not deliverables:
            self.blockers.append("No deliverables listed in execution report")
            return False

        missing_files = []
        for item in deliverables:
            path_str = item.get("path")
            if not path_str:
                continue
            path = pathlib.Path(path_str)
            if not path.exists():
                missing_files.append(str(path))

        if missing_files:
            self.blockers.append(f"Deliverable files not found: {missing_files}")
            return False

        return True

    def check_evidence_refs(self) -> bool:
        """Check evidence refs are valid."""
        evidence_refs = self.execution_report.get("evidence_refs", [])
        if not evidence_refs:
            self.blockers.append("No evidence refs in execution report")
            return False

        # Check at least some evidence exists
        valid_count = 0
        for ref in evidence_refs:
            locator = ref.get("locator")
            if locator:
                path = pathlib.Path(locator)
                if path.exists():
                    valid_count += 1

        if valid_count == 0:
            self.warnings.append("No evidence refs point to existing files")
            return False

        return True

    def check_gate_decision(self) -> bool:
        """Check gate decision exists (non-blocking for local accept)."""
        if not self.gate_decision:
            self.warnings.append(f"Gate decision not found: {self.gate_decision_path}")
            return True  # Non-blocking

        # If exists, check decision is ALLOW
        decision = self.gate_decision.get("decision") or self.gate_decision.get("gate_decision", {}).get("decision")
        if decision and decision not in ["ALLOW", "PASS"]:
            self.warnings.append(f"Gate decision is {decision}, not ALLOW/PASS")

        return True

    def check_compliance_attestation(self) -> bool:
        """Check compliance attestation exists (non-blocking for local accept)."""
        if not self.compliance_attestation:
            self.warnings.append(f"Compliance attestation not found: {self.compliance_attestation_path}")
            return True  # Non-blocking

        # If exists, check decision is PASS
        decision = self.compliance_attestation.get("decision") or self.compliance_attestation.get("attestation", {}).get("decision")
        if decision and decision != "PASS":
            self.warnings.append(f"Compliance attestation is {decision}, not PASS")

        return True

    def generate_decision(self) -> dict[str, Any]:
        """Generate local accept decision."""
        # Run all checks
        report_ok = self.check_execution_report()
        deliverables_ok = self.check_deliverables()
        evidence_ok = self.check_evidence_refs()
        gate_ok = self.check_gate_decision()
        compliance_ok = self.check_compliance_attestation()

        # Determine decision
        if self.blockers:
            decision = "DENY"
            self.next_steps.append("Resolve all blockers before local accept")
        elif self.warnings:
            decision = "REQUIRES_CHANGES"
            self.next_steps.append("Review warnings and address if necessary")
        else:
            decision = "ALLOW"
            self.next_steps.append("Local accept passed, ready for final accept")

        # Build required changes from warnings
        for warning in self.warnings:
            self.required_changes.append({
                "issue_key": f"LA-{self.task_id}-{len(self.required_changes) + 1}",
                "reason": warning,
                "next_action": "Review and resolve warning"
            })

        # Build decision
        local_accept_decision = {
            "schema_version": "local_accept_v1",
            "version": LOCAL_ACCEPT_VERSION,
            "checked_at_utc": self.checked_at,
            "task_id": self.task_id,
            "decision": decision,
            "summary": self._build_summary(decision, report_ok, deliverables_ok, evidence_ok, gate_ok, compliance_ok),
            "verification_results": {
                "execution_report": report_ok,
                "deliverables": deliverables_ok,
                "evidence_refs": evidence_ok,
                "gate_decision": gate_ok,
                "compliance_attestation": compliance_ok,
            },
            "blocking_evidence": {
                "blockers": self.blockers,
                "warnings": self.warnings,
            },
            "required_changes": self.required_changes,
            "next_steps": self.next_steps,
            "artifacts": {
                "execution_report": str(self.execution_report_path),
                "gate_decision": str(self.gate_decision_path) if self.gate_decision_path.exists() else None,
                "compliance_attestation": str(self.compliance_attestation_path) if self.compliance_attestation_path.exists() else None,
            }
        }

        return local_accept_decision

    def _build_summary(
        self,
        decision: str,
        report_ok: bool,
        deliverables_ok: bool,
        evidence_ok: bool,
        gate_ok: bool,
        compliance_ok: bool
    ) -> str:
        """Build human-readable summary."""
        parts = [
            f"Local Accept Decision: {decision}",
            f"",
            f"Task ID: {self.task_id}",
            f"Checked At: {self.checked_at}",
            f"",
            f"Verification Results:",
            f"  - Execution Report: {'PASS' if report_ok else 'FAIL'}",
            f"  - Deliverables: {'PASS' if deliverables_ok else 'FAIL'}",
            f"  - Evidence Refs: {'PASS' if evidence_ok else 'FAIL'}",
            f"  - Gate Decision: {'PASS' if gate_ok else 'WARN'}",
            f"  - Compliance Attestation: {'PASS' if compliance_ok else 'WARN'}",
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
        description="Local Accept - Local Main Chain Back-End Unified Entry"
    )
    parser.add_argument("--task-id", required=True, help="Task ID to check")
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
        help="Output path (default: docs/{date}/verification/{task_id}_local_accept_decision.json)"
    )
    args = parser.parse_args()

    verification_dir = pathlib.Path(args.verification_dir) if args.verification_dir else pathlib.Path(DEFAULT_VERIFICATION_DIR.format(date=args.date))
    output_path = pathlib.Path(args.out) if args.out else verification_dir / f"{args.task_id}_local_accept_decision.json"

    print("=" * 60)
    print("LOCAL ACCEPT - Local Main Chain Back-End")
    print("=" * 60)
    print(f"Task ID: {args.task_id}")
    print(f"Verification Dir: {verification_dir}")
    print(f"Output: {output_path}")
    print("=" * 60)

    # Create checker
    checker = LocalAcceptChecker(args.task_id, verification_dir)

    # Generate decision
    decision = checker.generate_decision()

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
