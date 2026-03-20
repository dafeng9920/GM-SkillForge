# 系统执行层 preparation 历史资产退役模块范围文档 v1

## 当前阶段
- 当前阶段：`system_execution_preparation 历史资产退役模块 v1`
- 当前角色：`Codex = 主控者 / 拆分者 / 分派者 / 回收者 / 验收者`

## 当前唯一目标
- 在不破坏 frozen 主线与已通过的 `system_execution` 最小落地模块的前提下，完成 `system_execution_preparation/` 历史资产的退役准备与清理落位。

## 本模块最小推进范围
- 仅处理：
  - `skillforge/src/system_execution_preparation/` 目录
  - 与该目录直接相关的文档引用
  - 与该目录直接相关的自检脚本引用
  - 退役说明、迁移说明、历史资产清理记录

## 允许项
- 盘点旧目录残留引用。
- 将仍使用旧路径的文档/自检说明改到新路径。
- 为旧目录增加退役说明。
- 在确认无活跃引用后删除旧目录。
- 补充退役报告与 change control 规则。

## 禁止项
- 不得改写 frozen 主线。
- 不得改写 `system_execution/` 五子面的职责边界。
- 不得借清理进入 runtime / external integration。
- 不得顺手重构系统执行层实现。
- 不得把“路径清理”扩成新一轮模块开发。

## 固定输出
- `SYSTEM_EXECUTION_PREPARATION_RETIREMENT_MODULE_V1_SCOPE.md`
- `SYSTEM_EXECUTION_PREPARATION_RETIREMENT_MODULE_V1_BOUNDARY_RULES.md`
- `SYSTEM_EXECUTION_PREPARATION_RETIREMENT_MODULE_V1_TASK_BOARD.md`
- `SYSTEM_EXECUTION_PREPARATION_RETIREMENT_MODULE_V1_ACCEPTANCE.md`
- `SYSTEM_EXECUTION_PREPARATION_RETIREMENT_MODULE_V1_PROMPTS.md`
- `SYSTEM_EXECUTION_PREPARATION_RETIREMENT_MODULE_V1_REPORT.md`
