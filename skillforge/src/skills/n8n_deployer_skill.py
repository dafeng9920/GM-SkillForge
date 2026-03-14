from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

from skills.experience_capture import FixKind, capture_gate_event

SKILL_NAME = "n8n_deployer_skill"
SKILL_VERSION = "0.1.0"

@dataclass
class DeploymentResult:
    """Result of n8n deployment."""
    ok: bool
    workflow_id: Optional[str] = None
    webhook_url: Optional[str] = None
    error_message: Optional[str] = None
    evidence_ref: Optional[str] = None

class N8NDeployerSkill:
    """
    Skill: n8n_deployer_skill — Deploys or updates an n8n workflow.
    
    The Mapping Layer (Phase 3) actuator.
    """

    def __init__(self, api_base: str = "http://localhost:5678"):
        self.skill_name = SKILL_NAME
        self.version = SKILL_VERSION
        self.api_base = api_base

    def _compute_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def deploy(self, workflow_json: Dict[str, Any]) -> DeploymentResult:
        """
        Deploys workflow to n8n. (Mocked for Phase 3 MVP)
        """
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        run_id = f"ND-{int(time.time() * 1000)}"
        
        workflow_name = workflow_json.get("name", "unnamed_workflow")
        
        # Simulated API call success
        workflow_id = f"wf_{int(time.time())}"
        webhook_path = workflow_json.get("nodes", [{}])[0].get("parameters", {}).get("path", "webhook/default")
        webhook_url = f"{self.api_base}/{webhook_path}"

        content_hash = self._compute_hash(json.dumps(workflow_json, sort_keys=True))
        evidence_ref = f"deployment_receipt://{run_id}"

        # Capture Experience
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
            fix_kind=FixKind.PUBLISH_PACK,
            summary=f"Workflow '{workflow_name}' deployed successfully to n8n.",
            metadata={"workflow_id": workflow_id, "webhook_url": webhook_url}
        )

        return DeploymentResult(
            ok=True,
            workflow_id=workflow_id,
            webhook_url=webhook_url,
            evidence_ref=evidence_ref
        )

def main():
    """Manual test."""
    deployer = N8NDeployerSkill()
    mock_workflow = {"name": "Test Workflow", "nodes": [{"parameters": {"path": "test"}}]}
    result = deployer.deploy(mock_workflow)
    if result.ok:
        print(f"Deployment Success!")
        print(f"Workflow ID: {result.workflow_id}")
        print(f"Webhook URL: {result.webhook_url}")

if __name__ == "__main__":
    main()
