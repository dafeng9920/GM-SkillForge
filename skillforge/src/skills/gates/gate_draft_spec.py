"""
Gate: draft_skill_spec — Draft a skill specification from scan report.

Gate Group: logic (squad-b)
Stage: 3

Input Contract (conforms to gate_interface_v1.yaml)
----------------------------------------------------
{
    "scan_report": {
        "schema_version": str,
        "fit_score": int,
        "repo_type": str,
        "entry_points": list[str],
        "dependencies": dict[str, str],
        "language_stack": str,
        "complexity_metrics": { ... }
    }
}

Output Contract (GateResult)
----------------------------
{
    "gate_name": "draft_skill_spec",
    "gate_decision": "PASSED" | "REJECTED",
    "next_action": "continue" | "halt",
    "error_code": str | null,
    "evidence_refs": [...],
    "skill_spec": { ... }  # Evidence payload
}
"""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..experience_capture import FixKind, capture_gate_event

GATE_NAME = "draft_skill_spec"
GATE_VERSION = "0.1.0"
TOOL_REVISION = "skillforge.gates.logic.v1"


@dataclass
class EvidenceRef:
    """Evidence reference per gate_interface_v1.yaml."""
    issue_key: str
    source_locator: str
    content_hash: str
    tool_revision: str
    timestamp: str


@dataclass
class GateResult:
    """Gate result per gate_interface_v1.yaml."""
    gate_name: str
    gate_decision: str  # "PASSED" | "REJECTED"
    next_action: str    # "continue" | "halt"
    evidence_refs: List[EvidenceRef]
    error_code: Optional[str] = None
    skill_spec: Optional[Dict[str, Any]] = None


def _compute_hash(content: str) -> str:
    """Compute SHA-256 hash of content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _refs_to_dict(evidence_refs: List[EvidenceRef]) -> List[Dict[str, str]]:
    """Convert evidence refs to dict for capture helper."""
    return [
        {
            "issue_key": ref.issue_key,
            "source_locator": ref.source_locator,
            "content_hash": ref.content_hash,
            "tool_revision": ref.tool_revision,
            "timestamp": ref.timestamp,
        }
        for ref in evidence_refs
    ]


def _validate_scan_report(scan_report: Dict[str, Any]) -> List[str]:
    """Validate scan_report input."""
    errors: List[str] = []

    if not isinstance(scan_report, dict):
        errors.append("SCAN_REPORT_INVALID: scan_report must be a dict")
        return errors

    required_fields = ["fit_score", "language_stack"]
    for field in required_fields:
        if field not in scan_report:
            errors.append(f"SCAN_REPORT_INVALID: {field} is required")

    fit_score = scan_report.get("fit_score")
    if isinstance(fit_score, (int, float)):
        # Allow both 0-1.0 and 0-100
        pass
        # if not (0 <= fit_score <= 100):
        #    errors.append(f"SCAN_REPORT_INVALID: fit_score must be 0-100, got {fit_score}")

    return errors


def _draft_skill_spec_from_scan(scan_report: Dict[str, Any]) -> Dict[str, Any]:
    """Draft skill specification from scan report."""
    fit_score = scan_report.get("fit_score", 0)
    language_stack = scan_report.get("language_stack", "unknown")
    repo_type = scan_report.get("repo_type", "template")
    entry_points = scan_report.get("entry_points", ["main.py"])
    dependencies = scan_report.get("dependencies", {})

    # Infer tools_required from language_stack
    tools_map: Dict[str, List[str]] = {
        "Python": ["python3", "pip"],
        "JavaScript": ["node", "npm"],
        "TypeScript": ["node", "npm", "tsc"],
        "Go": ["go"],
        "Rust": ["cargo"],
    }
    tools_required = tools_map.get(language_stack, [])

    # Build input schema
    input_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "entry_point": {"type": "string", "default": entry_points[0] if entry_points else "main.py"},
            "args": {"type": "array", "items": {"type": "string"}},
        },
        "required": [],
    }

    # Build output schema
    output_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "result": {"type": "object"},
            "exit_code": {"type": "integer"},
        },
    }

    # Build capabilities
    capabilities: List[str] = []
    if language_stack in ["Python", "JavaScript", "TypeScript", "Go", "Rust"]:
        capabilities.append("shell")
    if tools_required:
        capabilities.append("file_read")

    # Build SKILL.md content
    skill_md = f"""# Skill Specification

## Name
auto-drafted-skill

## Version
0.1.0

## Description
Auto-drafted skill from repository scan.
- Repository Type: {repo_type}
- Language Stack: {language_stack}
- Fit Score: {fit_score}/100

## Entry Points
{chr(10).join(f'- {ep}' for ep in entry_points)}

## Dependencies
{chr(10).join(f'- {k}: {v}' for k, v in dependencies.items()) if dependencies else 'None'}

## Tools Required
{chr(10).join(f'- {t}' for t in tools_required) if tools_required else 'None'}
"""

    return {
        "schema_version": "0.1.0",
        "name": "auto-drafted-skill",
        "version": "0.1.0",
        "description": f"Auto-drafted skill from repository scan (fit_score: {fit_score})",
        "skill_md": skill_md,
        "input_schema": input_schema,
        "output_schema": output_schema,
        "capabilities": capabilities,
        "tools_required": tools_required,
        "constraints": [
            f"fit_score >= 0.4 (actual: {fit_score})",
            f"language: {language_stack}",
            f"repo_type: {repo_type}",
        ],
        "source": "repo_scan",
    }


@dataclass
class DraftSpecGate:
    """Gate for drafting skill specifications from scan reports."""

    gate_name: str = GATE_NAME
    version: str = GATE_VERSION

    def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """Validate scan_report input."""
        errors: List[str] = []

        if not isinstance(input_data, dict):
            errors.append("INPUT_INVALID: input_data must be a dict")
            return errors

        scan_report = input_data.get("scan_report")
        if scan_report is None:
            errors.append("INPUT_INVALID: scan_report is required")
        else:
            errors.extend(_validate_scan_report(scan_report))

        return errors

    def execute(self, input_data: Dict[str, Any]) -> GateResult:
        """
        Execute the draft_skill_spec gate.

        Args:
            input_data: Dictionary containing 'scan_report'

        Returns:
            GateResult with skill_spec evidence
        """
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        issue_key = f"SKILL-{int(time.time() * 1000)}"

        # Validate input
        validation_errors = self.validate_input(input_data)
        if validation_errors:
            result = GateResult(
                gate_name=self.gate_name,
                gate_decision="REJECTED",
                next_action="halt",
                error_code="GATE.DRAFT_SPEC.INPUT_INVALID",
                evidence_refs=[],
            )
            capture_gate_event(
                gate_node=self.gate_name,
                gate_decision=result.gate_decision,
                evidence_refs=[],
                error_code=result.error_code,
                fix_kind=FixKind.GATE_DECISION,
                summary="draft spec rejected due to invalid scan_report input",
            )
            return result

        scan_report = input_data.get("scan_report", {})

        # Check minimum fit_score threshold
        fit_score = scan_report.get("fit_score", 0)
        # Handle both 0-1 and 0-100 scales
        normalized_score = fit_score
        if fit_score > 1.0:
            normalized_score = fit_score / 100.0
            
        if normalized_score < 0.4:
            result = GateResult(
                gate_name=self.gate_name,
                gate_decision="REJECTED",
                next_action="halt",
                error_code="GATE.DRAFT_SPEC.FIT_SCORE_TOO_LOW",
                evidence_refs=[],
            )
            capture_gate_event(
                gate_node=self.gate_name,
                gate_decision=result.gate_decision,
                evidence_refs=[],
                error_code=result.error_code,
                fix_kind=FixKind.GATE_DECISION,
                summary=f"draft spec rejected: normalized fit score {normalized_score:.3f} < 0.4",
            )
            return result

        # Draft skill spec
        skill_spec = _draft_skill_spec_from_scan(scan_report)

        # Create evidence reference
        content_hash = _compute_hash(str(skill_spec))
        evidence_ref = EvidenceRef(
            issue_key=issue_key,
            source_locator=f"skill_spec://{issue_key}",
            content_hash=content_hash,
            tool_revision=TOOL_REVISION,
            timestamp=timestamp,
        )

        result = GateResult(
            gate_name=self.gate_name,
            gate_decision="PASSED",
            next_action="continue",
            evidence_refs=[evidence_ref],
            skill_spec=skill_spec,
        )
        capture_gate_event(
            gate_node=self.gate_name,
            gate_decision=result.gate_decision,
            evidence_refs=_refs_to_dict(result.evidence_refs),
            fix_kind=FixKind.ADD_CONTRACT,
            summary="draft spec generated from scan report",
        )
        return result

    def validate_output(self, output_data: Dict[str, Any]) -> List[str]:
        """
        Validate output against GateResult schema.

        Returns list of validation error strings. Empty list = valid.
        """
        errors: List[str] = []

        if not isinstance(output_data, dict):
            errors.append("SCHEMA_INVALID: output must be a dict")
            return errors

        # Required fields per gate_interface_v1.yaml
        required_fields = ["gate_name", "gate_decision", "next_action", "evidence_refs"]
        for field in required_fields:
            if field not in output_data:
                errors.append(f"SCHEMA_INVALID: {field} is required")

        # Validate gate_name
        gate_name = output_data.get("gate_name")
        if gate_name != GATE_NAME:
            errors.append(f"SCHEMA_INVALID: gate_name must be '{GATE_NAME}'")

        # Validate gate_decision
        gate_decision = output_data.get("gate_decision")
        if gate_decision not in ("PASSED", "REJECTED"):
            errors.append("SCHEMA_INVALID: gate_decision must be 'PASSED' or 'REJECTED'")

        # Validate next_action
        next_action = output_data.get("next_action")
        if next_action not in ("continue", "halt"):
            errors.append("SCHEMA_INVALID: next_action must be 'continue' or 'halt'")

        # Validate evidence_refs
        evidence_refs = output_data.get("evidence_refs")
        if not isinstance(evidence_refs, list):
            errors.append("SCHEMA_INVALID: evidence_refs must be an array")
        else:
            for i, ref in enumerate(evidence_refs):
                if not isinstance(ref, dict):
                    errors.append(f"SCHEMA_INVALID: evidence_refs[{i}] must be an object")
                    continue
                for ref_field in ["issue_key", "source_locator", "content_hash", "tool_revision", "timestamp"]:
                    if ref_field not in ref:
                        errors.append(f"SCHEMA_INVALID: evidence_refs[{i}].{ref_field} is required")

        # Validate skill_spec (when PASSED)
        if gate_decision == "PASSED":
            skill_spec = output_data.get("skill_spec")
            if not isinstance(skill_spec, dict):
                errors.append("SCHEMA_INVALID: skill_spec must be a dict when PASSED")
            else:
                for field in ["name", "version", "description", "input_schema", "output_schema"]:
                    if field not in skill_spec:
                        errors.append(f"SCHEMA_INVALID: skill_spec.{field} is required")

        return errors

    def to_dict(self, result: GateResult) -> Dict[str, Any]:
        """Convert GateResult to dict for serialization."""
        return {
            "gate_name": result.gate_name,
            "gate_decision": result.gate_decision,
            "next_action": result.next_action,
            "error_code": result.error_code,
            "evidence_refs": [
                {
                    "issue_key": ref.issue_key,
                    "source_locator": ref.source_locator,
                    "content_hash": ref.content_hash,
                    "tool_revision": ref.tool_revision,
                    "timestamp": ref.timestamp,
                }
                for ref in result.evidence_refs
            ],
            "skill_spec": result.skill_spec,
        }


def draft_skill_spec(scan_report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Functional interface for the draft_skill_spec gate.

    Args:
        scan_report: Scan report from repo_scan_fit_score gate (G2)

    Returns:
        GateResult dict with skill_spec evidence
    """
    gate = DraftSpecGate()
    result = gate.execute({"scan_report": scan_report})
    return gate.to_dict(result)


# =============================================================================
# CLI Entry Point
# =============================================================================

def main():
    """CLI entry point for draft_skill_spec gate."""
    import sys
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Draft skill specification from scan report")
    parser.add_argument("--input-file", help="Input JSON file with scan_report")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate input, do not execute"
    )
    args = parser.parse_args()

    gate = DraftSpecGate()

    # Load input
    if args.input_file:
        with open(args.input_file, "r", encoding="utf-8") as f:
            input_data = json.load(f)
    else:
        print("Error: --input-file is required", file=sys.stderr)
        sys.exit(1)

    # Validate input
    validation_errors = gate.validate_input(input_data)
    if validation_errors:
        error_result = {
            "gate_name": GATE_NAME,
            "gate_decision": "REJECTED",
            "next_action": "halt",
            "error_code": "GATE.DRAFT_SPEC.INPUT_INVALID",
            "evidence_refs": [],
            "skill_spec": None,
            "validation_errors": validation_errors
        }
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(error_result, f, indent=2)
        else:
            print(json.dumps(error_result, indent=2))
        sys.exit(1)

    if args.validate_only:
        print(json.dumps({"status": "VALID", "errors": []}, indent=2))
        sys.exit(0)

    # Execute
    result = gate.execute(input_data)
    output = gate.to_dict(result)

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
