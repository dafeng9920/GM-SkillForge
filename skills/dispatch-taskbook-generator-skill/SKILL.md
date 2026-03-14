---
name: dispatch-taskbook-generator-skill
description: 生成可一键转发的多AI协作任务单（执行者、输入、验收、交付物、回传格式），用于 T1/T2/T3/T4/T5 等并行收口。
---

# dispatch-taskbook-generator-skill

## 触发条件

- 需要将目标拆分给多个执行者并行推进
- 需要统一任务模板、避免口头分配歧义
- 需要收集三权记录（execution / gate / compliance）

## 输入

```yaml
input:
  objective: "L3 gap closure / final adjudication"
  tasks:
    - task_id
    - owner
    - scope
    - required_files
    - acceptance_rules
  output_dir: "docs/{date}/tasks"
  dispatch_file: "docs/{date}/task_dispatch_l3_closure.md"
```

## 输出

```yaml
output:
  dispatch_doc: "docs/{date}/task_dispatch_l3_closure.md"
  task_docs:
    - "docs/{date}/tasks/T1_*.md"
    - "docs/{date}/tasks/T2_*.md"
    - "docs/{date}/tasks/T3_*.md"
    - "docs/{date}/tasks/T4_*.md"
    - "docs/{date}/tasks/T5_*.md"
  required_sections:
    - "Executor"
    - "Exact Commands"
    - "Deliverables"
    - "Pass/Fail Criteria"
    - "Return Template"
```

## DoD

- [ ] 每个任务有唯一执行者与可执行命令
- [ ] 每个任务包含必需交付物路径
- [ ] 每个任务定义机器可判定的通过条件
- [ ] 回传模板统一，可直接汇总到 `final_gate_decision`

