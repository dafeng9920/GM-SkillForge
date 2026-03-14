---
name: final-gate-adjudicator-skill
description: 基于三权记录和killer tests结果输出最终门禁裁决（ALLOW/REQUIRES_CHANGES/DENY）。用于L3/L4阶段收口。
---

# final-gate-adjudicator-skill

## 触发条件

- Tn 执行/审查/合规文件齐备后
- 需要出 `final_gate_decision.json`
- 需要按固定规则自动裁决

## 输入

```yaml
input:
  verification_dir: "docs/{date}/verification"
  required_triplet:
    - "Tn_execution_report"
    - "Tn_gate_decision"
    - "Tn_compliance_attestation"
  killer_summary: "reports/l3_gap_closure/{date}/summary.json"
  policy:
    missing_triplet: "DENY"
    compliance_not_pass: "REQUIRES_CHANGES"
    killer_not_green: "REQUIRES_CHANGES"
    all_green: "ALLOW"
```

## 输出

```yaml
output:
  final_gate_decision: "docs/{date}/verification/final_gate_decision.json"
  fields:
    - decision
    - summary
    - blocking_evidence
    - required_changes
    - next_steps
```

## DoD

- [ ] 裁决结果可追溯到具体证据路径
- [ ] `decision` 与规则一致
- [ ] 缺失项/阻断项被明确列出
- [ ] 输出为机器可读 JSON

