#!/usr/bin/env python3
"""
Generate Sample Evidence Package for Third-Party Verification Demo

This script creates a complete, signed evidence package that can be verified
using verify_evidence.py.

Usage:
    python sample_evidence.py

Outputs:
    - sample_evidence.json - The evidence package
    - sample_public_key.txt - The public key (hex) for verification
    - sample_public_key.pem - The public key (PEM) for verification
"""

import base64
import hashlib
import json
import time
import uuid
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization


def canonical_json_hash(obj) -> str:
    """Compute canonical JSON hash (SHA-256)."""
    def sort_keys(o):
        if isinstance(o, dict):
            return {k: sort_keys(v) for k, v in sorted(o.items())}
        elif isinstance(o, list):
            return [sort_keys(item) for item in o]
        return o

    canonical = json.dumps(sort_keys(obj), separators=(',', ':'), ensure_ascii=False)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def create_sample_evidence():
    """Create a sample evidence package with signature."""

    # Generate Ed25519 keypair directly
    print("Generating Ed25519 keypair...")
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    # Get key representations
    public_key_raw = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    public_key_hex = public_key_raw.hex()

    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode('utf-8')

    # Create evidence body
    body = {
        "task_id": "T11",
        "issue_id": "ISSUE-10",
        "executor": "Kior-B",
        "action": "third_party_verification_demo",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "details": {
            "description": "Sample evidence for third-party verification",
            "version": "1.0.0",
            "protocol": "L6-authenticity",
        },
        "metrics": {
            "tests_passed": 42,
            "tests_failed": 0,
            "coverage_percent": 100,
        }
    }

    # Create header
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    envelope_id = f"ev-{uuid.uuid4().hex[:8]}"

    header = {
        "envelope_id": envelope_id,
        "schema_version": "1.0.0",
        "created_at": now,
        "node_id": "node-kior-b-001",
        "body_hash": canonical_json_hash(body),
        "body_encoding": "json",
        "content_type": "application/json",
        "trace_id": f"trace-{uuid.uuid4().hex[:12]}",
    }

    # Sign the header hash
    header_hash = canonical_json_hash(header)
    signature_bytes = private_key.sign(header_hash.encode('utf-8'))

    # Create signature
    signature = {
        "algorithm": "Ed25519",
        "value": base64.b64encode(signature_bytes).decode('utf-8'),
        "signed_fields": ["header"],
        "signed_at": now,
    }

    # Create certificate
    cert = {
        "node_id": "node-kior-b-001",
        "public_key": public_key_hex,
        "algorithm": "Ed25519",
        "issued_at": now,
        "issuer": "self-signed",
    }

    # Assemble envelope
    envelope = {
        "header": header,
        "signature": signature,
        "cert": cert,
        "body": body,
    }

    return envelope, public_key_hex, public_key_pem


def main():
    output_dir = Path(__file__).parent / "sample_evidence"
    output_dir.mkdir(exist_ok=True)

    print("Creating sample evidence package...")

    # Create evidence
    envelope, public_key_hex, public_key_pem = create_sample_evidence()

    # Save evidence package
    evidence_path = output_dir / "sample_evidence.json"
    with open(evidence_path, 'w', encoding='utf-8') as f:
        json.dump(envelope, f, indent=2, sort_keys=True)
    print(f"✅ Saved evidence package: {evidence_path}")

    # Save public key (hex)
    pubkey_hex_path = output_dir / "sample_public_key.txt"
    with open(pubkey_hex_path, 'w') as f:
        f.write(public_key_hex)
    print(f"✅ Saved public key (hex): {pubkey_hex_path}")

    # Save public key (PEM)
    pubkey_pem_path = output_dir / "sample_public_key.pem"
    with open(pubkey_pem_path, 'w') as f:
        f.write(public_key_pem)
    print(f"✅ Saved public key (PEM): {pubkey_pem_path}")

    # Print verification instructions
    print("\n" + "=" * 60)
    print("Third-Party Verification Instructions")
    print("=" * 60)
    print(f"""
To verify this evidence package independently:

1. Using hex public key:
   python verify_evidence.py \\
       --package {evidence_path} \\
       --pubkey {public_key_hex}

2. Using PEM file:
   python verify_evidence.py \\
       --package {evidence_path} \\
       --pubkey {pubkey_pem_path}

3. Verbose output:
   python verify_evidence.py \\
       --package {evidence_path} \\
       --pubkey {pubkey_hex_path} \\
       --verbose

Evidence ID: {envelope['header']['envelope_id']}
Node ID: {envelope['header']['node_id']}
Created: {envelope['header']['created_at']}
""")

    return envelope, public_key_hex


if __name__ == "__main__":
    main()
