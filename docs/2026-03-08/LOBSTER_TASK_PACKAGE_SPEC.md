# LOBSTER TASK PACKAGE SPEC

- 日期：`2026-03-08`
- 适用对象：云端 Executor / Reviewer / Compliance / 本地主控

## 目标

把云端执行结果固定成 **待验收任务包**，而不是直接入仓代码或口头播报。

## 法定交付目录

所有任务包默认进入：

- `DROPZONE_ROOT/<task_id>/`

不得直接写 authoritative 主仓代码树。

## 最小必需件

标准任务包至少包含：

- `blueprint.md`
- `risk_statement.md`
- `changes.diff`
- `test_report.md`
- `completion_record.md`
- `manifest.json`
- `logs/`
- `evidence/`

其中 `manifest.json` 必须包含：

- `task_id`
- `artifacts`
- `evidence`
- `env`

`env` 至少记录以下运行时变量快照：

- `APP_ROOT`
- `DROPZONE_ROOT`
- `DOCS_ROOT`

文档/证据型任务至少包含：

- `execution_receipt.json`
- `completion_record.md`
- `resume_handoff.md`
- `checkpoint/state.yaml`

如任务属于真实执行任务，建议再包含：

- `execution_runtime_report.json`
- `execution_runtime_summary.md`
- `execution_runtime_moments.md`

其中运行时统计至少覆盖：

- 起止时间
- 有效工作时长
- 改动文件数/代码量
- 遇到的问题
- 使用过的 skill
- 最终完成状态

## 任务包状态

允许使用的状态：

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

## 三位一体联署

任务包进入可吸收状态前，必须有：

- Executor 交付
- Reviewer 证据化结论
- Compliance 证据化结论

不得由 executor 自称“已验收完成”。

## 吸收原则

吸收动作由宿主机或本地主控执行：

- 先 `pre_absorb_check`
- 再 `absorb`

吸收成功不等于最终业务验收通过。

当前默认脚本入口：

- `scripts/verify_governance_env.sh`
- `scripts/pre_absorb_check.sh <TASK_ID>`
- `scripts/absorb.sh <TASK_ID>`

## 红线

- 缺关键件
- 越权写主仓
- 跳过 manifest 白名单
- completion record 混入 review/compliance/final gate 结论
- 只靠口头播报，不给落盘证据
