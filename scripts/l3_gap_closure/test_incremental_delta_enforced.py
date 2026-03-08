from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_json, run_cli_refine, utc_now, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="L3 killer test C: incremental delta enforcement")
    parser.add_argument("--report", required=True, help="Output report path")
    args = parser.parse_args()

    report_path = Path(args.report).resolve()
    prompts = [
        "生成一个量化交易系统Skill蓝图",
        "在已有量化交易系统Skill基础上新增实时风险监控",
        "在已有量化交易系统Skill基础上新增实时风险监控并升级异常告警",
    ]

    with tempfile.TemporaryDirectory(prefix="l3-delta-") as tmp:
        workspace = Path(tmp)
        outputs = []
        commands = []

        for i, prompt in enumerate(prompts, start=1):
            out_path = workspace / f"round{i}.json"
            cmd = run_cli_refine(
                workspace=workspace,
                prompt=prompt,
                output_path=out_path,
            )
            output = load_json(out_path) if out_path.exists() else {}
            outputs.append(output)
            commands.append(
                {
                    "round": i,
                    "command": cmd.command,
                    "returncode": cmd.returncode,
                    "stdout_tail": cmd.stdout[-500:],
                    "stderr_tail": cmd.stderr[-500:],
                }
            )

        publish = [o.get("publish_result") or {} for o in outputs]
        skill_ids = [p.get("skill_id") for p in publish]
        versions = [p.get("version") for p in publish]

        unique_skill_ids = {s for s in skill_ids if s}
        unique_versions = {v for v in versions if v}

        versioning_ok = len(unique_skill_ids) > 1 or len(unique_versions) > 1

        # Require explicit graph artifact exposure in output payload
        graph_signals = [
            any(k in o for k in ("updated_graph", "graph_diff", "graph_update", "UpdatedGraph"))
            for o in outputs
        ]
        graph_ok = any(graph_signals)

        # Require explicit release manifest/rollback exposure
        manifest_signals = [
            any(k in o for k in ("release_manifest", "manifest", "rollback_to", "ReleaseManifest"))
            for o in outputs
        ]
        manifest_ok = any(manifest_signals)

        passed = versioning_ok and graph_ok and manifest_ok

        payload = {
            "test_id": "C_incremental_delta_enforced",
            "timestamp_utc": utc_now(),
            "workspace": str(workspace),
            "commands": commands,
            "round_outputs_snapshot": [
                {
                    "round": i + 1,
                    "status": o.get("status"),
                    "publish_result": o.get("publish_result"),
                    "gate_decisions": o.get("gate_decisions"),
                    "error": o.get("error"),
                }
                for i, o in enumerate(outputs)
            ],
            "evaluation": {
                "passed": passed,
                "checks": {
                    "version_or_skill_evolves": versioning_ok,
                    "graph_update_exposed": graph_ok,
                    "release_manifest_or_rollback_exposed": manifest_ok,
                },
                "observed": {
                    "skill_ids": skill_ids,
                    "versions": versions,
                    "unique_skill_id_count": len(unique_skill_ids),
                    "unique_version_count": len(unique_versions),
                    "graph_signals_by_round": graph_signals,
                    "manifest_signals_by_round": manifest_signals,
                },
            },
        }
        write_json(report_path, payload)
        return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
