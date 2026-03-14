#!/usr/bin/env python3
"""
Antigravity-1 Final Gate Adjudicator

Aggregates baseline freeze and task contract artifacts to output final gate decision.
Performs P0 final adjudication for Antigravity-1 execution.

Usage:
    python scripts/antigravity_final_gate.py --baseline-id <id> --task-id <id>
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys


# =============================================================================
# Configuration
# =============================================================================
ANTIGRAVITY_VERSION = "1.0.0"
BASELINE_FREEZE_DIR = pathlib.Path(".tmp/antigravity-baseline")
TASK_CONTRACT_DIR = pathlib.Path(".tmp/openclaw-dispatch")
VERIFICATION_DIR = pathlib.Path("docs/2026-03-04/verification")
AUDIT_EVIDENCE_DIR = pathlib.Path("AuditPack/evidence")


# =============================================================================
# Utility Functions
# =============================================================================
def utc_now_iso() -> str:
    """Get current UTC time in ISO format with Z suffix."""
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: pathlib.Path) -> dict:
    """Read JSON file."""
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: pathlib.Path, obj: dict) -> None:
    """Write JSON file with UTF-8 encoding."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def pick_value(obj: dict, keys: list[str]) -> str:
    """Pick first non-empty value from object by key priority."""
    for k in keys:
        v = obj.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


# =============================================================================
# Final Gate Adjudicator
# =============================================================================
class AntigravityFinalGate:
    """
    Antigravity-1 Final Gate Adjudicator

    Performs P0 final adjudication for baseline freeze and task contract.
    Outputs ALLOW|REQUIRES_CHANGES|DENY decision with blocking evidence.
    """

    def __init__(self, baseline_id: str, task_id: str):
        self.baseline_id = baseline_id
        self.task_id = task_id
        self.adjudicated_at = utc_now_iso()
        self.baseline_dir = BASELINE_FREEZE_DIR / baseline_id
        self.task_dir = TASK_CONTRACT_DIR / task_id

        # Evidence collection
        self.evidence = {
            "baseline_manifest": read_json(self.baseline_dir / "BASELINE_MANIFEST.json"),
            "baseline_activation": read_json(self.baseline_dir / "ACTIVATION.json"),
            "task_contract": read_json(self.task_dir / "task_contract.json"),
            "dispatch_summary": read_json(self.task_dir / "dispatch_summary.json"),
        }

        # Decision state
        self.blockers: list[str] = []
        self.warnings: list[str] = []
        self.required_changes: list[str] = []
        self.next_steps: list[str] = []

    def check_baseline_freeze(self) -> bool:
        """Check baseline freeze artifacts."""
        manifest = self.evidence["baseline_manifest"]
        activation = self.evidence["baseline_activation"]

        # Check manifest exists
        if not manifest:
            self.blockers.append("BASELINE_MANIFEST.json missing or invalid")
            return False

        # Check activation exists
        if not activation:
            self.blockers.append("ACTIVATION.json missing or invalid")
            return False

        # Check baseline_id consistency
        if manifest.get("baseline_id") != self.baseline_id:
            self.blockers.append(f"baseline_id mismatch: manifest has {manifest.get('baseline_id')}")
            return False

        if activation.get("baseline_id") != self.baseline_id:
            self.blockers.append(f"baseline_id mismatch: activation has {activation.get('baseline_id')}")
            return False

        # Check activation status
        if activation.get("status") != "ACTIVE":
            self.blockers.append(f"Baseline activation status is {activation.get('status')}, expected ACTIVE")
            return False

        # Check baseline SHA256
        baseline_sha256 = manifest.get("baseline_sha256")
        if not baseline_sha256 or len(baseline_sha256) != 64:
            self.blockers.append("baseline_sha256 missing or invalid length")
            return False

        # Check files snapshot
        files = manifest.get("files", [])
        if not files:
            self.warnings.append("No files in baseline snapshot")
            return True

        # Verify each file has required fields
        for file_info in files:
            if not all(k in file_info for k in ["name", "sha256", "snapshot_path"]):
                self.warnings.append(f"File {file_info.get('name', '?')} missing required fields")

        return True

    def check_task_contract(self) -> bool:
        """Check task contract artifacts."""
        contract = self.evidence["task_contract"]
        summary = self.evidence["dispatch_summary"]

        # Check contract exists
        if not contract:
            self.blockers.append("task_contract.json missing or invalid")
            return False

        # Check summary exists
        if not summary:
            self.warnings.append("dispatch_summary.json missing (non-critical)")

        # Check task_id consistency
        if contract.get("task_id") != self.task_id:
            self.blockers.append(f"task_id mismatch: contract has {contract.get('task_id')}")
            return False

        if summary and summary.get("task_id") != self.task_id:
            self.warnings.append(f"task_id mismatch: summary has {summary.get('task_id')}")

        # Check required fields
        required_fields = [
            "schema_version", "task_id", "created_at_utc", "objective",
            "relay", "target", "policy", "command_allowlist",
            "acceptance", "required_artifacts", "contract_sha256"
        ]

        for field in required_fields:
            if field not in contract:
                self.blockers.append(f"Contract missing required field: {field}")
                return False

        # Check contract SHA256
        contract_sha256 = contract.get("contract_sha256")
        if not contract_sha256 or len(contract_sha256) != 64:
            self.blockers.append("contract_sha256 missing or invalid length")
            return False

        # Check policy
        policy = contract.get("policy", {})
        if not policy.get("fail_closed"):
            self.blockers.append("policy.fail_closed must be true")
            return False

        # Check command allowlist
        allowlist = contract.get("command_allowlist", [])
        if not allowlist:
            self.blockers.append("command_allowlist is empty")
            return False

        # Check required artifacts
        required_artifacts = contract.get("required_artifacts", [])
        required = {"execution_receipt.json", "stdout.log", "stderr.log", "audit_event.json"}
        if not set(required_artifacts) >= required:
            missing = required - set(required_artifacts)
            self.blockers.append(f"Missing required artifacts: {missing}")
            return False

        return True

    def check_consistency(self) -> bool:
        """Check consistency between baseline and contract."""
        manifest = self.evidence["baseline_manifest"]
        contract = self.evidence["task_contract"]

        if not manifest or not contract:
            return False

        # Check version consistency
        manifest_version = manifest.get("version")
        if manifest_version != ANTIGRAVITY_VERSION:
            self.warnings.append(f"Version mismatch: manifest has {manifest_version}, expected {ANTIGRAVITY_VERSION}")

        # Check relay configuration
        relay = contract.get("relay", {})
        if relay.get("agent") != "Antigravity-Gemini":
            self.warnings.append(f"Unexpected relay agent: {relay.get('agent')}")

        if relay.get("channel") != "BlueLobster-Cloud":
            self.warnings.append(f"Unexpected relay channel: {relay.get('channel')}")

        # Check if summary references baseline
        summary = self.evidence["dispatch_summary"]
        if summary:
            summary_baseline_id = summary.get("baseline_id")
            if summary_baseline_id != self.baseline_id:
                self.blockers.append(f"Summary references different baseline: {summary_baseline_id}")
                return False

        return True

    def check_audit_evidence(self) -> bool:
        """Check audit evidence was created."""
        audit_path = AUDIT_EVIDENCE_DIR / f"antigravity_baseline_activation_{self.baseline_id}.json"
        if not audit_path.exists():
            self.warnings.append(f"Audit evidence not found: {audit_path}")
            return False

        audit_data = read_json(audit_path)
        if not audit_data:
            self.warnings.append("Audit evidence file is empty")
            return False

        if audit_data.get("baseline_id") != self.baseline_id:
            self.warnings.append("Audit evidence baseline_id mismatch")
            return False

        return True

    def adjudicate(self) -> dict:
        """Perform final gate adjudication."""
        # Run all checks
        baseline_ok = self.check_baseline_freeze()
        contract_ok = self.check_task_contract()
        consistency_ok = self.check_consistency()
        audit_ok = self.check_audit_evidence()

        # Determine decision
        if self.blockers:
            decision = "DENY"
            self.next_steps.append("Resolve all blockers before proceeding")
        elif self.warnings:
            decision = "REQUIRES_CHANGES"
            self.next_steps.append("Review warnings and address if necessary")
        else:
            decision = "ALLOW"
            self.next_steps.append("Ready for cloud dispatch via Gemini relay")

        # Build required changes from warnings
        for warning in self.warnings:
            self.required_changes.append(f"Review and resolve: {warning}")

        # Build final decision
        final_decision = {
            "schema_version": "antigravity_final_gate_v1",
            "antigravity_version": ANTIGRAVITY_VERSION,
            "adjudicated_at_utc": self.adjudicated_at,
            "baseline_id": self.baseline_id,
            "task_id": self.task_id,
            "decision": decision,
            "summary": self._build_summary(decision, baseline_ok, contract_ok, consistency_ok, audit_ok),
            "blocking_evidence": {
                "blockers": self.blockers,
                "warnings": self.warnings,
            },
            "required_changes": self.required_changes,
            "next_steps": self.next_steps,
            "artifacts": {
                "baseline_manifest": str(self.baseline_dir / "BASELINE_MANIFEST.json"),
                "baseline_activation": str(self.baseline_dir / "ACTIVATION.json"),
                "task_contract": str(self.task_dir / "task_contract.json"),
                "handoff_note": str(self.task_dir / "handoff_note.md"),
                "dispatch_summary": str(self.task_dir / "dispatch_summary.json"),
                "audit_evidence": str(AUDIT_EVIDENCE_DIR / f"antigravity_baseline_activation_{self.baseline_id}.json"),
            },
            "verification_results": {
                "baseline_freeze": baseline_ok,
                "task_contract": contract_ok,
                "consistency": consistency_ok,
                "audit_evidence": audit_ok,
            }
        }

        return final_decision

    def _build_summary(
        self,
        decision: str,
        baseline_ok: bool,
        contract_ok: bool,
        consistency_ok: bool,
        audit_ok: bool
    ) -> str:
        """Build human-readable summary."""
        parts = [
            f"Antigravity-1 Final Gate Adjudication",
            f"Decision: {decision}",
            f"",
            f"Baseline ID: {self.baseline_id}",
            f"Task ID: {self.task_id}",
            f"",
            f"Verification Results:",
            f"  - Baseline Freeze: {'PASS' if baseline_ok else 'FAIL'}",
            f"  - Task Contract: {'PASS' if contract_ok else 'FAIL'}",
            f"  - Consistency: {'PASS' if consistency_ok else 'FAIL'}",
            f"  - Audit Evidence: {'PASS' if audit_ok else 'FAIL'}",
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
        description="Antigravity-1: Final gate adjudication for baseline freeze and task contract"
    )
    parser.add_argument("--baseline-id", required=True, help="Baseline freeze ID")
    parser.add_argument("--task-id", required=True, help="Task contract ID")
    parser.add_argument("--out", default=VERIFICATION_DIR / "antigravity_final_gate_decision.json",
                        help="Output path for final gate decision")
    args = parser.parse_args()

    print(f"[Antigravity-1] Final Gate Adjudication")
    print(f"[Antigravity-1] Version: {ANTIGRAVITY_VERSION}")
    print(f"[Antigravity-1] Baseline ID: {args.baseline_id}")
    print(f"[Antigravity-1] Task ID: {args.task_id}")
    print()

    # Create adjudicator
    adjudicator = AntigravityFinalGate(args.baseline_id, args.task_id)

    # Perform adjudication
    decision = adjudicator.adjudicate()

    # Write output
    output_path = pathlib.Path(args.out)
    write_json(output_path, decision)

    # Print result
    print(f"[Decision] {decision['decision']}")
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

    # Print summary
    print(decision["summary"])

    return 0 if decision["decision"] == "ALLOW" else 1


if __name__ == "__main__":
    sys.exit(main())
