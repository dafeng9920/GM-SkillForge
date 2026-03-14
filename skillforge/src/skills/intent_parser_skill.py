from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from skills.experience_capture import FixKind, capture_gate_event

SKILL_NAME = "intent_parser_skill"
SKILL_VERSION = "0.1.0"

@dataclass
class DemandSpec:
    """Structured user intent after NL parsing."""
    intent_id: str
    user_goal: str
    domain: str
    requirements: List[str]
    constraints: List[str]
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class IntentParserResult:
    """Result of intent parsing."""
    ok: bool
    demand_spec: Optional[DemandSpec] = None
    error_message: Optional[str] = None
    evidence_ref: Optional[str] = None

class IntentParserSkill:
    """
    Skill: intent_parser_skill — Parses Natural Language into a structured DemandSpec.
    
    The first step in the Skill Factory pipeline (Phase 2).
    """

    def __init__(self):
        self.skill_name = SKILL_NAME
        self.version = SKILL_VERSION

    def _compute_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def parse(self, nl_input: str, context: Optional[Dict[str, Any]] = None) -> IntentParserResult:
        """
        Parses NL input into DemandSpec.
        
        Currently implemented as a robust heuristic-based mock, but designed to be replaced by LLM.
        """
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        run_id = f"IP-{int(time.time() * 1000)}"
        
        if not nl_input or len(nl_input.strip()) < 5:
            return IntentParserResult(
                ok=False,
                error_message="Input too short or empty. Please provide a clear goal.",
                evidence_ref=None
            )

        # TODO: Replace with real LLM call
        # For now, we simulate LLM output structure
        
        # Simple domain detection
        domain = "unknown"
        if any(kw in nl_input.lower() for kw in ["github", "repo", "git"]):
            domain = "devops"
        elif any(kw in nl_input.lower() for kw in ["seo", "rank", "search"]):
            domain = "marketing"
        elif any(kw in nl_input.lower() for kw in ["finance", "stock", "price"]):
            domain = "finance"

        demand_spec = DemandSpec(
            intent_id=run_id,
            user_goal=nl_input,
            domain=domain,
            requirements=[f"Analyze intent: {nl_input}"],
            constraints=["constitution_v1.md compliance required"],
            context=context or {}
        )

        content_hash = self._compute_hash(json.dumps(demand_spec.__dict__, sort_keys=True))
        evidence_ref = f"demand_spec://{run_id}"

        # Capture experience
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
            summary=f"NL intent parsed into DemandSpec for domain: {domain}",
            metadata={"domain": domain, "input_len": len(nl_input)}
        )

        return IntentParserResult(
            ok=True,
            demand_spec=demand_spec,
            evidence_ref=evidence_ref
        )

def main():
    """Manual test for IntentParserSkill."""
    skill = IntentParserSkill()
    test_inputs = [
        "帮我做一个定时抓取 Reddit 数据并发送邮件的工具",
        "Analyze the SEO performance of my website",
        "Short"
    ]
    
    for input_text in test_inputs:
        print(f"\nEvaluating: {input_text}")
        result = skill.parse(input_text)
        if result.ok:
            print(f"Result: SUCCESS")
            print(f"Domain: {result.demand_spec.domain}")
            print(f"Evidence: {result.evidence_ref}")
        else:
            print(f"Result: FAILED - {result.error_message}")

if __name__ == "__main__":
    main()
