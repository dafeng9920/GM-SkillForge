# Antigravity-1 Execution Guide

## Overview

Antigravity-1 is the execution pattern for creating baseline freezes, generating task contracts, and dispatching tasks to the cloud via Gemini relay.

## Architecture

```
Local SkillForge
    |
    v
[Antigravity-1 Baseline Freeze]
    |
    +-- 1. Create baseline freeze (snapshot with SHA256)
    +-- 2. Generate task contract (with allowlist)
    +-- 3. Prepare handoff note for Gemini
    |
    v
Gemini Relay (Antigravity-Gemini)
    |
    v
Cloud OpenClaw (BlueLobster-Cloud)
    |
    +-- Execute per contract
    +-- Generate execution receipt
    |
    v
Local Verification
    |
    +-- Verify receipt against contract
    +-- PASS/FAIL decision
```

## Components

### 1. Baseline Freeze

Creates a frozen snapshot of baseline artifacts with SHA256 hashes for integrity verification.

**Location**: `.tmp/antigravity-baseline/<baseline_id>/`

**Artifacts**:
- `BASELINE_MANIFEST.json` - Manifest with file hashes
- `ACTIVATION.json` - Activation record
- Snapshot files with SHA256

### 2. Task Contract

Defines the execution contract for cloud OpenClaw with strict constraints.

**Location**: `.tmp/openclaw-dispatch/<task_id>/`

**Artifacts**:
- `task_contract.json` - Formal task contract
- `handoff_note.md` - Human-readable handoff for Gemini
- `dispatch_summary.json` - Summary of dispatch

### 3. Verification

Validates the execution receipt against the original contract.

**Script**: `skills/openclaw-cloud-bridge-skill/scripts/verify_execution_receipt.py`

## Usage

### Quick Start

```bash
# Basic usage with default health check commands
python scripts/antigravity_baseline_freeze.py \
  --objective "OpenClaw 云端健康巡检"

# With baseline smoketest
python scripts/antigravity_baseline_freeze.py \
  --objective "OpenClaw 云端健康巡检" \
  --run-smoketest

# Custom parameters
python scripts/antigravity_baseline_freeze.py \
  --objective "Execute custom task" \
  --project-dir "/root/openclaw-box" \
  --max-duration-sec 1800 \
  --max-commands 20 \
  --run-smoketest
```

### Command Options

| Option | Description | Default |
|--------|-------------|---------|
| `--objective` | Task objective summary | (required) |
| `--project-dir` | Remote project directory | `/root/openclaw-box` |
| `--max-duration-sec` | Maximum execution duration (seconds) | 900 |
| `--max-commands` | Maximum commands to execute | 10 |
| `--baseline-id` | Specific baseline ID | (auto-generated) |
| `--task-id` | Specific task ID | (auto-generated) |
| `--run-smoketest` | Run baseline E2E smoketest | false |
| `--smoketest-input` | Path to smoketest input | `skills/gm-baseline-e2e-smoketest-skill/references/sample_input.json` |

## Default Commands

The following default commands are included for health checks:

1. `docker compose ps` - Check container status
2. `docker compose logs --since 10m openclaw-agent | tail -n 200` - Recent logs
3. `ss -lntp | grep 18789 || true` - Port check
4. `df -h` - Disk usage
5. `free -m` - Memory usage
6. `uptime` - System uptime

## Default Acceptance Criteria

1. `openclaw_core is Up` - Core container running
2. `no EACCES in last 10m logs` - No permission errors
3. `no Unknown model in last 10m logs` - No model errors

## Workflow

### Step 1: Create Baseline Freeze

```bash
python scripts/antigravity_baseline_freeze.py \
  --objective "OpenClaw 云端健康巡检" \
  --run-smoketest
```

This creates:
- Baseline freeze with SHA256-hashed snapshots
- Task contract with command allowlist
- Handoff note for Gemini relay

### Step 2: Dispatch to Cloud

Send the `handoff_note.md` to the Gemini relay agent. Gemini will:
1. Parse the task contract
2. Execute commands in allowlist order
3. Generate execution receipt

### Step 3: Verify Receipt

```bash
python skills/openclaw-cloud-bridge-skill/scripts/verify_execution_receipt.py \
  --contract .tmp/openclaw-dispatch/<task_id>/task_contract.json \
  --receipt .tmp/openclaw-dispatch/<task_id>/execution_receipt.json
```

### Step 4: Audit Trail

All evidence is stored in `AuditPack/evidence/`:
- `antigravity_baseline_activation_<baseline_id>.json`
- `openclaw_cloud_bridge_<task_id>.json`

## Schema References

- **Task Contract**: [schemas/openclaw_cloud_task_contract.schema.json](../../schemas/openclaw_cloud_task_contract.schema.json)
- **Execution Receipt**: [schemas/openclaw_execution_receipt.schema.json](../../schemas/openclaw_execution_receipt.schema.json)
- **Baseline Input**: [schemas/gm_baseline_e2e_smoketest_input.schema.json](../../schemas/gm_baseline_e2e_smoketest_input.schema.json)
- **Baseline Output**: [schemas/gm_baseline_e2e_smoketest_output.schema.json](../../schemas/gm_baseline_e2e_smoketest_output.schema.json)

## Governance Constraints

### Hard Constraints (Must)

1. **fail_closed**: Any missing contract field = reject execution
2. **command_allowlist**: Only allowlisted commands may execute
3. **no_free_shell**: No arbitrary command injection
4. **artifact_required**: execution_receipt.json must be returned
5. **local_review_gate**: Local review must PASS before claiming completion

### Preflight Checklist

Before dispatch:
- [ ] IsolationCheck: Execution endpoint is in controlled environment
- [ ] ScopeCheck: Target path is limited to `/root/openclaw-box`
- [ ] ImpactCheck: No irreversible operations (delete, overwrite, system-level)

## Examples

### Example 1: Basic Health Check

```bash
python scripts/antigravity_baseline_freeze.py \
  --objective "OpenClaw 云端健康巡检"
```

### Example 2: Custom Commands

Edit the script to add custom commands to the `default_commands` list, then run:

```bash
python scripts/antigravity_baseline_freeze.py \
  --objective "Custom diagnostic task"
```

### Example 3: Extended Duration

```bash
python scripts/antigravity_baseline_freeze.py \
  --objective "Long-running analysis" \
  --max-duration-sec 3600 \
  --max-commands 50
```

## Troubleshooting

### Issue: Smoketest fails

**Solution**: Check that the sample input file exists:
```bash
ls skills/gm-baseline-e2e-smoketest-skill/references/sample_input.json
```

### Issue: Contract verification fails

**Solution**: Check that:
1. `task_id` matches between contract and receipt
2. All executed commands are in the allowlist
3. All required artifacts are present
4. Receipt status is `success`

### Issue: Baseline hash mismatch

**Solution**: Verify that source files haven't changed between snapshot creation and verification.

## Version

- **Antigravity Version**: 1.0.0
- **Channel**: BlueLobster-Cloud
- **Agent**: Antigravity-Gemini
- **Date**: 2026-03-04

## Related Skills

- [gm-baseline-e2e-smoketest-skill](../../skills/gm-baseline-e2e-smoketest-skill/SKILL.md)
- [openclaw-cloud-bridge-skill](../../skills/openclaw-cloud-bridge-skill/SKILL.md)
- [l4-evidence-freeze-skill](../../skills/l4-evidence-freeze-skill/SKILL.md)
