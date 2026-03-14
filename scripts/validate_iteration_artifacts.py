#!/usr/bin/env python3
"""
PR3-T1: Iteration Artifacts Validation - Diff / Rationale / Tombstone

Validates that when three hashes change (demand/contract/decision), the
required iteration artifacts must exist:

Required artifacts:
- demand_diff.json
- contract_diff.json
- decision_diff.json
- rationale.json or rationale.md
- tombstone.json (if replacing/superseding old revision)

Missing any artifact => FAIL with specific error code.

Spec source:
- docs/2026-03-04/v0-L5/"三哈希口径"落成validate.py 的硬校验（v0）.md (rules 9-10)
- docs/2026-03-04/v0-L5/Gap Analysis v0 模板（可喂给 AI 修复 & 可被审计复核）.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import TypedDict


# Error codes per v0-L5 specification
ERROR_CODES = {
    "DEMAND_DIFF_MISSING": "SF_ITERATION_DEMAND_DIFF_MISSING",
    "CONTRACT_DIFF_MISSING": "SF_ITERATION_CONTRACT_DIFF_MISSING",
    "DECISION_DIFF_MISSING": "SF_ITERATION_DECISION_DIFF_MISSING",
    "RATIONALE_MISSING": "SF_ITERATION_RATIONALE_MISSING",
    "TOMBSTONE_MISSING": "SF_ITERATION_TOMBSTONE_MISSING",
    "ITERATION_ARTIFACTS_INCOMPLETE": "SF_ITERATION_ARTIFACTS_INCOMPLETE",
    "HASH_DETECTION_FAILED": "SF_HASH_DETECTION_FAILED",
    "REVISION_FORMAT_INVALID": "SF_REVISION_FORMAT_INVALID",
}

# SHA256 hash pattern
SHA256_PATTERN = re.compile(r'^(sha256:)?[0-9a-f]{64}$')


class ValidationResult(TypedDict):
    """Machine-readable validation result."""
    status: str  # "PASS" or "FAIL"
    error_code: str | None
    hashes_changed: dict[str, bool]
    missing_artifacts: list[dict[str, str]]
    present_artifacts: list[dict[str, str]]
    checked_at: str
    revision_from: str | None
    revision_to: str | None
    requires_tombstone: bool


def extract_hash(manifest: dict, hash_key: str) -> str | None:
    """Extract hash value from manifest."""
    value = manifest.get(hash_key)
    if value and isinstance(value, str):
        match = SHA256_PATTERN.match(value.strip())
        if match:
            return value.strip()
    return None


def hash_changed(from_hash: str | None, to_hash: str | None) -> bool:
    """Check if hash changed between revisions."""
    if not from_hash or not to_hash:
        return True  # Consider it changed if either is missing
    return from_hash != to_hash


def find_artifact_file(base_path: Path, pattern: str, name: str) -> dict | None:
    """
    Find artifact file matching pattern.

    Returns dict with name, path, found status.
    """
    matches = list(base_path.glob(pattern))

    for match in matches:
        if match.is_file():
            return {
                "name": name,
                "path": str(match),
                "found": True,
            }

    return {
        "name": name,
        "path": pattern,
        "found": False,
    }


def validate_iteration_artifacts(
    manifest_from: dict | None,
    manifest_to: dict,
    audit_base_path: Path,
    revision_from: str | None = None,
    revision_to: str | None = None,
    requires_tombstone: bool = False
) -> ValidationResult:
    """
    Validate that required iteration artifacts exist when hashes change.

    Args:
        manifest_from: Previous revision manifest (or None if initial)
        manifest_to: Current revision manifest
        audit_base_path: Base path for audit artifacts (audit/)
        revision_from: Previous revision ID (for artifact naming)
        revision_to: Current revision ID (for artifact naming)
        requires_tombstone: True if old revision is being replaced

    Returns:
        Machine-readable validation result.
    """
    result: ValidationResult = {
        "status": "FAIL",
        "error_code": None,
        "hashes_changed": {},
        "missing_artifacts": [],
        "present_artifacts": [],
        "checked_at": datetime.now(UTC).isoformat(),
        "revision_from": revision_from,
        "revision_to": revision_to,
        "requires_tombstone": requires_tombstone,
    }

    # Extract hashes from both manifests
    hash_keys = ["demand_hash", "contract_hash", "decision_hash"]

    hashes_from = {}
    hashes_to = {}

    for key in hash_keys:
        if manifest_from:
            hashes_from[key] = extract_hash(manifest_from, key)
        hashes_to[key] = extract_hash(manifest_to, key)

    # Check which hashes changed
    any_hash_changed = False
    for key in hash_keys:
        changed = hash_changed(hashes_from.get(key), hashes_to.get(key))
        result["hashes_changed"][key] = changed
        if changed:
            any_hash_changed = True

    # If no hashes changed and no tombstone required, iteration artifacts not needed
    if not any_hash_changed and not requires_tombstone:
        result["status"] = "PASS"
        return result

    # Validate required iteration artifacts
    missing_required = []

    # 1) demand_diff.json
    diff_pattern = f"diffs/*_to_{revision_to}/demand_diff.json" if revision_to else "diffs/**/demand_diff.json"
    artifact = find_artifact_file(audit_base_path, diff_pattern, "demand_diff.json")
    if artifact["found"]:
        result["present_artifacts"].append(artifact)
    else:
        result["missing_artifacts"].append(artifact)
        missing_required.append("demand_diff")

    # 2) contract_diff.json
    diff_pattern = f"diffs/*_to_{revision_to}/contract_diff.json" if revision_to else "diffs/**/contract_diff.json"
    artifact = find_artifact_file(audit_base_path, diff_pattern, "contract_diff.json")
    if artifact["found"]:
        result["present_artifacts"].append(artifact)
    else:
        result["missing_artifacts"].append(artifact)
        missing_required.append("contract_diff")

    # 3) decision_diff.json
    diff_pattern = f"diffs/*_to_{revision_to}/decision_diff.json" if revision_to else "diffs/**/decision_diff.json"
    artifact = find_artifact_file(audit_base_path, diff_pattern, "decision_diff.json")
    if artifact["found"]:
        result["present_artifacts"].append(artifact)
    else:
        result["missing_artifacts"].append(artifact)
        missing_required.append("decision_diff")

    # 4) rationale.json or rationale.md
    rationale_pattern = f"rationale/{revision_to}.json" if revision_to else "rationale/*.json"
    artifact = find_artifact_file(audit_base_path, rationale_pattern, "rationale.json")
    if not artifact["found"]:
        # Try .md
        rationale_pattern = f"rationale/{revision_to}.md" if revision_to else "rationale/*.md"
        artifact = find_artifact_file(audit_base_path, rationale_pattern, "rationale.md")
    if artifact["found"]:
        result["present_artifacts"].append(artifact)
    else:
        result["missing_artifacts"].append({
            "name": "rationale",
            "path": f"rationale/{revision_to}.(json|md)" if revision_to else "rationale/*.(json|md)",
            "found": False,
        })
        missing_required.append("rationale")

    # 5) tombstone.json (if required)
    if requires_tombstone:
        tombstone_pattern = f"tombstones/{revision_from}.json" if revision_from else "tombstones/*.json"
        artifact = find_artifact_file(audit_base_path, tombstone_pattern, "tombstone.json")
        if artifact["found"]:
            result["present_artifacts"].append(artifact)
        else:
            result["missing_artifacts"].append(artifact)
            missing_required.append("tombstone")

    # Determine overall status
    if missing_required:
        # Use specific error code for first missing item
        first_missing = missing_required[0].upper()
        error_key = f"{first_missing}_MISSING"
        result["error_code"] = ERROR_CODES.get(
            error_key,
            ERROR_CODES["ITERATION_ARTIFACTS_INCOMPLETE"]
        )
    else:
        result["status"] = "PASS"

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate iteration artifacts (diff/rationale/tombstone) when hashes change"
    )
    parser.add_argument(
        "--manifest-to",
        type=Path,
        required=True,
        help="Path to current revision manifest (with hashes)",
    )
    parser.add_argument(
        "--manifest-from",
        type=Path,
        help="Path to previous revision manifest (for comparison)",
    )
    parser.add_argument(
        "--audit-base",
        type=Path,
        default=Path("audit"),
        help="Base path for audit artifacts (default: audit/)",
    )
    parser.add_argument(
        "--revision-from",
        help="Previous revision ID (for artifact naming)",
    )
    parser.add_argument(
        "--revision-to",
        help="Current revision ID (for artifact naming)",
    )
    parser.add_argument(
        "--requires-tombstone",
        action="store_true",
        help="Set if old revision is being replaced (tombstone.json required)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write machine-readable result to file (JSON format)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only output status (PASS/FAIL), no details",
    )
    args = parser.parse_args()

    # Load current manifest
    try:
        manifest_to = json.loads(args.manifest_to.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERROR: Failed to load manifest-to: {e}", file=sys.stderr)
        return 1

    # Load previous manifest if provided
    manifest_from = None
    if args.manifest_from and args.manifest_from.exists():
        try:
            manifest_from = json.loads(args.manifest_from.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"WARNING: Failed to load manifest-from: {e}", file=sys.stderr)

    # Run validation
    result = validate_iteration_artifacts(
        manifest_from=manifest_from,
        manifest_to=manifest_to,
        audit_base_path=args.audit_base,
        revision_from=args.revision_from,
        revision_to=args.revision_to,
        requires_tombstone=args.requires_tombstone
    )

    # Write output file if requested
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    if args.quiet:
        print(result["status"])
    else:
        print(f"status: {result['status']}")
        print(f"checked_at: {result['checked_at']}")

        if args.revision_from or args.revision_to:
            print(f"revision_from: {result['revision_from'] or 'N/A'}")
            print(f"revision_to: {result['revision_to'] or 'N/A'}")

        print("\nhashes_changed:")
        for name, changed in result["hashes_changed"].items():
            print(f"  {name}: {changed}")

        if result["error_code"]:
            print(f"\nerror_code: {result['error_code']}")

        if result["present_artifacts"]:
            print("\npresent_artifacts:")
            for item in result["present_artifacts"]:
                print(f"  ✓ {item['name']}: {item['path']}")

        if result["missing_artifacts"]:
            print("\nmissing_artifacts:")
            for item in result["missing_artifacts"]:
                print(f"  ✗ {item['name']}: {item['path']}")

    # Exit code: 0 = PASS, 1 = FAIL
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
