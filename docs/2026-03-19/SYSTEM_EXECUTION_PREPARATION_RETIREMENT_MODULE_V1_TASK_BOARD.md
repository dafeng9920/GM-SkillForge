# 系统执行层 preparation 历史资产退役任务总表 v1

| Task | Scope | Execution | Review | Compliance | 目标 | 状态 |
|---|---|---|---|---|---|---|
| R1 | 引用盘点 | vs--cc1 | Kior-A | Kior-C | 生成旧路径引用清单与分类 | 通过 |
| R2 | 文档与自检引用修正 | Antigravity-1 | vs--cc3 | Kior-C | 将直接引用旧路径的材料修正到新路径 | 通过 |
| R3 | 旧目录退役说明 | Kior-B | vs--cc1 | Kior-C | 为旧目录增加退役说明与迁移指引 | 通过 |
| R4 | 旧目录删除候选清理 | Antigravity-2 | Kior-A | Kior-C | 在引用清零后清理旧目录 | 局部通过 |
| R5 | 活跃材料残留引用清理返工 | Antigravity-1 | vs--cc3 | Kior-C | 只清理 `system_execution/` 下仍指向旧路径的文档与自检引用 | 通过 |
| R6 | 退役模块文档状态同步 | Kior-B | Kior-A | Kior-C | 更新 retirement 模块报告与任务板状态，不扩大到历史归档材料 | 通过 |

## 统一回收路径
- `docs/2026-03-19/verification/system_execution_preparation_retirement/`

## Codex 回收规则
- R1 必须先完成，R2/R3 才能放行。
- R4 必须等待 R2/R3/R4 审查与合规全部通过后才允许执行删除。
- R5 只允许修正 `skillforge/src/system_execution/` 下的活跃文档与自检引用，不得修改历史执行报告。
- R6 只允许同步模块报告、任务总表与验收状态，不得重写 R1-R4 事实记录。
- R5/R6 回收完成后，由 Codex 进行退役模块最终验收。

## Codex 最终验收
- 终验日期：`2026-03-19`
- 模块结论：`通过`
- 结论依据：
  - `R5_execution_report / R5_review_report / R5_compliance_attestation` 已回收并通过
  - `R6_execution_report / R6_review_report / R6_compliance_attestation` 已回收并通过
  - `skillforge/src/system_execution/` 下已无阻断性的旧路径活跃引用
  - 保留的旧路径文本仅用于退役说明和历史审计注释，不视为阻断
