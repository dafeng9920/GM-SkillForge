#!/usr/bin/env python3
"""
Third-Party Evidence Verification Script (T11 - ISSUE-10)

This is a standalone script that allows ANY third party to independently verify
the authenticity of a SkillForge evidence package using ONLY:
1. The evidence package (JSON file)
2. The node's public key (hex string or PEM file)

No internal SkillForge dependencies required - only standard Python crypto libraries.

Verification Steps:
1. Schema Validation - Verify envelope structure
2. Signature Verification - Verify Ed25519 signature against public key
3. Timestamp Validation - Verify evidence is not expired
4. Nonce Validation - Verify nonce challenge response (if present)
5. Hash Verification - Verify body hash matches content

Usage:
    python verify_evidence.py --package evidence.json --pubkey <hex_or_pem>

Examples:
    # Verify with hex public key
    python verify_evidence.py --package sample_evidence.json --pubkey abc123def456...

    # Verify with PEM file
    python verify_evidence.py --package sample_evidence.json --pubkey node_public.pem

    # Verbose output
    python verify_evidence.py --package sample_evidence.json --pubkey abc123... --verbose

Executor: Kior-B
Task: T11 - ISSUE-10: 第三方可验证最小演示
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union, Any

# Try to import cryptography (required for signature verification)
try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives import serialization
    from cryptography.exceptions import InvalidSignature
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    ed25519 = None
    InvalidSignature = Exception


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class VerificationResult:
    """Result of a single verification step."""
    step: str
    passed: bool
    message: str
    details: Optional[dict] = None


@dataclass
class OverallResult:
    """Overall verification result."""
    valid: bool
    steps: list[VerificationResult]
    summary: str
    evidence_id: Optional[str] = None
    node_id: Optional[str] = None
    verified_at: Optional[str] = None


# ============================================================================
# Verification Functions
# ============================================================================

def load_public_key(pubkey_input: str) -> ed25519.Ed25519PublicKey:
    """
    Load Ed25519 public key from hex string or PEM file.

    Args:
        pubkey_input: Either a hex string (64 chars) or path to PEM file

    Returns:
        Ed25519PublicKey object

    Raises:
        ValueError: If key cannot be loaded
    """
    if not CRYPTOGRAPHY_AVAILABLE:
        raise RuntimeError(
            "cryptography library required. Install with: pip install cryptography"
        )

    # Check if it's a file path
    pubkey_path = Path(pubkey_input)
    if pubkey_path.exists() and pubkey_path.is_file():
        with open(pubkey_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        # Check if it's a PEM file
        if content.startswith('-----BEGIN'):
            try:
                return serialization.load_pem_public_key(content.encode('utf-8'))
            except Exception as e:
                raise ValueError(f"Failed to load PEM public key: {e}")
        else:
            # Treat file content as hex string
            pubkey_input = content

    # Treat as hex string
    try:
        # Remove any whitespace or 0x prefix
        hex_str = pubkey_input.strip().lower()
        if hex_str.startswith('0x'):
            hex_str = hex_str[2:]

        key_bytes = bytes.fromhex(hex_str)
        if len(key_bytes) != 32:
            raise ValueError(f"Invalid public key length: expected 32 bytes, got {len(key_bytes)}")

        return ed25519.Ed25519PublicKey.from_public_bytes(key_bytes)
    except ValueError:
        raise ValueError(
            f"Invalid public key format. Expected 64-char hex string or PEM file path. "
            f"Got: {pubkey_input[:20]}..."
        )


def load_evidence_package(package_input: str) -> dict:
    """
    Load evidence package from JSON file or JSON string.

    Args:
        package_input: Path to JSON file or JSON string

    Returns:
        Parsed evidence package dict

    Raises:
        ValueError: If package cannot be loaded or parsed
    """
    package_path = Path(package_input)

    if package_path.exists() and package_path.is_file():
        with open(package_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = package_input

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse evidence package: {e}")


def canonical_json_hash(obj: Any) -> str:
    """
    Compute canonical JSON hash (SHA-256).

    This follows the same rules as SkillForge's canonical_json_hash:
    - Keys sorted alphabetically
    - No extra whitespace
    - UTF-8 encoding
    """
    def sort_keys(o):
        if isinstance(o, dict):
            return {k: sort_keys(v) for k, v in sorted(o.items())}
        elif isinstance(o, list):
            return [sort_keys(item) for item in o]
        return o

    canonical = json.dumps(sort_keys(obj), separators=(',', ':'), ensure_ascii=False)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


# ============================================================================
# Verification Steps
# ============================================================================

def verify_schema(package: dict) -> VerificationResult:
    """
    Step 1: Verify envelope schema structure.

    Checks:
    - Required top-level fields: header, signature, cert
    - Required header fields: envelope_id, schema_version, created_at, node_id, body_hash
    - Signature has algorithm and signed_fields
    """
    errors = []

    # Top-level required fields
    required_top = ["header", "signature", "cert"]
    for field in required_top:
        if field not in package:
            errors.append(f"Missing required field: {field}")

    # Header required fields
    header = package.get("header", {})
    required_header = ["envelope_id", "schema_version", "created_at", "node_id", "body_hash"]
    for field in required_header:
        if field not in header:
            errors.append(f"Missing required header field: {field}")

    # Signature fields
    sig = package.get("signature", {})
    if "algorithm" not in sig:
        errors.append("Missing signature algorithm")
    if "signed_fields" not in sig:
        errors.append("Missing signed_fields in signature")

    if errors:
        return VerificationResult(
            step="schema_validation",
            passed=False,
            message=f"Schema validation failed with {len(errors)} errors",
            details={"errors": errors}
        )

    return VerificationResult(
        step="schema_validation",
        passed=True,
        message="Schema validation passed",
        details={
            "envelope_id": header.get("envelope_id"),
            "schema_version": header.get("schema_version"),
            "node_id": header.get("node_id"),
        }
    )


def verify_signature(package: dict, public_key: ed25519.Ed25519PublicKey) -> VerificationResult:
    """
    Step 2: Verify Ed25519 signature.

    This verifies that the signature was created by the holder of the private key
    corresponding to the provided public key.
    """
    try:
        sig = package.get("signature", {})
        header = package.get("header", {})

        signature_value = sig.get("value")
        if not signature_value:
            return VerificationResult(
                step="signature_verification",
                passed=False,
                message="No signature value found in package"
            )

        # Decode signature from base64
        try:
            signature_bytes = base64.b64decode(signature_value)
        except Exception as e:
            return VerificationResult(
                step="signature_verification",
                passed=False,
                message=f"Invalid signature encoding: {e}"
            )

        # Build the signed payload (canonical header + body_hash)
        # The signature covers: canonical(header) + body_hash
        signed_payload = canonical_json_hash(header).encode('utf-8')

        # Verify signature
        try:
            public_key.verify(signature_bytes, signed_payload)
            return VerificationResult(
                step="signature_verification",
                passed=True,
                message="Signature verification passed - evidence is authentic",
                details={
                    "algorithm": sig.get("algorithm", "Ed25519"),
                    "signed_fields": sig.get("signed_fields", []),
                    "signed_at": sig.get("signed_at"),
                }
            )
        except InvalidSignature:
            return VerificationResult(
                step="signature_verification",
                passed=False,
                message="SIGNATURE INVALID - evidence may have been tampered with or is not from the claimed node"
            )

    except Exception as e:
        return VerificationResult(
            step="signature_verification",
            passed=False,
            message=f"Signature verification error: {e}"
        )


def verify_timestamp(package: dict, tolerance_seconds: int = 300) -> VerificationResult:
    """
    Step 3: Verify timestamp validity.

    Checks:
    - created_at is a valid ISO-8601 timestamp
    - Evidence is not from the future (with tolerance)
    - Evidence has not expired (if expires_at is set)
    """
    try:
        header = package.get("header", {})
        created_at_str = header.get("created_at")
        expires_at_str = header.get("expires_at")

        if not created_at_str:
            return VerificationResult(
                step="timestamp_validation",
                passed=False,
                message="No created_at timestamp found"
            )

        # Parse ISO-8601 timestamp (simplified parsing)
        # Expected format: 2026-02-26T18:00:00Z
        try:
            # Remove Z suffix and parse
            created_str = created_at_str.rstrip('Z')
            created_at = time.mktime(time.strptime(created_str, "%Y-%m-%dT%H:%M:%S"))
        except ValueError as e:
            return VerificationResult(
                step="timestamp_validation",
                passed=False,
                message=f"Invalid timestamp format: {created_at_str}"
            )

        now = time.time()

        # Check if evidence is from the future (with tolerance)
        if created_at > now + tolerance_seconds:
            return VerificationResult(
                step="timestamp_validation",
                passed=False,
                message=f"Evidence timestamp is in the future: {created_at_str}"
            )

        # Check expiration
        if expires_at_str:
            try:
                expires_str = expires_at_str.rstrip('Z')
                expires_at = time.mktime(time.strptime(expires_str, "%Y-%m-%dT%H:%M:%S"))

                if now > expires_at:
                    return VerificationResult(
                        step="timestamp_validation",
                        passed=False,
                        message=f"EVIDENCE EXPIRED at {expires_at_str}"
                    )
            except ValueError:
                pass  # Ignore invalid expiration format

        # Calculate age
        age_seconds = int(now - created_at)
        age_human = f"{age_seconds // 3600}h {(age_seconds % 3600) // 60}m {age_seconds % 60}s"

        return VerificationResult(
            step="timestamp_validation",
            passed=True,
            message="Timestamp validation passed",
            details={
                "created_at": created_at_str,
                "expires_at": expires_at_str,
                "age": age_human,
                "age_seconds": age_seconds,
            }
        )

    except Exception as e:
        return VerificationResult(
            step="timestamp_validation",
            passed=False,
            message=f"Timestamp validation error: {e}"
        )


def verify_nonce(package: dict) -> VerificationResult:
    """
    Step 4: Verify nonce challenge response (if present).

    If the evidence includes a nonce, this verifies that the evidence
    was created in response to a challenge (not replayed from an old capture).

    Note: Full nonce validation requires the challenge store. This script
    only verifies the nonce is present and properly formatted.
    """
    try:
        header = package.get("header", {})
        nonce = header.get("nonce")

        if not nonce:
            # No nonce present - this is acceptable for some evidence types
            return VerificationResult(
                step="nonce_validation",
                passed=True,
                message="No nonce present (acceptable for non-challenge evidence)"
            )

        # Verify nonce format (should be hex string, typically 32 bytes)
        try:
            nonce_bytes = bytes.fromhex(nonce)
            if len(nonce_bytes) < 16:
                return VerificationResult(
                    step="nonce_validation",
                    passed=False,
                    message=f"Nonce too short: {len(nonce_bytes)} bytes (minimum 16)"
                )
        except ValueError:
            return VerificationResult(
                step="nonce_validation",
                passed=False,
                message="Invalid nonce format (expected hex string)"
            )

        return VerificationResult(
            step="nonce_validation",
            passed=True,
            message="Nonce validation passed",
            details={
                "nonce_length": len(nonce_bytes),
                "nonce_preview": nonce[:16] + "..." if len(nonce) > 16 else nonce,
            }
        )

    except Exception as e:
        return VerificationResult(
            step="nonce_validation",
            passed=False,
            message=f"Nonce validation error: {e}"
        )


def verify_body_hash(package: dict) -> VerificationResult:
    """
    Step 5: Verify body hash integrity.

    If the package contains a plaintext body, verifies that the body_hash
    in the header matches the actual body content.
    """
    try:
        header = package.get("header", {})
        expected_hash = header.get("body_hash")
        body = package.get("body")

        if not expected_hash:
            return VerificationResult(
                step="body_hash_verification",
                passed=False,
                message="No body_hash found in header"
            )

        if body is None:
            # Encrypted envelope - cannot verify body hash without decryption
            return VerificationResult(
                step="body_hash_verification",
                passed=True,
                message="Body is encrypted - hash verification skipped (verify via signature)"
            )

        # Compute actual hash
        actual_hash = canonical_json_hash(body)

        if actual_hash == expected_hash:
            return VerificationResult(
                step="body_hash_verification",
                passed=True,
                message="Body hash verification passed - content is intact",
                details={
                    "expected_hash": expected_hash[:32] + "...",
                    "actual_hash": actual_hash[:32] + "...",
                }
            )
        else:
            return VerificationResult(
                step="body_hash_verification",
                passed=False,
                message="BODY HASH MISMATCH - content may have been modified",
                details={
                    "expected_hash": expected_hash,
                    "actual_hash": actual_hash,
                }
            )

    except Exception as e:
        return VerificationResult(
            step="body_hash_verification",
            passed=False,
            message=f"Body hash verification error: {e}"
        )


# ============================================================================
# Main Verification Function
# ============================================================================

def verify_evidence(
    package: dict,
    public_key: ed25519.Ed25519PublicKey,
    verbose: bool = False,
) -> OverallResult:
    """
    Perform full evidence verification.

    Runs all verification steps and returns overall result.
    """
    steps = [
        verify_schema(package),
        verify_signature(package, public_key),
        verify_timestamp(package),
        verify_nonce(package),
        verify_body_hash(package),
    ]

    # Overall result is valid only if ALL steps pass
    all_passed = all(step.passed for step in steps)

    # Extract metadata
    header = package.get("header", {})
    evidence_id = header.get("envelope_id")
    node_id = header.get("node_id")
    verified_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    if all_passed:
        summary = f"✅ EVIDENCE VALID - All verification steps passed for {evidence_id}"
    else:
        failed_steps = [s.step for s in steps if not s.passed]
        summary = f"❌ EVIDENCE INVALID - Failed steps: {', '.join(failed_steps)}"

    return OverallResult(
        valid=all_passed,
        steps=steps,
        summary=summary,
        evidence_id=evidence_id,
        node_id=node_id,
        verified_at=verified_at,
    )


def print_result(result: OverallResult, verbose: bool = False):
    """Print verification result to stdout."""
    print("\n" + "=" * 60)
    print("SkillForge Evidence Verification Report")
    print("=" * 60)

    print(f"\nEvidence ID: {result.evidence_id or 'Unknown'}")
    print(f"Node ID: {result.node_id or 'Unknown'}")
    print(f"Verified At: {result.verified_at or 'Unknown'}")

    print("\n" + "-" * 60)
    print("Verification Steps:")
    print("-" * 60)

    for step in result.steps:
        status = "✅ PASS" if step.passed else "❌ FAIL"
        print(f"\n{step.step}: {status}")
        print(f"  {step.message}")

        if verbose and step.details:
            for key, value in step.details.items():
                print(f"    {key}: {value}")

    print("\n" + "=" * 60)
    print(result.summary)
    print("=" * 60 + "\n")

    return result.valid


# ============================================================================
# CLI Entry Point
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Third-Party Evidence Verification Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --package evidence.json --pubkey abc123def456...
  %(prog)s --package evidence.json --pubkey node_public.pem --verbose
        """
    )

    parser.add_argument(
        "--package", "-p",
        required=True,
        help="Path to evidence package JSON file or JSON string"
    )

    parser.add_argument(
        "--pubkey", "-k",
        required=True,
        help="Public key (64-char hex string) or path to PEM file"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )

    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Only output pass/fail (for scripting)"
    )

    args = parser.parse_args()

    # Check cryptography availability
    if not CRYPTOGRAPHY_AVAILABLE:
        print("ERROR: cryptography library required.", file=sys.stderr)
        print("Install with: pip install cryptography", file=sys.stderr)
        sys.exit(2)

    try:
        # Load public key
        public_key = load_public_key(args.pubkey)

        # Load evidence package
        package = load_evidence_package(args.package)

        # Verify
        result = verify_evidence(package, public_key, args.verbose)

        if args.quiet:
            print("PASS" if result.valid else "FAIL")
        else:
            print_result(result, args.verbose)

        sys.exit(0 if result.valid else 1)

    except ValueError as e:
        if args.quiet:
            print("ERROR")
        else:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    except Exception as e:
        if args.quiet:
            print("ERROR")
        else:
            print(f"UNEXPECTED ERROR: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
