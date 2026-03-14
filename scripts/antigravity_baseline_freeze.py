#!/usr/bin/env python3
"""
Antigravity-1 Baseline Freeze Activation Script

This script creates and activates a new baseline freeze for the Antigravity-1 execution pattern.
It generates a task contract for cloud dispatch and prepares the necessary artifacts.

Usage:
    python scripts/antigravity_baseline_freeze.py --objective "Cloud health check"
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import uuid
from datetime import datetime, timezone

# =============================================================================
# Configuration
# =============================================================================
ANTIGRAVITY_VERSION = "1.0.0"
ANTIGRAVITY_CHANNEL = "BlueLobster-Cloud"
ANTIGRAVITY_AGENT = "Antigravity-Gemini"
DEFAULT_PROJECT_DIR = "/root/openclaw-box"
BASELINE_FREEZE_DIR = pathlib.Path(".tmp/antigravity-baseline")
TASK_CONTRACT_DIR = pathlib.Path(".tmp/openclaw-dispatch")
AUDIT_EVIDENCE_DIR = pathlib.Path("AuditPack/evidence")

# =============================================================================
# Utility Functions
# =============================================================================
def utc_now_iso() -> str:
    """Get current UTC time in ISO format with Z suffix."""
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def make_baseline_id() -> str:
    """Generate a unique baseline freeze identifier."""
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S")
    suffix = uuid.uuid4().hex[:8]
    return f"AG1-{stamp}-{suffix}"


def make_task_id() -> str:
    """Generate a unique task ID."""
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S")
    suffix = uuid.uuid4().hex[:8]
    return f"ocb-{stamp}-{suffix}"


def canonical_json(obj: dict) -> str:
    """Create canonical JSON representation for hashing."""
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def write_json(path: pathlib.Path, obj: dict) -> None:
    """Write JSON file with UTF-8 encoding."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: pathlib.Path) -> str:
    """Calculate SHA256 hash of a file."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# =============================================================================
# Baseline Freeze Management
# =============================================================================
class BaselineFreeze:
    """Manages baseline freeze artifacts for Antigravity-1."""

    def __init__(self, baseline_id: str, freeze_dir: pathlib.Path):
        self.baseline_id = baseline_id
        self.freeze_dir = freeze_dir / baseline_id
        self.freeze_dir.mkdir(parents=True, exist_ok=True)
        self.created_at = utc_now_iso()
        self.manifest = {}

    def create_snapshot(self, source_files: list[pathlib.Path]) -> dict:
        """Create a snapshot of source files with SHA256 hashes."""
        snapshot = {
            "baseline_id": self.baseline_id,
            "created_at_utc": self.created_at,
            "frozen_at_utc": utc_now_iso(),
            "version": ANTIGRAVITY_VERSION,
            "files": []
        }

        for src in source_files:
            if not src.exists():
                continue

            dest = self.freeze_dir / src.name
            shutil.copy2(src, dest)

            stat = dest.stat()
            file_info = {
                "name": src.name,
                "source_path": str(src),
                "snapshot_path": str(dest),
                "sha256": sha256_file(dest),
                "size_bytes": stat.st_size,
                "last_write_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            }
            snapshot["files"].append(file_info)

        # Calculate baseline hash
        snapshot_json = canonical_json(snapshot)
        snapshot["baseline_sha256"] = hashlib.sha256(snapshot_json.encode("utf-8")).hexdigest()

        self.manifest = snapshot
        write_json(self.freeze_dir / "BASELINE_MANIFEST.json", snapshot)
        return snapshot

    def activate(self) -> dict:
        """Activate the baseline freeze."""
        activation = {
            "baseline_id": self.baseline_id,
            "activated_at_utc": utc_now_iso(),
            "status": "ACTIVE",
            "manifest_path": str(self.freeze_dir / "BASELINE_MANIFEST.json"),
            "freeze_dir": str(self.freeze_dir)
        }
        write_json(self.freeze_dir / "ACTIVATION.json", activation)

        # Copy to audit evidence
        AUDIT_EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
        audit_path = AUDIT_EVIDENCE_DIR / f"antigravity_baseline_activation_{self.baseline_id}.json"
        shutil.copy2(self.freeze_dir / "BASELINE_MANIFEST.json", audit_path)

        return activation


# =============================================================================
# Task Contract Generation
# =============================================================================
class TaskContractGenerator:
    """Generates OpenClaw cloud task contracts."""

    def __init__(self, objective: str, project_dir: str = DEFAULT_PROJECT_DIR):
        self.objective = objective
        self.project_dir = project_dir
        self.task_id = make_task_id()
        self.created_at = utc_now_iso()
        self.contract = {}

    def generate(
        self,
        allowed_commands: list[str],
        acceptance_criteria: list[str],
        max_duration_sec: int = 900,
        max_commands: int = 10
    ) -> dict:
        """Generate the task contract."""
        contract = {
            "schema_version": "1.0.0",
            "task_id": self.task_id,
            "created_at_utc": self.created_at,
            "objective": self.objective,
            "relay": {
                "agent": ANTIGRAVITY_AGENT,
                "channel": ANTIGRAVITY_CHANNEL
            },
            "target": {
                "project_dir": self.project_dir
            },
            "policy": {
                "fail_closed": True,
                "max_duration_sec": max_duration_sec,
                "max_commands": max_commands
            },
            "command_allowlist": allowed_commands,
            "acceptance": acceptance_criteria,
            "required_artifacts": [
                "execution_receipt.json",
                "stdout.log",
                "stderr.log",
                "audit_event.json"
            ]
        }

        # Calculate contract hash
        contract_json = canonical_json(contract)
        contract["contract_sha256"] = hashlib.sha256(contract_json.encode("utf-8")).hexdigest()

        self.contract = contract
        return contract

    def save(self, output_dir: pathlib.Path) -> pathlib.Path:
        """Save the task contract to disk."""
        base = output_dir / self.task_id
        base.mkdir(parents=True, exist_ok=True)

        contract_path = base / "task_contract.json"
        write_json(contract_path, self.contract)

        # Also save handoff note
        self._save_handoff_note(base)

        return contract_path

    def _save_handoff_note(self, base_dir: pathlib.Path) -> None:
        """Generate the handoff note for Gemini relay."""
        lines = [
            "# OpenClaw Cloud Task Handoff - Antigravity-1",
            "",
            f"- task_id: `{self.contract['task_id']}`",
            f"- relay_agent: `{self.contract['relay']['agent']}`",
            f"- channel: `{self.contract['relay']['channel']}`",
            f"- objective: {self.contract['objective']}",
            f"- project_dir: `{self.contract['target']['project_dir']}`",
            f"- created_at: `{self.contract['created_at_utc']}`",
            "",
            "## Hard Constraints",
            "",
            "- fail_closed=true",
            "- Only execute commands in command_allowlist",
            "- Return required artifacts",
            f"- max_duration_sec={self.contract['policy']['max_duration_sec']}",
            f"- max_commands={self.contract['policy']['max_commands']}",
            "",
            "## command_allowlist",
            ""
        ]
        for cmd in self.contract["command_allowlist"]:
            lines.append(f"- `{cmd}`")

        lines.extend([
            "",
            "## required_artifacts",
            ""
        ])
        for item in self.contract["required_artifacts"]:
            lines.append(f"- `{item}`")

        lines.extend([
            "",
            "## acceptance_criteria",
            ""
        ])
        for item in self.contract["acceptance"]:
            lines.append(f"- `{item}`")

        handoff_path = base_dir / "handoff_note.md"
        handoff_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# =============================================================================
# Main Execution
# =============================================================================
def run_baseline_smoketest(input_path: pathlib.Path, output_path: pathlib.Path) -> dict:
    """Run the baseline E2E smoketest."""
    smoketest_script = pathlib.Path("skills/gm-baseline-e2e-smoketest-skill/scripts/run_smoketest.py")
    if not smoketest_script.exists():
        raise FileNotFoundError(f"Smoketest script not found: {smoketest_script}")

    result = subprocess.run(
        [sys.executable, str(smoketest_script), "--input", str(input_path), "--output", str(output_path)],
        capture_output=True,
        text=True
    )

    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Antigravity-1: Create baseline freeze and generate task contract for cloud dispatch"
    )
    parser.add_argument("--objective", required=True, help="Task objective summary")
    parser.add_argument("--project-dir", default=DEFAULT_PROJECT_DIR, help="Remote project directory")
    parser.add_argument("--max-duration-sec", type=int, default=900, help="Maximum execution duration")
    parser.add_argument("--max-commands", type=int, default=10, help="Maximum commands to execute")
    parser.add_argument("--baseline-id", default="", help="Specific baseline ID (auto-generated if empty)")
    parser.add_argument("--task-id", default="", help="Specific task ID (auto-generated if empty)")
    parser.add_argument("--run-smoketest", action="store_true", help="Run baseline E2E smoketest")
    parser.add_argument("--smoketest-input", default="skills/gm-baseline-e2e-smoketest-skill/references/sample_input.json",
                        help="Path to smoketest input")
    args = parser.parse_args()

    print(f"[Antigravity-1] Baseline Freeze Activation")
    print(f"[Antigravity-1] Version: {ANTIGRAVITY_VERSION}")
    print(f"[Antigravity-1] Channel: {ANTIGRAVITY_CHANNEL}")
    print(f"[Antigravity-1] Agent: {ANTIGRAVITY_AGENT}")
    print()

    # Step 1: Run baseline smoketest if requested
    if args.run_smoketest:
        print("[Step 1] Running baseline E2E smoketest...")
        smoketest_input = pathlib.Path(args.smoketest_input)
        smoketest_output = BASELINE_FREEZE_DIR / "smoketest_output.json"

        if not smoketest_input.exists():
            print(f"[FAIL] Smoketest input not found: {smoketest_input}")
            return 1

        try:
            result = run_baseline_smoketest(smoketest_input, smoketest_output)
            print(f"[ok] Smoketest completed with return code: {result['returncode']}")
            if result["stdout"]:
                print(f"[ok] {result['stdout']}")
        except Exception as e:
            print(f"[FAIL] Smoketest failed: {e}")
            return 1

    # Step 2: Create and activate baseline freeze
    print("[Step 2] Creating and activating baseline freeze...")
    baseline_id = args.baseline_id.strip() or make_baseline_id()
    baseline = BaselineFreeze(baseline_id, BASELINE_FREEZE_DIR)

    # Create snapshot of key files
    source_files = [
        pathlib.Path("schemas/openclaw_cloud_task_contract.schema.json"),
        pathlib.Path("schemas/openclaw_execution_receipt.schema.json"),
        pathlib.Path("schemas/gm_baseline_e2e_smoketest_input.schema.json"),
        pathlib.Path("schemas/gm_baseline_e2e_smoketest_output.schema.json"),
    ]

    if args.run_smoketest:
        output_file = BASELINE_FREEZE_DIR / "smoketest_output.json"
        if output_file.exists():
            source_files.append(output_file)

    snapshot = baseline.create_snapshot(source_files)
    activation = baseline.activate()

    print(f"[ok] baseline_id={baseline_id}")
    print(f"[ok] baseline_sha256={snapshot['baseline_sha256']}")
    print(f"[ok] freeze_dir={baseline.freeze_dir}")
    print()

    # Step 3: Generate task contract
    print("[Step 3] Generating task contract...")

    # Define default allowed commands for health check
    default_commands = [
        "docker compose ps",
        "docker compose logs --since 10m openclaw-agent | tail -n 200",
        "ss -lntp | grep 18789 || true",
        "df -h",
        "free -m",
        "uptime"
    ]

    # Define default acceptance criteria
    default_acceptance = [
        "openclaw_core is Up",
        "no EACCES in last 10m logs",
        "no Unknown model in last 10m logs"
    ]

    generator = TaskContractGenerator(args.objective, args.project_dir)

    if args.task_id:
        generator.task_id = args.task_id

    contract = generator.generate(
        allowed_commands=default_commands,
        acceptance_criteria=default_acceptance,
        max_duration_sec=args.max_duration_sec,
        max_commands=args.max_commands
    )

    contract_path = generator.save(TASK_CONTRACT_DIR)

    print(f"[ok] task_id={contract['task_id']}")
    print(f"[ok] contract={contract_path}")
    print(f"[ok] handoff={contract_path.parent / 'handoff_note.md'}")
    print(f"[ok] contract_sha256={contract['contract_sha256']}")
    print()

    # Step 4: Create dispatch summary
    print("[Step 4] Creating dispatch summary...")
    dispatch_summary = {
        "antigravity_version": ANTIGRAVITY_VERSION,
        "baseline_id": baseline_id,
        "task_id": contract["task_id"],
        "created_at_utc": utc_now_iso(),
        "objective": args.objective,
        "baseline_sha256": snapshot["baseline_sha256"],
        "contract_sha256": contract["contract_sha256"],
        "relay": {
            "agent": ANTIGRAVITY_AGENT,
            "channel": ANTIGRAVITY_CHANNEL
        },
        "paths": {
            "baseline_freeze_dir": str(baseline.freeze_dir),
            "baseline_manifest": str(baseline.freeze_dir / "BASELINE_MANIFEST.json"),
            "task_contract": str(contract_path),
            "handoff_note": str(contract_path.parent / "handoff_note.md"),
            "expected_receipt": str(contract_path.parent / "execution_receipt.json")
        },
        "status": "READY_FOR_DISPATCH"
    }

    summary_path = TASK_CONTRACT_DIR / contract["task_id"] / "dispatch_summary.json"
    write_json(summary_path, dispatch_summary)

    print(f"[ok] dispatch_summary={summary_path}")
    print()
    print("[Antigravity-1] Baseline freeze activation complete!")
    print("[Antigravity-1] Task contract generated successfully!")
    print(f"[Antigravity-1] Ready for cloud dispatch via {ANTIGRAVITY_AGENT}")
    print()
    print("Next steps:")
    print("1. Review the task contract and handoff note")
    print("2. Send handoff_note.md to Gemini relay agent")
    print("3. Wait for execution receipt from cloud")
    print("4. Verify receipt using: python skills/openclaw-cloud-bridge-skill/scripts/verify_execution_receipt.py")
    print()
    print(f"Baseline ID: {baseline_id}")
    print(f"Task ID: {contract['task_id']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
