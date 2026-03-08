import os
import json
import time

store_dir = r"D:\GM-SkillForge\AuditPack"
os.makedirs(store_dir, exist_ok=True)

dummy_pack1 = {
    "run_id": "RUN-TEST-001",
    "status": "PASSED",
    "intent_id": "rag_test",
    "pack_version": "v1.0",
    "generated_at": "2026-02-21T13:45:00Z",
    "evidence_ref": "EV-TEST-001",
    "repo_url": "https://github.com/mock/repo",
    "commit_sha": "abcd1234abcd1234abcd1234abcd1234abcd1234"
}

dummy_pack2 = {
    "run_id": "RUN-TEST-002",
    "status": "REJECTED",
    "intent_id": "audit_fail",
    "pack_version": "v1.0",
    "generated_at": "2026-02-21T13:46:00Z",
    "evidence_ref": "EV-TEST-002",
    "repo_url": "https://github.com/mock/repo",
    "commit_sha": "abcd1234abcd1234abcd1234abcd1234abcd1234"
}

with open(os.path.join(store_dir, "pack_RUN-TEST-001.json"), "w") as f:
    json.dump(dummy_pack1, f)
    
with open(os.path.join(store_dir, "pack_RUN-TEST-002.json"), "w") as f:
    json.dump(dummy_pack2, f)

print("Created dummy AuditPacks")
