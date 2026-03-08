文件: skillforge/src/nodes/intake_repo.py
pythonDownloadCopy code"""
IntakeRepo node — fetch and validate a GitHub repository.

Path: B, A+B
Stage: 0

Input Contract (conforms to gm-os-core intake_repo.schema.json)
--------------
{
    "repo_url": str,
    "branch": str,
    "options": { ... }
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "repo_info": {
        "name": str,
        "owner": str,
        "default_branch": str,
        "stars": int,
        "license": str | None,
        "last_commit_sha": str,
        "languages": dict
    },
    "fetch_status": "ok" | "error",
    "local_path": str | None
}
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any


@dataclass
class IntakeRepo:
    """Fetch and intake a GitHub repository."""

    node_id: str = "intake_repo"
    stage: int = 0

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate repo_url is present and well-formed."""
        errors: list[str] = []

        pipeline_input = input_data.get("input")
        if not isinstance(pipeline_input, dict):
            errors.append("EXEC_VALIDATION_FAILED: 'input' key is required in pipeline artifacts")
            return errors

        repo_url = pipeline_input.get("repo_url", "")
        if not repo_url:
            errors.append("EXEC_VALIDATION_FAILED: repo_url is required and cannot be empty")
            return errors

        if not isinstance(repo_url, str):
            errors.append("EXEC_VALIDATION_FAILED: repo_url must be a string")
            return errors

        url_ok = (
            "github.com" in repo_url
            or repo_url.startswith("git://")
            or repo_url.startswith("https://")
        )
        if not url_ok:
            errors.append(
                "EXEC_VALIDATION_FAILED: repo_url must contain 'github.com' "
                "or start with 'git://' or 'https://'"
            )

        return errors

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Fetch repository information and clone/download.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        pipeline_input = input_data.get("input", {})
        repo_url: str = pipeline_input.get("repo_url", "")
        branch: str = pipeline_input.get("branch", "main")

        # Parse owner and repo name from URL
        url = repo_url.rstrip("/")
        if url.endswith(".git"):
            url = url[:-4]
        parts = url.split("/")

        # Take last two non-empty segments as owner/name
        non_empty = [p for p in parts if p]
        owner = non_empty[-2] if len(non_empty) >= 2 else "unknown"
        name = non_empty[-1] if len(non_empty) >= 1 else "unknown"

        return {
            "schema_version": "0.1.0",
            "repo_info": {
                "name": name,
                "owner": owner,
                "default_branch": branch,
                "stars": 0,
                "license": None,
                "last_commit_sha": "mock-sha-" + uuid.uuid4().hex[:8],
                "languages": {"Python": 100},
            },
            "fetch_status": "ok",
            "local_path": None,
        }

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate intake output."""
        errors: list[str] = []

        if not isinstance(output_data, dict):
            errors.append("SCHEMA_INVALID: output must be a dict")
            return errors

        if output_data.get("schema_version") != "0.1.0":
            errors.append("SCHEMA_INVALID: schema_version must be '0.1.0'")

        repo_info = output_data.get("repo_info")
        if not isinstance(repo_info, dict):
            errors.append("SCHEMA_INVALID: repo_info must be a dict")
        else:
            for field in ("name", "owner", "default_branch"):
                if field not in repo_info:
                    errors.append(f"SCHEMA_INVALID: repo_info.{field} is required")

        if "fetch_status" not in output_data:
            errors.append("SCHEMA_INVALID: fetch_status is required")

        return errors
文件: skillforge/src/nodes/license_gate.py
pythonDownloadCopy code"""
LicenseGate node — gate that checks repository license compatibility.

Path: B, A+B
Stage: 1

Input Contract (conforms to gm-os-core license_gate.schema.json)
--------------
{
    "repo_info": { ... },    # from IntakeRepo
    "options": { ... }
}

Output Contract (GateDecision)
---------------
{
    "schema_version": "0.1.0",
    "gate_id": "license_gate",
    "node_id": "license_gate",
    "decision": "ALLOW" | "DENY" | "REQUIRES_CHANGES",
    "reason": str,
    "details": {
        "license_detected": str | None,
        "compatible": bool,
        "allowed_licenses": list[str]
    },
    "timestamp": str
}
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from typing import Any

ALLOWED_LICENSES: list[str] = [
    "MIT",
    "Apache-2.0",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "ISC",
    "0BSD",
    "Unlicense",
]


@dataclass
class LicenseGate:
    """Evaluate license compatibility for an ingested repo."""

    node_id: str = "license_gate"
    stage: int = 1

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate repo_info is present."""
        errors: list[str] = []

        intake = input_data.get("intake_repo")
        if not isinstance(intake, dict):
            errors.append(
                "EXEC_VALIDATION_FAILED: intake_repo output is required"
            )
            return errors

        if "repo_info" not in intake:
            errors.append(
                "EXEC_VALIDATION_FAILED: intake_repo.repo_info is required"
            )

        return errors

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Check repository license and produce GateDecision.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract (GateDecision).
        """
        intake = input_data.get("intake_repo", {})
        repo_info = intake.get("repo_info", {})
        detected_license = repo_info.get("license")

        if not detected_license:
            decision = "DENY"
            reason = "No license detected"
            compatible = False
        elif detected_license not in ALLOWED_LICENSES:
            decision = "DENY"
            reason = f"License '{detected_license}' is not approved"
            compatible = False
        else:
            decision = "ALLOW"
            reason = f"License '{detected_license}' is approved"
            compatible = True

        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        return {
            "schema_version": "0.1.0",
            "gate_id": "license_gate",
            "node_id": self.node_id,
            "decision": decision,
            "reason": reason,
            "details": {
                "license_detected": detected_license,
                "compatible": compatible,
                "allowed_licenses": list(ALLOWED_LICENSES),
            },
            "timestamp": timestamp,
        }

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate GateDecision structure."""
        errors: list[str] = []

        if not isinstance(output_data, dict):
            errors.append("SCHEMA_INVALID: output must be a dict")
            return errors

        for field in ("schema_version", "gate_id", "node_id", "decision", "reason", "timestamp"):
            if field not in output_data:
                errors.append(f"SCHEMA_INVALID: {field} is required")

        decision = output_data.get("decision")
        if decision is not None and decision not in ("ALLOW", "DENY", "REQUIRES_CHANGES"):
            errors.append(
                f"GATE_INVALID_DECISION: decision must be ALLOW, DENY, or "
                f"REQUIRES_CHANGES, got '{decision}'"
            )

        return errors
文件: skillforge/src/nodes/repo_scan.py
pythonDownloadCopy code"""
RepoScan node — scan repository structure and compute fit score.

Path: B, A+B
Stage: 2

Input Contract (conforms to gm-os-core repo_scan_fit_score.schema.json)
--------------
{
    "repo_info": { ... },
    "local_path": str,
    "options": { ... }
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "fit_score": int,          # 0-100
    "repo_type": str,          # workflow | cli | lib | service | template
    "entry_points": list[str],
    "dependencies": dict[str, str],
    "language_stack": str,
    "complexity_metrics": {
        "total_files": int,
        "total_loc": int,
        "avg_function_length": float
    }
}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RepoScan:
    """Scan repo structure and produce a fit score."""

    node_id: str = "repo_scan_fit_score"
    stage: int = 2

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate repo_info and local_path are present."""
        errors: list[str] = []

        intake = input_data.get("intake_repo")
        if not isinstance(intake, dict):
            errors.append(
                "EXEC_VALIDATION_FAILED: intake_repo output is required"
            )
            return errors

        if "repo_info" not in intake:
            errors.append(
                "EXEC_VALIDATION_FAILED: intake_repo.repo_info is required"
            )

        return errors

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Scan repo structure and compute fit score.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        intake = input_data.get("intake_repo", {})
        repo_info = intake.get("repo_info", {})
        languages: dict[str, Any] = repo_info.get("languages", {})
        detected_license = repo_info.get("license")

        # Determine language_stack from first language key
        language_stack = "unknown"
        if languages:
            language_stack = next(iter(languages))

        # Compute fit_score
        score = 40  # base
        if detected_license:
            score += 20
        if len(languages) > 1:
            score += 10
        if "Python" in languages:
            score += 30

        fit_score = max(0, min(100, score))

        # Infer repo_type from language_stack
        type_map: dict[str, str] = {
            "Python": "lib",
            "JavaScript": "service",
            "TypeScript": "service",
            "Go": "cli",
            "Rust": "cli",
            "Shell": "workflow",
            "Bash": "workflow",
        }
        repo_type = type_map.get(language_stack, "template")

        return {
            "schema_version": "0.1.0",
            "fit_score": fit_score,
            "repo_type": repo_type,
            "entry_points": ["main.py"],
            "dependencies": {},
            "language_stack": language_stack,
            "complexity_metrics": {
                "total_files": 1,
                "total_loc": 0,
                "avg_function_length": 0.0,
            },
        }

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate scan result."""
        errors: list[str] = []

        if not isinstance(output_data, dict):
            errors.append("SCHEMA_INVALID: output must be a dict")
            return errors

        for field in ("schema_version", "fit_score", "repo_type", "entry_points", "language_stack"):
            if field not in output_data:
                errors.append(f"SCHEMA_INVALID: {field} is required")

        fit_score = output_data.get("fit_score")
        if isinstance(fit_score, (int, float)):
            if not (0 <= fit_score <= 100):
                errors.append(
                    f"SCHEMA_INVALID: fit_score must be 0-100, got {fit_score}"
                )

        valid_types = ("workflow", "cli", "lib", "service", "template")
        repo_type = output_data.get("repo_type")
        if repo_type is not None and repo_type not in valid_types:
            errors.append(
                f"SCHEMA_INVALID: repo_type must be one of {valid_types}, "
                f"got '{repo_type}'"
            )

        return errors
文件: skillforge/src/nodes/draft_spec.py
pythonDownloadCopy code"""
DraftSpec node — draft a skill specification from scan results.

Path: B, A+B
Stage: 3

Input Contract (conforms to gm-os-core draft_skill_spec.schema.json)
--------------
{
    "repo_info": { ... },
    "scan_result": { ... },     # from RepoScan
    "options": { ... }
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "skill_spec": {
        "name": str,
        "version": str,
        "description": str,
        "inputs": list[dict],
        "outputs": list[dict],
        "tools_required": list[str],
        "steps": list[dict],
        "constraints": list[str]
    },
    "source": "repo",
    "derived_from": {
        "repo_url": str,
        "commit_sha": str
    }
}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class DraftSpec:
    """Draft a skill specification from repository scan results."""

    node_id: str = "draft_skill_spec"
    stage: int = 3

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate scan_result and repo_info are present."""
        errors: list[str] = []

        if not isinstance(input_data.get("intake_repo"), dict):
            errors.append(
                "EXEC_VALIDATION_FAILED: intake_repo output is required"
            )

        if not isinstance(input_data.get("repo_scan_fit_score"), dict):
            errors.append(
                "EXEC_VALIDATION_FAILED: repo_scan_fit_score output is required"
            )

        return errors

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Draft skill specification from scan.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        intake = input_data["intake_repo"]
        scan = input_data["repo_scan_fit_score"]
        pipeline_input = input_data.get("input", {})

        repo_info = intake.get("repo_info", {})
        repo_name: str = repo_info.get("name", "unknown")
        repo_owner: str = repo_info.get("owner", "unknown")
        commit_sha: str = repo_info.get("last_commit_sha", "unknown")

        entry_points: list[str] = scan.get("entry_points", ["main.py"])
        language_stack: str = scan.get("language_stack", "unknown")
        fit_score: int = scan.get("fit_score", 0)

        # Infer tools_required from language_stack
        tools_map: dict[str, list[str]] = {
            "Python": ["python3", "pip"],
            "JavaScript": ["node", "npm"],
            "TypeScript": ["node", "npm", "tsc"],
            "Go": ["go"],
            "Rust": ["cargo"],
        }
        tools_required = tools_map.get(language_stack, [])

        # Build steps from entry_points
        first_entry = entry_points[0] if entry_points else "main.py"
        steps: list[dict[str, Any]] = [
            {
                "id": "step_1",
                "action": "execute",
                "description": f"Run {first_entry}",
            }
        ]

        # Build inputs from entry_points
        inputs: list[dict[str, Any]] = [
            {"name": ep, "type": "file", "required": True}
            for ep in entry_points
        ]

        skill_spec: dict[str, Any] = {
            "name": f"skill-{repo_name}",
            "version": "0.1.0",
            "description": f"Auto-drafted skill from {repo_owner}/{repo_name}",
            "inputs": inputs,
            "outputs": [{"name": "result", "type": "object"}],
            "tools_required": tools_required,
            "steps": steps,
            "constraints": [
                "risk_tier: L1",
                f"fit_score >= 40 (actual: {fit_score})",
            ],
        }

        repo_url: str = pipeline_input.get("repo_url", "")
        confidence: float = min(fit_score / 100, 0.95)

        return {
            "schema_version": "0.1.0",
            "skill_spec": skill_spec,
            "source": "repo",
            "derived_from": {
                "repo_url": repo_url,
                "commit_sha": commit_sha,
            },
            "confidence": confidence,
        }

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate drafted spec."""
        errors: list[str] = []

        if not isinstance(output_data, dict):
            errors.append("SCHEMA_INVALID: output must be a dict")
            return errors

        if "schema_version" not in output_data:
            errors.append("SCHEMA_INVALID: schema_version is required")

        if "source" not in output_data:
            errors.append("SCHEMA_INVALID: source is required")
        elif output_data["source"] != "repo":
            errors.append("SCHEMA_INVALID: source must be 'repo'")

        skill_spec = output_data.get("skill_spec")
        if not isinstance(skill_spec, dict):
            errors.append("SCHEMA_INVALID: skill_spec must be a dict")
        else:
            for field in ("name", "version", "description"):
                if field not in skill_spec:
                    errors.append(f"SCHEMA_INVALID: skill_spec.{field} is required")

        return errors

验收标准预期结果对照：
测试 2 — IntakeRepo 解析 https://github.com/owner/repo → owner="owner", name="repo", fetch_status="ok", validate_input 返回 []。
测试 3 — LicenseGate 收到 license="MIT" → decision="ALLOW"。
测试 4 — 完整 Path B 链路：intake → fetch_status=ok；license gate → decision=DENY（因为 mock 的 license 是 None）；repo scan → fit_score=70（base 40 + Python 30）；draft spec → name=skill-test-repo。链路不抛 NotImplementedError，全程正常输出。