---
name: triple-record-validator-skill
description: 校验任务三件套（execution/gate/compliance）完整性与可机读性，输出缺失和解析错误清单。
---

# triple-record-validator-skill

## 触发条件

- 需要判断任务是否闭环
- 需要批量检查 Txx 三件套
- 出现“口头完成但文件不齐”争议

## 输入

```yaml
input:
  verification_dir: "docs/{date}/p0-governed-execution/verification"
  task_range: "T01-T11"
  required_files:
    - "{task}_execution_report.yaml"
    - "{task}_gate_decision.json"
    - "{task}_compliance_attestation.json"
```

## 输出

```yaml
output:
  validation_table:
    - task_id
    - execution_exists
    - gate_exists
    - gate_decision
    - compliance_exists
    - compliance_decision
    - parse_status
  blockers:
    - task_id
    - reason
```

## DoD

- [ ] 每个任务有统一字段状态
- [ ] JSON 解析失败明确标记
- [ ] 结果可直接用于 gate 放行

