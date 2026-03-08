import os
import json
import time
from datetime import datetime, timezone

store_dir = r"D:\GM-SkillForge\data\audit_packs"
os.makedirs(store_dir, exist_ok=True)

ts = int(time.time())
now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

dummy_pack1 = {
    "receipt_id": "RCP-L45-DEMO-001",
    "run_id": "RUN-N8N-1771681200-13E71147",
    "evidence_ref": "EV-N8N-INTENT-1771681200-C44A6259",
    "gate_decision": "ALLOW",
    "executed_at": now_iso,
    "skill_id": "l45_n8n_orchestration_boundary",
    "workflow_id": "wf_demo_001",
    "permit_token": "PERMIT-20260221-31B3E6BC",
    "audit_pack_ref": "audit://packs/L45-D2-DEMO",
    "replay_pointer": {
        "snapshot_ref": "snapshot://L45-D2-DEMO/v1",
        "at_time": now_iso,
        "revision": "v1.0.0",
        "evidence_bundle_ref": "evidence://bundles/L45-D2-DEMO"
    },
    "evidence_chain": {
        "evidence_refs": [
            {
                "ref_id": "EV-COG-L4-DEMO-A1B2C3D4",
                "type": "cognition",
                "source_locator": "cognition://dims/DEMO-A1B2C3D4",
                "content_hash": "sha256:abc123def456",
                "timestamp": now_iso,
                "tool_revision": "v1.0.0"
            }
        ]
    },
    "output": {
        "status": "success",
        "data": {
            "intent": "test_intent_1",
            "executed": True
        }
    }
}

with open(os.path.join(store_dir, "RCP-L45-DEMO-001.json"), "w") as f:
    json.dump(dummy_pack1, f, indent=2)
    
print(f"Created dummy AuditPack in {store_dir}")
