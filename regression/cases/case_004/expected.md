# Case 004: Audit Event Writer - Gate Finish Event Logging

## Description

Audit event writer test. Verifies that gate finish events are logged correctly with append-only behavior.

## Input Summary

| Field | Value |
|-------|-------|
| event_type | `GATE_FINISH` |
| job_id | `JOB-REGRESSION-004` |
| gate_node | `permit_gate` |
| decision | `PASS` |
| error_code | `null` |
| issue_keys | `["ISSUE-REGRESSION-004"]` |
| evidence_refs | `["EV-REGRESSION-004"]` |

## Expected Output

### Write Success

```
write_success: true
```

### Append-only

```
append_only: true
```

### Queryable

```
query_by_job_id("JOB-REGRESSION-004"): returns event
```

## Validation Points

1. **Event Written**: Gate finish event is successfully written.
2. **Append-only**: Events are appended, not overwritten.
3. **Queryable**: Events can be queried by job_id and gate_node.

## Why This Case?

This case verifies the P0-4 Audit Events (T19):
- Every gate finish writes an event
- PASS/FAIL/SKIPPED all write events
- Append-only storage
- Queryable by job_id/gate_node/decision

## Notes

- **Deterministic**: Input is fixed and does not change between runs.
- **No Network**: Does not depend on any external network calls.
- **No Randomness**: Expected output is fixed.
