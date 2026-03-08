from __future__ import annotations

import argparse
import sqlite3
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_json, run_cli_refine, utc_now, write_json


def tamper_latest_revision(db_path: Path, skill_id: str) -> dict:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT revision_id, manifest_sha256 FROM revisions WHERE skill_id=? ORDER BY effective_at DESC LIMIT 1",
            (skill_id,),
        ).fetchone()
        if row is None:
            return {"tampered": False, "reason": "no_revision_found"}

        revision_id = row["revision_id"]
        original = row["manifest_sha256"]
        conn.execute(
            "UPDATE revisions SET manifest_sha256=? WHERE revision_id=?",
            ("tampered-manifest-sha256-for-l3-test", revision_id),
        )
        conn.commit()
        return {
            "tampered": True,
            "revision_id": revision_id,
            "original_manifest_sha256": original,
            "new_manifest_sha256": "tampered-manifest-sha256-for-l3-test",
        }
    finally:
        conn.close()


def conflict_detected(second_output: dict) -> bool:
    status = second_output.get("status")
    error = second_output.get("error") or {}
    gate_decisions = second_output.get("gate_decisions") or []
    publish = second_output.get("publish_result") or {}

    if status in {"failed", "gate_denied"}:
        return True
    if error:
        msg = f"{error.get('code', '')} {error.get('message', '')}".lower()
        if any(k in msg for k in ("conflict", "integrity", "hash", "mismatch", "tamper")):
            return True
    for g in gate_decisions:
        decision = str(g.get("decision", "")).upper()
        if decision in {"DENY", "BLOCK", "REQUIRES_CHANGES"}:
            return True
    if publish.get("status") != "published":
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="L3 killer test B: registry/graph tamper integrity")
    parser.add_argument("--report", required=True, help="Output report path")
    args = parser.parse_args()

    report_path = Path(args.report).resolve()

    with tempfile.TemporaryDirectory(prefix="l3-integrity-") as tmp:
        workspace = Path(tmp)

        first_output_path = workspace / "round1_baseline.json"
        first_cmd = run_cli_refine(
            workspace=workspace,
            prompt="生成一个量化交易系统Skill蓝图",
            output_path=first_output_path,
        )
        first_output = load_json(first_output_path) if first_output_path.exists() else {}

        publish1 = first_output.get("publish_result") or {}
        skill_id = publish1.get("skill_id", "")
        db_path = workspace / "db" / "skillforge.sqlite"

        tamper_result = {"tampered": False, "reason": "missing_db_or_skill_id"}
        if db_path.exists() and skill_id:
            tamper_result = tamper_latest_revision(db_path, skill_id)

        second_output_path = workspace / "round2_after_tamper.json"
        second_cmd = run_cli_refine(
            workspace=workspace,
            prompt="在现有量化Skill基础上新增实时风险监控与异常告警能力",
            output_path=second_output_path,
        )
        second_output = load_json(second_output_path) if second_output_path.exists() else {}

        detected = conflict_detected(second_output)
        payload = {
            "test_id": "B_registry_graph_integrity",
            "timestamp_utc": utc_now(),
            "workspace": str(workspace),
            "first_command": first_cmd.command,
            "first_returncode": first_cmd.returncode,
            "second_command": second_cmd.command,
            "second_returncode": second_cmd.returncode,
            "db_path": str(db_path),
            "tamper_result": tamper_result,
            "first_output_snapshot": {
                "status": first_output.get("status"),
                "publish_result": first_output.get("publish_result"),
                "error": first_output.get("error"),
            },
            "second_output_snapshot": {
                "status": second_output.get("status"),
                "gate_decisions": second_output.get("gate_decisions"),
                "publish_result": second_output.get("publish_result"),
                "error": second_output.get("error"),
            },
            "evaluation": {
                "passed": detected,
                "checks": {
                    "tamper_applied": bool(tamper_result.get("tampered")),
                    "conflict_or_block_detected": detected,
                },
            },
        }
        write_json(report_path, payload)
        return 0 if detected else 1


if __name__ == "__main__":
    raise SystemExit(main())
