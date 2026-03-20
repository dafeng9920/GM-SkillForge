# Task Dispatcher State Machine v1

## 目的
- 统一定义 AI 军团任务从接单到主控终验的最小状态流转。

## 状态集合
- `PENDING`
- `ACCEPTED`
- `IN_PROGRESS`
- `WRITEBACK_DONE`
- `REVIEW_TRIGGERED`
- `REVIEW_DONE`
- `COMPLIANCE_TRIGGERED`
- `COMPLIANCE_DONE`
- `GATE_READY`
- `BLOCKED`
- `DENY`

## 最小状态流转

```text
PENDING
  -> ACCEPTED
  -> IN_PROGRESS
  -> WRITEBACK_DONE
  -> REVIEW_TRIGGERED
  -> REVIEW_DONE
  -> COMPLIANCE_TRIGGERED
  -> COMPLIANCE_DONE
  -> GATE_READY
```

## 触发条件

### PENDING -> ACCEPTED
- task envelope 字段完整
- assignee 明确
- source_of_truth 明确
- writeback 路径完整

### ACCEPTED -> IN_PROGRESS
- 执行单元确认接单
- 无阻断性依赖未解决

### IN_PROGRESS -> WRITEBACK_DONE
- 对应角色产出已写入标准 writeback 路径
- 文档存在且最小字段齐全

### WRITEBACK_DONE -> REVIEW_TRIGGERED
- 当前 role = execution
- execution_report 已存在

### REVIEW_TRIGGERED -> REVIEW_DONE
- review_report 已存在
- verdict 已写明 `PASS / REQUIRES_CHANGES / FAIL`

### REVIEW_DONE -> COMPLIANCE_TRIGGERED
- 当前 review 结果不是缺件
- compliance 信封已生成

### COMPLIANCE_TRIGGERED -> COMPLIANCE_DONE
- compliance_attestation 已存在
- 决定已写明 `PASS / REQUIRES_CHANGES / FAIL`

### COMPLIANCE_DONE -> GATE_READY
- execution / review / compliance 三件齐全
- 无缺件
- 当前任务满足主控终验输入条件

## 阻断态

### 任意状态 -> BLOCKED
- depends_on 未满足
- task envelope 缺关键字段
- writeback 路径缺失
- 状态停滞超时

### 任意状态 -> DENY
- 发生 scope violation
- 发生 frozen 主线倒灌
- 发生 runtime / 真实外部接入越界
- 发生 compliance fail 且不可局部修复

## 主控官注意点
- `WRITEBACK_DONE` 不等于任务通过
- `COMPLIANCE_DONE` 不等于模块通过
- 只有 `GATE_READY` 才允许进入主控终验池

