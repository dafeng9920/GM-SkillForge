import argparse
import json
import re
from pathlib import Path


TASK_ROW_RE = re.compile(r"^\|\s*([A-Z][A-Z0-9_-]*)\s*\|")


def infer_status(e: bool, r: bool, c: bool):
    if not e and not r and not c:
        return "未开始", None
    if e and not r and not c:
        return "待审查", None
    if e and r and not c:
        return "待合规", None
    if e and r and c:
        return "待验收", None
    return None, "invalid_writeback_combination"


def main() -> int:
    parser = argparse.ArgumentParser(description="Minimal task board updater based on writeback files.")
    parser.add_argument("--task-board", required=True)
    parser.add_argument("--verification-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    board_path = Path(args.task_board)
    verification_dir = Path(args.verification_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    lines = board_path.read_text(encoding="utf-8").splitlines()
    updated = []
    summary = []
    anomalies = []

    for line in lines:
        match = TASK_ROW_RE.match(line)
        if not match:
            updated.append(line)
            continue

        task_id = match.group(1)
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 3:
            updated.append(line)
            continue

        exec_exists = (verification_dir / f"{task_id}_execution_report.md").exists()
        review_exists = (verification_dir / f"{task_id}_review_report.md").exists()
        compliance_exists = (verification_dir / f"{task_id}_compliance_attestation.md").exists()

        status, anomaly = infer_status(exec_exists, review_exists, compliance_exists)
        current_status = parts[-2] if len(parts) >= 3 else ""

        if anomaly:
            anomalies.append({
                "task_id": task_id,
                "anomaly": anomaly,
                "writeback": {
                    "execution_report": exec_exists,
                    "review_report": review_exists,
                    "compliance_attestation": compliance_exists,
                },
                "current_status": current_status,
            })
            updated.append(line)
            continue

        parts[-2] = f" {status} "
        new_line = "|".join(parts)
        updated.append(new_line)

        summary.append({
            "task_id": task_id,
            "status": status,
            "writeback": {
                "execution_report": exec_exists,
                "review_report": review_exists,
                "compliance_attestation": compliance_exists,
            },
        })

    board_path.write_text("\n".join(updated) + "\n", encoding="utf-8")
    (output_dir / "task_board_update_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_dir / "task_board_update_anomalies.json").write_text(
        json.dumps(anomalies, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

