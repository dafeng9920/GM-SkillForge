---
name: dispatch-broadcast-builder-skill
description: 根据 task_dispatch 和当前阻断项生成可一键群发的任务指令与纠偏指令。
---

# dispatch-broadcast-builder-skill

## 触发条件

- 需要快速群发任务给多执行者
- 需要生成纠偏补单指令
- 需要统一话术与回传格式

## 输入

```yaml
input:
  dispatch_file: "docs/{date}/p0-governed-execution/task_dispatch.md"
  wave_status_file: "verification/Wave*_recheck*.json"
  target_tasks:
    - task_id
    - owner
    - reviewer
    - compliance_officer
```

## 输出

```yaml
output:
  broadcast_messages:
    - task_id
    - message_text
  reconciliation_messages:
    - blocker_task
    - fix_text
```

## DoD

- [ ] 每条消息有 task_id 和负责人
- [ ] 明确回传三件套路径
- [ ] 文案可直接复制转发

