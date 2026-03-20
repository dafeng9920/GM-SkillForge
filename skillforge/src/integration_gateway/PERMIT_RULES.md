# Integration Gateway Permit 使用规则

## 核心原则
**关键动作必须持 permit 行动，不能自行裁决。**

## Permit 类型

### 1. Publish Permit
**用途**: 发布 skill 到外部系统

**必需条件**:
- 必须持有有效的 publish_permit_ref
- permit 必须由 Governor 生成
- permit 必须未过期

**禁止事项**:
- 不得在无 permit 的情况下发布
- 不得自行判定 permit 可忽略

### 2. Sync Permit
**用途**: 同步状态到外部系统

**必需条件**:
- 必须持有有效的 sync_permit_ref
- permit 必须由 Governor 生成
- permit 必须针对目标系统

**禁止事项**:
- 不得在无 permit 的情况下同步
- 不得伪造 sync permit

### 3. Notify Permit
**用途**: 发送通知到外部系统

**必需条件**:
- 必须持有有效的 notify_permit_ref
- permit 必须由 Governor 生成
- permit 必须指定通知目标

**禁止事项**:
- 不得在无 permit 的情况下发送通知
- 不得批量绕过 permit

### 4. Execute Permit
**用途**: 执行外部动作

**必需条件**:
- 必须持有有效的 execute_permit_ref
- permit 必须由 Governor 生成
- permit 必须包含动作类型和范围

**禁止事项**:
- 不得在无 permit 的情况下执行外部动作
- 不得扩大 permit 范围

## Permit 验证流程

### 验证步骤
1. **接收**: 从 system_execution 接收 ExecutionIntent
2. **提取**: 提取 permit_ref 引用
3. **验证**: 验证 permit 有效性（当前阶段仅定义验证接口）
4. **传递**: 将 permit_ref 传递给 connector
5. **记录**: 记录 permit 使用（仅定义记录结构）

### 验证规则（仅定义，不实现）
```python
# 仅定义接口，不实现验证逻辑
class PermitValidator:
    def validate(self, permit_ref: str) -> ValidationResult:
        """验证 permit 有效性"""
        raise NotImplementedError("当前阶段不实现验证逻辑")

    def check_expiry(self, permit_ref: str) -> bool:
        """检查 permit 是否过期"""
        raise NotImplementedError("当前阶段不实现验证逻辑")

    def check_scope(self, permit_ref: str, action: str) -> bool:
        """检查 permit 范围是否覆盖动作"""
        raise NotImplementedError("当前阶段不实现验证逻辑")
```

## Permit 引用规则

### 引用传递
- Integration Gateway **只传递** permit 引用
- **不生成** 新的 permit
- **不修改** 引用的 permit

### 引用格式
```python
@dataclass
class PermitRef:
    """Permit 引用"""
    permit_id: str           # Permit ID
    governor_id: str         # 生成该 permit 的 Governor ID
    decision_ref: str        # 关联的 GateDecision 引用
    created_at: str          # 创建时间
    expires_at: str          # 过期时间
    scope: str               # 许可范围
```

## Permit 绕过检测

### 自动拒绝条件
- 如果 permit_ref 缺失 → 自动拒绝
- 如果 permit_ref 格式错误 → 自动拒绝
- 如果 permit 引用不存在的 Governor → 自动拒绝
- 如果 permit 已过期 → 自动拒绝（当前阶段仅定义）

### 违规后果
- 任何 permit 绕过尝试都应被记录
- 任何 permit 绕过尝试都应触发告警（当前阶段仅定义告警接口）

## 当前阶段限制
- **只定义**: permit 验证接口
- **不实现**: permit 验证逻辑
- **不连接**: 真实 Governor 进行验证
