# Retry / Compensation Boundary Permit 使用规则

## 核心原则
**重试与补偿动作必须持 permit 行动，不能自行裁决。**

## Permit 类型

### 1. Retry Permit
**用途**: 重试失败的执行

**必需条件**:
- 必须持有有效的 retry_permit_ref
- permit 必须由 Governor 生成
- permit 必须针对失败执行 ID
- permit 必须指定重试类型（立即/延迟）

**禁止事项**:
- 不得在无 permit 的情况下自动重试
- 不得自行判定重试可忽略 permit
- 不得扩大重试范围

### 2. Compensation Permit
**用途**: 执行补偿动作

**必需条件**:
- 必须持有有效的 compensation_permit_ref
- permit 必须由 Governor 生成
- permit 必须针对失败执行 ID
- permit 必须指定补偿类型（回滚/重做/人工）

**禁止事项**:
- 不得在无 permit 的情况下自动补偿
- 不得自行判定补偿可忽略 permit
- 不得修改补偿范围

### 3. Override Permit
**用途**: 覆盖原有的 GateDecision（仅限 Governor 裁决后）

**必需条件**:
- 必须持有有效的 override_permit_ref
- permit 必须由 Governor 生成
- permit 必须明确引用被覆盖的 GateDecision
- permit 必须说明覆盖理由

**禁止事项**:
- 不得在无 permit 的情况下覆盖决策
- 不得自行判定覆盖可忽略 permit
- 不得递归覆盖（覆盖后的决策不能再覆盖）

## Permit 与建议的关系

### 建议不等于 Permit
- Retry / Compensation Boundary 提供的是**建议**
- 建议采纳后，由 Governor 生成 **Permit**
- 没有 Permit，建议不能自动执行

### 建议包含 Permit 类型说明
```python
@dataclass
class RetryAdvice:
    """重试建议"""
    retry_type: str           # 重试类型
    retry_interval: int       # 重试间隔（秒）
    max_retries: int          # 最大重试次数
    required_permit_type: str # 需要的 permit 类型
```

### Permit 生成流程
1. Retry / Compensation Boundary 生成建议
2. Governor 接收建议
3. Governor 决定是否采纳
4. Governor 生成 permit（如采纳）
5. 持有 permit 的执行者执行重试/补偿

## Permit 验证流程

### 验证步骤
1. **接收**: 接收失败事件
2. **分析**: 分析失败类型与原因
3. **建议**: 生成重试/补偿建议
4. **等待**: 等待 Governor 决策
5. **验证**: 验证 permit 有效性（当前阶段仅定义验证接口）
6. **传递**: 将 permit 引用传递给执行者

### 验证规则（仅定义，不实现）
```python
# 仅定义接口，不实现验证逻辑
class PermitValidator:
    def validate_retry_permit(self, permit_ref: str) -> ValidationResult:
        """验证重试 permit 有效性"""
        raise NotImplementedError("当前阶段不实现验证逻辑")

    def validate_compensation_permit(self, permit_ref: str) -> ValidationResult:
        """验证补偿 permit 有效性"""
        raise NotImplementedError("当前阶段不实现验证逻辑")

    def validate_override_permit(self, permit_ref: str) -> ValidationResult:
        """验证覆盖 permit 有效性"""
        raise NotImplementedError("当前阶段不实现验证逻辑")
```

## Permit 引用规则

### 引用传递
- Retry / Compensation Boundary **只说明** 需要的 permit 类型
- **不生成** 新的 permit
- **不修改** 引用的 permit

### 引用格式
```python
@dataclass
class PermitRequirement:
    """Permit 需求说明"""
    action_type: str          # 动作类型 (retry/compensation/override)
    required_permit_type: str # 需要的 permit 类型
    source: str               # permit 来源 (Governor)
    scope: str                # permit 范围说明
```

## Permit 绕过检测

### 自动拒绝条件
- 如果建议要求 permit 但执行时无 permit → 自动拒绝
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
- **只说明**: 建议需要的 permit 类型
