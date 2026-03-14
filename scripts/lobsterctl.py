#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import shlex
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DISPATCH_DIR = ROOT / ".tmp" / "openclaw-dispatch"


def run_cmd(
    cmd: list[str],
    *,
    check: bool = True,
    capture: bool = False,
    timeout_sec: int = 120,
) -> subprocess.CompletedProcess[str]:
    kwargs: dict = {"text": True}
    if capture:
        kwargs["capture_output"] = True
    try:
        proc = subprocess.run(cmd, timeout=timeout_sec, **kwargs)
    except subprocess.TimeoutExpired:
        raise SystemExit(f"Command timed out after {timeout_sec}s: {' '.join(cmd)}")
    if check and proc.returncode != 0:
        raise SystemExit(proc.returncode)
    return proc


def powershell_file(script: str, args: list[str]) -> list[str]:
    return ["powershell", "-File", script, *args]


def cmd_submit(args: argparse.Namespace) -> int:
    script = str(ROOT / "scripts" / "run_cloud_task_detached.ps1")
    cmd = powershell_file(
        script,
        [
            "-TaskId",
            args.task_id,
            "-CloudHost",
            args.cloud_host,
            "-CloudUser",
            args.cloud_user,
            "-CloudRepo",
            args.cloud_repo,
        ],
    )
    run_cmd(cmd, check=True, capture=False, timeout_sec=180)
    return 0


def cmd_prepare(args: argparse.Namespace) -> int:
    task_dir = DISPATCH_DIR / args.task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    contract = {
        "task_id": args.task_id,
        "baseline_id": args.baseline_id,
        "objective": args.objective,
        "environment": "CLOUD-ROOT",
        "constraints": {"fail_closed": True},
        "policy": {"max_commands": 6},
        "command_allowlist": [
            "cd /root/gm-skillforge",
            "pwd",
            "python3 --version",
            "df -h",
            "free -m",
            "uptime",
        ],
        "required_artifacts": [
            "execution_receipt.json",
            "stdout.log",
            "stderr.log",
            "audit_event.json",
        ],
        "acceptance": [
            "execution_receipt.status == success",
            "execution_receipt.exit_code == 0",
            "executed_commands are a subset of command_allowlist",
            "required_artifacts are complete",
        ],
    }
    contract_path = task_dir / "task_contract.json"
    contract_path.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"CONTRACT_READY {contract_path}")
    return 0


def cmd_fetch(args: argparse.Namespace) -> int:
    script = str(ROOT / "scripts" / "fetch_cloud_task_artifacts.ps1")
    cmd = powershell_file(
        script,
        [
            "-TaskId",
            args.task_id,
            "-CloudHost",
            args.cloud_host,
            "-CloudUser",
            args.cloud_user,
            "-CloudRepo",
            args.cloud_repo,
        ],
    )
    run_cmd(cmd, check=True, capture=False, timeout_sec=180)
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    """Run verification with graceful error handling."""
    verification_dir = args.verification_dir
    if not verification_dir:
        today = dt.datetime.now().strftime("%Y-%m-%d")
        verification_dir = f"docs/{today}/verification"

    # Run enforce_cloud_lobster_closed_loop.py with graceful failure
    cmd1 = [
        sys.executable,
        str(ROOT / "scripts" / "enforce_cloud_lobster_closed_loop.py"),
        "--task-id",
        args.task_id,
        "--action",
        "verify",
    ]
    proc1 = run_cmd(cmd1, check=False, capture=False, timeout_sec=90)
    if proc1.returncode != 0:
        print(f"[WARNING] enforce_cloud_lobster_closed_loop.py returned exit code {proc1.returncode}", file=sys.stderr)
        print("[INFO] Continuing to verify_and_gate.py for partial results...")

    # Run verify_and_gate.py
    cmd2 = [
        sys.executable,
        str(ROOT / "scripts" / "verify_and_gate.py"),
        "--task-id",
        args.task_id,
        "--verification-dir",
        verification_dir,
    ]
    proc2 = run_cmd(cmd2, check=False, capture=False, timeout_sec=120)
    return proc2.returncode


def cmd_status(args: argparse.Namespace) -> int:
    """Check remote task status with bounded output and proper error handling."""
    pid_file = f"/var/run/{args.task_id}.pid"
    log_file = f"/var/log/gm-skillforge/{args.task_id}.nohup.log"
    remote = (
        "set -e; "
        f'PID_FILE="{pid_file}"; LOG_FILE="{log_file}"; '
        'if [ -f "$PID_FILE" ]; then '
        '  PID=$(cat "$PID_FILE" 2>/dev/null || true); '
        '  if [ -n "$PID" ] && ps -p "$PID" >/dev/null 2>&1; then STATE=RUNNING; else STATE=EXITED; fi; '
        'else STATE=NO_PID; PID=""; fi; '
        'if [ -f "$LOG_FILE" ]; then LOG_EXISTS=true; LOG_SIZE=$(wc -c < "$LOG_FILE" 2>/dev/null || echo 0); else LOG_EXISTS=false; LOG_SIZE=0; fi; '
        f'printf \'{{"task_id":"{args.task_id}","state":"%s","pid":"%s","log_exists":%s,"log_size":%s}}\\n\' "$STATE" "$PID" "$LOG_EXISTS" "$LOG_SIZE"'
    )
    # Avoid shell init side effects on remote host; run non-interactive bash explicitly.
    cmd = [
        "ssh",
        "-T",
        "-o",
        "BatchMode=yes",
        "-o",
        "ConnectTimeout=10",
        "-o",
        "ServerAliveInterval=5",
        "-o",
        "ServerAliveCountMax=2",
        f"{args.cloud_user}@{args.cloud_host}",
        "bash",
        "--noprofile",
        "--norc",
        "-lc",
        remote,
    ]
    proc = run_cmd(cmd, check=False, capture=True, timeout_sec=30)
    if proc.stdout:
        print(proc.stdout.strip())
    if proc.returncode != 0:
        if proc.stderr:
            print(proc.stderr.strip(), file=sys.stderr)
        return proc.returncode
    if getattr(args, "tail_lines", 0) > 0:
        tail_lines = min(args.tail_lines, 100)  # Bound tail lines to avoid hangs
        tail_cmd = [
            "ssh",
            "-T",
            "-o",
            "BatchMode=yes",
            "-o",
            "ConnectTimeout=10",
            "-o",
            "ServerAliveInterval=5",
            "-o",
            "ServerAliveCountMax=2",
            f"{args.cloud_user}@{args.cloud_host}",
            "bash",
            "--noprofile",
            "--norc",
            "-lc",
            f'tail -n {tail_lines} "{log_file}" 2>/dev/null || echo "(log file not accessible)"',
        ]
        tail_proc = run_cmd(tail_cmd, check=False, capture=True, timeout_sec=20)
        if tail_proc.stdout:
            print(tail_proc.stdout.strip())
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Lobster control-plane CLI for cloud closed-loop tasks.")
    sub = p.add_subparsers(dest="command", required=True)

    def add_common(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--task-id", required=True, help="Task ID, e.g. r1-cloud-smoke-20260306-0900")
        sp.add_argument("--cloud-host", default="BlueLobster-Cloud", help="SSH host/alias")
        sp.add_argument("--cloud-user", default="root", help="SSH user")
        sp.add_argument("--cloud-repo", default="/root/gm-skillforge", help="Repo path on cloud host")

    prepare = sub.add_parser("prepare", help="Create task_contract.json locally for R1 smoke task")
    prepare.add_argument("--task-id", required=True, help="Task ID, e.g. r1-cloud-smoke-20260306-0900")
    prepare.add_argument("--baseline-id", default="AG2-FIXED-CALIBER-TG1-20260304", help="Baseline ID")
    prepare.add_argument("--objective", default="R1 CLOUD-ROOT 基础链路回归（目录/版本/资源）", help="Task objective")
    prepare.set_defaults(func=cmd_prepare)

    submit = sub.add_parser("submit", help="Submit detached cloud execution for a prepared task contract")
    add_common(submit)
    submit.set_defaults(func=cmd_submit)

    status = sub.add_parser("status", help="Check remote pid/log status and tail cloud log")
    add_common(status)
    status.add_argument("--tail-lines", type=int, default=0, help="Optional remote log tail lines")
    status.set_defaults(func=cmd_status)

    fetch = sub.add_parser("fetch", help="Fetch cloud artifacts and run local gate checks")
    add_common(fetch)
    fetch.set_defaults(func=cmd_fetch)

    verify = sub.add_parser("verify", help="Run local enforce + verify_and_gate on fetched artifacts")
    verify.add_argument("--task-id", required=True, help="Task ID")
    verify.add_argument("--verification-dir", default="", help="Output directory for dual gate files")
    verify.set_defaults(func=cmd_verify)

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
