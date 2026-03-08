# Case 005: Usage Meter - Quota Accounting on Enqueue

## Description

Usage meter test. Verifies that usage is recorded on enqueue (not completion) with append-only behavior.

## Input Summary

| Field | Value |
|-------|-------|
| account_id | `ACC-REGRESSION-005` |
| action | `AUDIT_L3` |
| units | `1` |
| job_id | `JOB-REGRESSION-005` |

## Expected Output

### Record Success

```
record_success: true
```

### Append-only

```
append_only: true
```

### Queryable by Account

```
get_usage("ACC-REGRESSION-005"): returns usage records
```

## Validation Points

1. **Record on Enqueue**: Usage is recorded when job is enqueued, not on completion.
2. **Append-only**: Records are appended, not overwritten.
3. **Queryable**: Usage can be queried by account_id and action.

## Why This Case?

This case verifies the P0-5 Usage/Quota (T20):
- Usage is recorded on enqueue/accept (not completion)
- Append-only storage
- Queryable for quota checking and cost accounting

## Notes

- **Deterministic**: Input is fixed and does not change between runs.
- **No Network**: Does not depend on any external network calls.
- **No Randomness**: Expected output is fixed.
