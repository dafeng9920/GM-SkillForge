# Skillization Gate Report Schema

> 版本: v1.0.0
> 更新时间: 2026-02-19

---

## 报告结构

```json
{
  "gate_name": "skillization_gate",
  "timestamp": "2026-02-19T00:00:00Z",
  "passed": true,
  "summary": {
    "total_checks": 5,
    "passed_checks": 5,
    "required_total": 5,
    "required_passed": 5
  },
  "duration_ms": 209,
  "checks": [
    {
      "name": "structure",
      "script": "check_skill_structure.ps1",
      "required": true,
      "passed": true,
      "duration_ms": 43,
      "error": null
    }
  ]
}
```

---

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `gate_name` | string | 固定值 `skillization_gate` |
| `timestamp` | string | ISO8601 时间戳 |
| `passed` | bool | 总体结果 |
| `summary.total_checks` | int | 总检查数 |
| `summary.passed_checks` | int | 通过检查数 |
| `summary.required_total` | int | 必需检查总数 |
| `summary.required_passed` | int | 必需检查通过数 |
| `duration_ms` | int | 执行耗时（毫秒） |
| `checks` | array | 各检查结果 |

---

## 检查项

| # | 名称 | 脚本 | 必需 |
|---|------|------|------|
| 1 | structure | check_skill_structure.ps1 | ✅ |
| 2 | openai_yaml | check_openai_yaml.ps1 | ✅ |
| 3 | contract_markers | check_skill_contract_markers.ps1 | ✅ |
| 4 | evidence_refs | check_evidence_refs.ps1 | ✅ |
| 5 | error_semantics | check_error_semantics_consistency.ps1 | ✅ |

---

## 输出路径

- 总控报告: `ci/out/skillization_gate_report.json`
- 结构检查: `ci/out/structure_check.json`
- YAML 检查: `ci/out/openai_yaml_check.json`
- 契约检查: `ci/out/contract_markers_check.json`
- 证据检查: `ci/out/evidence_refs_check.json`
- 语义检查: `ci/out/error_semantics_check.json`

---

## 阻断规则

| 条件 | 退出码 |
|------|--------|
| 所有 required 检查通过 | 0 (PASS) |
| 任一 required 检查失败 | 1 (FAIL) |

---

*版本: v1.0.0 | 更新时间: 2026-02-19*
