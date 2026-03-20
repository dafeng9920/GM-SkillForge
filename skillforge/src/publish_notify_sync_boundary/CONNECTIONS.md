# Publish / Notify / Sync Boundary 接口关系

## 上游: system_execution

### 接口定义
```
system_execution/orchestrator → publish_notify_sync_boundary/boundary
```

### 数据流向
1. orchestrator 完成内部编排
2. 生成执行意图 (ExecutionIntent)
3. boundary 接收执行意图
4. boundary 检查动作类型和 permit

### 接口契约
- **输入**: ExecutionIntent (包含 skill_id, action_type, payload, permit_ref)
- **输出**: BoundaryCheckResult (包含 allowed, block_reason, permit_check_result)

### 只读承接规则
- Boundary **只读** ExecutionIntent
- 不修改 ExecutionIntent 的内容
- 不重新编排执行流程

## 协作: E4 External Action Policy

### 接口定义
```
publish_notify_sync_boundary → external_action_policy
```

### 协作方式
1. Boundary 检查动作类型
2. 调用 E4 的 `is_critical_action()` 检查是否为关键动作
3. 调用 E4 的 `evaluate_action()` 进行 permit 校验
4. E4 返回 ActionPolicyDecision
5. Boundary 根据 Decision 决定是否允许动作

### 数据结构
```python
# E4 提供
class ActionPolicyDecision:
    action: str
    allowed: bool
    category: ActionCategory
    permit_required: bool
    block_reason: ExecutionBlockReason | None
    permit_check_result: PermitCheckResult | None

# E6 使用
class BoundaryCheckResult:
    action: str
    boundary_type: BoundaryType  # PUBLISH/NOTIFY/SYNC
    allowed: bool
    block_reason: str | None
    permit_required: bool
    policy_decision: ActionPolicyDecision  # 来自 E4
```

## 协作: E5 Retry/Compensation Boundary

### 接口定义
```
retry_compensation/observer → publish_notify_sync_boundary/boundary
```

### 协作方式
1. E5 观察到失败事件
2. E5 生成重试/补偿建议
3. E6 接收建议（仅定义接口）
4. E6 需要新的 permit 才能重新执行

### 数据结构
```python
# E5 提供
class RetryAdvice:
    action: str
    retry_recommended: bool
    max_retries: int
    required_permit_type: str  # "RETRY_PERMIT"

class CompensationAdvice:
    action: str
    compensation_recommended: bool
    compensation_type: str
    required_permit_type: str  # "COMPENSATION_PERMIT"

# E6 使用
class ReexecuteRequest:
    original_action: str
    advice: RetryAdvice | CompensationAdvice
    new_permit_ref: str  # 必须有新的 permit
```

## 下游: External Connector

### 接口定义
```
publish_notify_sync_boundary/boundary → external_connector/executor
```

### 数据流向
1. Boundary 完成边界检查
2. Boundary 生成连接器请求
3. Connector 执行动作（当前阶段不实现）
4. Connector 返回执行结果

### 接口契约
- **输入**: ConnectorRequest (包含 connector_type, action, payload, permit_ref)
- **输出**: ConnectorResult (包含 status, output, evidence_ref)

### 不实现规则
- 当前阶段**不实现**真实 connector
- 只定义 connector 接口契约
- Boundary 只负责边界检查，不负责执行

## 旁路: Governor/Gate/Release

### 引用关系
```
publish_notify_sync_boundary → governor/gate/release
```

### 引用类型
- **permit_ref**: 引用 Governor 生成的 permit
- **gate_decision_ref**: 引用 Gate 的审查决策
- **release_decision_ref**: 引用 Release 的发布决策

### 只引用规则
- Boundary **只引用** 上述决策对象
- **不生成** 新的决策对象
- **不修改** 引用的决策对象

## 引用: Evidence/AuditPack

### 引用关系
```
publish_notify_sync_boundary → evidence/audit_pack
```

### 引用类型
- **evidence_ref**: 引用内核生成的 Evidence
- **audit_pack_ref**: 引用内核生成的 AuditPack

### 只搬运规则
- Boundary **只搬运** Evidence/AuditPack 引用
- **不生成** 新的 Evidence/AuditPack
- **不修改** 引用的 Evidence/AuditPack

## 接口文件
- [boundary_interface.py](./boundary_interface.py) - 边界接口定义
- [publish_boundary.py](./publish_boundary.py) - 发布边界接口
- [notify_boundary.py](./notify_boundary.py) - 通知边界接口
- [sync_boundary.py](./sync_boundary.py) - 同步边界接口
