---
name: gm-baseline-e2e-smoketest-skill
description: GM 闭环基线模板技能。用于验证 Skill -> OpenClaw -> 执行 -> 回传 -> 自动验收 -> 落盘记录 全链路是否可用。
---

# gm-baseline-e2e-smoketest-skill

## Skill Identity

- skill_id: `gm.baseline.e2e-smoketest`
- version: `0.1.0`
- layer: `Execution Validation`
- type: `Closed-Loop Verification Skill`

## Purpose

本 Skill 只做闭环验收，不追求业务复杂度。目标是验证：

`Local Skill -> OpenClaw -> Execute -> Callback -> Auto Acceptance -> Persist`

## Input Contract

Required:

- `task_payload` (object)
- `validation_mode` (string: `strict|loose`, default `strict`)

Optional:

- `timeout_ms` (integer)

Constraints:

- 输入必须是 JSON
- 顶层对象不能为空
- `task_payload` 不能为空对象

## State Contract

Read:

- `system.runtime_version`
- `environment.variables`
- `execution.timestamp`

Write:

- `run_id`
- `execution_trace`
- `output_payload`
- `acceptance_report`

限制:

- 禁止修改全局共享状态

## Execution Protocol

必须按顺序写入 `execution_trace`：

1. `prepare`
2. `execute`
3. `package_result`
4. `acceptance_validation`

## Output Contract

输出必须匹配：

- `schemas/gm_baseline_e2e_smoketest_output.schema.json`

并包含：

- `run_id`
- `skill.id=gm.baseline.e2e-smoketest`
- `skill.version=0.1.0`
- `status`
- `input_snapshot`
- `execution_trace` (>=4)
- `output_payload.artifacts`
- `output_payload.metrics.elapsed_ms`
- `acceptance_report`

## Acceptance Rules

PASS 条件:

- `status == success`
- JSON 可解析
- `execution_trace` 至少 4 步
- `artifacts` 非空
- `elapsed_ms > 0`
- `acceptance_report.result == PASS`
- strict 模式下 `replayable == true`

FAIL 条件:

- 任一关键字段缺失
- JSON 结构错误
- 异常未捕获
- artifacts 为空
- elapsed_ms == 0
- strict 模式下 replayable 为 false

## Failure Tree

- `INPUT_INVALID`
- `EXECUTION_TIMEOUT`
- `OUTPUT_SCHEMA_ERROR`
- `ACCEPTANCE_MISMATCH`
- `UNKNOWN_EXCEPTION`

## Logging Requirements

必须记录：

- `run_id`
- `skill_id`
- `skill_version`
- `execution_timestamp`
- `elapsed_ms`
- `acceptance_result`

## Replay Protocol

相同 `input_snapshot` 下重跑要求：

- 相同 `status`
- `replayable=true`
- 差异必须写入 `diff_summary`

## Compliance Flag

以下场景置 `compliance_flag=true`：

- 文件写入
- 网络请求
- 外部 API 调用

否则 `false`。

## L4/L5 Readiness

L4:

- 连续 5 次 PASS
- 无 `UNKNOWN_EXCEPTION`
- replay 成功率 >= 90%

L5:

- 支持跨任务类型
- 失败自动归类
- 日志可回放
- 可生成运行统计
- 具备冲突检测扩展接口

## Runner

```bash
python skills/gm-baseline-e2e-smoketest-skill/scripts/run_smoketest.py ^
  --input skills/gm-baseline-e2e-smoketest-skill/references/sample_input.json ^
  --output .tmp/gm-smoketest/output.json
```

