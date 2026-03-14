import json
import os
import subprocess
import socket
from pathlib import Path

def run_cmd(cmd):
    print(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result

task_id = "r1-cloud-smoke-20260305-2353"
dispatch_dir = Path("/root/gm-skillforge/.tmp/openclaw-dispatch") / task_id
dispatch_dir.mkdir(parents=True, exist_ok=True)

# 1. Identity Proof
print("--- CLOUD LOBSTER IDENTITY ---")
print(f"Hostname: {socket.gethostname()}")
try:
    import requests
    print(f"Public IP: {requests.get('https://api.ipify.org').text}")
except:
    print("Could not fetch public IP (requests missing)")
print("------------------------------")

# 2. Create Contract
contract = {
  "task_id": task_id,
  "baseline_id": "AG2-FIXED-CALIBER-TG1-20260304",
  "objective": "R1 CLOUD-ROOT 基础链路回归",
  "environment": "CLOUD-ROOT",
  "constraints": { "fail_closed": True },
  "policy": { "max_commands": 6 },
  "command_allowlist": [
    "cd /root/gm-skillforge",
    "pwd",
    "python3 --version",
    "df -h",
    "free -m",
    "uptime"
  ],
  "required_artifacts": [
    "execution_receipt.json",
    "stdout.log",
    "stderr.log",
    "audit_event.json"
  ],
  "acceptance": [
    "execution_receipt.status == success",
    "execution_receipt.exit_code == 0",
    "executed_commands are a subset of command_allowlist",
    "required_artifacts are complete"
  ]
}

with open(dispatch_dir / "task_contract.json", "w") as f:
    json.dump(contract, f, indent=2)

# 3. Execute Task
os.chdir("/root/gm-skillforge")
exec_cmd = ["python3", "scripts/execute_antigravity_task.py", "--task-id", task_id, "--no-verify"]
res = run_cmd(exec_cmd)
print(res.stdout)
print(res.stderr)

# 4. Final Verification of Artifacts
print("--- REMOTE ARTIFACT CHECK ---")
for f in ["execution_receipt.json", "stdout.log", "audit_event.json"]:
    p = dispatch_dir / f
    status = "EXISTS" if p.exists() else "MISSING"
    print(f"{f}: {status}")
    if p.exists() and f == "stdout.log":
        print("--- STDOUT LOG SNIPPET ---")
        print(p.read_text()[:500])
