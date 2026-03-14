#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import pathlib
import uuid


REQUIRED_ARTIFACTS = [
    "execution_receipt.json",
    "stdout.log",
    "stderr.log",
    "audit_event.json",
]

DEFAULT_ACCEPTANCE = [
    "All commands executed successfully",
    "All commands within allowlist",
    "No unauthorized commands detected",
    "Four-piece artifacts complete",
    "Exit code 0 achieved",
]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def make_task_id() -> str:
    return f"tg1-official-{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M')}-{uuid.uuid4().hex[:4]}"


def write_json(path: pathlib.Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_handoff(path: pathlib.Path, task_id: str, contract_path: pathlib.Path) -> None:
    lines = [
        f"# {task_id} Cloud Handoff",
        "",
        "## 对执行体说（agent prompt）",
        "你是 Antigravity-3（小龙虾），只允许按 task_contract.json 的 command_allowlist 顺序执行。",
        "必须回传 execution_receipt.json/stdout.log/stderr.log/audit_event.json。",
        "任一缺失按 FAIL_CLOSED 处理。",
        "",
        "## 合同路径",
        str(contract_path).replace("\\", "/"),
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create fixed-caliber cloud task contract for Antigravity-3.")
    parser.add_argument("--task-id", default="")
    parser.add_argument("--baseline-id", required=True)
    parser.add_argument("--objective", required=True)
    parser.add_argument("--target-dir", default="/root/openclaw-box")
    parser.add_argument("--created-by", default="Antigravity-1")
    parser.add_argument("--allow", action="append", required=True)
    parser.add_argument("--accept", action="append")
    parser.add_argument("--max-duration-sec", type=int, default=300)
    parser.add_argument("--max-commands", type=int, default=10)
    parser.add_argument("--out-dir", default=".tmp/openclaw-dispatch")
    args = parser.parse_args()

    task_id = args.task_id.strip() or make_task_id()
    acceptance = args.accept if args.accept else list(DEFAULT_ACCEPTANCE)

    contract = {
        "schema_version": "openclaw_task_contract_v1",
        "task_id": task_id,
        "baseline_id": args.baseline_id,
        "created_at": utc_now(),
        "created_by": args.created_by,
        "environment": "CLOUD-ROOT",
        "objective": args.objective,
        "target": {"project_dir": args.target_dir},
        "command_allowlist": args.allow,
        "constraints": {
            "max_duration_sec": args.max_duration_sec,
            "max_commands": args.max_commands,
            "fail_closed": True,
        },
        # Kept for compatibility with existing verifier implementation.
        "policy": {
            "max_duration_sec": args.max_duration_sec,
            "max_commands": args.max_commands,
            "fail_closed": True,
        },
        "acceptance": acceptance,
        "required_artifacts": list(REQUIRED_ARTIFACTS),
    }

    base = pathlib.Path(args.out_dir) / task_id
    contract_path = base / "task_contract.json"
    handoff_path = base / "handoff_note.md"
    write_json(contract_path, contract)
    write_handoff(handoff_path, task_id, contract_path)

    print(f"[ok] task_id={task_id}")
    print(f"[ok] contract={contract_path.as_posix()}")
    print(f"[ok] handoff={handoff_path.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

