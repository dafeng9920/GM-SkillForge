#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
TEST_DIR = ROOT / "scripts" / "l3_gap_closure"

TESTS = [
    ("A_constitution_hard_gate", TEST_DIR / "test_constitution_hard_gate.py"),
    ("B_registry_graph_integrity", TEST_DIR / "test_registry_graph_integrity.py"),
    ("C_incremental_delta_enforced", TEST_DIR / "test_incremental_delta_enforced.py"),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run L3 gap-closure killer tests in one command")
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "reports" / "l3_gap_closure" / datetime.now(timezone.utc).strftime("%Y-%m-%d")),
        help="Directory for per-test reports and summary outputs",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for test_id, test_script in TESTS:
        report_path = output_dir / f"{test_id}.json"
        cmd = [sys.executable, str(test_script), "--report", str(report_path)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        passed = proc.returncode == 0
        results.append(
            {
                "test_id": test_id,
                "script": str(test_script),
                "report_path": str(report_path),
                "passed": passed,
                "returncode": proc.returncode,
                "stdout_tail": proc.stdout[-1000:],
                "stderr_tail": proc.stderr[-1000:],
            }
        )
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {test_id} -> {report_path}")

    total = len(results)
    passed_count = sum(1 for r in results if r["passed"])
    failed_count = total - passed_count
    overall = "PASS" if failed_count == 0 else "FAIL"

    summary = {
        "suite_id": "L3_gap_closure_killer_tests",
        "generated_at_utc": utc_now(),
        "total": total,
        "passed": passed_count,
        "failed": failed_count,
        "overall_status": overall,
        "results": results,
    }

    summary_json = output_dir / "summary.json"
    summary_md = output_dir / "summary.md"
    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# L3 Gap Closure Killer Tests Summary",
        "",
        f"- Generated at: {summary['generated_at_utc']}",
        f"- Total: {total}",
        f"- Passed: {passed_count}",
        f"- Failed: {failed_count}",
        f"- Overall: {overall}",
        "",
        "## Test Results",
    ]
    for r in results:
        lines.append(
            f"- `{r['test_id']}`: {'PASS' if r['passed'] else 'FAIL'} "
            f"(report: `{r['report_path']}`)"
        )
    summary_md.write_text("\n".join(lines), encoding="utf-8")

    print(f"[SUMMARY] {summary_json}")
    print(f"[SUMMARY] {summary_md}")
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
