# Escalation Protocol v1

## 目标
- 定义什么情况下任务必须升级到主控官，以及升级时应附带什么信息。

## 允许升级的触发条件
- `scope_violation`
- `blocking_dependency`
- `ambiguous_spec`
- `review_deny`
- `compliance_fail`
- `state_timeout`

## 升级规则

### 1. scope_violation
- 发现任务要求超出原任务卡边界
- 动作：暂停当前任务，升级主控官

### 2. blocking_dependency
- 依赖任务未完成且本任务无法继续
- 动作：标记 `BLOCKED`，升级主控官

### 3. ambiguous_spec
- 任务说明不足，执行者无法合理推断
- 动作：不允许自行扩权，升级主控官

### 4. review_deny
- review 给出 `FAIL`
- 动作：停止进入 compliance，升级主控官裁决

### 5. compliance_fail
- compliance 给出 `FAIL`
- 动作：停止继续接力，升级主控官裁决

### 6. state_timeout
- 任务长时间停留在某状态
- 动作：标记超时并升级主控官

## 升级包最小内容
- `task_id`
- `current_role`
- `current_state`
- `trigger`
- `blocking_reason`
- `evidence_ref`
- `suggested_next_action`

## 主控官收到升级后的裁决类型
- `允许局部修正后继续`
- `退回到前一环`
- `整体退回`
- `拒绝继续`

## 边界提醒
- escalation protocol 只负责“何时叫回主控官”
- 不负责替主控官做最终决定

