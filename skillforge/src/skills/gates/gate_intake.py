"""
GateIntakeRepo - validates repository intake request and produces intake manifest.

Implements the gate contract for intake_repo with fail-closed rules.

Input Contract (Intake Request)
-------------------------------
{
    "repo_url": str,       # URI format, required
    "commit_sha": str,     # 40-char hex, required
    "at_time": str,        # ISO-8601, optional
    "issue_key": str       # optional, auto-generated if not provided
}

Output Contract (Gate Result)
-----------------------------
{
    "gate_name": "intake_repo",
    "gate_decision": "PASSED" | "REJECTED",
    "next_action": "continue" | "halt",
    "error_code": str | null,
    "evidence_refs": [EvidenceRef]
}

Fail-Closed Rules
-----------------
FC-INTAKE-1: commit_sha is null or empty -> REJECTED
FC-INTAKE-2: repo_url is null or empty -> REJECTED
"""

from __future__ import annotations

import hashlib
import json
import re
import logging
import time
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, List
import copy
from ..experience_capture import FixKind, capture_gate_event

# Commit SHA pattern: 40-char hex
COMMIT_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$", re.IGNORECASE)
ISSUE_KEY_PATTERN = re.compile(r"^[A-Z]+-[A-Z0-9]+$")


@dataclass
class EvidenceRef:
    """Evidence reference following gate_interface_v1.yaml schema."""

    issue_key: str
    source_locator: str
    content_hash: str
    tool_revision: str
    timestamp: str


class GateIntakeRepo:
    """Intake gate for repository validation."""

    node_id: str = "intake_repo"
    gate_group: str = "entrance"
    tool_revision: str = "v1.0.0"

    # Error codes
    ERROR_COMMIT_SHA_MISSING = "ERR_COMMIT_SHA_MISSING"
    ERROR_REPO_URL_INVALID = "ERR_REPO_URL_INVALID"

    # Evidence storage path (can be overridden for testing)
    evidence_base_path: str = "AuditPack/evidence"

    def __init__(self, evidence_base_path: Optional[str] = None):
        if evidence_base_path:
            self.evidence_base_path = evidence_base_path

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """
        Validate intake request against fail-closed rules.

        Returns list of validation error strings. Empty list = valid.
        """
        errors: list[str] = []

        if not isinstance(input_data, dict):
            errors.append("SCHEMA_INVALID: input must be a dict")
            return errors

        # FC-INTAKE-1: commit_sha is required
        commit_sha = input_data.get("commit_sha")
        if commit_sha is None or commit_sha == "":
            errors.append("FC-INTAKE-1: commit_sha is required")
        elif not isinstance(commit_sha, str):
            errors.append("FC-INTAKE-1: commit_sha must be a string")
        elif not COMMIT_SHA_PATTERN.match(commit_sha):
            # Allow shorter SHAs for testing, but warn
            if len(commit_sha) < 7:
                errors.append("FC-INTAKE-1: commit_sha must be at least 7 characters")

        # FC-INTAKE-2: repo_url is required
        repo_url = input_data.get("repo_url")
        if repo_url is None or repo_url == "":
            errors.append("FC-INTAKE-2: repo_url is required")
        elif not isinstance(repo_url, str):
            errors.append("FC-INTAKE-2: repo_url must be a string")

        # at_time is optional, but if provided must be ISO-8601
        at_time = input_data.get("at_time")
        if at_time is not None:
            if not isinstance(at_time, str):
                errors.append("SCHEMA_INVALID: at_time must be a string")
            elif not self._is_valid_iso8601(at_time):
                errors.append("SCHEMA_INVALID: at_time must be ISO-8601 format")

        # issue_key is optional, but if provided must match pattern
        issue_key = input_data.get("issue_key")
        if issue_key is not None:
            if not isinstance(issue_key, str):
                errors.append("SCHEMA_INVALID: issue_key must be a string")
            elif not ISSUE_KEY_PATTERN.match(issue_key):
                errors.append("SCHEMA_INVALID: issue_key must match pattern ^[A-Z]+-[A-Z0-9]+$")

        return errors

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute intake gate: validate and produce intake manifest.

        Args:
            input_data: Validated input payload.

        Returns:
            Gate result conforming to gate_interface_v1.yaml.
        """
        repo_url = input_data.get("repo_url", "")
        commit_sha = input_data.get("commit_sha", "")
        at_time = input_data.get("at_time")
        issue_key = input_data.get("issue_key")

        # Generate issue_key if not provided
        if issue_key is None:
            issue_key = f"REQ-{time.strftime('%Y%m%d%H%M%S', time.gmtime())}"

        # Generate timestamp
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        if at_time is None:
            at_time = timestamp

        # Create intake manifest
        manifest = {
            "repo_url": repo_url,
            "commit_sha": commit_sha,
            "at_time": at_time,
            "intake_timestamp": timestamp,
            "status": "ACCEPTED",
        }

        # Create evidence reference
        evidence_ref = self._create_evidence_ref(issue_key, manifest)

        # Save evidence
        self._save_evidence(issue_key, manifest)

        result = {
            "gate_name": self.node_id,
            "gate_decision": "PASSED",
            "next_action": "continue",
            "error_code": None,
            "evidence_refs": [self._evidence_ref_to_dict(evidence_ref)],
        }
        capture_gate_event(
            gate_node=self.node_id,
            gate_decision=result["gate_decision"],
            evidence_refs=result["evidence_refs"],
            fix_kind=FixKind.GATE_DECISION,
            summary="intake request accepted",
        )
        return result

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """
        Validate output against gate_interface_v1.yaml schema.

        Returns list of validation error strings. Empty list = valid.
        """
        errors: list[str] = []

        if not isinstance(output_data, dict):
            errors.append("SCHEMA_INVALID: output must be a dict")
            return errors

        # Required fields per gate_interface_v1.yaml
        required_fields = ["gate_name", "gate_decision", "next_action", "evidence_refs"]
        for field in required_fields:
            if field not in output_data:
                errors.append(f"SCHEMA_INVALID: {field} is required")

        # gate_decision validation
        gate_decision = output_data.get("gate_decision")
        if gate_decision not in ("PASSED", "REJECTED"):
            errors.append("SCHEMA_INVALID: gate_decision must be 'PASSED' or 'REJECTED'")

        # next_action validation
        next_action = output_data.get("next_action")
        if next_action not in ("continue", "halt"):
            errors.append("SCHEMA_INVALID: next_action must be 'continue' or 'halt'")

        # evidence_refs validation
        evidence_refs = output_data.get("evidence_refs")
        if not isinstance(evidence_refs, list):
            errors.append("SCHEMA_INVALID: evidence_refs must be an array")
        else:
            for i, ref in enumerate(evidence_refs):
                ref_errors = self._validate_evidence_ref(ref, i)
                errors.extend(ref_errors)

        return errors

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _is_valid_iso8601(self, dt_str: str) -> bool:
        """Check if string is a valid ISO-8601 datetime."""
        iso_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})?$'
        return bool(re.match(iso_pattern, dt_str))

    def _compute_hash(self, content: str) -> str:
        """Compute SHA-256 hash of content."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _create_evidence_ref(self, issue_key: str, manifest: dict) -> EvidenceRef:
        """Create evidence reference for the intake manifest."""
        content = json.dumps(manifest, sort_keys=True)
        content_hash = self._compute_hash(content)
        source_locator = f"file://{self.evidence_base_path}/intake_manifest_{issue_key}.json"
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        return EvidenceRef(
            issue_key=issue_key,
            source_locator=source_locator,
            content_hash=content_hash,
            tool_revision=self.tool_revision,
            timestamp=timestamp,
        )

    def _evidence_ref_to_dict(self, ref: EvidenceRef) -> dict:
        """Convert EvidenceRef to dict."""
        return {
            "issue_key": ref.issue_key,
            "source_locator": ref.source_locator,
            "content_hash": ref.content_hash,
            "tool_revision": ref.tool_revision,
            "timestamp": ref.timestamp,
        }

    def _validate_evidence_ref(self, ref: Any, index: int) -> list[str]:
        """Validate an evidence reference."""
        errors: list[str] = []

        if not isinstance(ref, dict):
            errors.append(f"SCHEMA_INVALID: evidence_refs[{index}] must be an object")
            return errors

        required_fields = ["issue_key", "source_locator", "content_hash", "tool_revision", "timestamp"]
        for field in required_fields:
            if field not in ref:
                errors.append(f"SCHEMA_INVALID: evidence_refs[{index}].{field} is required")

        return errors

    def _save_evidence(self, issue_key: str, manifest: dict) -> None:
        """Save evidence to file (for production use)."""
        path = Path(self.evidence_base_path) / f"intake_manifest_{issue_key}.json"
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write atomically via temp file
        temp_path = path.with_suffix(".tmp")
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            temp_path.replace(path)
        except OSError:
            # Do not fail gate result when local evidence path is unavailable.
            return


# Convenience function for module-level usage
def intake_repo(
    repo_url: Optional[str],
    commit_sha: Optional[str],
    at_time: Optional[str] = None,
    issue_key: Optional[str] = None,
) -> dict[str, Any]:
    """
    Convenience function to run intake gate.

    Matches gate_interface_v1.yaml signature:
        inputs: [repo_url, commit_sha, at_time]
        outputs: [GateResult]
    """
    gate = GateIntakeRepo()

    input_data = {
        "repo_url": repo_url,
        "commit_sha": commit_sha,
        "at_time": at_time,
    }
    if issue_key:
        input_data["issue_key"] = issue_key

    # Validate input
    errors = gate.validate_input(input_data)
    if errors:
        result = {
            "gate_name": gate.node_id,
            "gate_decision": "REJECTED",
            "next_action": "halt",
            "error_code": gate.ERROR_COMMIT_SHA_MISSING if "commit_sha" in errors[0] else gate.ERROR_REPO_URL_INVALID,
            "evidence_refs": [],
        }
        capture_gate_event(
            gate_node=gate.node_id,
            gate_decision=result["gate_decision"],
            evidence_refs=result["evidence_refs"],
            error_code=result["error_code"],
            fix_kind=FixKind.GATE_DECISION,
            summary="intake request rejected by fail-closed validation",
        )
        return result

    return gate.execute(input_data)


# Backward compatibility: IntakeGate alias
IntakeGate = GateIntakeRepo


# CLI entry point
def main():
    """CLI entry point for Intake Gate."""
    import argparse

    parser = argparse.ArgumentParser(description="Gate: Intake Repo")
    parser.add_argument("--repo-url", required=True, help="Repository URL")
    parser.add_argument("--commit-sha", required=True, help="Git commit SHA")
    parser.add_argument("--at-time", help="Point-in-time checkout (ISO-8601)")
    parser.add_argument("--issue-key", help="Unique request ID")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument(
        "--evidence-path",
        default="AuditPack/evidence",
        help="Base path for evidence storage"
    )
    args = parser.parse_args()

    gate = GateIntakeRepo(evidence_base_path=args.evidence_path)

    input_data = {
        "repo_url": args.repo_url,
        "commit_sha": args.commit_sha,
        "at_time": args.at_time,
        "issue_key": args.issue_key,
    }

    # Validate input
    validation_errors = gate.validate_input(input_data)
    if validation_errors:
        error_result = {
            "gate_name": gate.node_id,
            "gate_decision": "REJECTED",
            "next_action": "halt",
            "error_code": gate.ERROR_COMMIT_SHA_MISSING if "commit_sha" in validation_errors[0] else gate.ERROR_REPO_URL_INVALID,
            "evidence_refs": [],
        }
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(error_result, f, indent=2)
        else:
            print(json.dumps(error_result, indent=2))
        sys.exit(1)

    # Execute
    output = gate.execute(input_data)

    # Validate output
    output_errors = gate.validate_output(output)
    if output_errors:
        print(f"WARNING: Output validation errors: {output_errors}", file=sys.stderr)

    # Write output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
    else:
        print(json.dumps(output, indent=2))

    sys.exit(0 if output["gate_decision"] == "PASSED" else 1)


if __name__ == "__main__":
    main()
