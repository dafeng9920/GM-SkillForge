from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from skills.experience_capture import FixKind, capture_gate_event

SKILL_NAME = "re_planner_skill"
SKILL_VERSION = "0.1.0"

@dataclass
class RecourseStrategy:
    """Strategy for recovering from a failure."""
    action: str  # 'retry_with_params' | 'human_intervention' | 'fallback_path'
    rationale: str
    suggested_params: Dict[str, Any] = field(default_factory=dict)
    instructions_for_user: Optional[str] = None

@dataclass
class RePlannerResult:
    """Result of the re-planning process."""
    ok: bool
    strategy: Optional[RecourseStrategy] = None
    error_message: Optional[str] = None

class RePlannerSkill:
    """
    Skill: re_planner_skill — Diagnoses n8n failures and suggests recourse strategies.
    
    The Adaptive Recourse (Phase 4) brain.
    """

    def __init__(self):
        self.skill_name = SKILL_NAME
        self.version = SKILL_VERSION

    def diagnose_and_plan(
        self, 
        error_context: Dict[str, Any], 
        skill_spec_name: str
    ) -> RePlannerResult:
        """
        Analyzes error context and returns a recourse strategy.
        """
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        run_id = f"RP-{int(time.time() * 1000)}"
        
        node_name = error_context.get("node", "unknown_node")
        error_message = error_context.get("message", "No error details provided.")
        
        # Simulated LLM diagnosis logic
        strategy = None
        
        if "timeout" in error_message.lower() or "408" in error_message:
            strategy = RecourseStrategy(
                action="retry_with_params",
                rationale="Service timeout detected. Suggesting retry with increased timeout limit.",
                suggested_params={"timeout": 60000}
            )
        elif "rate limit" in error_message.lower() or "429" in error_message:
            strategy = RecourseStrategy(
                action="fallback_path",
                rationale="Rate limit hit on primary source. Suggesting switch to secondary discovery source.",
                suggested_params={"source_priority": "secondary"}
            )
        else:
            strategy = RecourseStrategy(
                action="human_intervention",
                rationale=f"Unexpected error in node '{node_name}': {error_message}. Manual diagnostic required.",
                instructions_for_user=f"Please check the connection settings for node '{node_name}' and verify the API key."
            )

        content_hash = hashlib.sha256(json.dumps(error_context).encode()).hexdigest()
        evidence_ref = f"recourse_plan://{run_id}"

        # Capture Experience (L3 Standard)
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
            summary=f"Recourse plan generated for skill '{skill_spec_name}' following error in '{node_name}'.",
            metadata={"strategy": strategy.action, "node": node_name}
        )

        return RePlannerResult(ok=True, strategy=strategy)

def main():
    """Manual test."""
    planner = RePlannerSkill()
    error_ctx = {
        "node": "HTTP Request (network)",
        "message": "Error: 408 Request Timeout"
    }
    result = planner.diagnose_and_plan(error_ctx, "reddit_scraper")
    if result.ok:
        print(f"Strategy: {result.strategy.action}")
        print(f"Rationale: {result.strategy.rationale}")

if __name__ == "__main__":
    main()
