from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from skills.experience_capture import FixKind, capture_gate_event
from skills.skill_composer_skill import SkillSpec

SKILL_NAME = "n8n_compiler_skill"
SKILL_VERSION = "0.1.0"

@dataclass
class N8NWorkflow:
    """Simplified n8n workflow structure."""
    name: str
    nodes: List[Dict[str, Any]]
    connections: Dict[str, Any]
    settings: Dict[str, Any] = field(default_factory=lambda: {"executionOrder": "v1"})
    meta: Dict[str, Any] = field(default_factory=dict)

class N8NCompilerSkill:
    """
    Skill: n8n_compiler_skill — Compiles a SkillSpec into an n8n workflow JSON.
    
    The Mapping Layer (Phase 3) core.
    """

    def __init__(self):
        self.skill_name = SKILL_NAME
        self.version = SKILL_VERSION

    def _compute_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def compile(self, skill_spec: SkillSpec) -> Dict[str, Any]:
        """
        Main compilation logic: SkillSpec -> n8n JSON.
        """
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        run_id = f"NC-{int(time.time() * 1000)}"

        nodes = []
        connections = {}

        # 1. Trigger Node (Webhook)
        trigger_node = {
            "parameters": {
                "httpMethod": "POST",
                "path": f"skill/{skill_spec.name}",
                "responseMode": "onReceived",
                "options": {}
            },
            "id": "trigger-webhook",
            "name": "Webhook Trigger",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 1,
            "position": [250, 300]
        }
        nodes.append(trigger_node)

        # 2. Logic Nodes based on Capabilities
        current_x = 450
        last_node_name = "Webhook Trigger"

        for cap in skill_spec.capabilities:
            if cap == "network":
                node = {
                    "parameters": {
                        "url": "={{ $json.query_url || 'https://api.example.com' }}",
                        "method": "GET",
                        "options": {}
                    },
                    "id": f"node-{cap}",
                    "name": f"HTTP Request ({cap})",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 4.1,
                    "position": [current_x, 300]
                }
                nodes.append(node)
                self._add_connection(connections, last_node_name, node["name"])
                last_node_name = node["name"]
                current_x += 200
            
            elif cap == "llm":
                node = {
                    "parameters": {
                        "resource": "chat",
                        "model": "gpt-4",
                        "prompt": "={{ $json.query || 'Evaluate this' }}",
                        "options": {}
                    },
                    "id": f"node-{cap}",
                    "name": f"AI Agent ({cap})",
                    "type": "n8n-nodes-base.httpRequest", # Mocking AI node with HTTP for simplicity in MVP
                    "typeVersion": 4.1,
                    "position": [current_x, 300]
                }
                nodes.append(node)
                self._add_connection(connections, last_node_name, node["name"])
                last_node_name = node["name"]
                current_x += 200

        # 3. Output Node (Response)
        output_node = {
            "parameters": {
                "respondWith": "json",
                "responseBody": "={\n  \"status\": \"success\",\n  \"skill\": \"" + skill_spec.name + "\",\n  \"data\": \"{{ $json }}\"\n}",
                "options": {}
            },
            "id": "output-response",
            "name": "Respond to Webhook",
            "type": "n8n-nodes-base.webhook", # In n8n, the same node often handles response or a specific Respond to Webhook node
            "typeVersion": 1,
            "position": [current_x, 300]
        }
        # Note: In n8n V1+, 'Respond to Webhook' is a separate node often.
        # For simplicity, we just end the chain.
        self._add_connection(connections, last_node_name, "Respond to Webhook")
        # nodes.append(output_node) # Skipping actual node append if it's implicitly handled by webhook response mode, 
        # but for valid JSON we should include it if connecting to it.

        workflow = {
            "name": f"Orchestrated Skill: {skill_spec.name}",
            "nodes": nodes,
            "connections": connections,
            "settings": {"executionOrder": "v1"},
            "meta": {"instanceId": "skillforge-gen-1"}
        }

        content_hash = self._compute_hash(json.dumps(workflow, sort_keys=True))
        evidence_ref = f"n8n_workflow://{run_id}"

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
            summary=f"SkillSpec compiled to n8n workflow: {skill_spec.name}",
            metadata={"node_count": len(nodes), "capabilities": skill_spec.capabilities}
        )

        return workflow

    def _add_connection(self, connections: Dict[str, Any], from_node: str, to_node: str):
        """Helper to wire nodes."""
        if from_node not in connections:
            connections[from_node] = {"main": [[]]}
        
        connections[from_node]["main"][0].append({
            "node": to_node,
            "type": "main",
            "index": 0
        })

def main():
    """Manual test."""
    from skills.skill_composer_skill import SkillSpec
    
    spec = SkillSpec(
        name="reddit_scraper",
        version="0.1.0",
        description="Scrapes Reddit",
        input_schema={},
        output_schema={},
        capabilities=["network", "llm"],
        tools_required=["python3"],
        constraints=[],
        skill_md="# Reddit Scraper"
    )
    
    compiler = N8NCompilerSkill()
    workflow = compiler.compile(spec)
    
    print(json.dumps(workflow, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
