# Case 003: Registry Store - Append-only Behavior

## Description

Registry store append-only behavior verification. Verifies that:
1. New entries can be appended
2. History is not overwritten
3. Latest ACTIVE revision can be read

## Input Summary

| Field | Value |
|-------|-------|
| skill_id | `SKILL-REGRESSION-003` |
| revision | `REV-001` |
| pack_hash | `PACK-HASH-REGRESSION-003` |
| permit_id | `PERMIT-REGRESSION-003` |
| tombstone_state | `ACTIVE` |

## Expected Output

### Append Success

```
append_success: true
```

### Read Latest

```
get_latest_active("SKILL-REGRESSION-003"): REV-001
```

### Append-only Behavior

```
append_only: true (history not overwritten)
```

## Validation Points

1. **Append Success**: Entry can be appended to registry.
2. **Read Latest**: `get_latest_active()` returns the latest ACTIVE revision.
3. **Append-only**: Subsequent appends do not overwrite previous entries.

## Why This Case?

This case verifies the P0-1 Registry (T17):
- Append-only storage (cannot overwrite history)
- Read latest ACTIVE revision by skill_id
- Supports skill_id + revision + pack_hash + permit_id + tombstone_state

## Notes

- **Deterministic**: Input is fixed and does not change between runs.
- **No Network**: Does not depend on any external network calls.
- **No Randomness**: Expected output is fixed.
