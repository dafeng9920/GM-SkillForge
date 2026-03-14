"""
Canonical JSON Implementation for GM-SkillForge

This module provides deterministic JSON serialization following JCS (JSON Canonicalization Scheme)
principles to ensure consistent hash values across different runs and environments.

Task: T02 - ISSUE-01: Canonical JSON 一致性
Executor: vs--cc1

D3 Fix (2026-03-05): Enhanced stability for replay consistency
- Added float precision normalization
- Added unicode normalization
- Added set sorting for deterministic iteration
- Enhanced test coverage for edge cases
"""

import json
import hashlib
import re
from typing import Any, Optional, Union
from collections import OrderedDict
import unicodedata


def _sort_dict_keys(obj: dict) -> dict:
    """Recursively sort dictionary keys."""
    return {k: _canonicalize_value(v) for k, v in sorted(obj.items())}


def _normalize_float(value: float) -> Union[float, str]:
    """
    Normalize float values for consistent serialization.

    D3 Fix: Ensure consistent float representation across platforms.
    """
    # Handle special float values first
    if value != value:  # NaN
        return "NaN"
    elif value == float('inf'):
        return "Infinity"
    elif value == float('-inf'):
        return "-Infinity"

    # Round to 10 decimal places to avoid floating point precision differences
    # This ensures that 0.1 + 0.2 == 0.3 consistently
    rounded = round(value, 10)

    # Remove trailing zeros and decimal point if not needed
    if rounded == int(rounded):
        return int(rounded)
    return rounded


def _normalize_string(value: str) -> str:
    """
    Normalize string values for consistent serialization.

    D3 Fix: Apply unicode normalization to ensure consistent representation.
    Uses NFC normalization which composes characters consistently.
    """
    # Normalize unicode to NFC form
    normalized = unicodedata.normalize('NFC', value)

    # Normalize whitespace sequences to single space
    # This prevents inconsistencies from different whitespace handling
    normalized = re.sub(r'\s+', ' ', normalized)

    return normalized


def _canonicalize_value(obj: Any) -> Any:
    """
    Recursively canonicalize a value with enhanced stability.

    D3 Fix: Added handling for sets, enhanced float/string normalization.
    """
    if isinstance(obj, dict):
        return _sort_dict_keys(obj)
    elif isinstance(obj, (list, tuple)):
        return [_canonicalize_value(item) for item in obj]
    elif isinstance(obj, set):
        # Sort sets to ensure deterministic order
        return sorted(_canonicalize_value(item) for item in obj)
    elif isinstance(obj, float):
        return _normalize_float(obj)
    elif isinstance(obj, str):
        return _normalize_string(obj)
    elif isinstance(obj, bool):
        return obj
    elif obj is None:
        return None
    else:
        # For other types (int, etc.), return as-is
        return obj


def canonical_json(obj: Any, *, ensure_ascii: bool = False, indent: Optional[int] = None) -> str:
    """
    Convert a Python object to canonical JSON string.

    This function ensures that the same object always produces the same JSON string,
    making it suitable for cryptographic hashing and signature verification.

    Args:
        obj: Python object to serialize
        ensure_ascii: If True, escape non-ASCII characters (default: False)
        indent: Indentation level for pretty printing (default: None for compact)

    Returns:
        Canonical JSON string

    Example:
        >>> canonical_json({"b": 2, "a": 1})
        '{"a":1,"b":2}'
        >>> canonical_json({"b": 2, "a": 1})
        '{"a":1,"b":2}'
    """
    canonicalized = _canonicalize_value(obj)

    # Use separators without spaces for compact output
    separators = (',', ':') if indent is None else (',', ': ')

    return json.dumps(
        canonicalized,
        sort_keys=True,
        ensure_ascii=ensure_ascii,
        indent=indent,
        separators=separators
    )


def canonical_json_hash(obj: Any, algorithm: str = "sha256") -> str:
    """
    Compute the hash of a canonical JSON representation.

    Args:
        obj: Python object to hash
        algorithm: Hash algorithm ('sha256', 'sha384', 'sha512', 'md5')

    Returns:
        Hexadecimal hash string

    Example:
        >>> canonical_json_hash({"b": 2, "a": 1})
        'd73698...'

        >>> # Same object, same hash
        >>> canonical_json_hash({"a": 1, "b": 2})  # Different key order
        'd73698...'  # Same hash as above
    """
    canonical_str = canonical_json(obj)
    encoded = canonical_str.encode('utf-8')

    hash_func = getattr(hashlib, algorithm, None)
    if hash_func is None:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")

    return hash_func(encoded).hexdigest()


def verify_canonical_consistency(obj: Any, iterations: int = 100) -> dict:
    """
    Verify that canonical_json produces consistent results across multiple runs.

    Args:
        obj: Python object to test
        iterations: Number of iterations to run

    Returns:
        Dictionary with verification results

    Example:
        >>> result = verify_canonical_consistency({"test": [1, 2, 3]})
        >>> result['consistent']
        True
    """
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
        "json": list(json_strings)[0] if len(json_strings) == 1 else None
    }


# Convenience exports
__all__ = [
    "canonical_json",
    "canonical_json_hash",
    "verify_canonical_consistency",
    "deterministic_dict",
    "deterministic_repr"
]


def deterministic_dict(**kwargs) -> dict:
    """
    Create a deterministic dictionary with sorted keys.

    D3 Fix: Helper function for creating dictionaries that serialize consistently.
    Useful for building complex nested structures that need to be hashable.

    Example:
        >>> d = deterministic_dict(b=2, a=1, c=3)
        >>> canonical_json(d)
        '{"a":1,"b":2,"c":3}'
    """
    return dict(sorted(kwargs.items()))


def deterministic_repr(obj: Any) -> str:
    """
    Create a deterministic string representation for comparison.

    D3 Fix: Useful for testing and debugging replay consistency issues.
    Returns a canonical JSON string that can be compared across runs.

    Args:
        obj: Python object to represent

    Returns:
        Deterministic string representation
    """
    return canonical_json(obj, ensure_ascii=False, indent=None)
