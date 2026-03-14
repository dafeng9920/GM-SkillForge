#!/usr/bin/env python3
"""
Gate Engine - Gate Decision Evaluation Entry Point (v0)

Thin wrapper for the gate engine implementation.
Provides the single entry point for the 8 Gate evaluation process.

This is the designated module for:
- 8 Gate sequential execution
- GateDecision production
- EvidenceRef collection

Spec source: docs/2026-03-04/v0-L5/GM-SkillForge v0 封板范围声明（10 个必须模块）.md
Implementation: skillforge-spec-pack/skillforge/src/orchestration/gate_engine.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Add skillforge-spec-pack to path for imports
_spec_pack_path = Path(__file__).parent.parent / "skillforge-spec-pack"
if str(_spec_pack_path) not in sys.path:
    sys.path.insert(0, str(_spec_pack_path))

try:
    from skillforge.src.orchestration.gate_engine import GateEngine
    _IMPLEMENTATION_SOURCE = "skillforge-spec-pack/skillforge/src/orchestration/gate_engine.py"
except ImportError as _import_exc:
    # FAIL-CLOSED: GateEngine must be available. A missing implementation is NOT
    # a recoverable situation — allowing gates to silently pass would nullify the
    # entire audit/permit trust chain.
    #
    # Fix: ensure skillforge-spec-pack is installed and the path is correct:
    #   pip install -e skillforge-spec-pack/
    # or verify that PYTHONPATH includes the spec-pack root.
    raise RuntimeError(
        "[FATAL] GateEngine implementation not found. "
        "Gate evaluation CANNOT proceed in fail-open mode. "
        "Ensure 'skillforge-spec-pack' is correctly installed and importable. "
        f"Original ImportError: {_import_exc}"
    ) from _import_exc

__all__ = [
    "GateEngine",
    "IMPLEMENTATION_SOURCE",
    "FIXED_GATE_ORDER",
]

IMPLEMENTATION_SOURCE = _IMPLEMENTATION_SOURCE

# Fixed 8 Gate order per v0 specification
FIXED_GATE_ORDER = [
    "intake_repo",
    "license_gate",
    "repo_scan_fit_score",
    "draft_skill_spec",
    "constitution_risk_gate",
    "scaffold_skill_impl",
    "sandbox_test_and_trace",
    "pack_audit_and_publish",
]


def execute_gate_plan(
    contract: dict[str, Any],
    artifacts: dict[str, Any],
    gate_plan: list[str] | None = None
) -> list[dict[str, Any]]:
    """
    Execute the fixed 8 Gate plan sequentially.

    Args:
        contract: Constitution Contract with gate_plan
        artifacts: Accumulated artifacts for gate evaluation
        gate_plan: Optional custom gate plan (defaults to FIXED_GATE_ORDER)

    Returns:
        List of GateDecision dicts in execution order
    """
    if gate_plan is None:
        gate_plan = FIXED_GATE_ORDER

    engine = GateEngine()
    decisions = []

    for gate_name in gate_plan:
        decision = engine.evaluate(gate_name, artifacts)
        decision["gate_name"] = gate_name
        decisions.append(decision)

        # Stop on DENY or REQUIRES_CHANGES (fail-closed)
        if decision.get("decision") in ("DENY", "REQUIRES_CHANGES"):
            break

    return decisions


def main() -> int:
    """CLI entry point for gate execution."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Execute 8 Gate evaluation (v0)")
    parser.add_argument("--contract", type=Path, required=True, help="Constitution Contract file")
    parser.add_argument("--artifacts", type=Path, help="Artifacts JSON file (optional)")
    parser.add_argument("--output", "-o", type=Path, required=True, help="Output decisions file")
    args = parser.parse_args()

    # Load contract
    try:
        contract = json.loads(args.contract.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERROR: Failed to load contract: {e}", file=sys.stderr)
        return 1

    # Load artifacts if provided
    artifacts = {}
    if args.artifacts:
        try:
            artifacts = json.loads(args.artifacts.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"WARNING: Failed to load artifacts: {e}", file=sys.stderr)

    # Get gate plan from contract or use default
    gate_plan = contract.get("gate_plan", FIXED_GATE_ORDER)

    # Execute gates
    try:
        decisions = execute_gate_plan(contract, artifacts, gate_plan)
    except Exception as e:
        print(f"ERROR: Failed to execute gates: {e}", file=sys.stderr)
        return 1

    # Write output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    output_data = {
        "gate_decisions": decisions,
        "execution_summary": {
            "total_gates": len(decisions),
            "passed": sum(1 for d in decisions if d.get("decision") == "ALLOW"),
            "failed": sum(1 for d in decisions if d.get("decision") == "DENY"),
            "requires_changes": sum(1 for d in decisions if d.get("decision") == "REQUIRES_CHANGES"),
        },
    }
    args.output.write_text(json.dumps(output_data, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"OK: Executed {len(decisions)} gate(s), wrote to {args.output}")
    for d in decisions:
        print(f"  [{d['gate_name']}] {d.get('decision', 'UNKNOWN')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
