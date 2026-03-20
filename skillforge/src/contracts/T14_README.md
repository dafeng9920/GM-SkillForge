# T14: Audit Pack - Discovery -> Adjudication -> Delivery Pipeline

## Task Summary

**Task ID**: T14
**Executor**: vs--cc3
**Deliverables**:
- `audit_pack.schema.json` - Schema for final audit pack
- `audit_pack.py` - Pipeline implementation
- `T14_samples/` - Regression samples (3 scenarios)
- `T14_README.md` - This file

## Objective

串起第 2 批对象成"发现 -> 裁决 -> 交付"的最小闭环：
- findings (T6) -> adjudication (T8) -> coverage/evidence (T9) -> release decision (T10)
  -> owner review (T11) -> issues/fixes (T12) -> audit pack (T14)

## Hard Constraints Enforced

1. **不得需要人工拼接** - Single command orchestrates entire pipeline
2. **不得引入第 3 批 runtime 能力** - Static analysis only, no runtime execution
3. **无 EvidenceRef 不得宣称完成** - All findings must have evidence refs
4. **固定输出目录** - `run/<run_id>/audit_pack.json`

## Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    T14 Audit Pack Pipeline                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Discovery (T1-T6)           Adjudication (T8-T9)                │
│  ┌─────────────┐             ┌─────────────┐                    │
│  │ T1: Intake  │             │  T8: Adjudic │                    │
│  │ T2: Parse   │────┐        │  ation      │                    │
│  │ T3: Validate│    │        │             │                    │
│  │ T4: Scan    │    ├───────>│  T9: Cover  │                    │
│  │ T5: Pattern │    │        │  age/Evid   │                    │
│  │ T6: Finding │────┘        │  ence       │                    │
│  └─────────────┘             └──────┬──────┘                    │
│                                     │                            │
│                                     ▼                            │
│  Delivery (T10-T12)         ┌─────────────┐                    │
│  ┌─────────────┐             │  T10: Rel   │                    │
│  │T10:Judgment │             │  ease/Over  │                    │
│  │ Overrides   │<────┐       │  rides/Risk │                    │
│  │T10:Residual │     │       └──────┬──────┘                    │
│  │ Risks       │─────┘              │                            │
│  │T11:Owner    │                    ▼                            │
│  │ Review      │             ┌─────────────┐                    │
│  │T12:Issue    │             │ T12: Issues │                    │
│  │ Records     │<────────────│ & Fixes     │                    │
│  │T12:Fix      │             └─────────────┘                    │
│  │ Recommend.  │                    │                            │
│  └──────┬──────┘                    │                            │
│         │                           │                            │
│         ▼                           ▼                            │
│  ┌─────────────────────────────────────────┐                   │
│  │          T14: Audit Pack                │                   │
│  │  Consolidates all artifacts with        │                   │
│  │  complete traceability & evidence       │                   │
│  └─────────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

## Output Directory Structure (FIXED)

```
run/<run_id>/
├── intake_request.json           # T1 (optional)
├── normalized_skill_spec.json    # T2 (optional)
├── validation_report.json        # T3 (optional)
├── rule_scan_report.json         # T4 (optional)
├── pattern_detection_report.json # T5 (optional)
├── findings.json                 # T6 (REQUIRED)
├── adjudication_report.json      # T8 (REQUIRED)
├── coverage_statement.json       # T9 (optional)
├── judgment_overrides.json       # T10 (optional)
├── residual_risks.json           # T10 (optional)
├── release_decision.json         # T10 (REQUIRED)
├── owner_review.json             # T11 (optional)
├── issue_records.json            # T12 (optional)
├── fix_recommendations.json      # T12 (optional)
└── audit_pack.json               # T14 (OUTPUT)
```

## Usage

### Option 1: Build from existing run directory (推荐)

```bash
# 基本用法（输出到 run/<run_id>/audit_pack.json）
python -m skillforge.src.contracts.run_t14_pipeline --run-id t14_test_demo

# 自定义输出路径
python -m skillforge.src.contracts.run_t14_pipeline --run-id t14_test_demo --output run/custom/audit_pack.json

# 验证现有 audit pack（不创建新文件）
python -m skillforge.src.contracts.run_t14_pipeline --run-id t14_test_demo --validate-only

# 只显示摘要（不保存）
python -m skillforge.src.contracts.run_t14_pipeline --run-id t14_test_demo --summary-only
```

**参数说明**：
- `--run-id`: Run identifier（必需）- 对应 `run/<run_id>/` 目录
- `--run-dir`: Base run directory（可选，默认 "run"）
- `--output`, `-o`: 自定义输出路径（可选，默认 `run/<run_id>/audit_pack.json`）
- `--validate-only`: 仅验证现有 audit pack，不创建新文件
- `--summary-only`: 只显示摘要，不保存文件
- `--context`: Pack context（可选，默认 "exit_gate"）

### Option 2: Full pipeline (ONE command to rule them all)

```python
from skillforge.src.contracts.audit_pack import run_audit_pipeline

pack = run_audit_pipeline(
    skill_dir="path/to/skill",
    intent_id="AUDIT_001",           # T1 白名单
    repo_url="https://github.com/user/repo",
    commit_sha="abc123def456",
    run_base_dir="run",
    run_id="20260316_120000",       # 可选，自动生成
)
```

This single command executes:
1. **Discovery Pipeline (T1-T6)**: intake → parse → validate → scan → pattern → findings
2. **Adjudication (T8)**: convert findings to rule decisions
3. **Release Decision (T10)**: make release decision with evidence binding
4. **Audit Pack (T14)**: consolidate all artifacts

### Option 3: Use API programmatically

```python
from skillforge.src.contracts.audit_pack import (
    AuditPackBuilder,
    build_audit_pack,
    validate_audit_pack,
)

# Build pack from existing run directory
pack = build_audit_pack(run_id="20260316_120000")

# Validate
is_valid, errors = validate_audit_pack(pack)
if not is_valid:
    for error in errors:
        print(f"❌ {error}")

# Save
pack.save("run/20260316_120000/audit_pack.json")
```

## Regression Samples

Three regression samples are provided in `T14_samples/`:

### Sample 1: Clean Release (`sample_1_clean_release.json`)

- **Outcome**: RELEASE
- **Findings**: 2 (1 LOW, 1 INFO)
- **Overrides**: 0
- **Residual Risks**: 0
- **Compliance**: ✅ Full

Demonstrates minimal artifact set with all checks passed.

### Sample 2: Conditional Release (`sample_2_conditional_release.json`)

- **Outcome**: CONDITIONAL_RELEASE
- **Findings**: 8 (2 HIGH, 3 MEDIUM, 2 LOW, 1 INFO)
- **Overrides**: 2
- **Residual Risks**: 2 (MEDIUM, LOW)
- **Compliance**: ✅ Full (with conditions)

Demonstrates full artifact set with overrides and residual risks.

### Sample 3: Rejection (`sample_3_rejection.json`)

- **Outcome**: REJECT
- **Findings**: 5 (1 CRITICAL, 2 HIGH, 1 MEDIUM, 1 LOW)
- **Overrides**: 0
- **Residual Risks**: 0
- **Compliance**: ❌ Evidence ref incomplete

Demonstrates T14 hard constraint enforcement (finding without evidence).

## Audit Pack Schema

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `meta.pack_id` | string | Unique pack identifier |
| `meta.run_id` | string | Run identifier |
| `meta.created_at` | string | ISO-8601 timestamp |
| `artifacts.discovery.findings_report` | string | Path to T6 findings (REQUIRED) |
| `artifacts.adjudication.adjudication_report` | string | Path to T8 report (REQUIRED) |
| `artifacts.delivery.release_decision` | string | Path to T10 decision (REQUIRED) |
| `evidence_manifest` | object | Evidence summary |
| `summary` | object | Summary statistics |

### Evidence Manifest

```json
{
  "total_evidence_refs": 24,
  "by_kind": {
    "FILE": 10,
    "CODE_LOCATION": 6,
    "LOG": 3,
    "TICKET": 2
  },
  "evidence_digest": "sha256 digest of all locators",
  "findings_with_evidence": 8,
  "findings_without_evidence": 0  // T14 Hard Constraint: MUST be 0
}
```

### Compliance Flags

| Flag | Condition |
|------|-----------|
| `antigravity_compliant` | Evidence refs complete + no violations |
| `closed_loop_complete` | All required artifacts present |
| `evidence_ref_complete` | All findings have evidence refs (T14 HC) |
| `governance_gaps_identified` | Count of governance gaps found |
| `security_findings_count` | Count of security findings |

## T14 Hard Constraints

1. **不得需要人工拼接**
   - Single `run_audit_pipeline()` command orchestrates everything
   - Or `build_audit_pack()` consolidates existing artifacts

2. **不得引入第 3 批 runtime 能力**
   - No test execution
   - No runtime verification
   - Static analysis only

3. **无 EvidenceRef 不得宣称完成**
   - `findings_without_evidence` MUST be 0
   - Validation fails if any finding lacks evidence

4. **固定输出目录**
   - `run/<run_id>/audit_pack.json`

## Validation

Audit pack validation checks:

```python
def validate(pack: AuditPack) -> list[str]:
    errors = []

    # Required artifacts
    if not pack.findings_report:
        errors.append("Missing: findings_report")
    if not pack.adjudication_report:
        errors.append("Missing: adjudication_report")
    if not pack.release_decision:
        errors.append("Missing: release_decision")

    # T14 Hard Constraint
    if pack.evidence_manifest.findings_without_evidence > 0:
        errors.append("T14 HC Violation: findings without evidence")

    # Evidence must exist
    if pack.evidence_manifest.total_evidence_refs == 0:
        errors.append("T14 HC Violation: no evidence refs")

    return errors
```

## Integration Points

**Input from (Batch 2)**:
- T6: `findings.json` (Unified Finding)
- T8: `adjudication_report.json` (RuleDecision)
- T9: `coverage_statement.json`, `evidence_level.json`
- T10: `judgment_overrides.json`, `residual_risks.json`, `release_decision.json`
- T11: `owner_review.json`
- T12: `issue_records.json`, `fix_recommendations.json`

**Output to**:
- Gate decision process
- Audit archive
- Compliance reports

## Antigravity-1 Compliance

**Closed-Loop Contract Standards**:
- ✅ Receipt references: `run_id`, `pack_id`, `evidence_digest`
- ✅ Dual-gate: `entry_gate` and `exit_gate` contexts supported
- ✅ Evidence binding: All findings have `evidence_refs`

**EvidenceRef Requirements**:
- All findings MUST have at least one evidence ref
- Evidence kinds: FILE, LOG, DIFF, SNIPPET, URL, CODE_LOCATION
- Evidence digest provides tamper detection

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0-t14 | 2026-03-16 | Initial T14 deliverable |

## References

- T6: Finding Builder
- T8: Adjudicator
- T9: Coverage Statement / Evidence Level
- T10: Release Decision / Judgment Overrides / Residual Risks
- T11: Owner Review
- T12: Issue Records / Fix Recommendations
- T13: Case Ledger / Anti-Collapse Report
