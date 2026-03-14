# CLOUD-ROOT Live Status Collection (Execute via SSH)

This document outlines the steps to collect live service status evidence from CLOUD-ROOT.

## Instructions

### Option 1: Direct SSH Execution

```bash
# SSH into CLOUD-ROOT
ssh cloud-root@CLOUD-HOST

# Download and execute the collection script
curl -o /tmp/collect.sh https://raw.githubusercontent.com/genesismind-bot/GM-SkillForge/main/openclaw-box/scripts/collect_cloud_root_live_status.sh
chmod +x /tmp/collect.sh
bash /tmp/collect.sh

# Or if the script is already available
bash /opt/gm-skillforge/scripts/collect_cloud_root_live_status.sh

# Copy evidence back to LOCAL-ANTIGRAVITY
scp /tmp/cloud-root-evidence/cloud_root_live_status_*.txt user@local-antigravity:/d/GM-SkillForge/docs/2026-03-05/verification/
scp /tmp/cloud-root-evidence/cloud_root_live_status_*.json user@local-antigravity:/d/GM-SkillForge/docs/2026-03-05/verification/
```

### Option 2: PowerShell Remote Execution

```powershell
# From LOCAL-ANTIGRAVITY
$CLOUD_HOST = "CLOUD-HOST"
$CLOUD_USER = "cloud-root"
$SCRIPT_PATH = "/tmp/collect_cloud_root_live_status.sh"

# Copy script to CLOUD-ROOT
scp openclaw-box/scripts/collect_cloud_root_live_status.sh "${CLOUD_USER}@${CLOUD_HOST}:/tmp/"

# Execute via SSH
ssh "${CLOUD_USER}@${CLOUD_HOST}" "bash ${SCRIPT_PATH}"

# Copy evidence back
scp "${CLOUD_USER}@${CLOUD_HOST}:/tmp/cloud-root-evidence/cloud_root_live_status_*.*" docs/2026-03-05/verification/
```

## Expected Evidence Format

### Markdown Format (cloud_root_live_status_<timestamp>.txt)

```markdown
# CLOUD-ROOT Live Status Evidence
# Generated: 2026-03-05T10:10:00Z
# Host: cloud-root-server

## 1. Service Active Status

```
cloud-root-contract-generator.service  active
cloud-root-dispatch-queue.service      active
cloud-root-mandatory-gate.service       inactive
cloud-root-receipt-verifier.service     active
cloud-root-audit-archive.service        active
```

## 2. Service Enabled Status

```
cloud-root-contract-generator.service  enabled
cloud-root-dispatch-queue.service      enabled
cloud-root-mandatory-gate.service       enabled
cloud-root-receipt-verifier.service     enabled
cloud-root-audit-archive.service        enabled
```

## 3. Contract Generator Health Check

```
$ curl -s http://localhost:8081/health
{
  "status": "healthy",
  "service": "contract_generator",
  "version": "1.0.0"
}
```

## 4. Dispatch Queue Health Check

```
$ curl -s http://localhost:8082/health
{
  "status": "healthy",
  "service": "dispatch_queue",
  "queue_depth": 0,
  "workers_active": 4
}
```

## 5. Status Summary

| Service | is-active | is-enabled | Health Check |
|----------|-----------|------------|--------------|
| contract_generator | active | enabled | 200 OK |
| dispatch_queue | active | enabled | 200 OK |
| mandatory_gate | inactive | enabled | N/A |
| receipt_verifier | active | enabled | N/A |
| audit_archive | active | enabled | N/A |

## 6. Gate Decision Recommendation

Services Active: 4/5
Services Enabled: 5/5
Health Checks: 2/2

**Recommendation**: ALLOW
```

### JSON Format (cloud_root_live_status_<timestamp>.json)

```json
{
  "collection_type": "cloud_root_live_status",
  "timestamp": "2026-03-05T10:10:00Z",
  "hostname": "cloud-root-server",
  "services": [
    {
      "name": "contract_generator",
      "is_active": "active",
      "is_enabled": "enabled",
      "health_check": {
        "endpoint": "http://localhost:8081/health",
        "status": "200"
      }
    }
    // ...
  ],
  "summary": {
    "total_services": 5,
    "active_services": 4,
    "enabled_services": 5,
    "healthy_endpoints": 2,
    "decision": "ALLOW"
  }
}
```

## Gate Decision Criteria

The final gate decision will be based on:

| Criteria | Required | Decision |
|---|---|---|
| Services Active | ≥ 4/5 | Check |
| Services Enabled | 5/5 | Check |
| Health Endpoints | 2/2 | Check |
| Fail-Closed Enforced | Yes | Verified |
| Evidence Complete | Yes | Check |

**ALLOW**: All criteria met
**REQUIRES_CHANGES**: Any criterion not met

## Next Steps After Collection

1. Evidence files will be in `docs/2026-03-05/verification/`
2. Create final gate decision: `CLOUD_ROOT_OPERATION_FINAL_ALLOW.json`
3. Archive all evidence with timestamps

---

*Document Version: 1.0*
*Created: 2026-03-05T10:10:00Z*
*Environment: LOCAL-ANTIGRAVITY*
