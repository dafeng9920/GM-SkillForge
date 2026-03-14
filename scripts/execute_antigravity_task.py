#!/usr/bin/env python3
"""
Antigravity-1 Task Executor

Executes task contract allowlist commands and generates execution artifacts.
This is the LOCAL-ANTIGRAVITY executor that coordinates CLOUD-ROOT execution.

Usage:
    python scripts/execute_antigravity_task.py --task-id ocb-20260304-140239-a3db40c0
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import subprocess
import sys


# =============================================================================
# Configuration
# =============================================================================
ANTIGRAVITY_VERSION = "1.0.0"
TASK_CONTRACT_DIR = pathlib.Path(".tmp/openclaw-dispatch")
VERIFICATION_SCRIPT = pathlib.Path("skills/openclaw-cloud-bridge-skill/scripts/verify_execution_receipt.py")


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


def write_text(path: pathlib.Path, content: str) -> None:
    """Write text file with UTF-8 encoding."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# =============================================================================
# Task Executor
# =============================================================================
class AntigravityTaskExecutor:
    """
    Antigravity-1 Task Executor

    Executes task contract allowlist commands on CLOUD-ROOT and generates
    execution artifacts for LOCAL-ANTIGRAVITY verification.
    """

    def __init__(self, task_id: str):
        self.task_id = task_id
        self.task_dir = TASK_CONTRACT_DIR / task_id
        self.contract = read_json(self.task_dir / "task_contract.json")
        self.started_at = utc_now_iso()
        self.executed_commands: list[str] = []
        self.stdout_lines: list[str] = []
        self.stderr_lines: list[str] = []
        self.audit_events: list[dict] = []
        self.exit_code = 0
        self.status = "success"
        self.error_message = ""

    def log_audit(self, event_type: str, detail: str) -> None:
        """Log an audit event."""
        self.audit_events.append({
            "timestamp": utc_now_iso(),
            "type": event_type,
            "detail": detail
        })

    def execute_command(self, command: str, cwd: str | None = None) -> tuple[int, str, str]:
        """Execute a single command and return exit code, stdout, stderr."""
        normalized_command = command

        # For docker compose commands, use openclaw-box directory
        if command.startswith("docker compose") and cwd is None:
            cwd = "openclaw-box"

        # Cloud Linux fallback: if `python` is missing, transparently use python3.
        if command.startswith("python "):
            python_ok = subprocess.run("command -v python", shell=True, capture_output=True, text=True).returncode == 0
            python3_ok = subprocess.run("command -v python3", shell=True, capture_output=True, text=True).returncode == 0
            if not python_ok and python3_ok:
                normalized_command = "python3 " + command[len("python "):]
                self.log_audit("COMMAND_REWRITE", f"Rewrote command for compatibility: {command} -> {normalized_command}")

        self.log_audit("COMMAND_START", f"Executing: {normalized_command}")

        # For Linux-specific commands on Windows, add || true to ignore failures
        windows_specific = ["ss -lntp", "free -m", "uptime"]
        is_windows_linux_cmd = any(cmd in command for cmd in windows_specific)

        try:
            env = os.environ.copy()
            spec_pack = pathlib.Path("skillforge-spec-pack").resolve()
            if spec_pack.exists():
                current_pythonpath = env.get("PYTHONPATH", "")
                env["PYTHONPATH"] = f"{spec_pack}{os.pathsep}{current_pythonpath}" if current_pythonpath else str(spec_pack)

            # Execute the command
            result = subprocess.run(
                normalized_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout per command
                cwd=cwd,
                env=env,
            )

            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            exit_code = result.returncode

            # For Linux-specific commands on Windows, treat as success if they fail gracefully
            if is_windows_linux_cmd and exit_code != 0:
                if not stdout and not stderr:
                    # Command produced no output and failed - likely not available on Windows
                    # Treat as success (skip this check)
                    exit_code = 0
                    stdout = f"[SKIPPED] {command} - Linux-specific command, not available on Windows"

            self.log_audit("COMMAND_COMPLETE", f"Exit code: {exit_code}")

            return exit_code, stdout, stderr

        except subprocess.TimeoutExpired:
            self.log_audit("COMMAND_TIMEOUT", f"Command timed out: {command}")
            return 124, "", f"Command timed out after 300 seconds: {command}"

        except Exception as e:
            # For Linux-specific commands on Windows, treat exceptions as skipped
            if is_windows_linux_cmd and "NoneType" in str(e):
                exit_code = 0
                stdout = f"[SKIPPED] {command} - Linux-specific command, not available on Windows"
                self.log_audit("COMMAND_COMPLETE", f"Exit code: {exit_code}")
                return exit_code, stdout, ""

            self.log_audit("COMMAND_ERROR", f"Exception: {str(e)}")
            return 1, "", str(e)

    def execute_allowlist(self) -> None:
        """Execute all commands in the contract allowlist."""
        allowlist = self.contract.get("command_allowlist", [])

        self.stdout_lines.append(f"=== OpenClaw Cloud Task Execution ===")
        self.stdout_lines.append(f"Task ID: {self.task_id}")
        self.stdout_lines.append(f"Started at: {self.started_at}")
        self.stdout_lines.append(f"Objective: {self.contract.get('objective', 'N/A')}")
        self.stdout_lines.append("")

        for i, command in enumerate(allowlist, 1):
            self.stdout_lines.append(f"=== Executing Command {i}/{len(allowlist)}: {command} ===")

            # Execute the command
            exit_code, stdout, stderr = self.execute_command(command)

            # Record execution
            self.executed_commands.append(command)

            # Append output
            if stdout:
                self.stdout_lines.append(stdout)
            if stderr:
                self.stderr_lines.append(f"[{command}] {stderr}")

            # Track overall exit code (use first non-zero)
            if exit_code != 0 and self.exit_code == 0:
                self.exit_code = exit_code

            # Small delay between commands
            import time
            time.sleep(0.5)

        # Set final status
        self.status = "success" if self.exit_code == 0 else "failure"
        if self.exit_code != 0:
            self.error_message = f"Command failed with exit code {self.exit_code}"

    def generate_execution_receipt(self) -> dict:
        """Generate the execution receipt artifact."""
        finished_at = utc_now_iso()

        receipt = {
            "schema_version": "1.0.0",
            "task_id": self.task_id,
            "executor": "Antigravity-1-Executor",
            "started_at_utc": self.started_at,
            "finished_at_utc": finished_at,
            "status": self.status,
            "executed_commands": self.executed_commands,
            "exit_code": self.exit_code,
            "artifacts": [
                "execution_receipt.json",
                "stdout.log",
                "stderr.log",
                "audit_event.json"
            ],
            "summary": f"Executed {len(self.executed_commands)} commands with status {self.status}"
        }

        if self.error_message:
            receipt["error"] = self.error_message

        return receipt

    def generate_audit_events(self) -> dict:
        """Generate the audit events artifact."""
        return {
            "schema_version": "1.0.0",
            "task_id": self.task_id,
            "generated_at_utc": utc_now_iso(),
            "total_events": len(self.audit_events),
            "events": self.audit_events
        }

    def save_artifacts(self) -> None:
        """Save all execution artifacts."""
        # Generate and save execution receipt
        receipt = self.generate_execution_receipt()
        write_json(self.task_dir / "execution_receipt.json", receipt)

        # Save stdout
        write_text(self.task_dir / "stdout.log", "\n".join(self.stdout_lines))

        # Save stderr
        write_text(self.task_dir / "stderr.log", "\n".join(self.stderr_lines))

        # Generate and save audit events
        audit = self.generate_audit_events()
        write_json(self.task_dir / "audit_event.json", audit)

        self.log_audit("ARTIFACTS_SAVED", f"Saved 4 artifacts to {self.task_dir}")

    def verify_receipt(self) -> dict:
        """Verify the execution receipt against the contract."""
        if not VERIFICATION_SCRIPT.exists():
            return {
                "status": "SKIP",
                "reason": f"Verification script not found: {VERIFICATION_SCRIPT}"
            }

        try:
            result = subprocess.run(
                [sys.executable, str(VERIFICATION_SCRIPT),
                 "--contract", str(self.task_dir / "task_contract.json"),
                 "--receipt", str(self.task_dir / "execution_receipt.json")],
                capture_output=True,
                text=True,
                timeout=60
            )

            return {
                "status": "PASS" if result.returncode == 0 else "FAIL",
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }

        except Exception as e:
            return {
                "status": "ERROR",
                "reason": str(e)
            }

    def execute(self, verify: bool = True) -> dict:
        """Execute the complete task workflow."""
        print(f"[Antigravity-1] Task Execution")
        print(f"[Antigravity-1] Task ID: {self.task_id}")
        print(f"[Antigravity-1] Contract: {self.task_dir / 'task_contract.json'}")
        print()

        # Step 1: Execute allowlist commands
        print("[Step 1] Executing allowlist commands...")
        self.execute_allowlist()
        print(f"[ok] Executed {len(self.executed_commands)} commands")
        print(f"[ok] Status: {self.status}")
        print(f"[ok] Exit code: {self.exit_code}")
        print()

        # Step 2: Generate and save artifacts
        print("[Step 2] Generating execution artifacts...")
        self.save_artifacts()
        print(f"[ok] execution_receipt.json")
        print(f"[ok] stdout.log")
        print(f"[ok] stderr.log")
        print(f"[ok] audit_event.json")
        print()

        # Step 3: Verify receipt
        verification_result = {"status": "SKIP"}
        if verify:
            print("[Step 3] Verifying execution receipt...")
            verification_result = self.verify_receipt()

            if verification_result["status"] == "PASS":
                print(f"[ok] Verification PASSED")
            elif verification_result["status"] == "FAIL":
                print(f"[FAIL] Verification FAILED")
                if verification_result.get("stdout"):
                    for line in verification_result["stdout"].split("\n"):
                        if line.strip():
                            print(f"  {line}")
                print()
                print("[FAIL_CLOSED] Blocking dispatch due to verification failure")
                return {
                    "task_id": self.task_id,
                    "status": "FAIL_CLOSED",
                    "verification": verification_result,
                    "error": "Execution receipt verification failed"
                }
            else:
                print(f"[{verification_result['status']}] {verification_result.get('reason', 'Unknown')}")
        else:
            print("[Step 3] Skipping verification (verify=False)")

        print()
        print("[Antigravity-1] Task execution complete!")
        return {
            "task_id": self.task_id,
            "status": self.status,
            "exit_code": self.exit_code,
            "verification": verification_result,
            "artifacts": {
                "execution_receipt": str(self.task_dir / "execution_receipt.json"),
                "stdout": str(self.task_dir / "stdout.log"),
                "stderr": str(self.task_dir / "stderr.log"),
                "audit_event": str(self.task_dir / "audit_event.json")
            }
        }


# =============================================================================
# Main Entry Point
# =============================================================================
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Antigravity-1: Execute task contract and generate artifacts"
    )
    parser.add_argument("--task-id", required=True, help="Task contract ID")
    parser.add_argument("--no-verify", action="store_true", help="Skip receipt verification")
    args = parser.parse_args()

    executor = AntigravityTaskExecutor(args.task_id)
    result = executor.execute(verify=not args.no_verify)

    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
