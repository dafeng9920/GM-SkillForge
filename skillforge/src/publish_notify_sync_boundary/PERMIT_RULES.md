# Publish / Notify / Sync Boundary Permit 使用规则

## 核心原则
**所有 publish / notify / sync 动作必须持 permit 行动，不能自行裁决。**

## Permit 类型

### 1. PublishPermit
**用途**: 发布技能或资源到外部系统

**必需条件**:
- 必须持有有效的 publish_permit_ref
- permit 必须由 Governor 生成
- permit 必须包含目标系统信息
- permit 必须包含发布范围

**关联动作**:
- PUBLISH_LISTING
- UPGRADE_REPLACE_ACTIVE

**禁止事项**:
- 不得在无 permit 的情况下发布
- 不得扩大 permit 范围

### 2. NotifyPermit
**用途**: 向外部系统发送通知消息

**必需条件**:
- 必须持有有效的 notify_permit_ref
- permit 必须由 Governor 生成
- permit 必须包含通知目标
- permit 必须包含通知类型

**关联动作**:
- SEND_SLACK_MESSAGE
- SEND_EMAIL_NOTIFICATION
- SEND_WEBHOOK_NOTIFICATION

**禁止事项**:
- 不得在无 permit 的情况下发送通知
- 不得批量绕过 permit

### 3. SyncPermit
**用途**: 同步状态到外部系统

**必需条件**:
- 必须持有有效的 sync_permit_ref
- permit 必须由 Governor 生成
- permit 必须包含同步目标
- permit 必须包含同步范围

**关联动作**:
- SYNC_SKILL_STATUS
- SYNC_CONFIGURATION
- SYNC_STATE_TO_EXTERNAL

**禁止事项**:
- 不得在无 permit 的情况下同步
- 不得伪造同步 permit

### 4. RetryPermit (与 E5 协作)
**用途**: 重试失败的 publish/notify/sync 动作

**必需条件**:
- 必须持有有效的 retry_permit_ref
- permit 必须由 Governor 生成（基于 E5 的建议）
- permit 必须包含重试动作和范围

**禁止事项**:
- 不得在无 permit 的情况下重试
- 不得无限重试

## Permit 验证流程

### 验证步骤
1. **接收**: 从 system_execution 接收 ExecutionIntent
2. **分类**: 确定动作类型 (PUBLISH/NOTIFY/SYNC)
3. **委托**: 调用 E4 的 `evaluate_action()` 进行 permit 校验
4. **检查**: 检查 permit 类型是否匹配动作类型
5. **传递**: 将 permit_ref 传递给 connector
6. **记录**: 记录 permit 使用（仅定义记录结构）

### 验证规则（委托给 E4）
```python
# E6 定义接口，E4 实现校验
class BoundaryInterface:
    def check_permit_for_action(self, action: str, permit_ref: str) -> PermitCheckResult:
        """检查动作的 permit 有效性"""
        # 委托给 E4 的 permit_check.py
        return external_action_policy.validate_permit(permit_ref, action)

    def check_permit_type_match(self, action: str, permit_ref: str) -> bool:
        """检查 permit 类型是否匹配动作类型"""
        # PUBLISH 动作需要 PublishPermit
        # NOTIFY 动作需要 NotifyPermit
        # SYNC 动作需要 SyncPermit
        raise NotImplementedError("当前阶段不实现验证逻辑")
```

## Permit 类型映射

### 动作类型 → Permit 类型

| 动作类型 | Permit 类型 | E4 关键动作 |
|---------|------------|------------|
| PUBLISH_LISTING | PublishPermit | ✅ |
| UPGRADE_REPLACE_ACTIVE | PublishPermit | ✅ |
| SEND_SLACK_MESSAGE | NotifyPermit | - |
| SEND_EMAIL_NOTIFICATION | NotifyPermit | - |
| SYNC_SKILL_STATUS | SyncPermit | - |
| SYNC_CONFIGURATION | SyncPermit | - |

### Permit 错误码（使用 E4 定义的错误码）

| 错误码 | 含义 | 处理 |
|--------|------|------|
| PERMIT_REQUIRED | permit 缺失 | 阻断执行 |
| PERMIT_INVALID | permit 格式无效 | 阻断执行 |
| PERMIT_EXPIRED | permit 过期 | 阻断执行 |
| PERMIT_SCOPE_MISMATCH | scope 不匹配 | 阻断执行 |
| PERMIT_SUBJECT_MISMATCH | subject 不匹配 | 阻断执行 |
| PERMIT_TYPE_MISMATCH | permit 类型不匹配 | 阻断执行 |
| PERMIT_REVOKED | permit 已撤销 | 阻断执行 |

## Permit 引用规则

### 引用传递
- Boundary **只传递** permit 引用
- **不生成** 新的 permit
- **不修改** 引用的 permit

### 引用格式
```python
@dataclass
class PermitRef:
    """Permit 引用"""
    permit_id: str           # Permit ID
    permit_type: str         # Permit 类型 (PUBLISH/NOTIFY/SYNC/RETRY)
    governor_id: str         # 生成该 permit 的 Governor ID
    decision_ref: str        # 关联的 GateDecision 引用
    created_at: str          # 创建时间
    expires_at: str          # 过期时间
    scope: str               # 许可范围
    target_system: str       # 目标系统
```

## Permit 绕过检测

### 自动拒绝条件
- 如果 permit_ref 缺失 → 自动拒绝
- 如果 permit_ref 格式错误 → 自动拒绝
- 如果 permit 引用不存在的 Governor → 自动拒绝
- 如果 permit 已过期 → 自动拒绝（委托给 E4）
- 如果 permit 类型不匹配 → 自动拒绝

### 违规后果
- 任何 permit 绕过尝试都应被记录
- 任何 permit 绕过尝试都应触发告警（当前阶段仅定义告警接口）

## 与 E5 Retry/Compensation 的 Permit 规则

### 重试需要新 Permit
- 原动作失败后，需要新的 RetryPermit 才能重试
- RetryPermit 必须基于 E5 的 RetryAdvice 生成
- RetryPermit 由 Governor 生成，不是 E6

### 补偿需要新 Permit
- 补偿动作需要新的 CompensationPermit
- CompensationPermit 必须基于 E5 的 CompensationAdvice 生成
- CompensationPermit 由 Governor 生成，不是 E6

### Permit 链路
```
Original Action (with Permit)
    ↓ (Fail)
E5 RetryAdvice
    ↓
Governor generates RetryPermit
    ↓
E6 Boundary checks RetryPermit
    ↓
Retry Action
```

## 当前阶段限制
- **只定义**: permit 验证接口
- **不实现**: permit 验证逻辑（委托给 E4）
- **不连接**: 真实 Governor 进行验证
