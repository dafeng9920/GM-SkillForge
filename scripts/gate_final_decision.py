#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_final_decision(date: str, job_id: str, verification_dir: Path) -> dict:
    # Required evidence for T101 close
    required_files = [
        "T90_execution_report.yaml",
        "T91_execution_report.yaml",
        "T92_execution_report.yaml",
        "T93_gate_decision.json",
        "T94_compliance_attestation.json",
        "T95_execution_report.yaml",
        "T96_execution_report.yaml",
        "T97_execution_report.yaml",
        "T98_gate_decision.json",
        "T99_compliance_attestation.json",
        "T100_execution_report.yaml",
    ]

    missing = [f for f in required_files if not (verification_dir / f).exists()]
    if missing:
        return {
            "gate_id": f"L4P5-FINAL-GATE-{date.replace('-', '')}",
            "job_id": job_id,
            "orchestrator": "Codex",
            "stage": "L4 -> L4.5",
            "decided_at": now_iso(),
            "decision": "DENY",
            "summary": "Final Gate denied: missing required triad artifacts.",
            "blocking_evidence": [{"task": "ARTIFACTS", "required": "present", "actual": "missing", "locator": m} for m in missing],
            "required_changes": [{"issue_key": "SF-FINAL-001", "reason": "Missing required artifacts", "next_action": "Generate missing files and rerun final gate"}],
            "next_steps": [{"step": 1, "owner": "Orchestrator", "action": "Collect missing artifacts and rerun gate"}],
        }

    t93 = read_json(verification_dir / "T93_gate_decision.json").get("decision")
    t94 = read_json(verification_dir / "T94_compliance_attestation.json").get("decision")
    t98 = read_json(verification_dir / "T98_gate_decision.json").get("decision")
    t99 = read_json(verification_dir / "T99_compliance_attestation.json").get("decision")

    blockers = []
    if t93 != "ALLOW":
        blockers.append({"task": "T93", "required": "ALLOW", "actual": t93, "locator": str((verification_dir / "T93_gate_decision.json").as_posix())})
    if t94 != "PASS":
        blockers.append({"task": "T94", "required": "PASS", "actual": t94, "locator": str((verification_dir / "T94_compliance_attestation.json").as_posix())})
    if t98 != "ALLOW":
        blockers.append({"task": "T98", "required": "ALLOW", "actual": t98, "locator": str((verification_dir / "T98_gate_decision.json").as_posix())})
    if t99 != "PASS":
        blockers.append({"task": "T99", "required": "PASS", "actual": t99, "locator": str((verification_dir / "T99_compliance_attestation.json").as_posix())})

    if blockers:
        decision = "REQUIRES_CHANGES"
        summary = "Final Gate blocked: prerequisite decisions are not all satisfied."
        required_changes = [
            {
                "issue_key": "SF-FINAL-PREREQ-001",
                "reason": "Gate/compliance prerequisites not satisfied",
                "next_action": "Rerun blocked tasks and regenerate final gate",
            }
        ]
    else:
        decision = "ALLOW"
        summary = "Final Gate passed: dependency chain closed and all gate/compliance prerequisites satisfied."
        required_changes = []

    return {
        "gate_id": f"L4P5-FINAL-GATE-{date.replace('-', '')}",
        "job_id": job_id,
        "orchestrator": "Codex",
        "stage": "L4 -> L4.5",
        "decided_at": now_iso(),
        "decision": decision,
        "summary": summary,
        "blocking_evidence": blockers,
        "required_changes": required_changes,
        "next_steps": [
            {
                "step": 1,
                "owner": "Codex",
                "action": "Proceed to L5 wave kickoff" if decision == "ALLOW" else "Resolve blockers and rerun final gate",
            }
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute final gate decision for L4P5 batch.")
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--job-id", required=True)
    parser.add_argument(
        "--verification-dir",
        default=None,
        help="Override verification directory (default: docs/{date}/verification)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output path (default: docs/{date}/verification/L4P5_final_gate_decision.json)",
    )
    args = parser.parse_args()

    verification_dir = Path(args.verification_dir) if args.verification_dir else Path("docs") / args.date / "verification"
    output_path = Path(args.output) if args.output else verification_dir / "L4P5_final_gate_decision.json"

    decision = build_final_decision(args.date, args.job_id, verification_dir)
    output_path.write_text(json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[gate-final] output={output_path}")
    print(f"[gate-final] decision={decision['decision']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

