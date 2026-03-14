from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from skills.experience_capture import FixKind, capture_gate_event
from skills.intent_parser_skill import DemandSpec

SKILL_NAME = "source_strategy_skill"
SKILL_VERSION = "0.1.0"

@dataclass
class SourceStrategy:
    """Strategy decision for skill sourcing."""
    strategy: str  # "DISCOVER" | "GENERATE" | "SYNTHESIZE"
    rationale: str
    confidence: float
    next_steps: List[str]

@dataclass
class SourceStrategyResult:
    """Result of strategy decision."""
    ok: bool
    strategy: Optional[SourceStrategy] = None
    evidence_ref: Optional[str] = None
    error_message: Optional[str] = None

class SourceStrategySkill:
    """
    Skill: source_strategy_skill — Decides the sourcing path (Discover vs Generate).
    
    The second step in the Skill Factory pipeline (Phase 2).
    """

    def __init__(self):
        self.skill_name = SKILL_NAME
        self.version = SKILL_VERSION

    def _compute_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def decide(self, demand_spec: DemandSpec) -> SourceStrategyResult:
        """
        Decides the sourcing strategy based on DemandSpec.
        """
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        run_id = f"SS-{int(time.time() * 1000)}"

        # Logic for strategy decision
        # In a real system, this would query a Skill Registry or GitHub API.
        
        strategy = "GENERATE"
        confidence = 0.8
        rationale = "No existing skill matches this intent well. Proposing new generation."
        next_steps = ["Invoke skill-composer-skill", "Perform Constitution Risk check"]

        if demand_spec.domain == "devops":
            strategy = "DISCOVER"
            confidence = 0.9
            rationale = "High probability of finding matching DevOps skills in existing libraries."
            next_steps = ["Invoke github-discovery-skill", "Scan for fit score"]
        elif "Reddit" in demand_spec.user_goal:
            strategy = "SYNTHESIZE"
            confidence = 0.7
            rationale = "Can be synthesized from scraper-skill and email-skill."
            next_steps = ["Check component compatibility", "Compose Skill Spec"]

        source_strategy = SourceStrategy(
            strategy=strategy,
            rationale=rationale,
            confidence=confidence,
            next_steps=next_steps
        )

        content_hash = self._compute_hash(json.dumps(source_strategy.__dict__, sort_keys=True))
        evidence_ref = f"source_strategy://{run_id}"

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
            fix_kind=FixKind.GATE_DECISION,
            summary=f"Strategy: {strategy} decided for intent {demand_spec.intent_id}",
            metadata={"strategy": strategy, "confidence": confidence}
        )

        return SourceStrategyResult(
            ok=True,
            strategy=source_strategy,
            evidence_ref=evidence_ref
        )

def main():
    """Manual test."""
    from skills.intent_parser_skill import IntentParserSkill
    
    parser = IntentParserSkill()
    strategist = SourceStrategySkill()
    
    nl_input = "帮我做一个定时抓取 Reddit 数据并发送邮件的工具"
    parse_result = parser.parse(nl_input)
    
    if parse_result.ok:
        strategy_result = strategist.decide(parse_result.demand_spec)
        if strategy_result.ok:
            print(f"Strategy Result: {strategy_result.strategy.strategy}")
            print(f"Rationale: {strategy_result.strategy.rationale}")
            print(f"Next Steps: {strategy_result.strategy.next_steps}")

if __name__ == "__main__":
    main()
