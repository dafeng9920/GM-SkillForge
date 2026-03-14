#!/usr/bin/env python3
"""
Contract Compiler - Demand DSL to Constitution Contract v0 Compiler

Compiles Demand DSL v0 into Constitution Contract v0 format for gate evaluation.
Ensures contract_hash keyset fields are complete and stable.

Spec source: docs/2026-03-04/v0-L5/GM-SkillForge v0 封板范围声明（10 个必须模块）.md
"""

from __future__ import annotations

import copy
import json
import sys
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any


class CompilationError(str, Enum):
    """Compilation error types."""
    INVALID_INPUT = "invalid_input"
    MISSING_FIELD = "missing_field"
    INVALID_MODE = "invalid_mode"
    COMPILATION_FAILED = "compilation_failed"


@dataclass
class CompilationResult:
    """Result of compiling Demand DSL to Constitution Contract."""
    success: bool
    contract: dict[str, Any] | None = None
    error_code: str | None = None
    error_message: str | None = None
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class ContractCompiler:
    """
    Compiles Demand DSL v0 to Constitution Contract v0.

    The contract serves as the input for the 8 Gate evaluation process.
    Key requirements:
    - contract_hash keyset fields must be complete
    - gate_plan must be fixed 8 Gate in consistent order
    - network_policy must be explicit
    """

    SCHEMA_VERSION = "constitution_contract_v0"

    # Fixed 8 Gate order per v0 specification
    FIXED_GATE_PLAN = [
        "intake_repo",
        "license_gate",
        "repo_scan_fit_score",
        "draft_skill_spec",
        "constitution_risk_gate",
        "scaffold_skill_impl",
        "sandbox_test_and_trace",
        "pack_audit_and_publish",
    ]

    # Default quality thresholds
    DEFAULT_QUALITY = {
        "must_have": [
            "schema_version",
            "skill_id",
            "skill_version",
            "capabilities",
            "controls",
        ],
        "min_test_coverage": 0.8,
        "min_documentation_score": 0.7,
    }

    # Default risk tier
    DEFAULT_RISK_TIER = "L0"
    VALID_RISK_TIERS = {"L0", "L1", "L2", "L3"}

    def __init__(self):
        """Initialize the compiler."""
        pass

    def compile(self, demand_dsl: dict[str, Any]) -> CompilationResult:
        """
        Compile Demand DSL to Constitution Contract.

        Args:
            demand_dsl: The Demand DSL document to compile

        Returns:
            CompilationResult with contract or error details
        """
        warnings: list[str] = []

        # Validate input
        if not isinstance(demand_dsl, dict):
            return CompilationResult(
                success=False,
                error_code=CompilationError.INVALID_INPUT,
                error_message="Demand DSL must be a dictionary",
            )

        # Extract key fields from Demand DSL
        intent_id = demand_dsl.get("intent_id", f"intent_{uuid.uuid4().hex[:8]}")
        mode = demand_dsl.get("mode")

        # Map mode to contract goals
        primary_goals = self._map_mode_to_goals(mode, demand_dsl)

        # Build I/O section
        io_section = self._build_io_section(demand_dsl)

        # Build controls section
        controls_section = self._build_controls_section(demand_dsl)

        # Build quality section
        quality_section = self._build_quality_section(demand_dsl)

        # Build risk section
        risk_section = self._build_risk_section(demand_dsl)

        # Build goals section
        goals_section = {
            "primary": primary_goals,
            "non_goals": self._build_non_goals(mode),
        }

        # Build gate_plan (fixed order)
        gate_plan = copy.copy(self.FIXED_GATE_PLAN)

        # Assemble contract
        contract = {
            "schema_version": self.SCHEMA_VERSION,
            "intent_id": intent_id,
            "goals": goals_section,
            "io": io_section,
            "controls": controls_section,
            "quality": quality_section,
            "risk": risk_section,
            "gate_plan": gate_plan,
        }

        return CompilationResult(
            success=True,
            contract=contract,
            warnings=warnings,
            metadata={
                "compiled_at": datetime.now(UTC).isoformat(),
                "source_mode": mode,
            },
        )

    def _map_mode_to_goals(self, mode: str | None, demand_dsl: dict[str, Any]) -> list[dict[str, Any]]:
        """Map execution mode to contract goals."""
        mode = mode or "generate_skill"

        goals = []

        if mode == "generate_skill":
            goals.append({
                "goal_id": "generate_skill_from_nl",
                "description": "Generate a new skill from natural language description",
                "success_metrics": [
                    "Skill manifest is valid",
                    "Dry-run execution succeeds",
                    "No BLOCKER findings from static analysis",
                ],
            })

        elif mode == "modify_skill":
            goals.append({
                "goal_id": "modify_existing_skill",
                "description": "Modify an existing skill according to requirements",
                "success_metrics": [
                    "Modified skill passes all tests",
                    "Backward compatibility maintained",
                    "Changes are minimal and focused",
                ],
            })

        elif mode == "audit_skill":
            goals.append({
                "goal_id": "audit_skill_compliance",
                "description": "Audit an existing skill for compliance and security",
                "success_metrics": [
                    "All security checks pass",
                    "License is approved",
                    "No BLOCKER violations found",
                ],
            })

        elif mode == "compose_workflow":
            goals.append({
                "goal_id": "compose_skill_workflow",
                "description": "Compose multiple skills into a workflow",
                "success_metrics": [
                    "Workflow orchestration is valid",
                    "Data flow between skills is correct",
                    "No circular dependencies",
                ],
            })

        else:
            # Default goal for unknown modes
            goals.append({
                "goal_id": "process_demand",
                "description": f"Process demand with mode: {mode}",
                "success_metrics": [
                    "Demand is processed successfully",
                    "Output is generated",
                ],
            })

        return goals

    def _build_non_goals(self, mode: str | None) -> list[str]:
        """Build non_goals list based on v0 scope."""
        mode = mode or "generate_skill"

        non_goals = [
            "Architecture Blueprint IR / PlanSpec auto-generation",
            "Multi-Agent autonomous planning",
            "Complex state machine execution",
            "Real external system execution (except tests-only/dry-run)",
            "Unlimited API calls",
        ]

        if mode == "generate_skill":
            non_goals.extend([
                "Full DDD deconstruction",
                "Autonomous feature planning",
            ])

        return non_goals

    def _build_io_section(self, demand_dsl: dict[str, Any]) -> dict[str, Any]:
        """Build I/O section from Demand DSL sources/destinations."""
        sources = demand_dsl.get("sources", [])
        destinations = demand_dsl.get("destinations", [])

        inputs = []
        for source in sources:
            input_spec = {
                "kind": source.get("kind"),
                "locator": source.get("locator"),
            }
            if source.get("version"):
                input_spec["version"] = source["version"]
            if source.get("format"):
                input_spec["format"] = source["format"]
            inputs.append(input_spec)

        outputs = []
        for dest in destinations:
            output_spec = {
                "kind": dest.get("kind"),
                "locator": dest.get("locator"),
                "write_mode": dest.get("write_mode"),
            }
            if dest.get("format"):
                output_spec["format"] = dest["format"]
            outputs.append(output_spec)

        return {
            "inputs": inputs,
            "outputs": outputs,
        }

    def _build_controls_section(self, demand_dsl: dict[str, Any]) -> dict[str, Any]:
        """Build controls section from Demand DSL constraints."""
        constraints = demand_dsl.get("constraints", {})

        controls = {
            "network_policy": constraints.get("network_policy", "deny_by_default"),
            "execution_mode": constraints.get("execution_mode", "dry_run"),
        }

        # Allowed domains (if any)
        allowed_domains = constraints.get("allowed_domains", [])
        if allowed_domains:
            controls["allowed_domains"] = allowed_domains

        # Human approval points
        approval_points = constraints.get("human_approval_points", [])
        if approval_points:
            controls["human_approval_points"] = approval_points

        # Resource limits
        resource_limits = constraints.get("resource_limits", {})
        if resource_limits:
            controls["resource_limits"] = resource_limits

        return controls

    def _build_quality_section(self, demand_dsl: dict[str, Any]) -> dict[str, Any]:
        """Build quality section with default thresholds."""
        acceptance = demand_dsl.get("acceptance", {})
        quality_gates = acceptance.get("quality_gates", {})

        quality = copy.copy(self.DEFAULT_QUALITY)

        # Override with acceptance criteria if specified
        if "min_test_pass_rate" in quality_gates:
            quality["min_test_pass_rate"] = quality_gates["min_test_pass_rate"]
        else:
            quality["min_test_pass_rate"] = 1.0

        if quality_gates.get("security_scan_required"):
            quality["security_scan_required"] = True

        # Map success criteria to quality checks
        success_criteria = acceptance.get("success_criteria", [])
        quality["acceptance_criteria"] = [
            {
                "criterion": c.get("criterion"),
                "check_type": c.get("check_type"),
            }
            for c in success_criteria
        ]

        return quality

    def _build_risk_section(self, demand_dsl: dict[str, Any]) -> dict[str, Any]:
        """Build risk section with deny list and allowed actions."""
        constraints = demand_dsl.get("constraints", {})

        # Determine risk tier based on network policy and execution mode
        risk_tier = self.DEFAULT_RISK_TIER
        network_policy = constraints.get("network_policy", "deny_by_default")
        execution_mode = constraints.get("execution_mode", "dry_run")

        if network_policy == "allowlist":
            risk_tier = "L1"
        if execution_mode in ("sandboxed", "production"):
            risk_tier = "L2"

        # Build deny list (v0: dangerous capabilities)
        deny_list = [
            "SUBPROCESS",
            "SYS_ENV_WRITE",
            "DYNAMIC_IMPORT",
            "PERSIST_STORAGE",
        ]

        # Allowed actions based on mode
        mode = demand_dsl.get("mode", "generate_skill")
        allowed_actions = self._get_allowed_actions_for_mode(mode)

        return {
            "risk_tier": risk_tier,
            "deny_list": deny_list,
            "allowed_actions": allowed_actions,
        }

    def _get_allowed_actions_for_mode(self, mode: str) -> list[str]:
        """Get allowed actions based on execution mode."""
        # Base allowed actions for all modes
        base_actions = [
            "read_manifest",
            "validate_schema",
            "static_analysis",
            "dry_run_execution",
        ]

        if mode == "generate_skill":
            return base_actions + [
                "generate_code",
                "write_to_workspace",
            ]

        elif mode == "modify_skill":
            return base_actions + [
                "read_source_code",
                "modify_code",
                "write_to_workspace",
            ]

        elif mode == "audit_skill":
            return base_actions + [
                "read_source_code",
                "security_scan",
                "license_check",
            ]

        elif mode == "compose_workflow":
            return base_actions + [
                "read_skill_manifests",
                "generate_workflow",
            ]

        return base_actions


def main() -> int:
    """CLI entry point for compilation."""
    import argparse

    parser = argparse.ArgumentParser(description="Compile Demand DSL to Constitution Contract")
    parser.add_argument("demand_file", type=Path, help="Path to Demand DSL file")
    parser.add_argument("--output", type=Path, required=True, help="Output contract file")
    args = parser.parse_args()

    # Load Demand DSL
    try:
        demand_dsl = json.loads(args.demand_file.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERROR: Failed to load Demand DSL: {e}", file=sys.stderr)
        return 1

    # Compile
    compiler = ContractCompiler()
    result = compiler.compile(demand_dsl)

    if not result.success:
        print(f"ERROR: {result.error_code} - {result.error_message}", file=sys.stderr)
        return 1

    # Write output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result.contract, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"OK: Compiled contract written to {args.output}")
    print(f"  intent_id: {result.contract['intent_id']}")
    print(f"  gates: {len(result.contract['gate_plan'])}")

    if result.warnings:
        print("\nWarnings:")
        for w in result.warnings:
            print(f"  - {w}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
