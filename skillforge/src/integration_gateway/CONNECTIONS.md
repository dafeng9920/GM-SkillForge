# Integration Gateway 接口关系

## 上游: system_execution

### 接口定义
```
system_execution/orchestrator → integration_gateway/router
```

### 数据流向
1. orchestrator 完成内部编排
2. 生成执行意图 (ExecutionIntent)
3. router 接收执行意图
4. router 路由到对应的 connector

### 接口契约
- **输入**: ExecutionIntent (包含 skill_id, action_type, payload, permit_ref)
- **输出**: RoutingResult (包含 target_connector, transformed_payload)

### 只读承接规则
- Integration Gateway **只读** ExecutionIntent
- 不修改 ExecutionIntent 的内容
- 不重新编排执行流程

## 下游: External Connector

### 接口定义
```
integration_gateway/router → external_connector/executor
```

### 数据流向
1. router 确定目标 connector
2. transporter 转换 payload 格式
3. trigger 触发 connector 执行
4. transporter 接收 connector 结果

### 接口契约
- **输入**: ConnectorRequest (包含 connector_type, action, payload, permit_ref)
- **输出**: ConnectorResult (包含 status, output, evidence_ref)

### 不实现规则
- 当前阶段**不实现**真实 connector
- 只定义 connector 接口契约
- 只定义 connector 注册表结构

## 旁路: Governor/Gate/Release

### 引用关系
```
integration_gateway → governor/gate/release
```

### 引用类型
- **permit_ref**: 引用 Governor 生成的 permit
- **gate_decision_ref**: 引用 Gate 的审查决策
- **release_decision_ref**: 引用 Release 的发布决策

### 只引用规则
- Integration Gateway **只引用** 上述决策对象
- **不生成** 新的决策对象
- **不修改** 引用的决策对象

## 引用: Evidence/AuditPack

### 引用关系
```
integration_gateway → evidence/audit_pack
```

### 引用类型
- **evidence_ref**: 引用内核生成的 Evidence
- **audit_pack_ref**: 引用内核生成的 AuditPack

### 只搬运规则
- Integration Gateway **只搬运** Evidence/AuditPack 引用
- **不生成** 新的 Evidence/AuditPack
- **不修改** 引用的 Evidence/AuditPack

## 接口文件
- [gateway_interface.py](./gateway_interface.py) - 网关接口定义
- [router.py](./router.py) - 路由器接口
- [trigger.py](./trigger.py) - 触发器接口
- [transporter.py](./transporter.py) - 搬运器接口
