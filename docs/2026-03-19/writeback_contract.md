# Writeback Contract v1

## 目标
- 统一规定 AI 军团三权输出必须写回的标准文档与最小字段。

## 统一规则
- 不写回标准路径，不算完成
- 写回件缺最小字段，不算回收成功
- 口头“做完了”不构成正式回收

## Execution Report

### 文件
- `{task_id}_execution_report.md`

### 必填字段
- `task_id`
- `executor`
- `status`
- `deliverables`
- `notes`

### 最低要求
- 必须列出改动/产物
- 必须指向至少一个 EvidenceRef

## Review Report

### 文件
- `{task_id}_review_report.md`

### 必填字段
- `task_id`
- `reviewer`
- `executor`
- `decision`
- `findings`
- `evidence_ref`

### 决定值
- `PASS`
- `REQUIRES_CHANGES`
- `FAIL`

## Compliance Attestation

### 文件
- `{task_id}_compliance_attestation.md`

### 必填字段
- `task_id`
- `compliance_officer`
- `executor`
- `reviewer`
- `decision`
- `zero_exception_checks`
- `evidence_ref`

### 决定值
- `PASS`
- `REQUIRES_CHANGES`
- `FAIL`

## Final Gate

### 文件
- `{task_id}_final_gate.md`

### 必填字段
- `task_id`
- `controller`
- `module_decision`
- `basis`
- `next_action`

## 主控官回收检查清单
1. 三件是否都存在
2. decision 是否明确
3. EvidenceRef 是否存在
4. 路径是否与任务卡一致
5. 是否允许进入终验

