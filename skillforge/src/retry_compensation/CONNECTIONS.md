# Retry / Compensation Boundary 接口关系

## 上游: system_execution

### 接口定义
```
system_execution/service → retry_compensation/observer
```

### 数据流向
1. service 执行失败
2. observer 观察失败事件
3. observer 分析失败类型
4. observer 生成失败报告

### 接口契约
- **输入**: FailureEvent (包含 execution_id, error_type, error_context, evidence_ref)
- **输出**: FailureAnalysis (包含 failure_type, failure_reason, retry_advice, compensation_advice)

### 只读观察规则
- Retry / Compensation Boundary **只观察** FailureEvent
- 不修改 FailureEvent 的内容
- 不拦截 system_execution 的执行流程

## 上游: Integration Gateway

### 接口定义
```
integration_gateway/connector → retry_compensation/observer
```

### 数据流向
1. connector 连接失败
2. observer 观察失败事件
3. observer 分析失败类型
4. observer 生成失败报告

### 接口契约
- **输入**: ConnectorFailureEvent (包含 connector_id, error_type, error_context, permit_ref)
- **输出**: FailureAnalysis (包含 failure_type, failure_reason, retry_advice, compensation_advice)

### 只读观察规则
- Retry / Compensation Boundary **只观察** ConnectorFailureEvent
- 不修改 ConnectorFailureEvent 的内容
- 不触发 connector 的重试或补偿

## 下游: Governor

### 接口定义
```
retry_compensation/advisor → governor/decision_maker
```

### 数据流向
1. advisor 生成失败建议
2. governor 接收失败建议
3. governor 决定是否采纳建议
4. governor 生成 permit（如采纳）

### 接口契约
- **输入**: FailureAnalysis (来自 advisor)
- **输出**: GovernorDecision (采纳/拒绝建议，生成 permit)

### 建议提供规则
- Retry / Compensation Boundary **只提供** 建议
- 不强制 governor 采纳建议
- 等待 governor 的最终决策

## 旁路: Frozen 主线

### 引用关系
```
retry_compensation → frozen_main_line
```

### 引用类型
- **gate_decision_ref**: 引用 frozen 主线的 GateDecision
- **evidence_ref**: 引用 frozen 主线的 Evidence
- **audit_pack_ref**: 引用 frozen 主线的 AuditPack

### 只读引用规则
- Retry / Compensation Boundary **只引用** frozen 对象
- **不修改** frozen 对象
- **不覆盖** frozen 对象的决策结果

## 接口文件
- [boundary_interface.py](./boundary_interface.py) - 边界接口定义
- [retry_policy.py](./retry_policy.py) - 重试策略（仅骨架）
- [compensation_advisor.py](./compensation_advisor.py) - 补偿建议（仅骨架）
