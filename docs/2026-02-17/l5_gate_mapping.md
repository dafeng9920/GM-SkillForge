# L5 Hard Gate 映射表

> 基于 `skill_acceptance_L5_hard_gate_v3.md` (v1.1.0)

## 总览

| Gate | 名称 | 检查命令 | 证据文件 | 失败错误码 |
|------|------|----------|----------|------------|
| G1 | 能力可运行 | 4个 `--help` 命令 | `runtime_check_report.json` | `L5.G1.RUNTIME_NOT_READY` |
| G2 | 治理可阻断 | 检查边界审计报告 | `audit_report_boundary.json` | `L5.G2.GOVERNANCE_NOT_ENFORCED` |
| G3 | 证据可追溯 | 检查追溯字段完整性 | `traceability_report.json` | `L5.G3.TRACEABILITY_BROKEN` |
| G4 | 回放可复核 | 双次运行对比 | `replay_diff_report.json` | `L5.G4.REPLAY_NOT_REPRODUCIBLE` |
| G5 | 变更可控 | 检查契约一致性 | `audit_report_consistency.json` | `L5.G5.CHANGE_NOT_CONTROLLED` |

---

## G1 能力可运行

| 项目 | 值 |
|------|-----|
| **检查命令 (CLI)** | |
| (1) | `python -m skillforge.skills.contract_common_builder --help` |
| (2) | `python -m skillforge.skills.contract_module_builder --help` |
| (3) | `python -m skillforge.skills.contract_consistency_auditor --help` |
| (4) | `python -m skillforge.skills.governance_boundary_auditor --help` |
| **证据文件** | `runtime_check_report.json` |
| **关键字段 (JSONPath)** | `$.skills[*].exit_code` |
| **期望值** | 所有 4 个命令的 `exit_code` 均为 `0` |
| **失败错误码** | `L5.G1.RUNTIME_NOT_READY` |

### 证据文件结构示例

```json
{
  "skills": [
    {"name": "contract_common_builder", "exit_code": 0},
    {"name": "contract_module_builder", "exit_code": 0},
    {"name": "contract_consistency_auditor", "exit_code": 0},
    {"name": "governance_boundary_auditor", "exit_code": 0}
  ],
  "all_passed": true
}
```

---

## G2 治理可阻断

| 项目 | 值 |
|------|-----|
| **检查命令 (CLI)** | `python -m skillforge.skills.governance_boundary_auditor --input-file config/boundary_audit_input.json --output audit_report_boundary.json` |
| **证据文件** | `audit_report_boundary.json` |
| **关键字段 (JSONPath)** | |
| (1) | `$.summary.total_violations` |
| (2) | CI 配置存在违规即失败规则 (人工/脚本检查) |
| **期望值** | `total_violations == 0` 且 CI 配置正确 |
| **失败错误码** | `L5.G2.GOVERNANCE_NOT_ENFORCED` |

### 证据文件结构示例

```json
{
  "summary": {
    "total_violations": 0,
    "violations_by_type": {}
  },
  "violations": [],
  "ci_enforced": true
}
```

### CI 检查命令

```bash
# 检查 CI 配置是否包含违规即失败的规则
grep -r "exit 1" .github/workflows/ || grep -r "L5.G2" .github/workflows/
```

---

## G3 证据可追溯

| 项目 | 值 |
|------|-----|
| **检查命令 (CLI)** | TODO: Implement `python -m skillforge.skills.traceability_verifier` |
| **证据文件** | `traceability_report.json` |
| **关键字段 (JSONPath)** | |
| (1) | `$.reports[*].run_id` (非空) |
| (2) | `$.reports[*].trace_id` (非空) |
| (3) | `$.run_trace_mapping_valid` |
| **期望值** | 所有报告包含 `run_id` 和 `trace_id`，映射可复核为 `true` |
| **失败错误码** | `L5.G3.TRACEABILITY_BROKEN` |

### 证据文件结构示例

```json
{
  "reports": [
    {"file": "audit_report_boundary.json", "run_id": "run-001", "trace_id": "trace-001"},
    {"file": "audit_report_consistency.json", "run_id": "run-001", "trace_id": "trace-001"}
  ],
  "run_trace_mapping_valid": true,
  "all_traceable": true
}
```

---

## G4 回放可复核

| 项目 | 值 |
|------|-----|
| **检查命令 (CLI)** | TODO: Implement `python -m skillforge.skills.replay_verifier` |
| **执行方法** | 1. 同一输入运行两次，产出 `result_a.json`、`result_b.json`<br>2. 比较指定字段 |
| **证据文件** | `replay_diff_report.json` |
| **比较字段 (JSONPath)** | |
| (1) | `$.status` |
| (2) | `$.gates[*].id` |
| (3) | `$.gates[*].passed` |
| (4) | `$.gates[*].error_code` |
| **忽略字段** | `$.timestamp`, `$.trace.run_id`, `$.trace.trace_id` |
| **期望值** | `$.reproducible == true` (比较字段完全一致) |
| **失败错误码** | `L5.G4.REPLAY_NOT_REPRODUCIBLE` |

### 证据文件结构示例

```json
{
  "result_a": "l5_acceptance_result_run1.json",
  "result_b": "l5_acceptance_result_run2.json",
  "compared_fields": ["status", "gates[*].id", "gates[*].passed", "gates[*].error_code"],
  "ignored_fields": ["timestamp", "trace.run_id", "trace.trace_id"],
  "differences": [],
  "reproducible": true
}
```

---

## G5 变更可控

| 项目 | 值 |
|------|-----|
| **检查命令 (CLI)** | `python -m skillforge.skills.contract_consistency_auditor --input-file config/consistency_audit_input.json --output audit_report_consistency.json` |
| **证据文件** | `audit_report_consistency.json` |
| **关键字段 (JSONPath)** | |
| (1) | `$.naming_conflicts` |
| (2) | `$.broken_references` |
| (3) | `$.missing_sections` |
| (4) | `$.version_mismatches` |
| **期望值** | 所有字段均为 `0` |
| **失败错误码** | `L5.G5.CHANGE_NOT_CONTROLLED` |

### 证据文件结构示例

```json
{
  "naming_conflicts": 0,
  "broken_references": 0,
  "missing_sections": 0,
  "version_mismatches": 0,
  "details": {
    "conflicts": [],
    "broken_refs": [],
    "missing": [],
    "mismatches": []
  },
  "passed": true
}
```

---

## L5 整体执行命令

```bash
# 执行 L5 硬性验收门
python -m skillforge.skills.l5_hard_acceptance_gate \
  --input-file config/l5_acceptance_input.json \
  --output l5_acceptance_result.json
```

### 退出码约定

| 退出码 | 含义 |
|--------|------|
| `0` | `PASSED` |
| `1` | `REJECTED` |
| `2` | 输入 schema 校验失败 |
| `3` | 报告文件缺失或不可读 |

---

## 命令汇总（可复制粘贴）

```bash
# G1: 能力可运行检查
python -m skillforge.skills.contract_common_builder --help && \
python -m skillforge.skills.contract_module_builder --help && \
python -m skillforge.skills.contract_consistency_auditor --help && \
python -m skillforge.skills.governance_boundary_auditor --help && \
echo "G1 PASSED"

# G2: 治理可阻断检查
python -m skillforge.skills.governance_boundary_auditor \
  --input-file config/boundary_audit_input.json \
  --output audit_report_boundary.json

# G3: 证据可追溯检查
# TODO: Implement traceability_verifier
# python -m skillforge.skills.traceability_verifier --output traceability_report.json

# G4: 回放可复核检查
# TODO: Implement replay_verifier
# python -m skillforge.skills.replay_verifier --output replay_diff_report.json

# G5: 变更可控检查
python -m skillforge.skills.contract_consistency_auditor \
  --input-file config/consistency_audit_input.json \
  --output audit_report_consistency.json

# L5 整体验收
python -m skillforge.skills.l5_hard_acceptance_gate \
  --input-file config/l5_acceptance_input.json \
  --output l5_acceptance_result.json
```

---

## 待实现命令清单

| Gate | 缺失命令 | 备注 |
|------|----------|------|
| G3 | `skillforge.skills.traceability_verifier` | 需要实现 |
| G4 | `skillforge.skills.replay_verifier` | 需要实现 |

---

## 参考

- 源文档: `docs/2026-02-16/完整版模块清单 + 全量接口契约目录/skill_acceptance_L5_hard_gate_v3.md`
- 版本: v1.1.0
