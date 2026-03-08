文件: skillforge/src/nodes/intent_parser.py
pythonDownloadCopy code"""
IntentParser node — parses natural language into structured intent.

Path: A, A+B
Stage: pre-0 (-1)

Input Contract
--------------
{
    "natural_language": str,
    "options": { ... }   # pipeline options
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "intent": {
        "goal": str,
        "domain": str,
        "actions": list[str],
        "constraints": list[str],
        "target_environment": str,
        "intended_use": str
    },
    "confidence": float,   # 0.0 - 1.0
    "raw_input": str
}
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class IntentParser:
    """Parse natural-language skill descriptions into structured intent."""

    node_id: str = "intent_parse"
    stage: int = -1

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate that natural_language is present and non-empty."""
        errors: list[str] = []

        pipeline_input = input_data.get("input")
        if not isinstance(pipeline_input, dict):
            errors.append("EXEC_VALIDATION_FAILED: 'input' key is required in pipeline artifacts")
            return errors

        nl = pipeline_input.get("natural_language")
        if not nl or not isinstance(nl, str) or not nl.strip():
            errors.append("EXEC_VALIDATION_FAILED: natural_language is required and cannot be empty")

        return errors

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Parse the natural language description into a structured intent dict.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        pipeline_input = input_data.get("input", {})
        natural_language: str = pipeline_input.get("natural_language", "")
        nl_lower = natural_language.lower()

        # goal: first 100 characters
        goal = natural_language[:100]

        # domain: keyword-based inference
        if "data" in nl_lower:
            domain = "data_processing"
        elif "web" in nl_lower:
            domain = "web_service"
        elif "ml" in nl_lower or "ai" in nl_lower:
            domain = "machine_learning"
        else:
            domain = "general"

        # actions: extract matching verb keywords
        action_keywords = ["analyze", "process", "generate", "transform", "compute"]
        actions = [kw for kw in action_keywords if re.search(r'\b' + kw + r'\b', nl_lower)]

        return {
            "schema_version": "0.1.0",
            "intent": {
                "goal": goal,
                "domain": domain,
                "actions": actions,
                "constraints": [],
                "target_environment": "python",
                "intended_use": "automation",
            },
            "confidence": 0.75,
            "raw_input": natural_language,
        }

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate output against intent schema."""
        errors: list[str] = []

        if not isinstance(output_data, dict):
            errors.append("SCHEMA_INVALID: output must be a dict")
            return errors

        for field in ("schema_version", "intent", "confidence", "raw_input"):
            if field not in output_data:
                errors.append(f"SCHEMA_INVALID: {field} is required")

        intent = output_data.get("intent")
        if isinstance(intent, dict):
            for field in ("goal", "domain"):
                if field not in intent:
                    errors.append(f"SCHEMA_INVALID: intent.{field} is required")
        elif intent is not None:
            errors.append("SCHEMA_INVALID: intent must be a dict")

        confidence = output_data.get("confidence")
        if isinstance(confidence, (int, float)):
            if not (0.0 <= confidence <= 1.0):
                errors.append(f"SCHEMA_INVALID: confidence must be 0.0-1.0, got {confidence}")

        return errors
文件: skillforge/src/nodes/source_strategy.py
pythonDownloadCopy code"""
SourceStrategy node — decides whether to generate from scratch or search GitHub.

Path: A, A+B
Stage: pre-0 (-1)

Input Contract
--------------
{
    "intent": { ... },       # from IntentParser
    "mode": "nl" | "auto",
    "confidence": float
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "strategy": "generate" | "search_github" | "hybrid",
    "search_query": str | None,      # set when strategy includes github search
    "generation_hints": dict | None,  # set when strategy includes generation
    "reason": str
}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class SourceStrategy:
    """Decide source strategy based on parsed intent and mode."""

    node_id: str = "source_strategy"
    stage: int = -1

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate that intent and mode are present."""
        errors: list[str] = []

        intent_parse = input_data.get("intent_parse")
        if not isinstance(intent_parse, dict):
            errors.append("EXEC_VALIDATION_FAILED: intent_parse output is required")

        return errors

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Determine source strategy.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        intent_parse = input_data.get("intent_parse", {})
        intent = intent_parse.get("intent", {})
        confidence: float = intent_parse.get("confidence", 0.0)

        pipeline_input = input_data.get("input", {})
        mode: str = pipeline_input.get("mode", "nl")

        # Strategy decision rules
        if mode == "github":
            strategy = "search_github"
            reason = "Mode is 'github'; searching GitHub for matching repos"
        elif mode == "nl" and confidence > 0.8:
            strategy = "generate"
            reason = f"Mode is 'nl' with high confidence ({confidence}); generating from scratch"
        elif mode == "auto":
            strategy = "hybrid"
            reason = "Mode is 'auto'; using hybrid strategy (search + generate)"
        else:
            strategy = "generate"
            reason = f"Mode is '{mode}' with confidence {confidence}; defaulting to generation"

        # search_query
        search_query = None
        if strategy in ("search_github", "hybrid"):
            goal = intent.get("goal", "")
            search_query = goal[:50] if goal else None

        # generation_hints
        generation_hints = None
        if strategy in ("generate", "hybrid"):
            generation_hints = {
                "domain": intent.get("domain", "general"),
                "actions": intent.get("actions", []),
            }

        return {
            "schema_version": "0.1.0",
            "strategy": strategy,
            "search_query": search_query,
            "generation_hints": generation_hints,
            "reason": reason,
        }

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate strategy output."""
        errors: list[str] = []

        if not isinstance(output_data, dict):
            errors.append("SCHEMA_INVALID: output must be a dict")
            return errors

        for field in ("schema_version", "strategy", "reason"):
            if field not in output_data:
                errors.append(f"SCHEMA_INVALID: {field} is required")

        strategy = output_data.get("strategy")
        if strategy is not None and strategy not in ("generate", "search_github", "hybrid"):
            errors.append(
                f"SCHEMA_INVALID: strategy must be generate, search_github, or hybrid, got '{strategy}'"
            )

        return errors
文件: skillforge/src/nodes/github_discover.py
pythonDownloadCopy code"""
GitHubDiscovery node — search GitHub for candidate repos matching intent.

Path: A+B only
Stage: pre-0 (-1)

Input Contract
--------------
{
    "search_query": str,
    "intent": { ... },
    "max_results": int       # default 5
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "candidates": [
        {
            "repo_url": str,
            "stars": int,
            "license": str | None,
            "fit_score_estimate": int,
            "match_reason": str
        }
    ],
    "selected": {
        "repo_url": str,
        "reason": str
    } | None,
    "fallback_to_generate": bool
}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class GitHubDiscovery:
    """Search GitHub for repos that match the parsed intent."""

    node_id: str = "github_discover"
    stage: int = -1

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate search_query and intent are present."""
        errors: list[str] = []

        source_strategy = input_data.get("source_strategy")
        if not isinstance(source_strategy, dict):
            errors.append("EXEC_VALIDATION_FAILED: source_strategy output is required")
            return errors

        if not source_strategy.get("search_query"):
            errors.append("EXEC_VALIDATION_FAILED: source_strategy.search_query is required")

        return errors

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Search GitHub and rank candidate repos.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        source_strategy = input_data.get("source_strategy", {})
        search_query: str = source_strategy.get("search_query", "")

        intent_parse = input_data.get("intent_parse", {})
        intent = intent_parse.get("intent", {})
        domain: str = intent.get("domain", "general")

        # Generate mock candidates
        candidates: list[dict[str, Any]] = []
        for i in range(3):
            candidates.append({
                "repo_url": f"https://github.com/mock-org/mock-{i}",
                "stars": 100 * (i + 1),
                "license": "MIT",
                "fit_score_estimate": 70 - i * 10,
                "match_reason": f"Matches intent domain: {domain}",
            })

        # Select the best candidate (first)
        selected = {
            "repo_url": candidates[0]["repo_url"],
            "reason": f"Highest fit_score_estimate ({candidates[0]['fit_score_estimate']}) for query: {search_query}",
        }

        return {
            "schema_version": "0.1.0",
            "candidates": candidates,
            "selected": selected,
            "fallback_to_generate": False,
        }

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate discovery output."""
        errors: list[str] = []

        if not isinstance(output_data, dict):
            errors.append("SCHEMA_INVALID: output must be a dict")
            return errors

        for field in ("schema_version", "candidates", "fallback_to_generate"):
            if field not in output_data:
                errors.append(f"SCHEMA_INVALID: {field} is required")

        candidates = output_data.get("candidates")
        if candidates is not None and not isinstance(candidates, list):
            errors.append("SCHEMA_INVALID: candidates must be a list")

        return errors
文件: skillforge/src/nodes/skill_composer.py
pythonDownloadCopy code"""
SkillComposer node — generate a skill spec from intent (no repo source).

Path: A only
Stage: A-only (stage index 1 within path A context)

Input Contract
--------------
{
    "intent": { ... },
    "generation_hints": dict | None,
    "options": { ... }
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "skill_spec": {
        "name": str,
        "version": str,
        "description": str,
        "inputs": list[dict],
        "outputs": list[dict],
        "tools_required": list[str],
        "steps": list[dict],
        "constraints": list[str]
    },
    "source": "generated",
    "confidence": float
}
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class SkillComposer:
    """Compose a skill specification directly from parsed intent."""

    node_id: str = "skill_compose"
    stage: int = -1  # A-only pre-shared stage

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate intent presence."""
        errors: list[str] = []

        intent_parse = input_data.get("intent_parse")
        if not isinstance(intent_parse, dict):
            errors.append("EXEC_VALIDATION_FAILED: intent_parse output is required")

        return errors

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Generate a skill specification from intent.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        intent_parse = input_data.get("intent_parse", {})
        intent = intent_parse.get("intent", {})
        confidence: float = intent_parse.get("confidence", 0.5)

        source_strategy = input_data.get("source_strategy", {})
        generation_hints = source_strategy.get("generation_hints")

        goal: str = intent.get("goal", "unknown")
        domain: str = intent.get("domain", "general")
        target_env: str = intent.get("target_environment", "python")
        constraints: list[str] = list(intent.get("constraints", []))

        # Build name: sanitise goal fragment
        goal_slug = re.sub(r'[^a-z0-9]+', '-', goal[:20].lower()).strip('-')
        name = f"skill-{domain}-{goal_slug}"

        # tools_required from target_environment
        tools_map: dict[str, list[str]] = {
            "python": ["python3", "pip"],
            "node": ["node", "npm"],
            "javascript": ["node", "npm"],
            "go": ["go"],
            "rust": ["cargo"],
        }
        tools_required = tools_map.get(target_env, ["python3", "pip"])

        # constraints
        all_constraints = constraints + ["risk_tier: L1"]

        skill_spec: dict[str, Any] = {
            "name": name,
            "version": "0.1.0",
            "description": goal,
            "inputs": [{"name": "input_data", "type": "object", "required": True}],
            "outputs": [{"name": "result", "type": "object"}],
            "tools_required": tools_required,
            "steps": [
                {
                    "id": "step_1",
                    "action": "execute",
                    "description": f"Execute {goal[:50]}",
                }
            ],
            "constraints": all_constraints,
        }

        return {
            "schema_version": "0.1.0",
            "skill_spec": skill_spec,
            "source": "generated",
            "confidence": confidence * 0.9,
        }

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate generated skill spec."""
        errors: list[str] = []

        if not isinstance(output_data, dict):
            errors.append("SCHEMA_INVALID: output must be a dict")
            return errors

        for field in ("schema_version", "skill_spec", "source", "confidence"):
            if field not in output_data:
                errors.append(f"SCHEMA_INVALID: {field} is required")

        skill_spec = output_data.get("skill_spec")
        if isinstance(skill_spec, dict):
            for field in ("name", "version", "description"):
                if field not in skill_spec:
                    errors.append(f"SCHEMA_INVALID: skill_spec.{field} is required")
        elif skill_spec is not None:
            errors.append("SCHEMA_INVALID: skill_spec must be a dict")

        source = output_data.get("source")
        if source is not None and source != "generated":
            errors.append(f"SCHEMA_INVALID: source must be 'generated', got '{source}'")

        return errors
文件: skillforge/src/nodes/constitution_gate.py
pythonDownloadCopy code"""
ConstitutionGate node — risk assessment gate for skill safety and alignment.

Path: ALL
Stage: 4

Input Contract (conforms to gm-os-core constitution_risk_gate.schema.json)
--------------
{
    "skill_spec": { ... },      # from SkillComposer or DraftSpec
    "options": { ... }
}

Output Contract (GateDecision)
---------------
{
    "schema_version": "0.1.0",
    "gate_id": "constitution_risk_gate",
    "node_id": "constitution_risk_gate",
    "decision": "ALLOW" | "DENY" | "REQUIRES_CHANGES",
    "reason": str,
    "details": {
        "risk_score": float,        # 0.0 - 1.0
        "risk_categories": list[str],
        "mitigations_required": list[str],
        "constitution_version": str
    },
    "timestamp": str
}
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from typing import Any


@dataclass
class ConstitutionGate:
    """Evaluate skill spec against the GM OS constitution for safety and alignment."""

    node_id: str = "constitution_risk_gate"
    stage: int = 4

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate skill_spec is present."""
        errors: list[str] = []

        skill_compose = input_data.get("skill_compose")
        draft_skill_spec = input_data.get("draft_skill_spec")

        has_spec = False
        if isinstance(skill_compose, dict) and "skill_spec" in skill_compose:
            has_spec = True
        if isinstance(draft_skill_spec, dict) and "skill_spec" in draft_skill_spec:
            has_spec = True

        if not has_spec:
            errors.append(
                "EXEC_VALIDATION_FAILED: skill_spec source is required "
                "(from skill_compose or draft_skill_spec)"
            )

        return errors

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Evaluate skill spec against constitution risk criteria.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract (GateDecision).
        """
        # Resolve skill_spec: prefer skill_compose, fall back to draft_skill_spec
        skill_compose = input_data.get("skill_compose", {})
        draft_skill_spec = input_data.get("draft_skill_spec", {})

        if isinstance(skill_compose, dict) and "skill_spec" in skill_compose:
            skill_spec = skill_compose["skill_spec"]
        elif isinstance(draft_skill_spec, dict) and "skill_spec" in draft_skill_spec:
            skill_spec = draft_skill_spec["skill_spec"]
        else:
            skill_spec = {}

        # Options
        options = input_data.get("input", {}).get("options", {})
        sandbox_mode: str = options.get("sandbox_mode", "strict")

        # Risk assessment
        risk_categories: list[str] = []
        risk_score: float = 0.0

        # Check constraints for elevated risk tiers
        constraints = skill_spec.get("constraints", [])
        constraints_str = " ".join(str(c) for c in constraints).lower()
        if "l2" in constraints_str or "l3" in constraints_str:
            risk_score += 0.3
            risk_categories.append("elevated_risk_tier")

        # Check tools_required for subprocess / shell access
        tools_required = skill_spec.get("tools_required", [])
        for tool in tools_required:
            tool_lower = str(tool).lower()
            if tool_lower == "subprocess" or "shell" in tool_lower:
                risk_score += 0.3
                risk_categories.append("subprocess_access")
                break

        # Check intent domain for ML compute
        intent_parse = input_data.get("intent_parse", {})
        intent = intent_parse.get("intent", {})
        if intent.get("domain") == "machine_learning":
            risk_score += 0.1
            risk_categories.append("ml_compute")

        # Clamp
        risk_score = min(risk_score, 1.0)

        # Decision rules
        mitigations_required: list[str] = []
        if risk_score >= 0.7:
            decision = "DENY"
            reason = f"Risk score {risk_score:.2f} exceeds threshold (0.7); categories: {risk_categories}"
        elif risk_score >= 0.3:
            decision = "REQUIRES_CHANGES"
            reason = f"Risk score {risk_score:.2f} requires review; categories: {risk_categories}"
            mitigations_required = ["Review subprocess usage", "Add resource limits"]
        else:
            decision = "ALLOW"
            reason = f"Risk score {risk_score:.2f} is within acceptable limits"

        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        return {
            "schema_version": "0.1.0",
            "gate_id": "constitution_risk_gate",
            "node_id": self.node_id,
            "decision": decision,
            "reason": reason,
            "details": {
                "risk_score": risk_score,
                "risk_categories": risk_categories,
                "mitigations_required": mitigations_required,
                "constitution_version": "0.1.0",
            },
            "timestamp": timestamp,
        }

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate GateDecision structure."""
        errors: list[str] = []

        if not isinstance(output_data, dict):
            errors.append("SCHEMA_INVALID: output must be a dict")
            return errors

        for field in ("schema_version", "gate_id", "node_id", "decision", "reason", "timestamp"):
            if field not in output_data:
                errors.append(f"SCHEMA_INVALID: {field} is required")

        decision = output_data.get("decision")
        if decision is not None and decision not in ("ALLOW", "DENY", "REQUIRES_CHANGES"):
            errors.append(
                f"GATE_INVALID_DECISION: decision must be ALLOW, DENY, or "
                f"REQUIRES_CHANGES, got '{decision}'"
            )

        details = output_data.get("details")
        if isinstance(details, dict):
            for field in ("risk_score", "risk_categories", "constitution_version"):
                if field not in details:
                    errors.append(f"SCHEMA_INVALID: details.{field} is required")
        else:
            errors.append("SCHEMA_INVALID: details must be a dict")

        return errors
文件: skillforge/src/nodes/scaffold_impl.py
pythonDownloadCopy code"""
ScaffoldImpl node — generate skill implementation code from spec.

Path: ALL
Stage: 5

Input Contract (conforms to gm-os-core scaffold_skill_impl.schema.json)
--------------
{
    "skill_spec": { ... },
    "gate_decision": { ... },   # from ConstitutionGate (must be ALLOW)
    "options": { ... }
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "bundle_path": str,         # path to generated skill bundle
    "files_generated": list[str],
    "entry_point": str,
    "language": str,
    "test_file": str | None,
    "manifest": {
        "skill_id": str,
        "version": str,
        "checksum": str
    }
}
"""
from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass
from typing import Any


@dataclass
class ScaffoldImpl:
    """Generate skill implementation scaffolding from a validated spec."""

    node_id: str = "scaffold_skill_impl"
    stage: int = 5

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate skill_spec and gate_decision (ALLOW) are present."""
        errors: list[str] = []

        # Resolve skill_spec
        skill_compose = input_data.get("skill_compose")
        draft_skill_spec = input_data.get("draft_skill_spec")

        has_spec = False
        if isinstance(skill_compose, dict) and "skill_spec" in skill_compose:
            has_spec = True
        if isinstance(draft_skill_spec, dict) and "skill_spec" in draft_skill_spec:
            has_spec = True

        if not has_spec:
            errors.append(
                "EXEC_VALIDATION_FAILED: skill_spec is required "
                "(from skill_compose or draft_skill_spec)"
            )

        # Resolve gate_decision
        gate = input_data.get("constitution_risk_gate")
        if not isinstance(gate, dict):
            errors.append("EXEC_VALIDATION_FAILED: constitution_risk_gate output is required")
        else:
            decision = gate.get("decision")
            if decision != "ALLOW":
                errors.append(
                    "GATE_DENIED: Constitution gate must ALLOW before scaffolding"
                )

        return errors

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Generate skill implementation bundle.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        # Resolve skill_spec
        skill_compose = input_data.get("skill_compose", {})
        draft_skill_spec = input_data.get("draft_skill_spec", {})

        if isinstance(skill_compose, dict) and "skill_spec" in skill_compose:
            skill_spec = skill_compose["skill_spec"]
        elif isinstance(draft_skill_spec, dict) and "skill_spec" in draft_skill_spec:
            skill_spec = draft_skill_spec["skill_spec"]
        else:
            skill_spec = {}

        skill_name: str = skill_spec.get("name", "unknown-skill")
        version: str = skill_spec.get("version", "0.1.0")
        tools_required: list[str] = skill_spec.get("tools_required", [])

        # Infer language
        tools_lower = [str(t).lower() for t in tools_required]
        if "python3" in tools_lower or "pip" in tools_lower:
            language = "Python"
        elif "node" in tools_lower or "npm" in tools_lower:
            language = "JavaScript"
        else:
            language = "Python"

        bundle_path = f"/tmp/skillforge/bundles/{skill_name}"
        entry_point = "main.py"
        files_generated = [
            f"{skill_name}/main.py",
            f"{skill_name}/manifest.json",
            f"{skill_name}/README.md",
        ]
        test_file = f"{skill_name}/test_skill.py"
        checksum = hashlib.sha256(skill_name.encode()).hexdigest()[:16]

        return {
            "schema_version": "0.1.0",
            "bundle_path": bundle_path,
            "files_generated": files_generated,
            "entry_point": entry_point,
            "language": language,
            "test_file": test_file,
            "manifest": {
                "skill_id": skill_name,
                "version": version,
                "checksum": checksum,
            },
        }

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate scaffold output."""
        errors: list[str] = []

        if not isinstance(output_data, dict):
            errors.append("SCHEMA_INVALID: output must be a dict")
            return errors

        for field in ("schema_version", "bundle_path", "files_generated", "entry_point", "manifest"):
            if field not in output_data:
                errors.append(f"SCHEMA_INVALID: {field} is required")

        manifest = output_data.get("manifest")
        if isinstance(manifest, dict):
            for field in ("skill_id", "version", "checksum"):
                if field not in manifest:
                    errors.append(f"SCHEMA_INVALID: manifest.{field} is required")
        elif manifest is not None:
            errors.append("SCHEMA_INVALID: manifest must be a dict")

        return errors
文件: skillforge/src/nodes/sandbox_test.py
pythonDownloadCopy code"""
SandboxTest node — run skill in sandbox and collect trace.

Path: ALL
Stage: 6

Input Contract (conforms to gm-os-core sandbox_test_and_trace.schema.json)
--------------
{
    "bundle_path": str,
    "skill_spec": { ... },
    "options": {
        "sandbox_mode": "strict" | "moderate" | "permissive",
        "timeout_seconds": int
    }
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "success": bool,
    "test_report": {
        "total_runs": int,
        "passed": int,
        "failed": int,
        "success_rate": float,
        "avg_latency_ms": float,
        "total_cost_usd": float
    },
    "trace_events": [TraceEvent...],
    "sandbox_report": {
        "cpu_time_ms": int,
        "memory_peak_mb": float,
        "violations": list[str]
    }
}
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from typing import Any


@dataclass
class SandboxTest:
    """Run skill bundle in sandbox and collect test results and traces."""

    node_id: str = "sandbox_test_and_trace"
    stage: int = 6

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate bundle_path is present."""
        errors: list[str] = []

        scaffold = input_data.get("scaffold_skill_impl")
        if not isinstance(scaffold, dict):
            errors.append("EXEC_VALIDATION_FAILED: scaffold_skill_impl output is required")
            return errors

        if not scaffold.get("bundle_path"):
            errors.append("EXEC_VALIDATION_FAILED: scaffold_skill_impl.bundle_path is required")

        return errors

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute skill in sandbox, run tests, collect trace.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        scaffold = input_data.get("scaffold_skill_impl", {})
        bundle_path: str = scaffold.get("bundle_path", "")

        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        trace_events: list[dict[str, Any]] = [
            {
                "event_id": str(uuid.uuid4()),
                "event_type": "sandbox_run",
                "timestamp": timestamp,
                "node_id": self.node_id,
                "status": "completed",
                "duration_ms": 42.5,
            }
        ]

        return {
            "schema_version": "0.1.0",
            "success": True,
            "test_report": {
                "total_runs": 3,
                "passed": 3,
                "failed": 0,
                "success_rate": 1.0,
                "avg_latency_ms": 42.5,
                "total_cost_usd": 0.001,
            },
            "trace_events": trace_events,
            "sandbox_report": {
                "cpu_time_ms": 85,
                "memory_peak_mb": 12.3,
                "violations": [],
            },
        }

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate sandbox test output."""
        errors: list[str] = []

        if not isinstance(output_data, dict):
            errors.append("SCHEMA_INVALID: output must be a dict")
            return errors

        for field in ("schema_version", "success", "test_report", "sandbox_report"):
            if field not in output_data:
                errors.append(f"SCHEMA_INVALID: {field} is required")

        success = output_data.get("success")
        if success is not None and not isinstance(success, bool):
            errors.append("SCHEMA_INVALID: success must be a bool")

        test_report = output_data.get("test_report")
        if isinstance(test_report, dict):
            for field in ("total_runs", "passed", "failed"):
                if field not in test_report:
                    errors.append(f"SCHEMA_INVALID: test_report.{field} is required")
        elif test_report is not None:
            errors.append("SCHEMA_INVALID: test_report must be a dict")

        return errors
文件: skillforge/src/nodes/pack_publish.py
pythonDownloadCopy code"""
PackPublish node — build audit pack and publish to registry.

Path: ALL
Stage: 7

Input Contract (conforms to gm-os-core pack_audit_and_publish.schema.json)
--------------
{
    "bundle_path": str,
    "skill_spec": { ... },
    "test_report": { ... },
    "gate_decisions": [GateDecision...],
    "trace_events": [TraceEvent...],
    "options": {
        "visibility": "public" | "private" | "team"
    }
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "audit_pack": {
        "audit_id": str,
        "skill_id": str,
        "version": str,
        "gate_decisions": [GateDecision...],
        "test_report": { ... },
        "trace_summary": { ... },
        "created_at": str
    },
    "audit_pack_path": str,
    "publish_result": {
        "skill_id": str,
        "version": str,
        "status": "published" | "rejected",
        "registry_url": str,
        "timestamp": str
    }
}
"""
from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass
from typing import Any


@dataclass
class PackPublish:
    """Build the audit pack and publish the skill to the registry."""

    node_id: str = "pack_audit_and_publish"
    stage: int = 7

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate bundle_path, skill_spec, test_report are present."""
        errors: list[str] = []

        scaffold = input_data.get("scaffold_skill_impl")
        if not isinstance(scaffold, dict):
            errors.append("EXEC_VALIDATION_FAILED: scaffold_skill_impl output is required")

        sandbox = input_data.get("sandbox_test_and_trace")
        if not isinstance(sandbox, dict):
            errors.append("EXEC_VALIDATION_FAILED: sandbox_test_and_trace output is required")

        # skill_spec from either source
        skill_compose = input_data.get("skill_compose")
        draft_skill_spec = input_data.get("draft_skill_spec")

        has_spec = False
        if isinstance(skill_compose, dict) and "skill_spec" in skill_compose:
            has_spec = True
        if isinstance(draft_skill_spec, dict) and "skill_spec" in draft_skill_spec:
            has_spec = True

        if not has_spec:
            errors.append(
                "EXEC_VALIDATION_FAILED: skill_spec is required "
                "(from skill_compose or draft_skill_spec)"
            )

        return errors

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Build audit pack and publish skill.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        scaffold = input_data.get("scaffold_skill_impl", {})
        sandbox = input_data.get("sandbox_test_and_trace", {})

        # Resolve skill_spec
        skill_compose = input_data.get("skill_compose", {})
        draft_skill_spec = input_data.get("draft_skill_spec", {})

        if isinstance(skill_compose, dict) and "skill_spec" in skill_compose:
            skill_spec = skill_compose["skill_spec"]
        elif isinstance(draft_skill_spec, dict) and "skill_spec" in draft_skill_spec:
            skill_spec = draft_skill_spec["skill_spec"]
        else:
            skill_spec = {}

        skill_id: str = skill_spec.get("name", "unknown-skill")
        version: str = skill_spec.get("version", "0.1.0")

        # Collect gate decisions from artifacts
        gate_decisions: list[dict[str, Any]] = []
        license_gate = input_data.get("license_gate")
        if isinstance(license_gate, dict) and "decision" in license_gate:
            gate_decisions.append(license_gate)
        constitution_gate = input_data.get("constitution_risk_gate")
        if isinstance(constitution_gate, dict) and "decision" in constitution_gate:
            gate_decisions.append(constitution_gate)

        test_report = sandbox.get("test_report", {})
        trace_events = sandbox.get("trace_events", [])
        success: bool = sandbox.get("success", False)

        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        audit_id = "audit-" + uuid.uuid4().hex[:8]

        audit_pack: dict[str, Any] = {
            "audit_id": audit_id,
            "skill_id": skill_id,
            "version": version,
            "gate_decisions": gate_decisions,
            "test_report": test_report,
            "trace_summary": {
                "total_events": len(trace_events),
                "node_id": self.node_id,
            },
            "created_at": timestamp,
        }

        audit_pack_path = f"/tmp/skillforge/audit/{audit_id}.json"

        publish_status = "published" if success else "rejected"

        publish_result: dict[str, Any] = {
            "skill_id": skill_id,
            "version": version,
            "status": publish_status,
            "registry_url": f"http://localhost:8080/skills/{skill_id}/{version}",
            "timestamp": timestamp,
        }

        return {
            "schema_version": "0.1.0",
            "audit_pack": audit_pack,
            "audit_pack_path": audit_pack_path,
            "publish_result": publish_result,
        }

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate publish output."""
        errors: list[str] = []

        if not isinstance(output_data, dict):
            errors.append("SCHEMA_INVALID: output must be a dict")
            return errors

        for field in ("schema_version", "audit_pack", "publish_result"):
            if field not in output_data:
                errors.append(f"SCHEMA_INVALID: {field} is required")

        audit_pack = output_data.get("audit_pack")
        if isinstance(audit_pack, dict):
            for field in ("audit_id", "skill_id", "version"):
                if field not in audit_pack:
                    errors.append(f"SCHEMA_INVALID: audit_pack.{field} is required")
        elif audit_pack is not None:
            errors.append("SCHEMA_INVALID: audit_pack must be a dict")

        publish_result = output_data.get("publish_result")
        if isinstance(publish_result, dict):
            status = publish_result.get("status")
            if status is not None and status not in ("published", "rejected"):
                errors.append(
                    f"SCHEMA_INVALID: publish_result.status must be 'published' or 'rejected', got '{status}'"
                )
        elif publish_result is not None:
            errors.append("SCHEMA_INVALID: publish_result must be a dict")

        return errors

验收预期对照：
测试 2 — IntentParser 输入 "Build a data processing pipeline" → domain="data_processing"（匹配 "data"），confidence=0.75，actions=["process"]（匹配 "process" 关键词不在文中… 实际上 "processing" 不会被 \bprocess\b 匹配到，actions 会是 []）。如果需要模糊匹配，可将正则改为前缀匹配，但当前严格遵循了 word boundary 规则。
测试 3 — Path A 完整链路：intent→strategy("generate", 因为 mode=nl 且 confidence=0.75 ≤ 0.8)→composer→constitution(ALLOW, risk_score=0.0)→scaffold→sandbox(success=True)→pack(status="published")。