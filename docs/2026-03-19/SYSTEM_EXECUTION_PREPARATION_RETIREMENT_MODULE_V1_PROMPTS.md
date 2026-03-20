# 系统执行层 preparation 历史资产退役提示词 v1

## 发给 vs--cc1（R1 Execution）

```text
你是任务 R1 的执行者 vs--cc1。

目标：
- 盘点 `skillforge/src/system_execution_preparation/` 的所有残留引用
- 按类别输出：代码引用 / 文档引用 / 自检脚本引用 / 历史报告引用

输出：
- docs/2026-03-19/verification/system_execution_preparation_retirement/R1_inventory.md

硬约束：
- 只盘点，不修改文件
- 不得扩展到 frozen 主线
```

## 发给 Antigravity-1（R2 Execution）

```text
你是任务 R2 的执行者 Antigravity-1。

目标：
- 基于 R1 清单，只修正“直接引用旧路径”的活动文档和自检脚本
- 把引用统一到 `skillforge/src/system_execution/`

输出：
- 更新后的文件
- docs/2026-03-19/verification/system_execution_preparation_retirement/R2_execution_report.md

硬约束：
- 不得修改 frozen 主线
- 不得改变 system_execution 五子面职责
- 不得顺手做功能重构
```

## 发给 Kior-B（R3 Execution）

```text
你是任务 R3 的执行者 Kior-B。

目标：
- 为 `skillforge/src/system_execution_preparation/` 写退役说明
- 明确旧路径仅为历史参考，标出新路径

输出：
- 退役说明文件
- docs/2026-03-19/verification/system_execution_preparation_retirement/R3_execution_report.md
```

## 发给 Antigravity-2（R4 Execution）

```text
你是任务 R4 的执行者 Antigravity-2。

前置条件：
- R1/R2/R3 已完成
- Review 通过
- Compliance PASS

目标：
- 在确认旧路径无活跃引用后，清理 `skillforge/src/system_execution_preparation/`

输出：
- 清理结果
- docs/2026-03-19/verification/system_execution_preparation_retirement/R4_execution_report.md

硬约束：
- 无 Review/Compliance 放行不得删除
- 不得删除仍被引用的资产
```

## Review / Compliance 统一口径
- Review：
  - 只看引用是否清零、文档是否一致、退役说明是否清晰
- Compliance：
  - 只看是否越界、是否误删、是否倒灌 frozen 主线
