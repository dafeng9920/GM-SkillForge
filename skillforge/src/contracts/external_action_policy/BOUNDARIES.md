# External Action Policy - 边界说明

**Task ID**: X4
**Executor**: Kior-B
**Date**: 2026-03-20

## 概述

本文档定义 External Action Policy 子面与其他子面（Connector Contract、Integration Gateway、Secrets/Credentials Boundary、System Execution）的边界说明。

## 职责定位

### External Action Policy 的核心职责

1. **动作分类**: 区分关键动作和非关键动作
2. **Permit 要求判定**: 判断动作是否需要 permit
3. **策略决策**: 评估动作是否允许执行
4. **Evidence 搬运规则**: 定义只读搬运规则

### 不负责项（已声明）

1. **不负责** permit 生成（Governance 层负责）
2. **不负责** Evidence 生成（Gate 层负责）
3. **不负责** AuditPack 生成（T14 负责）
4. **不负责** 外部动作真实执行（External Connector 负责）
5. **不负责** 外部系统状态管理

---

## 与 Connector Contract 的边界

### 职责划分

| 子面 | 职责 | 接口 |
|------|------|------|
| **Connector Contract** | 定义外部连接契约 | `ExternalConnectionContract` |
| **External Action Policy** | 定义动作分类和 permit 要求 | `ActionPolicyDecision` |

### 数据流向

```
Connector Contract --> External Action Policy
                         (查询是否需要 permit)
                         <-- 返回决策
```

### 禁止项

1. **Connector Contract 不得**:
   - 实现动作分类逻辑
   - 判断是否需要 permit
   - 修改策略决策

2. **External Action Policy 不得**:
   - 定义外部连接接口
   - 实现连接逻辑
   - 存储连接凭据

### 接口契约

```python
# Connector Contract 声明需要的 permit
@dataclass(frozen=True)
class ExternalConnectionContract:
    required_permits: List[str]  # 声明

# External Action Policy 判断是否需要 permit
def requires_permit(action: str) -> bool:
    return action in CRITICAL_ACTIONS
```

---

## 与 Integration Gateway 的边界

### 职责划分

| 子面 | 职责 | 接口 |
|------|------|------|
| **Integration Gateway** | 搬运 ExecutionIntent 和 Evidence | `GatewayInterface` |
| **External Action Policy** | 评估动作是否允许执行 | `ExternalActionPolicy` |

### 数据流向

```
System Execution --> Integration Gateway
                          |
                          v
                   External Action Policy
                   (评估 action 是否允许)
                          |
                          <-- 返回决策
```

### Permit 使用时机

1. **Integration Gateway** 接收 `ExecutionIntent`
2. 提取 `action_type`
3. 咨询 `ExternalActionPolicy.evaluate_action()`
4. 如果 `allowed=False`，阻断执行
5. 如果 `allowed=True`，继续搬运

### 接口契约

```python
# Integration Gateway 的 ExecutionIntent
@dataclass
class ExecutionIntent:
    action_type: str  # "publish" | "sync" | "notify" | "execute"
    permit_ref: str
    evidence_refs: List[str]

# External Action Policy 的评估
decision = policy.evaluate_action(
    action="PUBLISH_LISTING",
    permit_token=intent.permit_ref,
    execution_context={...},
)
```

### 禁止项

1. **Integration Gateway 不得**:
   - 自行判断动作是否关键
   - 绕过 permit 检查
   - 修改策略决策

2. **External Action Policy 不得**:
   - 实现搬运逻辑
   - 连接外部系统
   - 存储执行状态

---

## 与 Secrets/Credentials Boundary 的边界

### 职责划分

| 子面 | 职责 | 接口 |
|------|------|------|
| **Secrets/Credentials Boundary** | 定义凭据分层规则 | `CredentialBoundary` |
| **External Action Policy** | 定义动作 permit 要求 | `ActionPolicyDecision` |

### 独立性说明

**External Action Policy 与凭据管理完全独立**:

1. **Permit ≠ Credentials**:
   - Permit 是执行许可证明
   - Credentials 是身份认证凭据
   - 两者分离存储和使用

2. **职责不重叠**:
   - Secrets Boundary 定义 L0-L4 凭据分层
   - Action Policy 定义关键动作分类
   - 无交叉依赖

### 接口契约

```python
# Secrets Boundary 的凭据引用
@dataclass(frozen=True)
class CredentialBoundary:
    credential_type: str  # L0 | L1 | L2 | L3 | L4
    access_pattern: str  # "read" | "reference"

# Action Policy 的 permit 要求
@dataclass
class ActionPolicyDecision:
    permit_required: bool
    allowed: bool
    block_reason: ExecutionBlockReason | None
```

### 禁止项

1. **Secrets Boundary 不得**:
   - 定义动作分类规则
   - 判断是否需要 permit

2. **External Action Policy 不得**:
   - 定义凭据分层规则
   - 存储或处理凭据值
   - 引用凭据哈希

---

## 与 System Execution 的边界

### 职责划分

| 子面 | 职责 | 接口 |
|------|------|------|
| **System Execution** | 承接内核执行控制 | `OrchestratorInterface` |
| **External Action Policy** | 提供策略决策 | `ExternalActionPolicy` |

### 接口调用方向

```
System Execution --> External Action Policy
                    (查询动作是否允许)
                    <-- 返回决策
```

### 接口清单

```python
# System Execution 导入
from skillforge.src.contracts.external_action_policy import (
    evaluate_action,
    is_critical_action,
    requires_permit,
)

# System Execution 使用
if is_critical_action(action_type):
    decision = evaluate_action(action_type, permit_token, context)
    if not decision.allowed:
        raise PermitRequiredError(action_type)
```

### 禁止项

1. **System Execution 不得**:
   - 自行实现动作分类
   - 绕过 permit 检查

2. **External Action Policy 不得**:
   - 实现执行控制逻辑
   - 管理执行状态
   - 调度任务执行

---

## 跨子面协同场景

### 场景 1: 发布技能到外部系统

```
1. System Execution 生成 ExecutionIntent (action="PUBLISH_LISTING")
2. Integration Gateway 接收 Intent
3. Integration Gateway 咨询 External Action Policy
4. External Action Policy 检查 permit
5. 如果允许，Integration Gateway 搬运到 Connector Contract
6. Connector Contract 声明需要 permit（验证）
7. Secrets Boundary 提供凭据引用（如需要）
8. 最终由 External Connector 执行（当前阶段未实现）
```

### 场景 2: 外部 API 调用

```
1. System Execution 生成 ExecutionIntent (action="EXECUTE_VIA_N8N")
2. Integration Gateway 接收 Intent
3. Integration Gateway 咨询 External Action Policy
4. External Action Policy 检查 permit
5. 如果允许，Integration Gateway 搬运到 Connector Contract
6. Connector Contract 验证 permit 声明
7. Secrets Boundary 提供 L1 凭据引用（如需要）
```

### 场景 3: 归档 AuditPack

```
1. System Execution 生成 ExecutionIntent (action="EXPORT_AUDIT_PACK")
2. Integration Gateway 接收 Intent
3. Integration Gateway 咨询 External Action Policy
4. External Action Policy 检查 permit
5. 如果允许，Integration Gateway 搬运 AuditPack（只读）
6. Connector Contract 声明需要 permit
7. 最终归档到外部存储（当前阶段未实现）
```

---

## 违规检测规则

### 检测点

1. **Permit 绕过检测**:
   - 关键动作无 permit
   - permit 格式错误
   - permit 已过期

2. **Evidence 篡改检测**:
   - source_locator 被修改
   - content_hash 不匹配
   - 引用链路断裂

3. **越界行为检测**:
   - Action Policy 实现连接逻辑
   - Gateway 自行裁决 permit
   - Connector 生成 permit

### 检测方法

```python
# 运行时检测（当前阶段未实现）
def detect_violation(intent: ExecutionIntent) -> ViolationReport:
    violations = []

    # 检测 permit 绕过
    if is_critical_action(intent.action_type):
        if not intent.permit_ref:
            violations.append("PERMIT_BYPASS")

    # 检测 Evidence 篡改
    for ref in intent.evidence_refs:
        if not verify_evidence_integrity(ref):
            violations.append("EVIDENCE_TAMPERED")

    return ViolationReport(violations)
```

---

## 边界违规后果

| 违规类型 | 后果 | 处理方式 |
|---------|------|---------|
| Permit 绕过 | 阻断执行 | 返回 PERMIT_REQUIRED |
| Evidence 篡改 | 阻断执行 | 返回 EVIDENCE_CORRUPTED |
| 越界行为 | 升级主控官 | 触发 ESCALATION |
| Secrets 泄露 | 立即终止 | 返回 SECRETS_LEAK_DETECTED |

---

**文档结束**
