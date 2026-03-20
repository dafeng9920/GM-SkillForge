# Integration Gateway 职责定义

## 负责事项

### 1. 触发 (Trigger)
- 接收来自 system_execution 的执行触发信号
- 将触发信号转换为外部系统可理解的格式
- 路由触发信号到正确的连接器

### 2. 路由 (Router)
- 根据执行意图类型，路由到对应的外部连接器
- 维护连接器注册表（仅定义，不实现）
- 提供路由决策的接口（仅骨架）

### 3. 搬运 (Transport)
- 在 SkillForge 内核与外部连接器之间搬运数据
- 转换数据格式（仅定义转换规则，不实现）
- 传递 Evidence/AuditPack 引用（不生成，只搬运）

### 4. 连接 (Connection)
- 提供与外部连接器的连接接口（仅定义）
- 管理连接器生命周期（仅定义生命周期规则）
- 维护连接器状态（仅定义状态模型）

### 5. 引用搬运 (Reference Transport)
- 搬运 GateDecision 引用（不生成）
- 搬运 permit 引用（不生成）
- 搬运 Evidence/AuditPack 引用（不生成）

## 不负责事项
详见 [EXCLUSIONS.md](./EXCLUSIONS.md)

## 接口关系
详见 [CONNECTIONS.md](./CONNECTIONS.md)

## Permit 规则
详见 [PERMIT_RULES.md](./PERMIT_RULES.md)

## Runtime 边界
详见 [RUNTIME_BOUNDARY.md](./RUNTIME_BOUNDARY.md)
