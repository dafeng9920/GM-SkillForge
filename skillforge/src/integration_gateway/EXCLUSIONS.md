# Integration Gateway 不负责项

## 绝对禁止

### 1. 裁决权
**禁止事项**:
- 不得生成 GateDecision
- 不得生成 permit
- 不得生成 AuditPack
- 不得做最终 PASS/FAIL 判定
- 不得替代 Governor 的裁决职责
- 不得替代 Gate 的审查职责
- 不得替代 Release 的发布职责

**理由**: 裁决权属于 Governor/Gate/Release/Audit，Integration Gateway 只是连接层。

### 2. Evidence 生成
**禁止事项**:
- 不得生成核心 Evidence
- 不得改写 AuditPack
- 不得覆盖 Evidence 引用
- 不得二次生成治理裁决对象

**理由**: Evidence/AuditPack 只能由 SkillForge 内核生成。

### 3. Runtime 执行
**禁止事项**:
- 不得进入 runtime 执行层
- 不得实现真实业务逻辑
- 不得接入真实外部系统
- 不得进行真实联调

**理由**: 当前阶段只做准备骨架，不进入 runtime。

### 4. Permit 绕过
**禁止事项**:
- 不得绕过 permit 触发关键动作
- 不得自行判定 permit 可忽略
- 不得修改 permit 语义

**理由**: 关键动作必须持 permit，这是治理底线。

## 接口边界

### 与 system_execution 的边界
**不做**:
- 不替代 system_execution 的编排职责
- 不做二次编排
- 不做二次路由决策

**只做**:
- 接收已编排的执行意图
- 按照编排结果路由到连接器

### 与 External Connector 的边界
**不做**:
- 不实现连接器逻辑
- 不管理连接器内部状态
- 不处理连接器错误恢复

**只做**:
- 提供连接器注册接口
- 路由到正确的连接器
- 搬运数据到连接器

### 与 Frozen 主线的边界
**不做**:
- 不修改 frozen 对象
- 不回写治理裁决对象
- 不改变 frozen 主线边界

**只做**:
- 只读承接 frozen 主线的公开结果
- 引用 frozen 的 GateDecision/permit/Evidence
