# Retry / Compensation Boundary 不负责项

## 绝对禁止

### 1. 自动重试
**禁止事项**:
- 不得自动触发重试
- 不得自动执行重试逻辑
- 不得自行决定重试次数
- 不得自行决定重试间隔

**理由**: 重试是执行动作，必须由 Governor 授权并持有 permit。

### 2. 自动补偿
**禁止事项**:
- 不得自动触发补偿
- 不得自动执行补偿逻辑
- 不得自行决定补偿方案
- 不得修改已执行的结果

**理由**: 补偿是改变系统状态的动作，必须由 Governor 授权并持有 permit。

### 3. 裁决权
**禁止事项**:
- 不得生成 GateDecision
- 不得修改原有的 GateDecision
- 不得覆盖原有的 PASS/FAIL 判定
- 不得替代 Governor 的裁决职责

**理由**: 失败建议 ≠ 最终裁决，裁决权属于 Governor。

### 4. Evidence 生成
**禁止事项**:
- 不得生成核心 Evidence
- 不得改写 AuditPack
- 不得覆盖 Evidence 引用
- 不得二次生成治理裁决对象

**理由**: Evidence/AuditPack 只能由 SkillForge 内核生成。

### 5. Runtime 执行
**禁止事项**:
- 不得进入 runtime 执行层
- 不得实现真实业务逻辑
- 不得接入真实外部系统
- 不得进行真实联调

**理由**: 当前阶段只做准备骨架，不进入 runtime。

### 6. Frozen 主线修改
**禁止事项**:
- 不得修改 frozen 主线的 GateDecision
- 不得修改 frozen 主线的 permit
- 不得修改 frozen 主线的 Evidence
- 不得修改 frozen 主线的 AuditPack

**理由**: Frozen 主线是不可变的，失败建议是旁路观察。

## 接口边界

### 与 system_execution 的边界
**不做**:
- 不干预 system_execution 的执行流程
- 不拦截 system_execution 的失败事件
- 不修改 system_execution 的执行结果

**只做**:
- 观察 system_execution 的失败事件
- 分析失败类型与原因
- 提供建议给 Governor

### 与 Governor 的边界
**不做**:
- 不替代 Governor 的裁决职责
- 不自动执行 Governor 的决策
- 不修改 Governor 的 permit

**只做**:
- 提供建议给 Governor
- 等待 Governor 采纳建议
- 等待 Governor 授权执行

### 与 Frozen 主线的边界
**不做**:
- 不修改 frozen 对象
- 不回写治理裁决对象
- 不改变 frozen 主线边界

**只做**:
- 只读承接 frozen 主线的公开结果
- 引用 frozen 的 GateDecision/permit/Evidence
- 基于 frozen 结果提供建议
