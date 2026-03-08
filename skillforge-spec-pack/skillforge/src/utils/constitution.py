"""
Constitution loader module.

Provides utilities for loading and hashing the constitution file
that governs SkillForge's governance constraints.

Constitution SSOT: docs/2026-02-16/constitution_v1.md
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Tuple


# Default constitution path relative to this module
_DEFAULT_CONSTITUTION_PATH = Path(__file__).resolve().parents[4] / "docs" / "2026-02-16" / "constitution_v1.md"


def load_constitution(constitution_path: str | Path | None = None) -> Tuple[str, str]:
    """
    Load constitution file and return its reference and SHA256 hash.

    Args:
        constitution_path: Optional path to constitution file.
                          If None, uses default path at docs/2026-02-16/constitution_v1.md

    Returns:
        Tuple of (constitution_ref, constitution_hash):
        - constitution_ref: filename of the constitution (e.g., "constitution_v1.md")
        - constitution_hash: SHA256 hex digest (64 characters) of file contents

        If file is missing or unreadable:
        - constitution_ref: "MISSING"
        - constitution_hash: "" (empty string)
    """
    if constitution_path is None:
        path = _DEFAULT_CONSTITUTION_PATH
    else:
        path = Path(constitution_path)

    if not path.exists():
        return ("MISSING", "")

    if not path.is_file():
        return ("MISSING", "")

    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, IOError):
        return ("MISSING", "")

    # Compute SHA256 hash
    constitution_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    constitution_ref = path.name

    return (constitution_ref, constitution_hash)
