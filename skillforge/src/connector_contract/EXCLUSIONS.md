# Connector Contract 不负责项

## 不实现连接

### 禁止事项
- 不实现真实外部系统连接
- 不实现协议客户端（Git、HTTP、WebSocket 等）
- 不实现连接池管理
- 不实现连接重试逻辑
- 不实现连接健康检查

### 理由
真实连接实现是 Integration Gateway 的职责。Connector Contract 只定义接口契约。

## 不生成 Permit

### 禁止事项
- 不生成任何类型的 permit
- 不验证 permit 有效性
- 不续期 permit
- 不撤销 permit
- 不存储 permit

### 理由
Permit 生成和验证是 Governor 的职责。Connector Contract 只声明 permit 需求。

## 不修改 Evidence/AuditPack

### 禁止事项
- 不生成 Evidence
- 不修改 Evidence
- 不生成 AuditPack
- 不修改 AuditPack
- 不删除 Evidence/AuditPack

### 理由
Evidence/AuditPack 生成和修改是 SkillForge 内核的职责。Connector Contract 只声明引用规则。

## 不裁决

### 禁止事项
- 不做 PASS/FAIL 判定
- 不做风险评估
- 不做质量判定
- 不做合规判定

### 理由
裁决是 Governor/Gate/Release 的职责。Connector Contract 只定义接口契约。

## 不进入 Runtime

### 禁止事项
- 不执行外部动作
- 不处理外部事件
- 不管理外部会话
- 不处理外部错误

### 理由
Runtime 执行是 Integration Gateway 的职责。Connector Contract 停留在骨架定义。

## 不改写 Frozen 主线

### 禁止事项
- 不修改 frozen 对象边界
- 不回写 GateDecision
- 不回写 EvidenceRef
- 不回写 AuditPack
- 不生成新的治理裁决对象

### 理由
Frozen 主线不可倒灌。Connector Contract 只读承接 frozen 结果。

## 不替代 Integration Gateway

### 禁止事项
- 不实现路由逻辑
- 不实现触发逻辑
- 不实现搬运逻辑
- 不实现连接器生命周期管理

### 理由
这些是 Integration Gateway 的职责。Connector Contract 只提供接口契约。

## 当前阶段硬约束
- 不得接入真实外部系统
- 不得进入 runtime
- 不得生成真实外部协议实现
- 不得改写 frozen 对象
