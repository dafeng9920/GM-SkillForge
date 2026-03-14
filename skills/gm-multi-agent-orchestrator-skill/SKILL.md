---
name: gm-multi-agent-orchestrator-skill
description: 用于把 GM-SkillForge 的多 agent 云端执行流程收敛成受控状态机，明确 executor、reviewer、compliance、local codex/controller 四类角色的职责、状态迁移、checkpoint/resume 规则，以及它们与现有 Skill/Contract/Permit 体系的接入边界。适用于设计或执行多 agent 并发、小任务串行升级、云端 dropzone 交付、主控吸收与最终裁决场景。
---

# gm-multi-agent-orchestrator-skill

## 目标

把多 agent 协作从“谁想干什么就干什么”收敛成 **状态机 + 角色分权 + dropzone 交付 + 本地最终裁决**。

本 skill 不负责写业务代码；本 skill 负责约束：

- 谁能执行
- 谁能审查
- 谁能做合规
- 谁能最终吸收/裁决
- 任务在什么状态之间可以迁移

## 角色模型

固定四类角色：

- `executor`
  - 只负责执行、产出任务包、写证据
- `reviewer`
  - 只负责逻辑审查与证据引用
- `compliance`
  - 只负责边界/路径/缺件/签署/越权审查
- `controller`
  - 只负责拆任务、推进状态、吸收交付、最终裁决

硬约束：

- `executor != reviewer`
- `executor != compliance`
- `reviewer != compliance`
- `controller` 不得把 `review/compliance` 结论伪装成执行结果

## 核心状态

统一使用以下状态，不自行发明新词：

- `BLUEPRINT_PENDING`
- `READY_FOR_EXECUTION`
- `IN_DROPPED_DELIVERY`
- `READY_TO_RESUME`
- `WAITING_REVIEW`
- `WAITING_COMPLIANCE`
- `ABSORB_READY`
- `ABSORBED_PENDING_LOCAL_ACCEPT`
- `CLOSED`
- `DENIED`
- `BLOCKED`

## 状态迁移

- `BLUEPRINT_PENDING -> READY_FOR_EXECUTION`
  - blueprint/risk statement 已齐
- `READY_FOR_EXECUTION -> IN_DROPPED_DELIVERY`
  - executor 开始在隔离工作区产出任务包
- `IN_DROPPED_DELIVERY -> READY_TO_RESUME`
  - 中断，但 checkpoint/handoff 已写好
- `IN_DROPPED_DELIVERY -> WAITING_REVIEW`
  - 执行完成，任务包齐全，等待 reviewer
- `WAITING_REVIEW -> WAITING_COMPLIANCE`
  - reviewer 明确 `ALLOW`
- `WAITING_REVIEW -> DENIED`
  - reviewer 明确 `DENY`
- `WAITING_COMPLIANCE -> ABSORB_READY`
  - compliance 明确 `PASS`
- `WAITING_COMPLIANCE -> DENIED`
  - compliance 明确 `FAIL`
- `ABSORB_READY -> ABSORBED_PENDING_LOCAL_ACCEPT`
  - 主控执行 absorb 成功
- `ABSORBED_PENDING_LOCAL_ACCEPT -> CLOSED`
  - 本地 Codex 完成最终业务验收
- 任意状态 -> `BLOCKED`
  - 合同缺失、路径越权、关键文件缺失、token/context 恢复失败

## checkpoint / resume

必须使用以下三件套：

- `checkpoint/state.yaml`
- `resume_handoff.md`
- `execution_receipt.json`

恢复顺序固定为：

1. 读取 `checkpoint/state.yaml`
2. 读取 `execution_receipt.json`
3. 读取 `resume_handoff.md`
4. 再读取任务包和当前工作树

只要缺任一关键件，就不能从 `READY_TO_RESUME` 自动继续。

## 与任务包协议的关系

执行层任务包规范由：

- `skills/lobster-task-package-skill/SKILL.md`

吸收门禁由：

- `skills/lobster-absorb-gate-skill/SKILL.md`

本 skill 负责调度和状态，不替代这两个 skill。

## 与 Skill / Contract / Permit 的接入边界

- `blueprint.md`
  - 绑定当前任务 contract / dispatch / objective
- `risk_statement.md`
  - 绑定风险说明，不等于 permit
- `completion_record.md`
  - 只能表达执行完成，不得写 final allow
- `review_decision`
  - 只能由 reviewer 产出
- `compliance_attestation`
  - 只能由 compliance 产出
- `permit/final_gate`
  - 只能由本地 controller / 主控侧决定

## 并发原则

允许：

- 多个 `executor` 并发跑小任务
- 多个任务都落到各自 `dropzone/<task_id>/`

不允许：

- 多个 executor 共享同一任务包目录
- reviewer/compliance 和 executor 同人
- 未 review/compliance 就 absorb

## DoD

- [ ] 任务始终有且只有一个状态
- [ ] 角色分权不被破坏
- [ ] executor 只能写 dropzone 交付包
- [ ] reviewer/compliance 都有独立证据和独立结论
- [ ] 本地 controller 才能 absorb 和 close

## 参考

- `docs/2026-03-08/CLOUD_MULTI_AGENT_OVERSIGHT_PROTOCOL_v1.md`
- `docs/2026-03-08/DOCKER_VOLUME_受控物理桥接方案_v1.md`
- `docs/2026-03-08/DOCKER_VOLUME_桥接实施包_v1.md`
- `skills/lobster-cloud-execution-governor-skill/SKILL.md`
