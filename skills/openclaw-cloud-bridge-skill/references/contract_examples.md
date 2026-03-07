# Contract Examples

## task_contract.json (minimal)

```json
{
  "schema_version": "1.0.0",
  "task_id": "ocb-20260302-120000-1a2b3c4d",
  "created_at_utc": "2026-03-02T12:00:00Z",
  "objective": "OpenClaw 云端健康巡检",
  "relay": {
    "agent": "Antigravity-Gemini",
    "channel": "BlueLobster-Cloud"
  },
  "target": {
    "project_dir": "/root/openclaw-box"
  },
  "policy": {
    "fail_closed": true,
    "max_duration_sec": 900,
    "max_commands": 10
  },
  "command_allowlist": [
    "docker compose ps",
    "docker compose logs --since 10m openclaw-agent | tail -n 200",
    "ss -lntp | grep 18789 || true"
  ],
  "acceptance": [
    "openclaw_core is Up",
    "no EACCES in logs"
  ],
  "required_artifacts": [
    "execution_receipt.json",
    "stdout.log",
    "stderr.log",
    "audit_event.json"
  ]
}
```

## execution_receipt.json (minimal)

```json
{
  "schema_version": "1.0.0",
  "task_id": "ocb-20260302-120000-1a2b3c4d",
  "executor": "openclaw-cloud",
  "started_at_utc": "2026-03-02T12:01:00Z",
  "finished_at_utc": "2026-03-02T12:01:40Z",
  "status": "success",
  "executed_commands": [
    "docker compose ps",
    "docker compose logs --since 10m openclaw-agent | tail -n 200",
    "ss -lntp | grep 18789 || true"
  ],
  "exit_code": 0,
  "artifacts": [
    "execution_receipt.json",
    "stdout.log",
    "stderr.log",
    "audit_event.json"
  ],
  "summary": "openclaw_core is Up; no EACCES found in last 10m logs."
}
```
