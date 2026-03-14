# GM SKILL SPECIFICATION

## Skill ID: `<skill.id>`

Version: `<semver>`
Layer: `<layer>`
Type: `<type>`

## 1. PURPOSE

描述该 Skill 要验证或完成的核心目标。

## 2. INPUT CONTRACT

### Required Fields

| Field | Type | Description |
| --- | --- | --- |
| task_payload | object | 需执行任务描述 |
| validation_mode | string | strict / loose |

### Optional Fields

| Field | Type | Description |
| --- | --- | --- |
| timeout_ms | integer | 最大执行时间 |

### Constraints

- 输入必须为 JSON
- 不允许空对象
- validation_mode 默认 strict

## 3. STATE CONTRACT

### Read Access

- system.runtime_version
- environment.variables
- execution.timestamp

### Write Access

- run_id
- execution_trace
- output_payload
- acceptance_report

禁止修改全局共享状态。

## 4. EXECUTION PROTOCOL

必须按顺序记录 execution_trace：

1. prepare
2. execute
3. package_result
4. acceptance_validation

## 5. OUTPUT SCHEMA

输出 JSON 必须至少包含：

- run_id
- skill.id/version
- status
- input_snapshot
- execution_trace
- output_payload
- acceptance_report

## 6. ACCEPTANCE RULES

PASS:

- status == success
- JSON 可解析
- execution_trace 至少 4 步
- output_payload.artifacts 非空
- metrics.elapsed_ms > 0
- acceptance_report.result == PASS

FAIL:

- 关键字段缺失
- JSON 结构错误
- 异常未捕获
- artifacts 为空
- elapsed_ms == 0
- strict 模式下 replayable == false

## 7. FAILURE TREE

1. INPUT_INVALID
2. EXECUTION_TIMEOUT
3. OUTPUT_SCHEMA_ERROR
4. ACCEPTANCE_MISMATCH
5. UNKNOWN_EXCEPTION

## 8. LOGGING REQUIREMENTS

必须记录：

- run_id
- skill_id
- skill_version
- execution_timestamp
- elapsed_ms
- acceptance_result

## 9. REPLAY PROTOCOL

同 input_snapshot 重跑要求：

- status 一致
- replayable=true
- 记录 diff_summary

## 10. COMPLIANCE FLAG

涉及文件写入、网络请求或外部 API 调用时：

- compliance_flag: true

否则 false。

## 11. L4 READINESS CRITERIA

- 连续 5 次 PASS
- 无 UNKNOWN_EXCEPTION
- replay 成功率 >= 90%

## 12. L5 READINESS CRITERIA

- 支持跨任务类型
- 失败自动归类
- 日志可回放
- 可生成运行统计报告
- 具备冲突检测扩展接口

