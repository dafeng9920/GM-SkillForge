import argparse
import json
from pathlib import Path


def read_if_exists(path: Path) -> str | None:
    return path.read_text(encoding="utf-8") if path.exists() else None


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def infer_state(execution_exists: bool, review_exists: bool, compliance_exists: bool) -> str:
    if execution_exists and review_exists and compliance_exists:
        return "GATE_READY"
    if execution_exists and review_exists:
        return "COMPLIANCE_TRIGGERED"
    if execution_exists:
        return "REVIEW_TRIGGERED"
    return "PENDING"


def build_envelope(task_id: str, module: str, role: str, assignee: str, verification_dir: Path) -> dict:
    next_hop = {
        "execution": "review",
        "review": "compliance",
        "compliance": "final_gate",
    }.get(role, "none")
    return {
        "task_envelope": {
            "task_id": task_id,
            "module": module,
            "role": role,
            "assignee": assignee,
            "depends_on": [],
            "parallel_group": "AUTO_RELAY",
            "source_of_truth": [],
            "writeback": {
                "execution_report": str(verification_dir / f"{task_id}_execution_report.md"),
                "review_report": str(verification_dir / f"{task_id}_review_report.md"),
                "compliance_attestation": str(verification_dir / f"{task_id}_compliance_attestation.md"),
                "final_gate": str(verification_dir / f"{task_id}_final_gate.md"),
            },
            "acceptance_criteria": [
                "required writeback exists",
                "no scope violation",
            ],
            "hard_constraints": [
                "no runtime",
                "no frozen mutation",
            ],
            "escalation_trigger": [
                "scope_violation",
                "blocking_dependency",
                "ambiguous_spec",
                "review_deny",
                "compliance_fail",
                "state_timeout",
            ],
            "next_hop": next_hop,
        }
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Minimal relay helper for task dispatcher protocol.")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--module", required=True)
    parser.add_argument("--verification-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--reviewer", default="REVIEWER_TBD")
    parser.add_argument("--compliance-officer", default="COMPLIANCE_TBD")
    parser.add_argument("--trigger", default=None, help="Optional escalation trigger to emit escalation_pack.")
    args = parser.parse_args()

    verification_dir = Path(args.verification_dir)
    output_dir = Path(args.output_dir)
    task_id = args.task_id

    execution_path = verification_dir / f"{task_id}_execution_report.md"
    review_path = verification_dir / f"{task_id}_review_report.md"
    compliance_path = verification_dir / f"{task_id}_compliance_attestation.md"

    execution_exists = execution_path.exists()
    review_exists = review_path.exists()
    compliance_exists = compliance_path.exists()

    state = infer_state(execution_exists, review_exists, compliance_exists)

    summary = {
        "task_id": task_id,
        "module": args.module,
        "state": state,
        "writeback": {
            "execution_report": execution_exists,
            "review_report": review_exists,
            "compliance_attestation": compliance_exists,
        },
    }
    write_json(output_dir / f"{task_id}_relay_summary.json", summary)

    if state == "REVIEW_TRIGGERED":
        payload = build_envelope(task_id, args.module, "review", args.reviewer, verification_dir)
        write_json(output_dir / f"{task_id}_review_envelope.json", payload)
    elif state == "COMPLIANCE_TRIGGERED":
        payload = build_envelope(task_id, args.module, "compliance", args.compliance_officer, verification_dir)
        write_json(output_dir / f"{task_id}_compliance_envelope.json", payload)
    elif state == "GATE_READY":
        payload = {
            "task_id": task_id,
            "module": args.module,
            "state": state,
            "execution_report": str(execution_path),
            "review_report": str(review_path),
            "compliance_attestation": str(compliance_path),
        }
        write_json(output_dir / f"{task_id}_final_gate_input.json", payload)

    if args.trigger:
        escalation = {
            "escalation": {
                "task_id": task_id,
                "current_state": state,
                "trigger": args.trigger,
                "blocking_reason": f"triggered:{args.trigger}",
                "evidence_ref": str(output_dir / f"{task_id}_relay_summary.json"),
                "suggested_next_action": "controller review required",
            }
        }
        write_json(output_dir / f"{task_id}_escalation_pack.json", escalation)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

