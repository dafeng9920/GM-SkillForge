# Case 001: Gate Permit Validation Baseline

## Description

Gate permit validation baseline test. Verifies that an invalid signature is correctly rejected with E003 error code.

## Input Summary

| Field | Value |
|-------|-------|
| permit_id | `PERMIT-REGRESSION-001` |
| repo_url | `https://github.com/regression/test-repo` |
| commit_sha | `deadbeef12345678901234567890123456789012` |
| run_id | `RUN-REGRESSION-001` |
| requested_action | `release` |

## Expected Output

### Gate Decision

```
gate_decision: BLOCK
```

### Error Code

```
error_code: E002
release_blocked_by: PERMIT_INVALID
```

### Release Allowed

```
release_allowed: false
```

## Validation Points

1. **Signature Validation**: The permit has an intentionally invalid signature (`FIXED_SIGNATURE_FOR_REGRESSION_TEST`) which must be detected and rejected.
2. **Error Code Mapping**: Must return `E003` for invalid signature, not any other error code.
3. **Fail-Closed**: Must return `release_allowed: false`, never `true` for invalid permits.

## Why This Case?

This case establishes a baseline for gate permit validation. It verifies:
- The permit validation pipeline is working
- Error codes are correctly mapped (E001/E002/E003/etc.)
- Fail-closed behavior is enforced

## Notes

- **Deterministic**: Input is fixed and does not change between runs.
- **No Network**: Does not depend on any external network calls.
- **No Randomness**: Expected output is fixed, not randomly generated.
