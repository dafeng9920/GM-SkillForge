# Publish / Notify / Sync Boundary 不负责项

## 绝对禁止

### 1. 真实动作执行
**禁止事项**:
- 不得执行真实发布操作
- 不得发送真实通知消息
- 不得执行真实同步操作
- 不得调用真实外部系统 API

**理由**: 当前阶段只定义边界，不进入 runtime。

### 2. Permit 生成
**禁止事项**:
- 不得生成 PublishPermit
- 不得生成 NotifyPermit
- 不得生成 SyncPermit
- 不得修改 permit 语义

**理由**: Permit 只能由 Governor 生成。

### 3. 裁决权
**禁止事项**:
- 不得做最终 PASS/FAIL 判定
- 不得替代 Governor 的裁决职责
- 不得替代 Gate 的审查职责
- 不得替代 Release 的发布职责

**理由**: 裁决权属于 Governor/Gate/Release，Boundary 只是边界层。

### 4. Evidence 生成
**禁止事项**:
- 不得生成核心 Evidence
- 不得改写 AuditPack
- 不得覆盖 Evidence 引用

**理由**: Evidence/AuditPack 只能由 SkillForge 内核生成。

### 5. 自动重试/补偿
**禁止事项**:
- 不得自动重试失败动作
- 不得自动执行补偿动作
- 不得自行决定重试策略

**理由**: 重试/补偿由 E5 (Retry/Compensation Boundary) 负责，且需要新的 permit。

## 接口边界

### 与 E4 External Action Policy 的边界
**不做**:
- 不重复定义关键动作列表
- 不重复实现 permit 校验逻辑

**只做**:
- 使用 E4 的 CRITICAL_ACTIONS
- 调用 E4 的 permit 校验接口
- 定义 publish/notify/sync 的具体边界规则

### 与 E5 Retry/Compensation Boundary 的边界
**不做**:
- 不实现失败观察逻辑
- 不实现重试建议生成
- 不实现补偿建议生成

**只做**:
- 接收 E5 的失败事件
- 根据 E5 的建议重新执行（仅定义接口）
- 需要新的 permit 才能重新执行

### 与 External Connector 的边界
**不做**:
- 不实现连接器逻辑
- 不管理连接器状态
- 不处理连接器错误

**只做**:
- 定义连接器请求接口
- 定义连接器结果接口
- 路由到正确的连接器

### 与 Frozen 主线的边界
**不做**:
- 不修改 frozen 对象
- 不回写治理裁决对象
- 不改变 frozen 主线边界

**只做**:
- 只读承接 frozen 主线的公开结果
- 引用 frozen 的 GateDecision/permit/Evidence

## 数据边界

### 输入数据
- 只接收来自 system_execution 的执行意图
- 只接收来自 E5 的重试/补偿建议
- 只读取 permit 引用

### 输出数据
- 只输出动作边界检查结果
- 只输出 permit 校验结果（委托给 E4）
- 不输出执行结果（因为没有真实执行）

### 传递数据
- 只传递 permit 引用
- 只传递 Evidence 引用
- 只传递 GateDecision 引用
