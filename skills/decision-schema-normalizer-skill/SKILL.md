---
name: decision-schema-normalizer-skill
description: 标准化 gate/compliance 决策文件字段，修复 decision 缺失或结构漂移，确保自动裁决器可解析。
---

# decision-schema-normalizer-skill

## 触发条件

- 出现 `PARSE_ERR` / `NO_DECISION`
- gate/compliance 文件字段不统一
- 需要批量对齐 `decision` 口径

## 输入

```yaml
input:
  target_files:
    - "*_gate_decision.json"
    - "*_compliance_attestation.json"
  required_fields:
    gate: ["task_id", "decision"]
    compliance: ["task_id", "decision"]
  preserve_semantics: true
```

## 输出

```yaml
output:
  normalized_files:
    - file
    - changed
    - before_schema
    - after_schema
  schema_diff_report: "reports/schema_normalization/{date}.json"
```

## DoD

- [ ] 所有目标文件可被标准 JSON parser 解析
- [ ] `decision` 字段存在且值不被错误改写
- [ ] 生成变更报告可审计

