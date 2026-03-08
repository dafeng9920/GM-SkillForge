#!/usr/bin/env python3
"""
evidence_sha256 Cross-Validation Chain Verifier
T71 Implementation by Kior-A

This script implements a blockchain-like evidence chain where each evidence
file's SHA256 hash is linked to form an immutable audit trail.

Usage:
    python scripts/verify_evidence_chain.py --init
    python scripts/verify_evidence_chain.py --add <evidence_file>
    python scripts/verify_evidence_chain.py --validate
    python scripts/verify_evidence_chain.py --chain-integrity
    python scripts/verify_evidence_chain.py --report
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

# Constants
CHAIN_VERSION = "1.0.0"
HASH_ALGORITHM = "SHA256"
GENESIS_HASH = "sha256:0000000000000000000000000000000000000000000000000000000000000000"

# Default paths
DEFAULT_CHAIN_PATH = Path("docs/2026-02-22/verification/evidence_chain_report.json")
DEFAULT_EVIDENCE_DIR = Path("docs/2026-02-22/verification")


class EvidenceChainError(Exception):
    """Custom exception for evidence chain errors."""
    pass


class EvidenceChain:
    """Manages the evidence SHA256 cross-validation chain."""

    def __init__(self, chain_path: Path = DEFAULT_CHAIN_PATH):
        self.chain_path = chain_path
        self.chain_data: Dict[str, Any] = {}
        self._load_or_init_chain()

    def _load_or_init_chain(self) -> None:
        """Load existing chain or initialize new one."""
        if self.chain_path.exists():
            with open(self.chain_path, 'r', encoding='utf-8') as f:
                self.chain_data = json.load(f)
        else:
            self.chain_data = self._create_genesis_chain()

    def _create_genesis_chain(self) -> Dict[str, Any]:
        """Create a new chain with genesis block."""
        return {
            "chain_id": f"evidence-chain-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "version": CHAIN_VERSION,
            "hash_algorithm": HASH_ALGORITHM,
            "genesis": {
                "hash": GENESIS_HASH,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "signed_by": "Kior-C"
            },
            "entries": [],
            "metadata": {
                "created_by": "T71_Kior-A",
                "purpose": "evidence_sha256 cross-validation chain"
            }
        }

    def _compute_sha256(self, file_path: Path) -> str:
        """Compute SHA256 hash of a file."""
        if not file_path.exists():
            raise EvidenceChainError(f"Evidence file not found: {file_path}")

        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256_hash.update(chunk)
        return f"sha256:{sha256_hash.hexdigest()}"

    def _compute_chain_hash(self, entry: Dict[str, Any]) -> str:
        """Compute chain hash for an entry."""
        # Create deterministic string representation for hashing
        hash_input = (
            f"{entry['index']}:"
            f"{entry['evidence_id']}:"
            f"{entry['evidence_sha256']}:"
            f"{entry['prev_hash']}:"
            f"{entry['timestamp']}"
        )
        sha256_hash = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
        return f"sha256:{sha256_hash}"

    def _get_last_hash(self) -> str:
        """Get the hash of the last entry in chain."""
        if not self.chain_data["entries"]:
            return self.chain_data["genesis"]["hash"]
        return self.chain_data["entries"][-1]["chain_hash"]

    def add_evidence(self, evidence_path: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Add a new evidence file to the chain."""
        evidence_file = Path(evidence_path)

        if not evidence_file.exists():
            raise EvidenceChainError(f"Evidence file not found: {evidence_path}")

        # Generate evidence ID
        evidence_id = f"EV-{len(self.chain_data['entries']) + 1:04d}"

        # Compute hashes
        evidence_sha256 = self._compute_sha256(evidence_file)
        prev_hash = self._get_last_hash()

        # Create new entry
        new_index = len(self.chain_data["entries"]) + 1
        new_entry = {
            "index": new_index,
            "evidence_id": evidence_id,
            "evidence_path": str(evidence_file),
            "evidence_sha256": evidence_sha256,
            "prev_hash": prev_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {}
        }

        # Compute chain hash (depends on all fields above)
        new_entry["chain_hash"] = self._compute_chain_hash(new_entry)

        # Add to chain
        self.chain_data["entries"].append(new_entry)

        return new_entry

    def validate_chain(self) -> Dict[str, Any]:
        """Validate the entire chain integrity."""
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "entries_checked": 0,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        prev_hash = self.chain_data["genesis"]["hash"]

        for i, entry in enumerate(self.chain_data["entries"]):
            result["entries_checked"] += 1

            # Check prev_hash linkage
            if entry["prev_hash"] != prev_hash:
                result["valid"] = False
                result["errors"].append({
                    "entry_index": entry["index"],
                    "error_type": "CHAIN_BREAK",
                    "message": f"prev_hash mismatch at index {entry['index']}: expected {prev_hash}, got {entry['prev_hash']}"
                })

            # Verify chain hash computation
            expected_chain_hash = self._compute_chain_hash(entry)
            if entry["chain_hash"] != expected_chain_hash:
                result["valid"] = False
                result["errors"].append({
                    "entry_index": entry["index"],
                    "error_type": "HASH_TAMPER",
                    "message": f"chain_hash mismatch at index {entry['index']}"
                })

            # Check index sequence
            if entry["index"] != i + 1:
                result["valid"] = False
                result["errors"].append({
                    "entry_index": entry["index"],
                    "error_type": "INDEX_MISMATCH",
                    "message": f"Expected index {i + 1}, got {entry['index']}"
                })

            prev_hash = entry["chain_hash"]

        return result

    def verify_evidence_existence(self) -> Dict[str, Any]:
        """Verify all evidence files exist and match their recorded hashes."""
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "files_checked": 0,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        for entry in self.chain_data["entries"]:
            result["files_checked"] += 1
            evidence_path = Path(entry["evidence_path"])

            if not evidence_path.exists():
                result["valid"] = False
                result["errors"].append({
                    "evidence_id": entry["evidence_id"],
                    "error_type": "FILE_MISSING",
                    "message": f"Evidence file not found: {entry['evidence_path']}"
                })
                continue

            # Verify SHA256 matches
            try:
                current_sha256 = self._compute_sha256(evidence_path)
                if current_sha256 != entry["evidence_sha256"]:
                    result["valid"] = False
                    result["errors"].append({
                        "evidence_id": entry["evidence_id"],
                        "error_type": "HASH_MISMATCH",
                        "message": f"Evidence file tampered: {entry['evidence_path']}"
                    })
            except Exception as e:
                result["valid"] = False
                result["errors"].append({
                    "evidence_id": entry["evidence_id"],
                    "error_type": "HASH_COMPUTE_ERROR",
                    "message": str(e)
                })

        return result

    def full_integrity_check(self) -> Dict[str, Any]:
        """Perform full chain integrity and evidence existence check."""
        chain_validation = self.validate_chain()
        existence_check = self.verify_evidence_existence()

        return {
            "valid": chain_validation["valid"] and existence_check["valid"],
            "chain_integrity": chain_validation,
            "evidence_existence": existence_check,
            "summary": {
                "total_entries": len(self.chain_data["entries"]),
                "chain_errors": len(chain_validation["errors"]),
                "existence_errors": len(existence_check["errors"])
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def save(self) -> None:
        """Save chain to file."""
        # Ensure directory exists
        self.chain_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.chain_path, 'w', encoding='utf-8') as f:
            json.dump(self.chain_data, f, indent=2, ensure_ascii=False)

    def get_report(self) -> Dict[str, Any]:
        """Generate a comprehensive chain report."""
        return {
            "chain_info": {
                "chain_id": self.chain_data["chain_id"],
                "version": self.chain_data["version"],
                "hash_algorithm": self.chain_data["hash_algorithm"],
                "total_entries": len(self.chain_data["entries"]),
                "genesis_created": self.chain_data["genesis"]["created_at"]
            },
            "entries": [
                {
                    "index": e["index"],
                    "evidence_id": e["evidence_id"],
                    "evidence_path": e["evidence_path"],
                    "evidence_sha256": e["evidence_sha256"],
                    "chain_hash": e["chain_hash"],
                    "timestamp": e["timestamp"],
                    "metadata": e.get("metadata", {})
                }
                for e in self.chain_data["entries"]
            ],
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": "verify_evidence_chain.py"
        }


def discover_evidence_files(directory: Path) -> List[Path]:
    """Discover evidence files in a directory."""
    evidence_patterns = [
        "*_execution_report.yaml",
        "*_execution_report.json",
        "*_gate_decision.json",
        "*_compliance_attestation.json",
        "*_report.json"
    ]

    evidence_files = []
    for pattern in evidence_patterns:
        evidence_files.extend(directory.glob(pattern))

    return sorted(set(evidence_files))


def main():
    parser = argparse.ArgumentParser(
        description="Evidence SHA256 Cross-Validation Chain Verifier"
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize a new evidence chain"
    )
    parser.add_argument(
        "--add",
        metavar="FILE",
        help="Add an evidence file to the chain"
    )
    parser.add_argument(
        "--add-dir",
        metavar="DIR",
        help="Add all evidence files from directory"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate chain integrity"
    )
    parser.add_argument(
        "--chain-integrity",
        action="store_true",
        help="Full chain integrity and evidence existence check"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate chain report"
    )
    parser.add_argument(
        "--chain-path",
        type=Path,
        default=DEFAULT_CHAIN_PATH,
        help=f"Path to chain file (default: {DEFAULT_CHAIN_PATH})"
    )
    parser.add_argument(
        "--metadata",
        type=json.loads,
        help="JSON metadata for --add operation"
    )

    args = parser.parse_args()

    # No arguments - show help
    if len(sys.argv) == 1:
        parser.print_help()
        return 0

    try:
        chain = EvidenceChain(args.chain_path)

        if args.init:
            # Initialize new chain
            chain.chain_data = chain._create_genesis_chain()
            chain.save()
            print(f"[OK] Chain initialized: {args.chain_path}")
            print(f"     Chain ID: {chain.chain_data['chain_id']}")
            return 0

        if args.add:
            # Add single evidence file
            entry = chain.add_evidence(args.add, args.metadata)
            chain.save()
            print(f"[OK] Evidence added to chain:")
            print(f"     Evidence ID: {entry['evidence_id']}")
            print(f"     Path: {entry['evidence_path']}")
            print(f"     SHA256: {entry['evidence_sha256']}")
            print(f"     Chain Hash: {entry['chain_hash']}")
            return 0

        if args.add_dir:
            # Add all evidence files from directory
            evidence_dir = Path(args.add_dir)
            if not evidence_dir.exists():
                print(f"[ERROR] Directory not found: {evidence_dir}", file=sys.stderr)
                return 1

            evidence_files = discover_evidence_files(evidence_dir)
            if not evidence_files:
                print(f"[WARN] No evidence files found in: {evidence_dir}")
                return 0

            for ef in evidence_files:
                entry = chain.add_evidence(str(ef), {"auto_discovered": True})
                print(f"[OK] Added: {ef.name} -> {entry['evidence_id']}")

            chain.save()
            print(f"\n[OK] Total evidence files added: {len(evidence_files)}")
            return 0

        if args.validate:
            # Validate chain integrity
            result = chain.validate_chain()
            if result["valid"]:
                print("[OK] CHAIN_VALID")
                print(f"     Entries checked: {result['entries_checked']}")
                return 0
            else:
                print("[FAIL] CHAIN_INVALID")
                for error in result["errors"]:
                    print(f"     - [{error['error_type']}] {error['message']}")
                return 1

        if args.chain_integrity:
            # Full integrity check
            result = chain.full_integrity_check()
            if result["valid"]:
                print("[OK] CHAIN_VALID")
                print(f"     Total entries: {result['summary']['total_entries']}")
                print(f"     Chain errors: {result['summary']['chain_errors']}")
                print(f"     Existence errors: {result['summary']['existence_errors']}")
                return 0
            else:
                print("[FAIL] CHAIN_INVALID")
                print(f"     Chain integrity: {'PASS' if result['chain_integrity']['valid'] else 'FAIL'}")
                print(f"     Evidence existence: {'PASS' if result['evidence_existence']['valid'] else 'FAIL'}")
                for error in result['chain_integrity']['errors']:
                    print(f"     [CHAIN] - {error['message']}")
                for error in result['evidence_existence']['errors']:
                    print(f"     [EXIST] - {error['message']}")
                return 1

        if args.report:
            # Generate report
            report = chain.get_report()
            report_path = args.chain_path
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"[OK] Report generated: {report_path}")
            return 0

    except EvidenceChainError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
