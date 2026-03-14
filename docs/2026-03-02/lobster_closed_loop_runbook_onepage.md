# Lobster Closed-Loop One-Page Runbook

## Purpose

Standard flow for:

`Contract -> Gemini relay -> Cloud execution -> Local verification -> Gate decision`

This runbook is for daily operation and incident-safe rollout.

## Environments

- `[LOCAL-ANTIGRAVITY]` local control plane, contract review, receipt verification
- `[CLOUD-ROOT]` cloud execution plane, OpenClaw runtime and cron monitors

## Golden Rules

1. Fail-closed by default
2. Contract-first, no free shell
3. Only allowlist commands can run
4. No next stage until local verification `PASS`
5. Any failure triggers rollback plan and gate `CLOSED`

## Standard Steps

1. Build contract locally
2. Review contract fields (allowlist, permit_id, rollback_plan, artifacts)
3. Relay to Gemini for cloud execution
4. Collect artifacts:
   - `execution_receipt.json`
   - `stdout.log`
   - `stderr.log`
   - `audit_event.json`
5. Verify locally with script
6. Decide `GO/NO-GO` for next task

## Required Contract Fields

- `task_id`
- `policy.fail_closed=true`
- `command_allowlist`
- `required_artifacts`
- `contract_sha256`
- (high risk) `human_permit_required`, `permit_id`, `rollback_plan`, `precondition`

## Required Receipt Conditions

- `task_id` matches contract
- `status=success`
- `exit_code=0`
- executed commands are subset of allowlist
- all required artifacts returned

## R0 Stability Window Rules

- `restart_count > 0` => `FAIL_CLOSED`
- `eacces > 0` => `FAIL_CLOSED`
- `unknown_model > 0` => `FAIL_CLOSED`
- `no_api_key > 0` => `FAIL_CLOSED`
- no P3 business contract before R0 gate release

## Hour 6 / Hour 12 Audit Package

- `stability_report.json` latest records
- `monitor.log` tail 40
- `crontab -l`
- top conclusion line:
  - `RHYTHM_FIX_VERIFIED=true|false`

## Fast Commands

### Contract verify

```powershell
python skills/openclaw-cloud-bridge-skill/scripts/verify_execution_receipt.py --contract <contract.json> --receipt <execution_receipt.json>
```

### Full local check

```powershell
powershell -ExecutionPolicy Bypass -File scripts/verify_all.ps1 -TaskDir ".tmp/openclaw-dispatch/<task_id>"
```

## Exit Criteria for Release

- Last task verification `PASS`
- Gate state `OPEN`
- R0 evidence complete and continuous
- No unresolved rollback event

