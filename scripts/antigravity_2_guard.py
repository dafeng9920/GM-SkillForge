#!/usr/bin/env python3
"""
Antigravity-2 Compliance Guard (LOCAL-ANTIGRAVITY)

FAIL-CLOSED 三重门禁系统：
1. Permit 五字段校验 (demand_hash, contract_hash, decision_hash, audit_pack_hash, revision)
2. Delivery 六件套校验 (Blueprint, Skill, n8n, Evidence, AuditPack, Permit)
3. Three-Hash Guard 总门禁 (验证 manifest 中的三哈希与实际文件一致)

任何检查失败 => DENY + 阻断

Spec source: docs/2026-03-04/v0-L5/
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

# Import the existing validators
sys.path.insert(0, str(Path(__file__).parent))
try:
    from validate_permit_binding import validate_permit_binding, ERROR_CODES
    from validate_delivery_completeness import validate_delivery_completeness
    from hash_calc import calc_three_hashes, read_json, read_yaml
except ImportError as e:
    print(f"ERROR: Failed to import validator modules: {e}", file=sys.stderr)
    sys.exit(1)


class GuardDecision(str, Enum):
    """Guard decision values."""
    ALLOW = "ALLOW"
    DENY = "DENY"


def validate_fixed_caliber_binding(
    permit_path: Path,
    demand_path: Path,
    contract_path: Path,
    decision_path: Path,
    fixed_caliber_config_path: Path = Path("orchestration/fixed_caliber_binding.yml")
) -> dict:
    """
    Validate that the provided paths match the fixed-caliber binding configuration.

    FAIL-CLOSED: 禁止跨批次混用，必须使用固定口径配置中指定的文件。

    Returns dict with status, error details.
    """
    result = {
        "status": "FAIL",
        "error_code": None,
        "error_details": [],
        "fixed_caliber_id": None,
        "config_file": str(fixed_caliber_config_path),
        "provided_paths": {},
        "expected_paths": {},
    }

    # If fixed-caliber config doesn't exist, skip this check (allow for backward compatibility)
    if not fixed_caliber_config_path.exists():
        result["status"] = "PASS"
        result["error_code"] = "SF_FIXED_CALIBER_CONFIG_NOT_FOUND"
        result["error_details"].append("Fixed-caliber config not found, skipping binding validation")
        return result

    # Read fixed-caliber config
    try:
        config = read_yaml(fixed_caliber_config_path)
    except Exception as e:
        result["error_code"] = "SF_FIXED_CALIBER_CONFIG_INVALID"
        result["error_details"].append(f"Failed to parse fixed-caliber config: {e}")
        return result

    result["fixed_caliber_id"] = config.get("caliber_id")
    result["expected_paths"] = {
        "permit": config.get("fixed_binding", {}).get("permit", {}).get("path"),
        "demand": config.get("fixed_binding", {}).get("three_rights", {}).get("demand", {}).get("path"),
        "contract": config.get("fixed_binding", {}).get("three_rights", {}).get("contract", {}).get("path"),
        "decision": config.get("fixed_binding", {}).get("three_rights", {}).get("decision", {}).get("path"),
    }

    result["provided_paths"] = {
        "permit": str(permit_path),
        "demand": str(demand_path),
        "contract": str(contract_path),
        "decision": str(decision_path),
    }

    # Compare each path (normalize path separators for cross-platform compatibility)
    mismatches = []
    for key in ["permit", "demand", "contract", "decision"]:
        expected = result["expected_paths"][key]
        provided = result["provided_paths"][key]

        # Normalize paths: replace both / and \ with os.path.sep for comparison
        if expected:
            expected_norm = str(Path(expected))
            provided_norm = str(Path(provided))

            if provided_norm != expected_norm:
                mismatches.append({
                    "file": key,
                    "expected": expected,
                    "provided": provided,
                    "expected_normalized": expected_norm,
                    "provided_normalized": provided_norm,
                })

    if mismatches:
        result["error_code"] = "SF_FIXED_CALIBER_VIOLATION"
        result["error_details"] = mismatches
        return result

    # Verify permit_id matches if specified in config
    expected_permit_id = config.get("fixed_binding", {}).get("permit", {}).get("permit_id")
    if expected_permit_id and permit_path.exists():
        try:
            permit_data = json.loads(permit_path.read_text(encoding="utf-8"))
            actual_permit_id = permit_data.get("permit_id")
            if actual_permit_id != expected_permit_id:
                result["error_code"] = "SF_FIXED_CALIBER_PERMIT_ID_MISMATCH"
                result["error_details"].append({
                    "field": "permit_id",
                    "expected": expected_permit_id,
                    "actual": actual_permit_id,
                })
                return result
        except Exception as e:
            result["error_code"] = "SF_FIXED_CALIBER_PERMIT_READ_ERROR"
            result["error_details"].append(f"Failed to read permit: {e}")
            return result

    result["status"] = "PASS"
    return result


class GuardResult:
    """Result of the Antigravity-2 guard check."""

    def __init__(self):
        self.status = GuardDecision.DENY
        self.permit_binding_result = None
        self.fixed_caliber_binding_result = None
        self.permit_hash_consistency_result = None
        self.delivery_completeness_result = None
        self.three_hash_result = None
        self.error_code = None
        self.errors = []
        self.required_changes = []
        self.checked_at = datetime.now(UTC).isoformat()

    def add_error(self, code: str, message: str, required_change: str):
        """Add an error and set DENY status."""
        self.error_code = code
        self.errors.append({"code": code, "message": message})
        self.required_changes.append(required_change)

    def set_allow(self):
        """Set status to ALLOW."""
        self.status = GuardDecision.ALLOW
        self.error_code = None


def validate_permit_hash_consistency(
    permit_path: Path,
    demand_path: Path,
    contract_path: Path,
    decision_path: Path,
    keysets_path: Path = Path("orchestration/hash_keysets.yml")
) -> dict:
    """
    Validate Permit hashes match actual three-rights files (固定单一口径).

    FAIL-CLOSED: Permit 中的哈希值必须与实际三权文件计算出的哈希值完全一致。
    不允许跨批次混用，发现不一致直接 DENY。

    Returns dict with status, error details, and required_changes.
    """
    result = {
        "status": "FAIL",
        "error_code": None,
        "error_details": [],
        "permit_hashes": {},
        "computed_hashes": {},
        "mismatch_details": [],
    }

    # Check permit exists
    if not permit_path.exists():
        result["error_code"] = "SF_PERMIT_MISSING"
        result["error_details"].append(f"Permit not found: {permit_path}")
        return result

    # Check source files exist
    for name, path in [("demand", demand_path), ("contract", contract_path), ("decision", decision_path)]:
        if not path.exists():
            result["error_code"] = f"SF_{name.upper()}_MISSING"
            result["error_details"].append(f"{name.capitalize()} file not found: {path}")
            return result

    # Read permit
    try:
        permit_data = json.loads(permit_path.read_text(encoding="utf-8"))
    except Exception as e:
        result["error_code"] = "SF_PERMIT_INVALID_JSON"
        result["error_details"].append(f"Failed to parse permit: {e}")
        return result

    # Extract hashes from permit
    permit_hashes = {
        "demand_hash": permit_data.get("demand_hash"),
        "contract_hash": permit_data.get("contract_hash"),
        "decision_hash": permit_data.get("decision_hash"),
    }
    result["permit_hashes"] = permit_hashes

    # Compute three hashes from actual files
    try:
        keysets = read_yaml(keysets_path) if keysets_path.exists() else {}
        computed = calc_three_hashes(
            read_json(demand_path),
            read_json(contract_path),
            read_json(decision_path),
            keysets
        )
        result["computed_hashes"] = {
            "demand_hash": computed.get("demand_hash"),
            "contract_hash": computed.get("contract_hash"),
            "decision_hash": computed.get("decision_hash"),
        }
    except Exception as e:
        result["error_code"] = "SF_HASH_CALCULATION_FAILED"
        result["error_details"].append(f"Failed to compute hashes: {e}")
        return result

    # Compare each hash
    mismatches = []
    for key in ("demand_hash", "contract_hash", "decision_hash"):
        permit_val = permit_hashes[key]
        computed_val = result["computed_hashes"][key]

        if permit_val != computed_val:
            mismatches.append({
                "field": key,
                "permit_value": permit_val,
                "computed_value": computed_val,
            })
            result["mismatch_details"].append({
                "field": key,
                "permit_hash": permit_val,
                "actual_hash": computed_val,
                "matches": False,
            })

    if mismatches:
        result["error_code"] = "SF_PERMIT_HASH_MISMATCH"
        result["error_details"] = mismatches
        return result

    result["status"] = "PASS"
    return result


def validate_three_hash_consistency(
    demand_path: Path,
    contract_path: Path,
    decision_path: Path,
    manifest_path: Path,
    keysets_path: Path = Path("orchestration/hash_keysets.yml")
) -> dict:
    """
    Validate three-hash consistency between actual files and manifest.

    Returns dict with status, error details.
    """
    result = {
        "status": "FAIL",
        "error_code": None,
        "error_details": [],
        "computed_hashes": {},
        "manifest_hashes": {},
    }

    # Check manifest exists
    if not manifest_path.exists():
        result["error_code"] = "SF_MANIFEST_MISSING"
        result["error_details"].append(f"Manifest not found: {manifest_path}")
        return result

    # Check source files exist
    for name, path in [("demand", demand_path), ("contract", contract_path), ("decision", decision_path)]:
        if not path.exists():
            result["error_code"] = f"SF_{name.upper()}_MISSING"
            result["error_details"].append(f"{name.capitalize()} file not found: {path}")
            return result

    # Read manifest
    try:
        manifest = read_json(manifest_path)
    except Exception as e:
        result["error_code"] = "SF_MANIFEST_INVALID_JSON"
        result["error_details"].append(f"Failed to parse manifest: {e}")
        return result

    # Compute three hashes from actual files
    try:
        keysets = read_yaml(keysets_path) if keysets_path.exists() else {}
        computed = calc_three_hashes(
            read_json(demand_path),
            read_json(contract_path),
            read_json(decision_path),
            keysets
        )
        result["computed_hashes"] = computed
    except Exception as e:
        result["error_code"] = "SF_HASH_CALCULATION_FAILED"
        result["error_details"].append(f"Failed to compute hashes: {e}")
        return result

    # Extract hashes from manifest
    result["manifest_hashes"] = {
        "hash_spec_version": manifest.get("hash_spec_version"),
        "demand_hash": manifest.get("demand_hash"),
        "contract_hash": manifest.get("contract_hash"),
        "decision_hash": manifest.get("decision_hash"),
    }

    # Compare each hash
    mismatch_errors = []
    for key in ("hash_spec_version", "demand_hash", "contract_hash", "decision_hash"):
        manifest_val = result["manifest_hashes"][key]
        computed_val = result["computed_hashes"].get(key)

        if manifest_val != computed_val:
            mismatch_errors.append({
                "field": key,
                "manifest": manifest_val,
                "computed": computed_val,
            })

    if mismatch_errors:
        result["error_code"] = "SF_THREE_HASH_MISMATCH"
        result["error_details"] = mismatch_errors
        return result

    result["status"] = "PASS"
    return result


def run_antigravity_2_guard(
    permit_path: Path,
    demand_path: Path | None = None,
    contract_path: Path | None = None,
    decision_path: Path | None = None,
    manifest_path: Path | None = None,
    base_path: Path | None = None,
    keysets_path: Path = Path("orchestration/hash_keysets.yml"),
    skip_three_hash: bool = False,
) -> GuardResult:
    """
    Run the Antigravity-2 compliance guard.

    Args:
        permit_path: Path to permit JSON file
        demand_path: Path to demand JSON file (for three-hash check)
        contract_path: Path to contract JSON file (for three-hash check)
        decision_path: Path to decision JSON file (for three-hash check)
        manifest_path: Path to manifest JSON file (for three-hash check)
        base_path: Base path for delivery completeness check (default: current directory)
        keysets_path: Path to hash keysets YAML file
        skip_three_hash: Skip three-hash consistency check (default: False)

    Returns:
        GuardResult with ALLOW/DENY decision
    """
    result = GuardResult()

    if base_path is None:
        base_path = Path.cwd()

    # Stage 1: Permit 五字段校验
    print(f"[AG-2] Stage 1: Validating permit binding (五字段校验)")
    print(f"[AG-2]   Permit: {permit_path}")

    permit_binding = validate_permit_binding(permit_path)
    result.permit_binding_result = {
        "status": permit_binding["status"],
        "error_code": permit_binding.get("error_code"),
        "missing_hashes": permit_binding.get("missing_hashes", []),
        "missing_fields": permit_binding.get("missing_fields", []),
        "invalid_hashes": permit_binding.get("invalid_hashes", []),
    }

    if permit_binding["status"] != "PASS":
        error_code = permit_binding.get("error_code", "UNKNOWN")
        if "MISSING" in error_code or "INCOMPLETE" in error_code:
            missing = permit_binding.get("missing_fields", [])
            result.add_error(
                error_code,
                f"Permit binding incomplete: missing {', '.join(missing)}",
                "Add all five required fields to permit (demand_hash, contract_hash, decision_hash, audit_pack_hash, revision)"
            )
        elif error_code == "SF_HASH_FORMAT_INVALID":
            invalid = permit_binding.get("invalid_hashes", [])
            for h in invalid:
                result.add_error(
                    error_code,
                    f"Invalid hash format for {h['name']}",
                    f"Fix hash format for {h['name']} (sha256:<64hex> or <64hex>)"
                )
        else:
            result.add_error(
                error_code,
                f"Permit validation failed: {error_code}",
                "Review permit and ensure all five required fields are present and valid"
            )

        print(f"[AG-2]   Result: FAIL - {error_code}")
        return result

    print(f"[AG-2]   Result: PASS")

    # Stage 1.2: 固定口径配置验证 (禁止跨批次混用)
    fixed_caliber_config_path = Path("orchestration/fixed_caliber_binding.yml")
    if fixed_caliber_config_path.exists():
        print(f"[AG-2] Stage 1.2: Validating fixed-caliber binding (禁止跨批次混用)")
        print(f"[AG-2]   Config: {fixed_caliber_config_path}")

        # Require explicit three-rights paths for fixed-caliber validation
        if demand_path is None or contract_path is None or decision_path is None:
            result.add_error(
                "SF_FIXED_CALIBER_PATHS_REQUIRED",
                "Fixed-caliber validation requires explicit demand/contract/decision paths",
                "Re-run with --demand, --contract, --decision arguments to match fixed-caliber binding"
            )
            print(f"[AG-2]   Result: FAIL - Three-rights paths not explicitly provided")
            return result

        fixed_caliber_result = validate_fixed_caliber_binding(
            permit_path, demand_path, contract_path, decision_path, fixed_caliber_config_path
        )

        result.fixed_caliber_binding_result = {
            "status": fixed_caliber_result["status"],
            "error_code": fixed_caliber_result.get("error_code"),
            "fixed_caliber_id": fixed_caliber_result.get("fixed_caliber_id"),
            "error_details": fixed_caliber_result.get("error_details", []),
            "expected_paths": fixed_caliber_result.get("expected_paths", {}),
            "provided_paths": fixed_caliber_result.get("provided_paths", {}),
        }

        if fixed_caliber_result["status"] != "PASS":
            # Skip if config doesn't exist (backward compatibility)
            if fixed_caliber_result.get("error_code") == "SF_FIXED_CALIBER_CONFIG_NOT_FOUND":
                print(f"[AG-2]   Result: SKIPPED (config not found)")
            else:
                error_code = fixed_caliber_result.get("error_code", "UNKNOWN")
                error_details = fixed_caliber_result.get("error_details", [])

                if error_code == "SF_FIXED_CALIBER_VIOLATION":
                    violations = [f"{e['file']}: expected {e['expected']}, got {e['provided']}" for e in error_details]
                    result.add_error(
                        error_code,
                        f"Fixed-caliber violation: {', '.join([e['file'] for e in error_details])}",
                        f"PROHIBITED: Use fixed-caliber paths only. Violations: {'; '.join(violations)}"
                    )
                elif error_code == "SF_FIXED_CALIBER_PERMIT_ID_MISMATCH":
                    permit_mismatch = error_details[0] if error_details else {}
                    result.add_error(
                        error_code,
                        f"Permit ID mismatch: expected {permit_mismatch.get('expected')}, got {permit_mismatch.get('actual')}",
                        f"PROHIBITED: Old permit detected. Use only the fixed-caliber permit: {permit_mismatch.get('expected')}"
                    )
                else:
                    result.add_error(
                        error_code,
                        f"Fixed-caliber validation failed: {error_details[0] if error_details else 'unknown'}",
                        "Ensure all paths match the fixed-caliber binding configuration"
                    )

                print(f"[AG-2]   Result: FAIL - {error_code}")
                return result
        else:
            print(f"[AG-2]   Result: PASS")
            print(f"[AG-2]   Fixed-caliber ID: {fixed_caliber_result.get('fixed_caliber_id')}")
    else:
        print(f"[AG-2] Stage 1.2: Fixed-caliber binding (SKIPPED - no config)")

    # Stage 1.5: Permit 哈希一致性校验 (固定单一口径)
    if not skip_three_hash:
        print(f"[AG-2] Stage 1.5: Validating permit hash consistency (固定单一口径)")

        # Require explicit three-rights paths for hash consistency check
        if demand_path is None or contract_path is None or decision_path is None:
            result.add_error(
                "SF_THREE_RIGHTS_PATHS_REQUIRED",
                "Permit hash consistency check requires explicit demand/contract/decision paths",
                "Re-run with --demand, --contract, --decision arguments to enforce single-caliber binding"
            )
            print(f"[AG-2]   Result: FAIL - Three-rights paths not explicitly provided")
            print(f"[AG-2]   ERROR: Fixed-caliber validation requires explicit path binding")
            return result

        # Verify all three-rights files exist
        for name, path in [("demand", demand_path), ("contract", contract_path), ("decision", decision_path)]:
            if not path.exists():
                result.add_error(
                    f"SF_{name.upper()}_MISSING",
                    f"{name.capitalize()} file not found: {path}",
                    f"Provide valid {name} file path or restore original three-rights files"
                )
                print(f"[AG-2]   Result: FAIL - {name.upper()}_MISSING")
                return result

        permit_hash_result = validate_permit_hash_consistency(
            permit_path, demand_path, contract_path, decision_path, keysets_path
        )

        if permit_hash_result["status"] != "PASS":
            error_code = permit_hash_result.get("error_code", "UNKNOWN")
            mismatches = permit_hash_result.get("mismatch_details", [])

            result.permit_hash_consistency_result = {
                "status": "FAIL",
                "error_code": error_code,
                "permit_hashes": permit_hash_result.get("permit_hashes", {}),
                "computed_hashes": permit_hash_result.get("computed_hashes", {}),
                "mismatch_details": mismatches,
            }

            # Build detailed error message
            mismatch_fields = [m["field"] for m in mismatches]
            result.add_error(
                error_code,
                f"Permit hash mismatch: {', '.join(mismatch_fields)}",
                "FIXED-CALIBER VIOLATION: Permit hashes must match actual three-rights files. "
                "Option A: Re-sign permit with current three-rights files. "
                "Option B: Restore original three-rights files that match the permit."
            )

            print(f"[AG-2]   Result: FAIL - {error_code}")
            print(f"[AG-2]   Mismatched fields: {', '.join(mismatch_fields)}")
            for m in mismatches:
                print(f"[AG-2]     {m['field']}:")
                print(f"[AG-2]       permit:  {m['permit_hash'][:16]}...")
                print(f"[AG-2]       actual:  {m['actual_hash'][:16]}...")
            return result
        else:
            result.permit_hash_consistency_result = {
                "status": "PASS",
                "permit_hashes": permit_hash_result.get("permit_hashes", {}),
                "computed_hashes": permit_hash_result.get("computed_hashes", {}),
                "mismatch_details": [],
            }
            print(f"[AG-2]   Result: PASS")
            print(f"[AG-2]   Fixed-caliber binding verified: permit matches three-rights files")

    # Stage 2: Delivery 六件套校验
    print(f"[AG-2] Stage 2: Validating delivery completeness (六件套校验)")
    print(f"[AG-2]   Base path: {base_path}")

    delivery_result = validate_delivery_completeness(base_path)
    result.delivery_completeness_result = {
        "status": delivery_result["status"],
        "error_code": delivery_result.get("error_code"),
        "missing_items": delivery_result.get("missing_items", []),
        "present_items": delivery_result.get("present_items", []),
    }

    if delivery_result["status"] != "PASS":
        error_code = delivery_result.get("error_code", "UNKNOWN")
        missing_items = delivery_result.get("missing_items", [])
        required_changes = delivery_result.get("required_changes", [])

        result.add_error(
            error_code,
            f"Delivery incomplete: missing {len(missing_items)} items",
            f"Add missing delivery items: {'; '.join(required_changes)}"
        )

        print(f"[AG-2]   Result: FAIL - {error_code}")
        return result

    print(f"[AG-2]   Result: PASS")
    print(f"[AG-2]   Present items: {', '.join([i['category'] for i in delivery_result['present_items']])}")

    # Stage 3: Three-Hash Guard 总门禁
    if skip_three_hash:
        print(f"[AG-2] Stage 3: Three-hash consistency check (SKIPPED)")
    else:
        print(f"[AG-2] Stage 3: Validating three-hash consistency (三哈希总门禁)")

        # Infer paths from permit if not provided
        if permit_path.exists():
            permit_data = json.loads(permit_path.read_text(encoding="utf-8"))

            # Try to find related files based on permit location
            permit_dir = permit_path.parent
            project_root = permit_dir.parent.parent  # permits/{task}/permit.json -> project root

            if demand_path is None:
                demand_path = project_root / "docs" / "2026-02-22" / "量化" / "demand.json"
            if contract_path is None:
                contract_path = project_root / "contracts" / "dsl" / "contract.yml"
            if decision_path is None:
                decision_path = project_root / "artifacts" / "decision.json"
            if manifest_path is None:
                # Look for MANIFEST.json in artifacts or permits dir
                manifest_path = permit_dir / "MANIFEST.json"
                if not manifest_path.exists():
                    manifest_path = project_root / "artifacts" / "MANIFEST.json"

        # Validate three-hash consistency
        print(f"[AG-2]   Demand: {demand_path}")
        print(f"[AG-2]   Contract: {contract_path}")
        print(f"[AG-2]   Decision: {decision_path}")
        print(f"[AG-2]   Manifest: {manifest_path}")
        print(f"[AG-2]   Keysets: {keysets_path}")

        three_hash_result = validate_three_hash_consistency(
            demand_path, contract_path, decision_path, manifest_path, keysets_path
        )
        result.three_hash_result = {
            "status": three_hash_result["status"],
            "error_code": three_hash_result.get("error_code"),
            "error_details": three_hash_result.get("error_details", []),
            "computed_hashes": three_hash_result.get("computed_hashes", {}),
            "manifest_hashes": three_hash_result.get("manifest_hashes", {}),
        }

        if three_hash_result["status"] != "PASS":
            error_code = three_hash_result.get("error_code", "UNKNOWN")
            error_details = three_hash_result.get("error_details", [])

            if error_code == "SF_THREE_HASH_MISMATCH":
                mismatch_desc = ", ".join([e["field"] for e in error_details])
                result.add_error(
                    error_code,
                    f"Three-hash mismatch: {mismatch_desc}",
                    "Regenerate manifest with correct hashes from demand/contract/decision files"
                )
            else:
                result.add_error(
                    error_code,
                    f"Three-hash validation failed: {error_details[0] if error_details else 'unknown'}",
                    "Ensure demand, contract, decision, and manifest files exist and are valid"
                )

            print(f"[AG-2]   Result: FAIL - {error_code}")
            return result

        print(f"[AG-2]   Result: PASS")
        print(f"[AG-2]   Hashes match: demand_hash, contract_hash, decision_hash")

    # All stages passed
    result.set_allow()
    return result


def main() -> int:
    """CLI entry point for Antigravity-2 guard."""
    parser = argparse.ArgumentParser(
        description="Antigravity-2 Compliance Guard - Permit + Delivery + Three-Hash (FAIL-CLOSED)"
    )
    parser.add_argument(
        "--permit",
        type=Path,
        required=True,
        help="Path to permit JSON file",
    )
    parser.add_argument(
        "--demand",
        type=Path,
        help="Path to demand JSON file (auto-detected if not provided)",
    )
    parser.add_argument(
        "--contract",
        type=Path,
        help="Path to contract JSON/YAML file (auto-detected if not provided)",
    )
    parser.add_argument(
        "--decision",
        type=Path,
        help="Path to decision JSON file (auto-detected if not provided)",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        help="Path to manifest JSON file (auto-detected if not provided)",
    )
    parser.add_argument(
        "--base-path",
        type=Path,
        default=Path.cwd(),
        help="Base path for delivery completeness check (default: current directory)",
    )
    parser.add_argument(
        "--keysets",
        type=Path,
        default=Path("orchestration/hash_keysets.yml"),
        help="Path to hash keysets YAML file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write guard decision to file (JSON format)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only output decision (ALLOW/DENY)",
    )
    parser.add_argument(
        "--skip-three-hash",
        action="store_true",
        help="Skip three-hash consistency check",
    )
    args = parser.parse_args()

    # Run guard
    print("=" * 60)
    print(f"[AG-2] Antigravity-2 Compliance Guard")
    print(f"[AG-2] Started at {datetime.now(UTC).isoformat()}")
    print("=" * 60)

    result = run_antigravity_2_guard(
        permit_path=args.permit,
        demand_path=args.demand,
        contract_path=args.contract,
        decision_path=args.decision,
        manifest_path=args.manifest,
        base_path=args.base_path,
        keysets_path=args.keysets,
        skip_three_hash=args.skip_three_hash,
    )

    print("=" * 60)
    print(f"[AG-2] Final Decision: {result.status.value}")
    print("=" * 60)

    if result.status == GuardDecision.DENY:
        print(f"\n[AG-2] DENY - Compliance check failed")
        print(f"[AG-2] Error code: {result.error_code}")
        print(f"\n[AG-2] Errors ({len(result.errors)}):")
        for e in result.errors:
            print(f"  [{e['code']}] {e['message']}")
        print(f"\n[AG-2] Required changes ({len(result.required_changes)}):")
        for i, c in enumerate(result.required_changes, 1):
            print(f"  {i}. {c}")
    else:
        print(f"\n[AG-2] ALLOW - All compliance checks passed")
        print(f"[AG-2] ✓ Permit binding (5 fields)")
        print(f"[AG-2] ✓ Delivery completeness (6 items)")
        if not args.skip_three_hash:
            print(f"[AG-2] ✓ Three-hash consistency")

    # Write output file if requested
    if args.output:
        output_data = {
            "decision": result.status.value,
            "error_code": result.error_code,
            "errors": result.errors,
            "required_changes": result.required_changes,
            "permit_binding": result.permit_binding_result,
            "fixed_caliber_binding": result.fixed_caliber_binding_result,
            "permit_hash_consistency": result.permit_hash_consistency_result,
            "delivery_completeness": result.delivery_completeness_result,
            "three_hash": result.three_hash_result,
            "checked_at": result.checked_at,
            "guard_version": "Antigravity-2",
            "execution_environment": "LOCAL-ANTIGRAVITY",
            "fail_closed_policy": True,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(output_data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n[AG-2] Decision written to: {args.output}")

    if args.quiet:
        print(result.status.value)

    return 0 if result.status == GuardDecision.ALLOW else 1


if __name__ == "__main__":
    sys.exit(main())
