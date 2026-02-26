---
name: l4-final-gate-aggregator-skill
description: 聚合 L4-01~L4-07 三件套并输出 L4-08 与 final_gate_decision 的规则化裁决技能。
---

# l4-final-gate-aggregator-skill

## 触发条件

- 需要汇总 `L4-01~L4-07` 三件套
- 需要按规则给出 `ALLOW / REQUIRES_CHANGES / DENY`
- 需要生成 `L4-08_*` 与 `final_gate_decision.json`

## 输入

```yaml
input:
  verification_dir: "docs/{date}/l4-n8n-execution/verification"
  task_range: ["L4-01", "L4-02", "L4-03", "L4-04", "L4-05", "L4-06", "L4-07"]
  rules:
    - missing_triplet: "DENY"
    - compliance_not_pass: "REQUIRES_CHANGES"
    - all_green: "ALLOW"
```

## 输出

```yaml
output:
  - "L4-08_execution_report.yaml"
  - "L4-08_gate_decision.json"
  - "L4-08_compliance_attestation.json"
  - "final_gate_decision.json"
```

## DoD

- [ ] 7 个任务三件套存在性已检查
- [ ] compliance 统一按 `PASS` 判定
- [ ] 裁决规则按顺序应用
- [ ] 产物四件套全部生成

