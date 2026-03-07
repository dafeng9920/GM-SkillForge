#!/usr/bin/env python3
import argparse
import datetime as dt
import hashlib
import json
import pathlib
import uuid


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def make_task_id() -> str:
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S")
    suffix = uuid.uuid4().hex[:8]
    return f"ocb-{stamp}-{suffix}"


def canonical_json(obj: dict) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def write_json(path: pathlib.Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_handoff(path: pathlib.Path, contract: dict) -> None:
    lines = [
        f"# OpenClaw Cloud Task Handoff",
        "",
        f"- task_id: `{contract['task_id']}`",
        f"- relay_agent: `{contract['relay']['agent']}`",
        f"- channel: `{contract['relay']['channel']}`",
        f"- objective: {contract['objective']}",
        f"- project_dir: `{contract['target']['project_dir']}`",
        "",
        "## Hard Constraints",
        "",
        "- fail_closed=true",
        "- Only execute commands in command_allowlist",
        "- Return required artifacts",
        "",
        "## command_allowlist",
        "",
    ]
    for cmd in contract["command_allowlist"]:
        lines.append(f"- `{cmd}`")
    lines.append("")
    lines.append("## required_artifacts")
    lines.append("")
    for item in contract["required_artifacts"]:
        lines.append(f"- `{item}`")
    lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create OpenClaw cloud task contract for Gemini relay.")
    parser.add_argument("--objective", required=True, help="Task objective summary")
    parser.add_argument("--project-dir", default="/root/openclaw-box", help="Remote project directory")
    parser.add_argument("--relay-agent", default="Antigravity-Gemini")
    parser.add_argument("--relay-channel", default="BlueLobster-Cloud")
    parser.add_argument("--allow", action="append", required=True, help="Allowed command (repeatable)")
    parser.add_argument("--accept", action="append", required=True, help="Acceptance criterion (repeatable)")
    parser.add_argument("--max-duration-sec", type=int, default=900)
    parser.add_argument("--max-commands", type=int, default=10)
    parser.add_argument("--task-id", default="")
    parser.add_argument("--out-dir", default=".tmp/openclaw-dispatch")
    args = parser.parse_args()

    task_id = args.task_id.strip() or make_task_id()
    created_at = utc_now_iso()

    contract = {
        "schema_version": "1.0.0",
        "task_id": task_id,
        "created_at_utc": created_at,
        "objective": args.objective,
        "relay": {"agent": args.relay_agent, "channel": args.relay_channel},
        "target": {"project_dir": args.project_dir},
        "policy": {
            "fail_closed": True,
            "max_duration_sec": args.max_duration_sec,
            "max_commands": args.max_commands,
        },
        "command_allowlist": args.allow,
        "acceptance": args.accept,
        "required_artifacts": ["execution_receipt.json", "stdout.log", "stderr.log", "audit_event.json"],
    }

    digest = hashlib.sha256(canonical_json(contract).encode("utf-8")).hexdigest()
    contract["contract_sha256"] = digest

    base = pathlib.Path(args.out_dir) / task_id
    write_json(base / "task_contract.json", contract)
    write_handoff(base / "handoff_note.md", contract)

    print(f"[ok] task_id={task_id}")
    print(f"[ok] contract={base / 'task_contract.json'}")
    print(f"[ok] handoff={base / 'handoff_note.md'}")
    print(f"[ok] contract_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
