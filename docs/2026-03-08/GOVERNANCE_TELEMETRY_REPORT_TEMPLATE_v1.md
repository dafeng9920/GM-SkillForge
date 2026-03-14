# Governance Telemetry Report

- Window Start: `YYYY-MM-DDTHH:MM:SSZ`
- Window End: `YYYY-MM-DDTHH:MM:SSZ`
- Generated At: `YYYY-MM-DDTHH:MM:SSZ`
- Scope: `cloud execution / bridge / absorb / review / compliance`

## 1. Sample Summary

- Total Tasks:
- Total Delivery Events:
- Total Sync Events:
- Total Probe Runs:

## 2. Issue Summary

| Issue Type | Count | Severity Mix | Human Intervention Needed | Notes |
|---|---:|---|---:|---|
| path_drift |  |  |  |  |
| false_completion |  |  |  |  |
| artifact_missing |  |  |  |  |
| role_boundary_violation |  |  |  |  |
| sync_failure |  |  |  |  |
| absorb_failure |  |  |  |  |
| probe_gap |  |  |  |  |
| skill_drift |  |  |  |  |
| resume_failure |  |  |  |  |
| governance_doc_drift |  |  |  |  |

## 3. Core Metrics

| Metric | Value | Unit | Sample Size | Evidence Refs | Interpretation |
|---|---:|---|---:|---|---|
| false_completion_rate |  | ratio |  |  |  |
| artifact_recovery_rate |  | ratio |  |  |  |
| manual_intervention_per_task |  | count_per_task |  |  |  |
| resume_success_rate |  | ratio |  |  |  |
| probe_escape_rate |  | ratio |  |  |  |
| sync_success_rate |  | ratio |  |  |  |
| governance_violation_rate |  | ratio |  |  |  |

## 4. Trend Read

- What improved:
- What stayed flat:
- What regressed:

## 5. Upgrade Decision

- Decision: `HOLD | LIMITED_UPGRADE | READY_FOR_NEXT_STAGE | ROLLBACK_NEEDED`

### Reasoning

- 

### Blocking Factors

1. 
2. 
3. 

### Recommended Next Step

- 

## 6. Evidence Refs

- 

## 7. Notes

- Do not declare upgrade readiness from a single clean run.
- Do not ignore manual intervention cost.
- If probe coverage is incomplete, state it explicitly.
