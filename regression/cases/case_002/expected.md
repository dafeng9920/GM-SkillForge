# Case 002: Permit Required Policy - PUBLISH_LISTING

## Description

Permit required policy test. Verifies that PUBLISH_LISTING action requires a valid permit.

## Input Summary

| Field | Value |
|-------|-------|
| action | `PUBLISH_LISTING` |
| permit_valid | `false` |
| permit_status | `MISSING` |

## Expected Output

### Action Requires Permit

```
permit_required("PUBLISH_LISTING"): true
```

### Error Code

```
error_code: PERMIT_REQUIRED
```

## Validation Points

1. **Action Classification**: `PUBLISH_LISTING` must be classified as requiring permit.
2. **Error Code Fixed**: Error code must be `PERMIT_REQUIRED`, not any other code.
3. **E001 Mapping**: This maps to E001 (permit missing) -> PERMIT_REQUIRED.

## Why This Case?

This case verifies the P0-3 Permit Required Policy (T21):
- All side-effect actions must go through `permit_required(action)`
- Error code is fixed to `PERMIT_REQUIRED`
- No semantic drift from gate_permit.py E001 mapping

## Notes

- **Deterministic**: Input is fixed and does not change between runs.
- **No Network**: Does not depend on any external network calls.
- **No Randomness**: Expected output is fixed.
