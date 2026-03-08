#!/usr/bin/env python3
"""
Guard Signature Verification Script
T70: 落实 guard_signature 校验

This script verifies digital signatures for execution reports and gate decisions
to ensure integrity and authenticity of guard artifacts.

Usage:
    python scripts/verify_guard_signature.py --verify-all --report <report_path>
    python scripts/verify_guard_signature.py --file <file_path> --verify
    python scripts/verify_guard_signature.py --sign <file_path> --key <key>

Exit codes:
    0 - All signatures valid
    1 - Some signatures invalid (report generated)
    2 - Error during execution
"""

import argparse
import hashlib
import hmac
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yaml


# Configuration
VERIFICATION_DIR = Path("docs/2026-02-22/verification")
REPORT_PATTERNS = ["*_execution_report.yaml", "*_gate_decision.json", "*_compliance_attestation.json"]
SIGNATURE_FIELD = "guard_signature"
SIGNER_ID_FIELD = "signer_id"
SIGNATURE_ALGORITHM = "HMAC-SHA256"

# L4-SKILL-07: Allowed signer_id list (Fail-Closed)
# These are the only authorized signers for guard artifacts
ALLOWED_SIGNER_IDS = {
    "Antigravity-1",   # Execution role
    "Antigravity-2",   # Review role
    "Kior-C",          # Compliance role
    "Codex",           # Orchestrator role
    "vs--cc2",         # Execution agent
    "vs--cc3"          # Execution agent
}

# Alert codes for signature verification
ALERT_MISSING_SIGNATURE = "MISSING_CRYPTO_SIGNATURE"
ALERT_SIGNATURE_MISMATCH = "SIGNATURE_MISMATCH"
ALERT_INVALID_SIGNER_ID = "INVALID_SIGNER_ID"
ALERT_MISSING_SIGNER_ID = "MISSING_SIGNER_ID"

# Get signing key from environment or use default for development
def get_signing_key() -> bytes:
    """Get the signing key from environment variable or default."""
    key = os.environ.get("GUARD_SIGNATURE_KEY", "skillforge-guard-default-key-2026")
    return key.encode("utf-8")


def compute_signature(content: str, key: bytes) -> str:
    """Compute HMAC-SHA256 signature for content."""
    return hmac.new(key, content.encode("utf-8"), hashlib.sha256).hexdigest()


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of file content."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def validate_signer_id(signer_id: Optional[str]) -> Tuple[bool, str]:
    """
    L4-SKILL-07: Validate signer_id against allowed list.
    Returns: (is_valid, message)
    """
    if signer_id is None:
        return False, "No signer_id field found"

    if signer_id not in ALLOWED_SIGNER_IDS:
        return False, f"Invalid signer_id '{signer_id}' (not in allowed list)"

    return True, f"Signer_id '{signer_id}' is valid"


def get_allowed_signer_ids() -> set:
    """Return the set of allowed signer IDs."""
    return ALLOWED_SIGNER_IDS.copy()


def load_yaml_file(file_path: Path) -> Optional[Dict]:
    """Load YAML file safely."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load YAML {file_path}: {e}")
        return None


def load_json_file(file_path: Path) -> Optional[Dict]:
    """Load JSON file safely."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load JSON {file_path}: {e}")
        return None


def verify_yaml_signature(file_path: Path, key: bytes) -> Tuple[bool, str, Optional[str]]:
    """
    Verify signature of a YAML execution report.
    Returns: (is_valid, message, existing_signature)
    """
    data = load_yaml_file(file_path)
    if data is None:
        return False, "Failed to load file", None

    # Get existing signature if present
    existing_sig = data.get(SIGNATURE_FIELD)
    if not existing_sig:
        return False, "No signature field found", None

    # Read raw content for signature verification
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove signature for verification (consistent with sign function)
    clean_content = _remove_signature_from_content(content)
    expected_sig = compute_signature(clean_content, key)

    if hmac.compare_digest(expected_sig, existing_sig):
        return True, "Signature valid", existing_sig
    else:
        return False, f"Signature mismatch (expected: {expected_sig[:16]}..., got: {existing_sig[:16]}...)", existing_sig


def verify_yaml_signature_with_signer(file_path: Path, key: bytes) -> Tuple[bool, str, Optional[str], Optional[str]]:
    """
    L4-SKILL-07: Verify signature and signer_id of a YAML file.
    Returns: (is_valid, message, existing_signature, signer_id)
    """
    data = load_yaml_file(file_path)
    if data is None:
        return False, "Failed to load file", None, None

    # Get signer_id
    signer_id = data.get(SIGNER_ID_FIELD)

    # Get existing signature if present
    existing_sig = data.get(SIGNATURE_FIELD)
    if not existing_sig:
        return False, "No signature field found", None, signer_id

    # Validate signer_id (L4-SKILL-07 requirement)
    signer_valid, signer_msg = validate_signer_id(signer_id)
    if not signer_valid:
        return False, signer_msg, existing_sig, signer_id

    # Read raw content for signature verification
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove signature for verification (consistent with sign function)
    clean_content = _remove_signature_from_content(content)
    expected_sig = compute_signature(clean_content, key)

    if hmac.compare_digest(expected_sig, existing_sig):
        return True, "Signature valid", existing_sig, signer_id
    else:
        return False, f"Signature mismatch (expected: {expected_sig[:16]}..., got: {existing_sig[:16]}...)", existing_sig, signer_id


def verify_json_signature(file_path: Path, key: bytes) -> Tuple[bool, str, Optional[str]]:
    """
    Verify signature of a JSON file.
    Returns: (is_valid, message, existing_signature)
    """
    data = load_json_file(file_path)
    if data is None:
        return False, "Failed to load file", None

    # Get existing signature if present
    existing_sig = data.get(SIGNATURE_FIELD)
    if not existing_sig:
        return False, "No signature field found", None

    # Create content without signature for verification
    data_copy = {k: v for k, v in data.items() if k != SIGNATURE_FIELD}
    content = json.dumps(data_copy, sort_keys=True, indent=2)

    expected_sig = compute_signature(content, key)

    if hmac.compare_digest(expected_sig, existing_sig):
        return True, "Signature valid", existing_sig
    else:
        return False, f"Signature mismatch (expected: {expected_sig[:16]}..., got: {existing_sig[:16]}...)", existing_sig


def verify_json_signature_with_signer(file_path: Path, key: bytes) -> Tuple[bool, str, Optional[str], Optional[str]]:
    """
    L4-SKILL-07: Verify signature and signer_id of a JSON file.
    Returns: (is_valid, message, existing_signature, signer_id)
    """
    data = load_json_file(file_path)
    if data is None:
        return False, "Failed to load file", None, None

    # Get signer_id
    signer_id = data.get(SIGNER_ID_FIELD)

    # Get existing signature if present
    existing_sig = data.get(SIGNATURE_FIELD)
    if not existing_sig:
        return False, "No signature field found", None, signer_id

    # Validate signer_id (L4-SKILL-07 requirement)
    signer_valid, signer_msg = validate_signer_id(signer_id)
    if not signer_valid:
        return False, signer_msg, existing_sig, signer_id

    # Create content without signature for verification
    data_copy = {k: v for k, v in data.items() if k not in [SIGNATURE_FIELD, SIGNER_ID_FIELD]}
    content = json.dumps(data_copy, sort_keys=True, indent=2)

    expected_sig = compute_signature(content, key)

    if hmac.compare_digest(expected_sig, existing_sig):
        return True, "Signature valid", existing_sig, signer_id
    else:
        return False, f"Signature mismatch (expected: {expected_sig[:16]}..., got: {existing_sig[:16]}...)", existing_sig, signer_id


def _remove_signature_from_content(content: str) -> str:
    """Remove signature lines from content for consistent signing/verifying."""
    lines = content.split("\n")
    content_without_sig = []
    in_signature = False
    for line in lines:
        if line.startswith(f"{SIGNATURE_FIELD}:"):
            in_signature = True
            continue
        if in_signature and line.startswith(" "):
            continue
        in_signature = False
        content_without_sig.append(line)
    return "\n".join(content_without_sig).strip()


def sign_yaml_file(file_path: Path, key: bytes) -> bool:
    """Add signature to a YAML file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check if signature already exists
        if SIGNATURE_FIELD + ":" in content:
            print(f"[WARN] {file_path} already has signature, updating...")

        # Remove existing signature before computing new one (consistent with verify)
        clean_content = _remove_signature_from_content(content)

        # Compute signature on content without signature
        signature = compute_signature(clean_content, key)

        # Append signature
        new_content = clean_content + f"\n\n{SIGNATURE_FIELD}: \"{signature}\"\n"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"[OK] Signed {file_path}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to sign {file_path}: {e}")
        return False


def sign_json_file(file_path: Path, key: bytes) -> bool:
    """Add signature to a JSON file."""
    try:
        data = load_json_file(file_path)
        if data is None:
            return False

        # Compute signature on content without signature field
        data_copy = {k: v for k, v in data.items() if k != SIGNATURE_FIELD}
        content = json.dumps(data_copy, sort_keys=True, indent=2)
        signature = compute_signature(content, key)

        # Add signature
        data[SIGNATURE_FIELD] = signature

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print(f"[OK] Signed {file_path}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to sign {file_path}: {e}")
        return False


def find_report_files(directory: Path) -> List[Path]:
    """Find all report files matching patterns."""
    files = []
    for pattern in REPORT_PATTERNS:
        files.extend(directory.glob(pattern))
    return sorted(set(files))


def verify_file_crypto_signature(file_path: Path, key: bytes) -> Dict:
    """
    L4-SKILL-07: Comprehensive crypto signature verification.
    Returns a dict with detailed verification results for use by aggregate_final_gate.py.

    Returns:
        {
            "file": str,
            "has_signature": bool,
            "signature_valid": bool,
            "signer_id": Optional[str],
            "signer_valid": bool,
            "status": "VALID" | "NO_SIGNATURE" | "SIGNATURE_INVALID" | "SIGNER_INVALID",
            "message": str,
            "alert_code": Optional[str]
        }
    """
    result = {
        "file": str(file_path),
        "has_signature": False,
        "signature_valid": False,
        "signer_id": None,
        "signer_valid": False,
        "status": "UNKNOWN",
        "message": "",
        "alert_code": None
    }

    if file_path.suffix == ".yaml":
        is_valid, message, sig, signer_id = verify_yaml_signature_with_signer(file_path, key)
    else:
        is_valid, message, sig, signer_id = verify_json_signature_with_signer(file_path, key)

    result["signer_id"] = signer_id

    if "No signature field" in message:
        result["has_signature"] = False
        result["status"] = "NO_SIGNATURE"
        result["message"] = "Missing guard_signature field"
        result["alert_code"] = ALERT_MISSING_SIGNATURE
    elif "No signer_id" in message or "Invalid signer_id" in message:
        result["has_signature"] = True
        result["signature_valid"] = is_valid
        result["signer_valid"] = False
        result["status"] = "SIGNER_INVALID"
        result["message"] = message
        result["alert_code"] = ALERT_INVALID_SIGNER_ID if "Invalid" in message else ALERT_MISSING_SIGNER_ID
    elif is_valid:
        result["has_signature"] = True
        result["signature_valid"] = True
        result["signer_valid"] = True
        result["status"] = "VALID"
        result["message"] = "Crypto signature and signer_id valid"
        result["alert_code"] = None
    else:
        result["has_signature"] = True
        result["signature_valid"] = False
        result["signer_valid"] = True  # signer_id was valid, signature was not
        result["status"] = "SIGNATURE_INVALID"
        result["message"] = message
        result["alert_code"] = ALERT_SIGNATURE_MISMATCH

    return result


def verify_triad_crypto_signatures(task_id: str, verification_dir: Path, key: bytes) -> Dict:
    """
    L4-SKILL-07: Verify crypto signatures for all triad files of a task.
    Returns aggregated verification result.

    Returns:
        {
            "task_id": str,
            "all_valid": bool,
            "has_missing_signature": bool,
            "has_invalid_signature": bool,
            "has_invalid_signer": bool,
            "files": [verify_file_crypto_signature results],
            "decision": "ALLOW" | "DENY" | "REQUIRES_CHANGES",
            "alert_codes": [str]
        }
    """
    triad_files = [
        verification_dir / f"{task_id}_execution_report.yaml",
        verification_dir / f"{task_id}_gate_decision.json",
        verification_dir / f"{task_id}_compliance_attestation.json"
    ]

    results = {
        "task_id": task_id,
        "all_valid": True,
        "has_missing_signature": False,
        "has_invalid_signature": False,
        "has_invalid_signer": False,
        "files": [],
        "decision": "ALLOW",
        "alert_codes": []
    }

    for file_path in triad_files:
        if not file_path.exists():
            results["all_valid"] = False
            results["files"].append({
                "file": str(file_path),
                "status": "FILE_NOT_FOUND",
                "message": f"File not found: {file_path}"
            })
            continue

        file_result = verify_file_crypto_signature(file_path, key)
        results["files"].append(file_result)

        if file_result["status"] == "NO_SIGNATURE":
            results["has_missing_signature"] = True
            results["all_valid"] = False
        elif file_result["status"] == "SIGNATURE_INVALID":
            results["has_invalid_signature"] = True
            results["all_valid"] = False
        elif file_result["status"] == "SIGNER_INVALID":
            results["has_invalid_signer"] = True
            results["all_valid"] = False

        if file_result["alert_code"]:
            results["alert_codes"].append(file_result["alert_code"])

    # L4-SKILL-07 Fail-Closed decision logic
    if results["has_invalid_signature"] or results["has_invalid_signer"]:
        results["decision"] = "DENY"
    elif results["has_missing_signature"]:
        results["decision"] = "REQUIRES_CHANGES"
    else:
        results["decision"] = "ALLOW"

    return results


def verify_all_reports(directory: Path, key: bytes) -> Dict:
    """Verify all report files in directory."""
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "directory": str(directory),
        "algorithm": SIGNATURE_ALGORITHM,
        "files_checked": 0,
        "files_valid": 0,
        "files_invalid": 0,
        "files_no_signature": 0,
        "details": []
    }

    files = find_report_files(directory)

    for file_path in files:
        results["files_checked"] += 1
        detail = {
            "file": str(file_path),
            "type": "yaml" if file_path.suffix == ".yaml" else "json",
            "sha256": compute_file_hash(file_path),
            "status": "UNKNOWN",
            "message": "",
            "signature": None
        }

        if file_path.suffix == ".yaml":
            is_valid, message, sig = verify_yaml_signature(file_path, key)
        else:
            is_valid, message, sig = verify_json_signature(file_path, key)

        detail["message"] = message
        detail["signature"] = sig

        if "No signature field" in message:
            detail["status"] = "NO_SIGNATURE"
            results["files_no_signature"] += 1
        elif is_valid:
            detail["status"] = "VALID"
            results["files_valid"] += 1
        else:
            detail["status"] = "INVALID"
            results["files_invalid"] += 1

        results["details"].append(detail)

    # Calculate pass rate
    if results["files_checked"] > 0:
        results["pass_rate"] = results["files_valid"] / results["files_checked"] * 100
    else:
        results["pass_rate"] = 0.0

    return results


def generate_report(results: Dict, output_path: Path) -> bool:
    """Generate verification report."""
    try:
        # Add metadata
        report = {
            "report_type": "GUARD_SIGNATURE_VERIFICATION",
            "task_id": "T70",
            "executor": "Antigravity-1",
            "generated_at": datetime.now(timezone.utc).isoformat() + "Z",
            "summary": {
                "total_files": results["files_checked"],
                "valid": results["files_valid"],
                "invalid": results["files_invalid"],
                "no_signature": results["files_no_signature"],
                "pass_rate_percent": round(results["pass_rate"], 2)
            },
            "verification_details": results["details"]
        }

        # Compute signature for the report itself
        key = get_signing_key()
        content = json.dumps(report, sort_keys=True, indent=2)
        report[SIGNATURE_FIELD] = compute_signature(content, key)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"[OK] Report generated: {output_path}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to generate report: {e}")
        return False


def print_summary(results: Dict):
    """Print verification summary."""
    print("\n" + "=" * 60)
    print("GUARD SIGNATURE VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"Timestamp: {results['timestamp']}")
    print(f"Directory: {results['directory']}")
    print(f"Algorithm: {results['algorithm']}")
    print("-" * 60)
    print(f"Files checked:    {results['files_checked']}")
    print(f"Valid signatures: {results['files_valid']}")
    print(f"Invalid signatures: {results['files_invalid']}")
    print(f"No signature:     {results['files_no_signature']}")
    print(f"Pass rate:        {results['pass_rate']:.2f}%")
    print("=" * 60)

    if results["files_invalid"] > 0:
        print("\nINVALID FILES:")
        for detail in results["details"]:
            if detail["status"] == "INVALID":
                print(f"  - {detail['file']}: {detail['message']}")

    if results["files_no_signature"] > 0:
        print("\nFILES WITHOUT SIGNATURE:")
        for detail in results["details"]:
            if detail["status"] == "NO_SIGNATURE":
                print(f"  - {detail['file']}")


def main():
    parser = argparse.ArgumentParser(
        description="Guard Signature Verification Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "--verify-all",
        action="store_true",
        help="Verify all report files in verification directory"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Single file to verify or sign"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify the file specified by --file"
    )
    parser.add_argument(
        "--sign",
        action="store_true",
        help="Sign the file specified by --file"
    )
    parser.add_argument(
        "--report",
        type=str,
        help="Path to output verification report"
    )
    parser.add_argument(
        "--directory",
        type=str,
        default=str(VERIFICATION_DIR),
        help=f"Directory to scan for reports (default: {VERIFICATION_DIR})"
    )
    parser.add_argument(
        "--key",
        type=str,
        help="Signing key (overrides GUARD_SIGNATURE_KEY env var)"
    )

    args = parser.parse_args()

    # Get signing key
    if args.key:
        key = args.key.encode("utf-8")
    else:
        key = get_signing_key()

    # Verify all reports
    if args.verify_all:
        directory = Path(args.directory)
        if not directory.exists():
            print(f"[ERROR] Directory not found: {directory}")
            sys.exit(2)

        results = verify_all_reports(directory, key)
        print_summary(results)

        # Generate report if requested
        if args.report:
            generate_report(results, Path(args.report))

        # Exit with appropriate code
        if results["files_invalid"] > 0:
            sys.exit(1)
        else:
            sys.exit(0)

    # Single file operations
    elif args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"[ERROR] File not found: {file_path}")
            sys.exit(2)

        if args.verify:
            if file_path.suffix == ".yaml":
                is_valid, message, _ = verify_yaml_signature(file_path, key)
            else:
                is_valid, message, _ = verify_json_signature(file_path, key)

            if is_valid:
                print(f"[OK] {file_path}: {message}")
                sys.exit(0)
            else:
                print(f"[FAIL] {file_path}: {message}")
                sys.exit(1)

        elif args.sign:
            if file_path.suffix == ".yaml":
                success = sign_yaml_file(file_path, key)
            else:
                success = sign_json_file(file_path, key)

            sys.exit(0 if success else 2)

        else:
            print("[ERROR] Specify --verify or --sign for single file operations")
            sys.exit(2)

    else:
        parser.print_help()
        sys.exit(2)


if __name__ == "__main__":
    main()
