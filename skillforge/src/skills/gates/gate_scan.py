"""
GateRepoScanFitScore — evaluates repository fit score for migration.

Implements the gate contract for repo_scan_fit_score with fail-closed rules.

Input Contract (Scan Request)
-----------------------------
{
    "repo_path": str,       # Local path, required
    "issue_key": str,       # optional, auto-generated if not provided
    "min_fit_score": float  # optional, default 0.6
}

Output Contract (Gate Result)
-----------------------------
{
    "gate_name": "repo_scan_fit_score",
    "gate_decision": "PASSED" | "REJECTED",
    "next_action": "continue" | "halt",
    "error_code": str | null,
    "evidence_refs": [EvidenceRef]
}

Fail-Closed Rules
-----------------
FC-SCAN-1: repo_path is null -> REJECTED
FC-SCAN-2: repo_path does not exist -> REJECTED
FC-SCAN-3: fit_score < min_fit_score -> REJECTED
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from ..experience_capture import FixKind, capture_gate_event

# Issue key pattern: REQ-123, SCAN-TEST-001
ISSUE_KEY_PATTERN = re.compile(r"^[A-Z]+-[A-Z0-9]+$")


@dataclass
class EvidenceRef:
    """Evidence reference following gate_interface_v1.yaml schema."""

    issue_key: str
    source_locator: str
    content_hash: str
    tool_revision: str
    timestamp: str


class GateRepoScanFitScore:
    """Scan gate for repository fit score evaluation."""

    node_id: str = "repo_scan_fit_score"
    gate_group: str = "entrance"
    tool_revision: str = "v1.0.0"

    # Error codes
    ERROR_FIT_SCORE_LOW = "ERR_FIT_SCORE_LOW"
    ERROR_REPO_NOT_FOUND = "ERR_REPO_NOT_FOUND"

    # Default minimum fit score
    MIN_FIT_SCORE: float = 0.6

    # Evidence storage path (can be overridden for testing)
    evidence_base_path: str = "AuditPack/evidence"

    def __init__(self, evidence_base_path: Optional[str] = None):
        if evidence_base_path:
            self.evidence_base_path = evidence_base_path

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """
        Validate scan request against fail-closed rules.

        Returns list of validation error strings. Empty list = valid.
        """
        errors: list[str] = []

        if not isinstance(input_data, dict):
            errors.append("SCHEMA_INVALID: input must be a dict")
            return errors

        # FC-SCAN-1: repo_path is required
        repo_path = input_data.get("repo_path")
        if repo_path is None or repo_path == "":
            errors.append("FC-SCAN-1: repo_path is required")
        elif not isinstance(repo_path, str):
            errors.append("FC-SCAN-1: repo_path must be a string")

        # min_fit_score is optional, but if provided must be valid
        min_fit_score = input_data.get("min_fit_score")
        if min_fit_score is not None:
            if not isinstance(min_fit_score, (int, float)):
                errors.append("SCHEMA_INVALID: min_fit_score must be a number")
            elif min_fit_score < 0.0 or min_fit_score > 1.0:
                errors.append("SCHEMA_INVALID: min_fit_score must be between 0.0 and 1.0")

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
        Execute scan gate: scan repository and evaluate fit score.

        Args:
            input_data: Validated input payload.

        Returns:
            Gate result conforming to gate_interface_v1.yaml.
        """
        repo_path = input_data.get("repo_path", "")
        issue_key = input_data.get("issue_key")
        min_fit_score = input_data.get("min_fit_score", self.MIN_FIT_SCORE)

        # Generate issue_key if not provided
        if issue_key is None:
            issue_key = f"SCAN-{time.strftime('%Y%m%d%H%M%S', time.gmtime())}"

        # Perform scan
        scan_result = self._scan_repository(repo_path)

        # Generate timestamp
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # FC-SCAN-3: Check fit score threshold
        if scan_result["fit_score"] < min_fit_score:
            report = {
                "repo_path": repo_path,
                "fit_score": scan_result["fit_score"],
                "findings": scan_result["findings"],
                "scan_timestamp": timestamp,
                "status": "REJECTED",
                "component_id": f"scan/{issue_key}",
            }
            evidence_ref = self._create_evidence_ref(issue_key, report)
            self._save_evidence(issue_key, report)

            result = {
                "gate_name": self.node_id,
                "gate_decision": "REJECTED",
                "next_action": "halt",
                "error_code": self.ERROR_FIT_SCORE_LOW,
                "evidence_refs": [self._evidence_ref_to_dict(evidence_ref)],
            }
            capture_gate_event(
                gate_node=self.node_id,
                gate_decision=result["gate_decision"],
                evidence_refs=result["evidence_refs"],
                error_code=result["error_code"],
                fix_kind=FixKind.GATE_DECISION,
                summary=f"fit score below threshold ({scan_result['fit_score']:.3f} < {min_fit_score:.3f})",
            )
            return result

        # Create successful scan report
        report = {
            "repo_path": repo_path,
            "fit_score": scan_result["fit_score"],
            "findings": scan_result["findings"],
            "scan_timestamp": timestamp,
            "status": "COMPLETED",
            "component_id": f"scan/{issue_key}",
            "language_stack": scan_result.get("language_stack", "Unknown")
        }
        evidence_ref = self._create_evidence_ref(issue_key, report)
        self._save_evidence(issue_key, report)

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
            summary=f"repo scan passed with fit score {scan_result['fit_score']:.3f}",
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
    # Scan Methods
    # =========================================================================

    def _scan_repository(self, repo_path: str) -> dict[str, Any]:
        """
        Perform repository scanning and calculate fit score.
        Uses only stdlib - no heavy dependencies like pandas.
        """
        findings: list[dict] = []
        file_count = 0
        fit_score = 0.0
        has_readme = False
        has_pyproject = False
        has_setup = False

        # FC-SCAN-2: Check if path exists
        if not os.path.exists(repo_path):
            return {
                "fit_score": 0.0,
                "findings": [{"severity": "CRITICAL", "description": "Repository path not found"}],
                "file_count": 0,
                "has_valid_structure": False,
            }

        try:
            # Count non-hidden files
            for _root, dirs, files in os.walk(repo_path):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                for f in files:
                    if not f.startswith("."):
                        file_count += 1

            # Check for valid project structure
            has_readme = os.path.exists(os.path.join(repo_path, "README.md"))
            has_pyproject = os.path.exists(os.path.join(repo_path, "pyproject.toml"))
            has_setup = os.path.exists(os.path.join(repo_path, "setup.py"))
            has_requirements = os.path.exists(os.path.join(repo_path, "requirements.txt"))
            has_src = os.path.isdir(os.path.join(repo_path, "src")) or os.path.isdir(os.path.join(repo_path, "skillforge"))

            language_stack = "Custom"
            if has_pyproject or has_setup or has_requirements:
                language_stack = "Python"

            # Calculate fit score based on criteria
            score_components = []

            if has_readme:
                score_components.append(0.2)
                findings.append({"severity": "LOW", "description": "README.md found"})

            if has_pyproject or has_setup or has_requirements:
                score_components.append(0.3)
                findings.append({"severity": "LOW", "description": "Package configuration found"})

            if has_src:
                score_components.append(0.2)
                findings.append({"severity": "LOW", "description": "Source directory structure found"})

            if file_count > 0:
                score_components.append(0.3)
                findings.append({
                    "severity": "LOW",
                    "description": f"Found {file_count} files",
                    "location": repo_path,
                })

            fit_score = sum(score_components)

        except Exception as e:
            findings.append({
                "severity": "HIGH",
                "description": f"Scan error: {str(e)}",
            })
            fit_score = 0.0
            language_stack = "Unknown"

        return {
            "fit_score": fit_score,
            "findings": findings,
            "file_count": file_count,
            "has_valid_structure": has_readme or has_pyproject or has_setup or has_requirements,
            "language_stack": language_stack
        }

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _compute_hash(self, content: str) -> str:
        """Compute SHA-256 hash of content."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _create_evidence_ref(self, issue_key: str, report: dict) -> EvidenceRef:
        """Create evidence reference for the scan report."""
        content = json.dumps(report, sort_keys=True)
        content_hash = self._compute_hash(content)
        source_locator = f"file://{self.evidence_base_path}/scan_report_{issue_key}.json"
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

    def _save_evidence(self, issue_key: str, report: dict) -> None:
        """Save evidence to file (for production use)."""
        path = Path(self.evidence_base_path) / f"scan_report_{issue_key}.json"
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write atomically via temp file
        temp_path = path.with_suffix(".tmp")
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            temp_path.replace(path)
        except OSError:
            # Do not fail gate result when local evidence path is unavailable.
            return


# Convenience function for module-level usage
def repo_scan_fit_score(
    repo_path: Optional[str],
    issue_key: Optional[str] = None,
) -> dict[str, Any]:
    """
    Convenience function to run scan gate.

    Matches gate_interface_v1.yaml signature:
        inputs: [repo_path]
        outputs: [GateResult]
    """
    gate = GateRepoScanFitScore()

    input_data = {"repo_path": repo_path}
    if issue_key:
        input_data["issue_key"] = issue_key

    # Validate input
    errors = gate.validate_input(input_data)
    if errors:
        result = {
            "gate_name": gate.node_id,
            "gate_decision": "REJECTED",
            "next_action": "halt",
            "error_code": gate.ERROR_REPO_NOT_FOUND,
            "evidence_refs": [],
        }
        capture_gate_event(
            gate_node=gate.node_id,
            gate_decision=result["gate_decision"],
            evidence_refs=result["evidence_refs"],
            error_code=result["error_code"],
            fix_kind=FixKind.GATE_DECISION,
            summary="repo scan rejected by input validation",
        )
        return result

    return gate.execute(input_data)


# Backward compatibility: ScanGate alias
ScanGate = GateRepoScanFitScore


# CLI entry point
def main():
    """CLI entry point for Scan Gate."""
    import argparse

    parser = argparse.ArgumentParser(description="Gate: Repo Scan Fit Score")
    parser.add_argument("--repo-path", required=True, help="Local path to repository")
    parser.add_argument("--issue-key", help="Unique request ID")
    parser.add_argument("--min-fit-score", type=float, default=0.6, help="Minimum fit score threshold")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument(
        "--evidence-path",
        default="AuditPack/evidence",
        help="Base path for evidence storage"
    )
    args = parser.parse_args()

    gate = GateRepoScanFitScore(evidence_base_path=args.evidence_path)

    input_data = {
        "repo_path": args.repo_path,
        "issue_key": args.issue_key,
        "min_fit_score": args.min_fit_score,
    }

    # Validate input
    validation_errors = gate.validate_input(input_data)
    if validation_errors:
        error_result = {
            "gate_name": gate.node_id,
            "gate_decision": "REJECTED",
            "next_action": "halt",
            "error_code": gate.ERROR_REPO_NOT_FOUND,
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
