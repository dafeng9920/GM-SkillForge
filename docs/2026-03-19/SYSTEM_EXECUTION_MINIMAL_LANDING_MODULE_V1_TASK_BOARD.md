# 系统执行层最小落地模块任务总表 v1

## 模式
- `multi-ai-collaboration = strict`
- 固定顺序：
  - `Execution -> Review -> Compliance -> Codex Acceptance`
- 注意：
  - Codex 仅做任务定义、回收、验收
  - AI 军团负责具体落地

## 模块任务总表

| Task | 子任务面 | Execution 单元 | Review 单元 | Compliance 单元 | 目标 | 交付物 | 禁止项 | 状态 |
|---|---|---|---|---|---|---|---|---|
| T1 | workflow | Antigravity-1 | vs--cc1 | Kior-C | workflow 最小落地 | workflow 骨架 + 职责文档 + 连接说明 | runtime / 外部集成 / 裁决语义 | 通过 |
| T2 | orchestrator | Antigravity-2 | vs--cc3 | Kior-C | orchestrator 最小落地 | orchestrator 骨架 + 职责文档 + 接口说明 | 裁决语义 / runtime 控制 | 通过 |
| T3 | service | vs--cc2 | Kior-A | Kior-C | service 最小落地 | service 骨架 + 职责文档 + 关系说明 | 真实业务执行 / 外部调用 | 通过 |
| T4 | handler | Kior-B | vs--cc1 | Kior-C | handler 最小落地 | handler 骨架 + 职责文档 + 调用边界 | 副作用动作 / runtime 分支 | 通过 |
| T5 | api | vs--cc3 | Kior-A | Kior-C | api 最小落地 | api 骨架 + 职责文档 + 连接说明 | 真实对外集成 / 外部协议 | 通过 |

## 统一目标路径
- 推荐由执行单元落位到：
  - `skillforge/src/system_execution/`
- 五子面建议路径：
  - `skillforge/src/system_execution/workflow/`
  - `skillforge/src/system_execution/orchestrator/`
  - `skillforge/src/system_execution/service/`
  - `skillforge/src/system_execution/handler/`
  - `skillforge/src/system_execution/api/`

## 状态定义
- `未开始`
- `进行中`
- `待审查`
- `待合规`
- `待验收`
- `通过`
- `退回`

## Codex 回收规则
- 缺任一交付物：不得进入审查。
- Review 标记阻断：直接退回对应执行单元。
- Compliance 标记越界：直接退回对应执行单元。
- 五任务全部达到 `待验收` 后，Codex 才做模块统一验收。

## 统一反馈写入路径
- 执行反馈：
  - `docs/2026-03-19/verification/system_execution_minimal_landing/T{N}_execution_report.md`
- 审查反馈：
  - `docs/2026-03-19/verification/system_execution_minimal_landing/T{N}_review_report.md`
- 合规反馈：
  - `docs/2026-03-19/verification/system_execution_minimal_landing/T{N}_compliance_attestation.md`
- 主控官终验：
  - `docs/2026-03-19/verification/system_execution_minimal_landing/T{N}_final_gate.md`
