#!/usr/bin/env python3
"""
Canonicalize - Canonical JSON Entry Point (v0)

Thin wrapper for the canonical JSON implementation.
Provides the single entry point for canonical JSON operations in v0.

This is the designated canonicalization module for:
- Three-hash calculation
- EvidenceRef content hashing
- All deterministic JSON serialization needs

Spec source: docs/2026-03-04/v0-L5/GM-SkillForge v0 封板范围声明（10 个必须模块）.md
Implementation: skillforge-spec-pack/skillforge/src/utils/canonical_json.py
"""

from __future__ import annotations

# Import from the existing implementation
import sys
from pathlib import Path
from typing import Any, Optional

# Add skillforge-spec-pack to path for imports
_spec_pack_path = Path(__file__).parent.parent / "skillforge-spec-pack"
if str(_spec_pack_path) not in sys.path:
    sys.path.insert(0, str(_spec_pack_path))

try:
    from skillforge.src.utils.canonical_json import (
        canonical_json,
        canonical_json_hash,
        verify_canonical_consistency,
    )
    _IMPLEMENTATION_SOURCE = "skillforge-spec-pack/skillforge/src/utils/canonical_json.py"
except ImportError:
    # Fallback to a local implementation if spec-pack is not available
    import hashlib
    import json

    def _canonicalize_value(obj: Any) -> Any:
        """Canonicalize a value recursively."""
        if isinstance(obj, dict):
            return {k: _canonicalize_value(v) for k, v in sorted(obj.items())}
        elif isinstance(obj, (list, tuple)):
            return [_canonicalize_value(item) for item in obj]
        elif isinstance(obj, float):
            if obj != obj:  # NaN
                return "NaN"
            elif obj == float('inf'):
                return "Infinity"
            elif obj == float('-inf'):
                return "-Infinity"
            return obj
        return obj

    def canonical_json(obj: Any, *, ensure_ascii: bool = False, indent: Optional[int] = None) -> str:
        """Convert object to canonical JSON string."""
        canonicalized = _canonicalize_value(obj)
        separators = (',', ':') if indent is None else (',', ': ')
        return json.dumps(
            canonicalized,
            sort_keys=True,
            ensure_ascii=ensure_ascii,
            indent=indent,
            separators=separators
        )

    def canonical_json_hash(obj: Any, algorithm: str = "sha256") -> str:
        """Compute hash of canonical JSON representation."""
        canonical_str = canonical_json(obj)
        encoded = canonical_str.encode('utf-8')
        hash_func = getattr(hashlib, algorithm, None)
        if hash_func is None:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
        return hash_func(encoded).hexdigest()

    def verify_canonical_consistency(obj: Any, iterations: int = 100) -> dict:
        """Verify canonical_json produces consistent results."""
        hashes = set()
        json_strings = set()
        for _ in range(iterations):
            json_str = canonical_json(obj)
            hash_val = canonical_json_hash(obj)
            hashes.add(hash_val)
            json_strings.add(json_str)
        return {
            "consistent": len(hashes) == 1 and len(json_strings) == 1,
            "iterations": iterations,
            "unique_hashes": len(hashes),
            "unique_json_strings": len(json_strings),
            "hash": list(hashes)[0] if len(hashes) == 1 else None,
            "json": list(json_strings)[0] if len(json_strings) == 1 else None,
        }
    _IMPLEMENTATION_SOURCE = "builtin_fallback"


__all__ = [
    "canonical_json",
    "canonical_json_hash",
    "verify_canonical_consistency",
    "IMPLEMENTATION_SOURCE",
]

IMPLEMENTATION_SOURCE = _IMPLEMENTATION_SOURCE


def main() -> int:
    """CLI entry point for canonicalization."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Canonicalize JSON for deterministic hashing")
    parser.add_argument("input_file", type=Path, help="Input JSON file")
    parser.add_argument("--output", "-o", type=Path, help="Output file (default: stdout)")
    parser.add_argument("--indent", type=int, help="Indentation for pretty printing")
    parser.add_argument("--hash", action="store_true", help="Output hash instead of JSON")
    parser.add_argument("--verify", action="store_true", help="Verify consistency across iterations")
    parser.add_argument("--iterations", type=int, default=100, help="Iterations for verification")
    args = parser.parse_args()

    # Load input
    try:
        data = json.loads(args.input_file.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERROR: Failed to load input: {e}", file=sys.stderr)
        return 1

    if args.verify:
        result = verify_canonical_consistency(data, args.iterations)
        print(f"Consistent: {result['consistent']}")
        print(f"Iterations: {result['iterations']}")
        print(f"Unique hashes: {result['unique_hashes']}")
        if result['consistent']:
            print(f"Hash: {result['hash']}")
        return 0 if result['consistent'] else 1

    # Canonicalize
    output = canonical_json(data, ensure_ascii=False, indent=args.indent)

    if args.hash:
        hash_value = canonical_json_hash(data)
        output = hash_value

    # Write output
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
        print(f"OK: Wrote to {args.output}")
    else:
        print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
