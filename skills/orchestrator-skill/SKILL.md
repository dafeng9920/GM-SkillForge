---
name: orchestrator-skill
description: OpenClaw 军团指挥官（Orchestrator）。负责多智能体协同、任务链状态管理以及“意志与门禁”的全局控制。
---

# orchestrator-skill

## 触发条件

- 复杂任务启动，需要调用多个专家 Sub-agents 时。
- 任务执行过程中出现冲突或需要重新排期（SAM 逻辑）时。
- 执行敏感操作，需要“双人复审”或“合规门禁”时。

## 指挥模式 (Command Modes)

1. **Sequential (序列模式)**: Agent A -> Agent B -> Agent C 的严谨流水线。
2. **Consultative (协商模式)**: 调度 Auditor 和 Analyst 针对某一决策进行“开会”辩论。
3. **Emergency Lock (紧急熔断)**: 当任一环节触发安全告警，立即终止全链路执行。

## 状态管理 (State Management)

- **Task Bus**: 维护全局任务总线，所有 Sub-agents 共享上下文快照。
- **Quality Gates**: 在关键节点强制执行 `Skill Vetter` 或 `Aegis Audit`。

## DoD

- [ ] 多智能体通信协议（P2P/Broadcast）已跑通
- [ ] 具备完备的任务超时与重试逻辑
- [ ] 支持动态调整 Sub-agents 的权限等级（Permit Levels）
