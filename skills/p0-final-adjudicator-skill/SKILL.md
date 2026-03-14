---
name: p0-final-adjudicator-skill
description: 聚合 T01-T11 三权记录并输出 final_gate_decision.json，执行 P0 终局裁决。
---

# p0-final-adjudicator-skill

## 触发条件

- Wave 4 完成后需要收口
- 需要输出 `final_gate_decision.json`
- 需要机器可复核的 ALLOW/REQUIRES_CHANGES/DENY 结论

## 输入

```yaml
input:
  verification_dir: "docs/{date}/p0-governed-execution/verification"
  tasks: ["T01","T02","T03","T04","T05","T06","T07","T08","T09","T10","T11"]
  rules:
    missing_any_record: "DENY"
    compliance_not_pass: "REQUIRES_CHANGES"
    all_gate_allow_and_compliance_pass: "ALLOW"
```

## 输出

```yaml
output:
  final_decision_file: "verification/final_gate_decision.json"
  summary:
    - tasks_total
    - complete_tasks
    - all_gate_allow
    - all_compliance_pass
```

## DoD

- [ ] 裁决规则可追溯
- [ ] 缺失项会进入 blocking_evidence
- [ ] 输出 JSON 可直接被后续流程消费

