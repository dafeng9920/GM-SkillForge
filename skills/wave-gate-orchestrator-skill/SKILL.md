---
name: wave-gate-orchestrator-skill
description: 负责 Wave 内并发调度与 Wave 间门禁放行，适用于多任务三权闭环推进。
---

# wave-gate-orchestrator-skill

## 触发条件

- 任务按 Wave 编排（如 T01-T11）
- 需要执行 `Wave内并发，Wave间门禁`
- 需要控制跨 Wave 放行

## 输入

```yaml
input:
  dispatch_file: "docs/{date}/p0-governed-execution/task_dispatch.md"
  verification_dir: "docs/{date}/p0-governed-execution/verification"
  wave_policy:
    intra_wave: "parallel"
    inter_wave: "gate_required"
```

## 输出

```yaml
output:
  wave_status:
    - wave
    - ready_to_release
    - blocking_tasks
  next_wave_actions:
    - dispatch_list
    - hold_list
```

## DoD

- [ ] 同 Wave 任务并发可见
- [ ] 跨 Wave 放行严格按门禁判断
- [ ] 阻断项有具体任务号与原因

