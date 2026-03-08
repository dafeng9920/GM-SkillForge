"""
Contract Module Builder - Build contract module structures.

Usage:
    python -m skillforge.skills.contract_module_builder --help
    python -m skillforge.skills.contract_module_builder --input-file <file> --output <file>

Exit codes:
    0 - success
    1 - processing error
    2 - invalid arguments
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="skillforge.skills.contract_module_builder",
        description="Build contract module structures for skill acceptance pipeline",
    )
    parser.add_argument(
        "--input-file",
        type=str,
        default=None,
        help="Input file path (JSON)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path (JSON)",
    )
    return parser


def build_module_contract(input_data: dict[str, Any] | None) -> dict[str, Any]:
    """Build a module contract structure.

    Args:
        input_data: Optional input data to incorporate into the contract.

    Returns:
        A module contract structure with metadata and status.
    """
    return {
        "contract_type": "module",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "built",
        "modules": [],
        "input": input_data,
        "metadata": {
            "builder": "contract_module_builder",
            "skillforge_version": "0.1.0",
        },
    }


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    # Read input if provided
    input_data = None
    if args.input_file:
        input_path = Path(args.input_file)
        if not input_path.exists():
            print(f"Error: Input file not found: {args.input_file}", file=sys.stderr)
            return 1
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                input_data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in input file: {e}", file=sys.stderr)
            return 1

    # Build module contract
    result = build_module_contract(input_data)

    # Write output
    output_str = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_str)
    else:
        print(output_str)

    return 0


if __name__ == "__main__":
    sys.exit(main())
