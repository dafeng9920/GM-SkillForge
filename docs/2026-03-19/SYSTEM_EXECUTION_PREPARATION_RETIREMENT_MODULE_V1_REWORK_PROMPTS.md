# 系统执行层 preparation 历史资产退役返工提示词 v1

## 本轮返工唯一目标
- 只清理 `skillforge/src/system_execution/` 下仍指向 `system_execution_preparation` 的活跃文档和自检引用
- 同步 retirement 模块报告与任务板状态
- 不重写历史盘点、不改 frozen 主线、不扩到 runtime / 外部集成

## 发给 Antigravity-1（R5 Execution）

```text
你是任务 R5 的执行者 Antigravity-1。

前置事实：
- `skillforge/src/system_execution_preparation/` 目录已删除
- retirement 模块未通过的唯一阻断点，是 `skillforge/src/system_execution/` 下仍有少量活跃材料引用旧路径

本轮唯一目标：
- 只清理 `skillforge/src/system_execution/` 下仍指向 `system_execution_preparation` 的活跃文档与自检引用

允许修改的范围：
- `skillforge/src/system_execution/workflow/CONNECTIONS.md`
- `skillforge/src/system_execution/workflow/WORKFLOW_RESPONSIBILITIES.md`
- `skillforge/src/system_execution/api/CONNECTIONS.md`
- `skillforge/src/system_execution/workflow/_self_check.py`
- 如确有同级 `system_execution/` 活跃材料仍残留旧路径引用，可一并修正，但必须在报告中逐条列出

禁止项：
- 不得修改 frozen 主线
- 不得修改历史执行报告 / 盘点报告 / 退役报告
- 不得恢复或重建 `system_execution_preparation/`
- 不得引入 runtime / 外部执行 / 集成语义
- 不得借机重构五子面职责

输出：
- 更新后的文件
- `docs/2026-03-19/verification/system_execution_preparation_retirement/R5_execution_report.md`

报告必须写明：
1. 实际修正了哪些文件
2. 每个文件把什么旧路径改成了什么新路径
3. 剩余未改项是否全部属于历史审计材料
4. 本轮是否引入任何非必要改动（必须明确写 NO / YES）
```

## 发给 vs--cc3（R5 Review）

```text
你是任务 R5 的审查者 vs--cc3。

你不做执行，只做普通结构审查。

审查目标：
1. R5 是否只修改了 `system_execution/` 下的活跃文档与自检引用
2. 文档中的模块路径与导入路径是否统一指向 `system_execution/`
3. 是否误改了历史执行报告、盘点报告、退役报告
4. 是否出现不必要的结构重写或职责漂移

输出：
- `docs/2026-03-19/verification/system_execution_preparation_retirement/R5_review_report.md`

必须明确给出：
- PASS / REQUIRES_CHANGES / FAIL
- 证据文件与行号
```

## 发给 Kior-C（R5 Compliance）

```text
你是任务 R5 的合规官 Kior-C。

本轮只做 B Guard 式硬审，不做执行，不做普通质量审查。

本轮只检查：
1. 是否只修正活跃材料中的旧路径引用
2. 是否倒灌 frozen 主线
3. 是否引入 runtime
4. 是否引入外部执行 / 集成
5. 是否借返工重写五子面职责

Zero Exception Directives：
- 只要修改了 frozen 主线，直接 FAIL
- 只要引入 runtime/external integration，直接 FAIL
- 只要借返工扩模块，直接 FAIL

输出：
- `docs/2026-03-19/verification/system_execution_preparation_retirement/R5_compliance_attestation.md`
- 必须明确写出 PASS 或 FAIL
```

## 发给 Kior-B（R6 Execution）

```text
你是任务 R6 的执行者 Kior-B。

前置条件：
- R5 已完成并回收 execution / review / compliance

本轮唯一目标：
- 只更新 retirement 模块的主控文档状态，使其反映当前真实进度

允许修改：
- `docs/2026-03-19/SYSTEM_EXECUTION_PREPARATION_RETIREMENT_MODULE_V1_TASK_BOARD.md`
- `docs/2026-03-19/SYSTEM_EXECUTION_PREPARATION_RETIREMENT_MODULE_V1_REPORT.md`

禁止项：
- 不得改写 R1-R4 的事实结论
- 不得修改历史执行报告
- 不得扩大到新任务面

输出：
- 更新后的模块文档
- `docs/2026-03-19/verification/system_execution_preparation_retirement/R6_execution_report.md`
```

## 发给 Kior-A（R6 Review）

```text
你是任务 R6 的审查者 Kior-A。

你只审查 retirement 模块状态文档是否与当前事实一致。

检查：
1. 任务板状态是否准确
2. 模块报告是否准确反映“目录已删但活跃引用清理仍待完成/或已完成”
3. 是否出现主控文档越权改写历史证据

输出：
- `docs/2026-03-19/verification/system_execution_preparation_retirement/R6_review_report.md`
- 明确 PASS / REQUIRES_CHANGES / FAIL
```

## 发给 Kior-C（R6 Compliance）

```text
你是任务 R6 的合规官 Kior-C。

本轮只做 B Guard 式硬审。

检查：
1. 是否只做状态同步
2. 是否改写历史事实
3. 是否借状态更新扩大模块范围

Zero Exception Directives：
- 只要改写历史事实，直接 FAIL
- 只要扩大模块范围，直接 FAIL

输出：
- `docs/2026-03-19/verification/system_execution_preparation_retirement/R6_compliance_attestation.md`
- 必须明确写出 PASS 或 FAIL
```

## Codex 终验条件
- `R5_execution_report / R5_review_report / R5_compliance_attestation` 全部回收
- `R6_execution_report / R6_review_report / R6_compliance_attestation` 全部回收
- `skillforge/src/system_execution/` 下不再存在指向 `system_execution_preparation` 的活跃文档和自检引用
- 历史审计材料保留旧路径记录，不视为阻断
