# 系统执行层最小落地模块范围文档 v1

## 当前阶段
- 当前阶段：`系统执行层最小落地模块 v1`
- 当前角色：`Codex = 主控者 / 拆分者 / 分派者 / 回收者 / 验收者`
- 已冻结前提：
  - `Production Chain v0 Frozen = true`
  - `Bridge Draft v0 Frozen = true`
  - `Bridge Minimal Implementation v0 Frozen = true`
  - `Governance Intake Minimal Implementation v0 Frozen = true`
  - `Gate Minimal Implementation Frozen = true`
  - `Review Minimal Implementation Frozen = true`
  - `Release Minimal Implementation Frozen = true`
  - `Audit Minimal Implementation Frozen = true`
  - `系统执行层准备模块 v1 = completed`

## 当前唯一目标
- 在不破坏 frozen 主线的前提下，把系统执行层做出“最小可承接、最小可落位、最小可验收”的内部落地骨架。

## 本模块最小推进范围
- 仅覆盖五个子面：
  - `workflow`
  - `orchestrator`
  - `service`
  - `handler`
  - `api`
- 仅允许：
  - 最小目录/文件落位
  - frozen 主线的只读承接路径
  - 最小内部调用链骨架
  - 最小接口连接关系
  - 导入/连接级验收
  - 模块文档、报告、变更控制规则

## 允许项
- AI 军团在明确任务卡边界内完成五子面最小骨架。
- Review Wing 只做结构/命名/职责审查。
- Compliance Wing 只做越界与 fail-closed 审查。
- Codex 只做分派、回收、验收与退回判断。

## 禁止项
- 不得回改 frozen 主线。
- 不得进入 `runtime`。
- 不得进入外部执行与集成。
- 不得落真实 webhook/queue/db/slack/email/repo 接入。
- 不得让 `workflow / orchestrator` 成为裁决者。
- 不得让 `service / handler / api` 提前长成真实执行层。
- Codex 不得亲自吞掉五子面的主实现。

## 固定输出
- `SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_SCOPE.md`
- `SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_BOUNDARY_RULES.md`
- `SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_TASK_BOARD.md`
- `SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_ACCEPTANCE.md`
- `SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_REPORT.md`
- `SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_CHANGE_CONTROL_RULES.md`
- `docs/2026-03-19/tasks/T1_workflow_minimal_landing.md`
- `docs/2026-03-19/tasks/T2_orchestrator_minimal_landing.md`
- `docs/2026-03-19/tasks/T3_service_minimal_landing.md`
- `docs/2026-03-19/tasks/T4_handler_minimal_landing.md`
- `docs/2026-03-19/tasks/T5_api_minimal_landing.md`

## 自动暂停条件
- 任一子任务要求修改 frozen 主线。
- 任一子任务进入 `runtime / external integration`。
- 任一子任务实现真实业务逻辑。
- 角色混线：Execution / Review / Compliance 边界失效。
- Codex 亲自代行五子面主实现。

## 本轮未触碰项
- 既有 frozen 文档正文未改。
- `contracts/` 下 frozen 对象未改。
- 既有 `skillforge/src/system_execution_preparation/` 资产仅作为参考，不在本轮重新实现。
