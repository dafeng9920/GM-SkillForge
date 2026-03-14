# REPO-SCAN-04: Misclassified Core Files

**Scan ID**: REPO-SCAN-04
**Scan Date**: 2026-03-11
**Review Mode**: Fail-Closed
**Scope**: Unclassified untracked paths in `/adapters/quant/`, `/core/`, `/db/`, etc.

---

## Decision

**FAIL**

---

## Executive Summary

Multiple untracked directories exist at repository root with unclear classification:
1. Cannot determine if they are mainline core (require T5 gate) or skill artifacts (require T4 gate)
2. Missing N1 command allowlist verification for production code paths
3. Potential permit bypass for infrastructure changes
4. No gate decisions authorizing creation/modification

---

## Violations

| Violation ID | Severity | Description |
|--------------|----------|-------------|
| V-04-001 | CRITICAL | Core classification unclear: T5 vs T4 gate requirement |
| V-04-002 | CRITICAL | Missing N1 command allowlist compliance verification |
| V-04-003 | HIGH | Governance violation: potential permit bypass |
| V-04-004 | HIGH | No gate_decision.json for untracked core directories |
| V-04-005 | MEDIUM | Unclear ownership and maintenance responsibility |

---

## Affected Items

### Unclassified Root Directories

```
?? adapters/quant/backtest/
?? adapters/quant/phase4/
?? adapters/quant/trading/
?? core/
?? db/
```

### Classification Analysis Required

| Path | Possible Classification | Gate Required | Evidence Status |
|------|------------------------|---------------|-----------------|
| `core/` | Mainline Core (T5) OR Skill Artifact (T4) | T5/T4 | MISSING |
| `db/` | Infrastructure (T5) OR Data Artifact (T4) | T5/T4 | MISSING |
| `adapters/quant/` | Edge Layer (separate repo) OR Skill Artifact | N/A | MISSING |
| `artifacts/` | Build Artifact (ignore) OR Evidence Artifact | N/A | MISSING |
| `reports/` | Output (ignore) OR Compliance Evidence | N/A | MISSING |

---

## Required Changes

### Step 1: Classification Determination

For each untracked path, determine:

**Is this Mainline Core?**
- YES: Requires T5 gate (Master-Control sign-off)
- NO: Is this a Skill Artifact?
  - YES: Requires T4 gate (skill deployment)
  - NO: Is this Edge Layer?
    - YES: Should be in separate repository
    - NO: Is this Build/Output Artifact?
      - YES: Should be in .gitignore

### Step 2: Evidence Generation

For Mainline Core (`core/`):

```json
{
  "gate_id": "T5_master_control",
  "task_id": "core-<timestamp>",
  "decision": "PASSED",
  "classification": "mainline_core",
  "n1_command_allowlist": "VERIFIED",
  "n2_artifact_completeness": "PASS",
  "n3_time_window": "PASS",
  "closed_loop_contract": "PASS",
  "evidence_refs": [
    {"type": "compliance_attestation", "path": "./core/compliance_attestation.json"}
  ]
}
```

For Skill Artifacts (`adapters/quant/`):

```json
{
  "gate_id": "T4_skill_deployment",
  "task_id": "quant-adapter-<timestamp>",
  "decision": "PASSED",
  "classification": "skill_artifact",
  "n1_command_allowlist": "VERIFIED",
  "n2_artifact_completeness": "PASS",
  "n3_time_window": "PASS",
  "closed_loop_contract": "PASS",
  "evidence_refs": [
    {"type": "compliance_attestation", "path": "./adapters/quant/compliance_attestation.json"}
  ]
}
```

### Step 3: N1 Command Allowlist Verification

For production code paths, verify:

```yaml
# n1_command_allowlist.yml
commands_allowed:
  - python -m core.runtime_interface
  - python -m core.compiler.contract_compiler
  # ... add verified commands

commands_blocked:
  - python -m core.*  # catch-all requires explicit approval
```

---

## Detailed Analysis

### `core/` Directory

**Hypothesis**: Contains unified runtime interface, contract compiler, DSL validator, Gate engine

**Classification Recommendation**: **MAINLINE CORE (T5)**

**Required Gate**: T5 Master-Control

**Evidence Required**:
- T5 gate decision
- N1 command allowlist verification
- N2 artifact completeness manifest
- Architecture review sign-off

### `db/` Directory

**Hypothesis**: Database schema, migrations, or data storage

**Classification Recommendation**: **INFRASTRUCTURE (T5)** OR **DATA ARTIFACT (.gitignore)**

**Investigation Required**:
- Is this schema/migration code? (Keep, T5 gate)
- Is this runtime data? (.gitignore)

### `adapters/quant/` Directory

**Hypothesis**: Quant trading adapter with A-share strategies, backtesting

**Classification Recommendation**: **EDGE LAYER (separate repository)**

**Rationale**:
- Contains complete trading system unrelated to SkillForge governance
- Should be in `gm-skillforge-quant` repository
- Or submit as skill through T4 gate

### `artifacts/` Directory

**Classification Recommendation**: **BUILD ARTIFACT (.gitignore)**

**Rationale**: Transient build outputs

---

## Evidence Required

| Path | Classification | Gate Required | Evidence Status |
|------|----------------|---------------|-----------------|
| `core/` | MAINLINE CORE (T5) | T5_master_control | MISSING |
| `db/` | INFRASTRUCTURE (T5) | T5_master_control | MISSING |
| `adapters/quant/` | EDGE LAYER | Separate repo | MISSING |
| `artifacts/` | BUILD OUTPUT | .gitignore | MISSING |
| `reports/` | OUTPUT | .gitignore | MISSING |
| `dropzone/` | TEMPORARY | .gitignore | MISSING |

---

## Recommendations

1. **Immediate**: Audit contents of `core/` and `db/` to determine classification
2. **Short-term**: Generate gate decisions for all core infrastructure
3. **Long-term**: Establish policy requiring classification before directory creation
4. **Governance**: Update CLAUDE.md with explicit core/edge/artifact classification rules

---

## References

- T5 Master-Control Gate: `docs/2026-03-07/T3_T2_WAVE2_任务回传模板_COMPLIANT_v1.md`
- N1 Command Allowlist: Antigravity-1 Contract Section 3.1
- Core vs Edge Classification: `docs/2026-03-11/repo_cleanup_round1/REPO-SCAN-04_report.md`
