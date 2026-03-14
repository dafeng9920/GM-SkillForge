from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from skills.experience_capture import FixKind, capture_gate_event
from skills.intent_parser_skill import DemandSpec
from skills.source_strategy_skill import SourceStrategy
from skills.gates.gate_risk import constitution_risk_gate

SKILL_NAME = "skill_composer_skill"
SKILL_VERSION = "0.1.0"

@dataclass
class SkillSpec:
    """Complete Skill Specification."""
    name: str
    version: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    capabilities: List[str]
    tools_required: List[str]
    constraints: List[str]
    skill_md: str
    schema_version: str = "0.1.0"

@dataclass
class SkillComposerResult:
    """Result of skill composition."""
    ok: bool
    skill_spec: Optional[SkillSpec] = None
    gate_decision: str = "REJECTED"
    evidence_ref: Optional[str] = None
    error_message: Optional[str] = None

class SkillComposerSkill:
    """
    Skill: skill_composer_skill — Synthesizes a SkillSpec and performs risk checks.
    
    The third step in the Skill Factory pipeline (Phase 2).
    """

    def __init__(self):
        self.skill_name = SKILL_NAME
        self.version = SKILL_VERSION

    def _compute_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def compose(self, demand_spec: DemandSpec, strategy: SourceStrategy) -> SkillComposerResult:
        """
        Synthesizes SkillSpec from DemandSpec and SourceStrategy.
        """
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        run_id = f"SC-{int(time.time() * 1000)}"

        # 1. Synthesize Spec (Simulated logic)
        skill_name = demand_spec.user_goal.lower().replace(" ", "_")[:32]
        if not skill_name:
            skill_name = "auto_generated_skill"

        # Map domain to capabilities
        capabilities = ["llm"]
        if any(kw in demand_spec.user_goal.lower() for kw in ["data", "fetch", "network", "reddit", "url"]):
            capabilities.append("network")
        if any(kw in demand_spec.user_goal.lower() for kw in ["file", "write", "save", "local"]):
            capabilities.append("file_write")
        
        # PROHIBITED CAPABILITY DETECTION (Fail-Closed)
        # English and Chinese keywords
        if any(kw in demand_spec.user_goal.lower() for kw in [
            "admin", "root", "sudo", "privilege", "system", "registry",
            "提权", "管理员", "系统", "注册表", "提升权限"
        ]):
            capabilities.append("privileged_execution")
        if any(kw in demand_spec.user_goal.lower() for kw in [
            "modify_system", "delete_root", "format_c",
            "修改系统", "删除根目录", "格式化"
        ]):
            capabilities.append("system_modification")
        
        # Tools required
        tools_required = ["python3"]
        if "network" in capabilities:
            tools_required.append("curl")

        skill_spec = SkillSpec(
            name=skill_name,
            version="0.1.0",
            description=f"Skill generated for goal: {demand_spec.user_goal}",
            input_schema={
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"]
            },
            output_schema={
                "type": "object",
                "properties": {"result": {"type": "string"}},
                "required": ["result"]
            },
            capabilities=capabilities,
            tools_required=tools_required,
            constraints=demand_spec.constraints,
            skill_md=f"# {skill_name}\n\n{demand_spec.user_goal}\n"
        )

        # 2. Perform Constitution Risk Gate (Hard Check)
        # Convert to dict for gate
        spec_dict = json.loads(json.dumps(skill_spec.__dict__))
        gate_result = constitution_risk_gate(spec_dict)
        
        gate_decision = gate_result.get("gate_decision", "REJECTED")
        
        if gate_decision != "PASSED":
            return SkillComposerResult(
                ok=False,
                gate_decision="REJECTED",
                error_message=f"Constitution Risk Gate rejected the spec: {gate_result.get('error_code')}",
                evidence_ref=gate_result.get("evidence_refs", [{}])[0].get("source_locator")
            )

        content_hash = self._compute_hash(json.dumps(spec_dict, sort_keys=True))
        evidence_ref = f"skill_spec://{run_id}"

        # 3. Capture Experience if PASSED
        capture_gate_event(
            gate_node=self.skill_name,
            gate_decision="PASSED",
            evidence_refs=[{
                "issue_key": run_id,
                "source_locator": evidence_ref,
                "content_hash": content_hash,
                "tool_revision": f"{self.skill_name}-{self.version}",
                "timestamp": timestamp,
            }],
            fix_kind=FixKind.ADD_CONTRACT,
            summary=f"SkillSpec composed and passed risk gate for: {skill_name}",
            metadata={"capabilities": capabilities, "gate_decision": gate_decision}
        )

        return SkillComposerResult(
            ok=True,
            skill_spec=skill_spec,
            gate_decision="PASSED",
            evidence_ref=evidence_ref
        )

def main():
    """Manual test."""
    from skills.intent_parser_skill import IntentParserSkill
    from skills.source_strategy_skill import SourceStrategySkill
    
    parser = IntentParserSkill()
    strategist = SourceStrategySkill()
    composer = SkillComposerSkill()
    
    nl_input = "帮我做一个抓取 Reddit 数据并保存到本地文件的工具"
    parse_result = parser.parse(nl_input)
    
    if parse_result.ok:
        strategy_result = strategist.decide(parse_result.demand_spec)
        if strategy_result.ok:
            composition_result = composer.compose(parse_result.demand_spec, strategy_result.strategy)
            
            if composition_result.ok:
                print(f"Composition SUCCESS: {composition_result.skill_spec.name}")
                print(f"Decision: {composition_result.gate_decision}")
                print(f"Capabilities: {composition_result.skill_spec.capabilities}")
            else:
                print(f"Composition FAILED: {composition_result.error_message}")

if __name__ == "__main__":
    main()
