# Connector Contract Permit 规则

## 核心原则
**只声明 permit 需求，不生成 permit。**

## Permit 声明规则

### 声明方式
Connector Contract 通过 `PermitRequirementDeclaration` 声明 permit 需求：

```python
@dataclass(frozen=True)
class PermitRequirementDeclaration:
    permit_type: str           # Permit 类型
    required_for: str          # 用途说明
    validation_rule: Optional[str] = None  # 验证规则（可选）
```

### 声明位置
- 在 `ExternalConnectionContract` 的 `required_permits` 字段中声明
- 每个 permit 需求是独立的 `PermitRequirementDeclaration` 实例

### 声明内容
- **permit_type**: 引用 Governor 定义的 permit 类型
- **required_for**: 说明 permit 的使用场景
- **validation_rule**: 可选的验证规则描述（不实现）

## 禁止事项

### 禁止生成 Permit
- 不生成任何 permit 实例
- 不创建 permit 对象
- 不分配 permit ID
- 不设置 permit 过期时间

### 禁止验证 Permit
- 不验证 permit 有效性
- 不检查 permit 过期时间
- 不检查 permit 范围
- 不拒绝 permit 请求

### 禁止存储 Permit
- 不存储 permit 实例
- 不缓存 permit 内容
- 不维护 permit 状态

## Permit 类型引用

### 引用来源
Permit 类型由 Governor 定义，Connector Contract 只引用：

```python
# 常见 permit 类型（由 Governor 定义）
EXTERNAL_ACTION_PERMIT = "external.action.execute"
PUBLISH_PERMIT = "external.publish"
SYNC_PERMIT = "external.sync"
NOTIFY_PERMIT = "external.notify"
```

### 引用方式
- 直接使用字符串引用 permit 类型
- 不在 Connector Contract 中定义 permit 类型常量
- 保持与 Governor 定义的一致性

## Permit 与连接类型的关系

### 常见映射

| 连接类型 | 所需 Permit |
|---------|-----------|
| git | external.action.execute |
| webhook | external.action.execute |
| api | external.action.execute |
| storage | external.action.execute |
| notification | external.notify |
| publish | external.publish |
| sync | external.sync |

### 声明示例
```python
ExternalConnectionContract(
    connection_type="git",
    required_permits=["external.action.execute"],
    ...
)
```

## Permit 引用传递

### 声明范围
- Connector Contract 声明 permit 需求
- Integration Gateway 接收 permit 引用
- 具体 Connector 验证 permit 有效性

### 流程
```
Connector Contract (声明需求)
    ↓
Integration Gateway (接收引用)
    ↓
External Connector (验证有效性)
```

## 与 Integration Gateway 的区别

| 层面 | 职责 |
|-----|-----|
| Connector Contract | 声明 permit 需求 |
| Integration Gateway | 传递 permit 引用 |
| External Connector | 验证 permit 有效性 |
| Governor | 生成 permit |

## 当前阶段限制
- **只声明**: permit 需求
- **不生成**: permit 实例
- **不验证**: permit 有效性
- **不连接**: 真实 Governor
