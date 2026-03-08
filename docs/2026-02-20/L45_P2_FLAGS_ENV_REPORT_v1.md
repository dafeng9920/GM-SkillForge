# L4.5 SEEDS P2 Feature Flags Environment Profiles Report

> Job ID: `L45-D6-SEEDS-P2-20260220-006`
> Skill ID: `l45_seeds_p2_operationalization`
> Task: T30 (Feature Flags 环境化)
> Date: 2026-02-20
> Status: ✅ COMPLETED

---

## Summary

This report documents the implementation of environment-aware feature flags for SEEDS P2 operationalization. The feature flags system now supports different profiles for `dev`, `staging`, and `prod` environments, with automatic environment detection and fail-closed behavior for unknown environments.

---

## Deliverables

| File | Type | Description |
|------|------|-------------|
| `orchestration/feature_flags.yml` | Modified | Environment profile configuration |
| `skillforge/src/contracts/governance/feature_flag_loader.py` | Modified | Environment-aware loader |
| `docs/2026-02-20/L45_P2_FLAGS_ENV_REPORT_v1.md` | New | This report |

---

## Constraints Verification

| Constraint | Status | Evidence |
|------------|--------|----------|
| 必须区分 dev/staging/prod | ✅ | Three profiles defined in YAML |
| prod 默认安全策略不得放宽 | ✅ | prod profile has all flags disabled |
| 缺 profile 必须 fail-closed | ✅ | unknown environment uses defaults (all false) |
| 不得硬编码单环境常量覆盖配置 | ✅ | Environment read from SKILLFORGE_ENV, not hardcoded |

---

## Environment Profile Design

### Profile Hierarchy

```
dev (most permissive)
  ↓
staging (production-like with test allowances)
  ↓
prod (most restrictive - all flags disabled)
```

### Profile Flags Matrix

| Flag | dev | staging | prod | Default (unknown) |
|------|-----|---------|------|-------------------|
| `enable_sandbox_test` | ✅ true | ✅ true | ❌ false | ❌ false |
| `enable_n8n_execution` | ✅ true | ✅ true | ❌ false | ❌ false |
| `enable_github_intake_external` | ✅ true | ❌ false | ❌ false | ❌ false |
| `enable_advanced_analytics` | ❌ false | ❌ false | ❌ false | ❌ false |
| `enable_beta_features` | ✅ true | ❌ false | ❌ false | ❌ false |

### Security Guarantee

**prod profile is most restrictive**: All potentially dangerous or half-finished capabilities are disabled by default in production.

---

## Implementation Details

### Environment Detection

```python
# Environment is read from SKILLFORGE_ENV environment variable
# Valid values: dev, staging, prod
# Missing/invalid: defaults to "unknown" (fail-closed)

export SKILLFORGE_ENV=dev    # Development
export SKILLFORGE_ENV=staging # Staging
export SKILLFORGE_ENV=prod   # Production
```

### Usage Example

```python
from skillforge.src.contracts.governance.feature_flag_loader import (
    is_enabled,
    check_with_evidence,
    get_current_environment,
)

# Get current environment
env = get_current_environment()  # Returns: dev, staging, prod, or unknown

# Check flag (environment-aware)
if is_enabled("enable_n8n_execution"):
    # n8n execution is enabled for this environment
    pass
else:
    # Get auditable evidence for why it was blocked
    result = check_with_evidence("enable_n8n_execution", run_id="RUN-123")
    return {"error": "FEATURE_DISABLED", "evidence": result.evidence.to_dict()}
```

### Evidence Includes Environment

When a flag is disabled, the evidence now includes the environment context:

```json
{
  "issue_key": "FEATURE-DISABLED-ENABLE_N8N_EXECUTION-A1B2C3D4",
  "source_locator": "feature_flag://enable_n8n_execution?env=prod",
  "flag_name": "enable_n8n_execution",
  "enabled": false,
  "environment": "prod",
  "action_taken": "BLOCKED_BY_DISABLED_FLAG",
  "reason": "Feature 'enable_n8n_execution' is disabled in 'prod' environment."
}
```

---

## Fail-Closed Behavior

### Missing Environment Variable

```
SKILLFORGE_ENV not set → environment="unknown" → uses defaults (all false)
```

### Invalid Environment Value

```
SKILLFORGE_ENV=invalid → environment="unknown" → uses defaults (all false)
```

### Missing Profile

```
Profile "uat" not defined → uses defaults (all false)
```

### Missing Config File

```
feature_flags.yml not found → all flags false
```

---

## Test Results

```bash
python -m pytest -q skillforge/tests/test_feature_flag_loader.py
...........................................
43 passed in 0.29s
```

### Test Coverage

- Environment detection from SKILLFORGE_ENV
- Profile loading for dev/staging/prod
- Fail-closed for unknown environment
- prod most restrictive validation
- Evidence includes environment
- Flag reading from profile-specific config
- Disabled flag produces auditable evidence
- No hardcoded environment constants

---

## Migration Notes

### Backward Compatibility

The loader maintains backward compatibility with existing code:

1. Existing `is_enabled()` calls work without changes
2. `check_with_evidence()` still returns same structure
3. Evidence now includes `environment` field (additive change)

### Configuration Migration

Old format (v1):
```yaml
version: 1
flags:
  enable_n8n_execution: false
```

New format (v2):
```yaml
version: 2
defaults:
  enable_n8n_execution: false
profiles:
  dev:
    flags:
      enable_n8n_execution: true
  prod:
    flags:
      enable_n8n_execution: false
```

---

## Operational Guidelines

### Adding New Flags

1. Add to `defaults` section (set to `false` for fail-closed)
2. Add to each profile (`dev`, `staging`, `prod`) as appropriate
3. Document the flag purpose and security implications
4. Add tests for the new flag

### Changing Flag Values

1. Never relax `prod` profile flags without security review
2. Changes to `defaults` affect all unknown environments
3. Test in `dev` before promoting to `staging`/`prod`

### Environment Setup

```bash
# Development
export SKILLFORGE_ENV=dev

# CI/CD Staging
export SKILLFORGE_ENV=staging

# Production
export SKILLFORGE_ENV=prod
```

---

## Gate Decision

```yaml
gate_decision: ALLOW
task_id: T30
constraints_met:
  - ✅ 区分 dev/staging/prod
  - ✅ prod 默认安全策略不放宽
  - ✅ 缺 profile 必须 fail-closed
  - ✅ 不硬编码单环境常量
test_results:
  total: 43
  passed: 43
  failed: 0
ready_for_merge: true
```

---

## Appendix: File Changes

### orchestration/feature_flags.yml

- Added `version: 2` (environment profiles)
- Added `defaults` section for fail-closed fallback
- Added `profiles` section with dev/staging/prod
- Added `environment_config` section for detection settings

### skillforge/src/contracts/governance/feature_flag_loader.py

- Added `get_current_environment()` function
- Added `is_valid_environment()` function
- Added `environment` parameter to loader
- Modified `_load_config()` to resolve profile-specific flags
- Added environment to `FeatureFlagEvidence`
- Added environment to `FeatureFlagResult`
- Added `get_all_profiles()` and `get_profile()` methods
- Cache now keyed by path+environment

---

*Report generated: 2026-02-20*
*Job ID: L45-D6-SEEDS-P2-20260220-006*
