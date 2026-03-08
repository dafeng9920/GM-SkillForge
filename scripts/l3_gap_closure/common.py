from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SPEC_PACK = ROOT / "skillforge-spec-pack"


@dataclass
class CommandResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def run_cli_refine(
    *,
    workspace: Path,
    prompt: str,
    output_path: Path,
    mode: str = "nl",
    timeout_sec: int = 120,
) -> CommandResult:
    output_path = output_path.resolve()
    ensure_parent(output_path)

    cmd = [
        sys.executable,
        "-m",
        "skillforge.src.cli",
        "refine",
        "--mode",
        mode,
        "--output",
        str(output_path),
        prompt,
    ]

    env = os.environ.copy()
    env["PYTHONPATH"] = str(SPEC_PACK)
    proc = subprocess.run(
        cmd,
        cwd=str(workspace),
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout_sec,
    )
    return CommandResult(
        command=cmd,
        returncode=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
    )


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def utc_now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
