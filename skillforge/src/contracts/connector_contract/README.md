# Connector Contract 子面 - 职责文档

## 概述

Connector Contract 是外部执行与集成准备模块的 **连接契约定义层**，负责定义与外部系统的连接接口规范和前置条件契约。

## 核心职责 (DOES)

### 1. 连接契约定义 (Connection Contract Definition)
- 定义外部系统的连接接口规范
- 声明连接所需的前置条件
- 定义连接失败的错误分类

### 2. 前置条件声明 (Prerequisite Declaration)
- 声明 permit 引用位置（不生成 permit）
- 声明 frozen 主线对象的只读依赖
- 声明 credentials 引用方式（不存储凭据）

### 3. 接口适配规范 (Interface Adaptation Specification)
- 定义 system_execution 与外部系统的适配边界
- 定义请求数据结构规范
- 定义响应数据结构规范

## 明确边界 (DOES NOT)

| 行为 | 是否属于 Connector Contract | 理由 |
|------|---------------------------|------|
| 定义外部连接接口 | ✅ 是 | 连接契约定义 |
| 声明 permit 依赖 | ✅ 是 | 前置条件声明 |
| 只读引用 frozen 对象 | ✅ 是 | 主线承接 |
| 实现真实外部连接 | ❌ 否 | Integration Gateway 职责 |
| 存储 credentials | ❌ 否 | Secrets Boundary 职责 |
| 生成 permit | ❌ 否 | Governor 裁决范围 |
| 改写 Evidence/AuditPack | ❌ 否 | 只读引用规则 |
| Runtime 执行控制 | ❌ 否 | Handler 层职责 |
| 实现业务逻辑 | ❌ 否 | Service 层职责 |

## 与其他子面的边界

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frozen Governance Mainline                   │
│  (GateDecision, Evidence, AuditPack, normalized_skill_spec...)  │
└────────────────────────────┬────────────────────────────────────┘
                             │ 只读引用
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Connector Contract Layer                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 1. 定义外部连接接口契约                                  │  │
│  │ 2. 声明 permit 前置条件（不生成）                        │  │
│  │ 3. 声明 frozen 对象只读依赖                              │  │
│  │ 4. 定义数据结构适配规范                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────────────┐
│ Integration      │ │ Secrets      │ │ External Action      │
│ Gateway          │ │ Boundary     │ │ Policy               │
│ (真实连接实现)   │ │ (凭据管理)   │ │ (动作分类规则)       │
└──────────────────┘ └──────────────┘ └──────────────────────┘
```

## 与 system_execution 的关系

```
system_execution (Service/Handler Layer)
    │
    │ 需要外部连接时
    ▼
Connector Contract (接口契约查询)
    │
    ├─→ 查询：连接需要什么 permit？
    ├─→ 查询：连接需要什么 frozen 对象？
    ├─→ 查询：请求数据结构是什么？
    └─→ 查询：响应数据结构是什么？
    │
    ▼ (返回接口规范，不执行连接)
system_execution (使用规范准备上下文)
    │
    ▼ (有 permit 后)
Integration Gateway (执行真实连接)
```

## Permit 引用规则

### 1. Permit 只声明不生成
```python
# ✅ 正确：声明需要的 permit 类型
class ExternalConnectionContract:
    required_permits: List[str] = [
        "external.git.push",
        "external.webhook.notify",
    ]

# ❌ 错误：生成 permit
def create_permit():
    return {"permit": "allowed"}  # 禁止！
```

### 2. Permit 前置检查规则
- 连接前必须检查 permit 存在性
- 无 permit 时不得进入 Integration Gateway
- permit 过期时连接失败（不自动续期）

## Frozen 主线引用规则

### 1. 只读原则
```python
# ✅ 正确：只读引用
from skillforge.src.contracts import normalized_skill_spec

def get_connection_target(spec_id: str):
    """只读方式读取 spec"""
    return normalized_skill_spec.get_spec(spec_id)

# ❌ 错误：修改 frozen 对象
def update_spec(spec_id: str, changes: Dict):
    normalized_skill_spec.update(spec_id, changes)  # 禁止！
```

### 2. 引用声明
- 所有 frozen 依赖必须在 contract 中显式声明
- 引用路径必须是公开接口
- 不得访问内部私有属性

## Evidence / AuditPack 引用规则

### 1. 只读引用
- 可以引用 EvidenceRef 指向的证据
- 可以读取 AuditPack 内容用于通知
- 不得修改、覆盖、重新生成

### 2. 搬运规则
```python
# ✅ 正确：搬运证据到外部
def upload_evidence_to_external(evidence_ref: EvidenceRef):
    """读取证据并上传到外部系统"""
    evidence = evidence_ref.load()  # 只读
    external_system.upload(evidence)  # 搬运

# ❌ 错误：修改证据
def modify_evidence(evidence_ref: EvidenceRef, changes: Dict):
    evidence = evidence_ref.load()
    evidence.update(changes)  # 禁止！
```

## 后续 Runtime 排除边界

### 明确不属于 Connector Contract 的 Runtime 行为：
1. 不建立持久连接
2. 不管理连接池
3. 不处理连接超时
4. 不实现重试逻辑
5. 不处理网络异常
6. 不管理会话状态

以上行为属于 Integration Gateway 和 Handler 层。

## 接口规范示例

### 外部连接接口契约
```python
@dataclass(frozen=True)
class ExternalConnectionContract:
    """外部连接接口契约定义"""

    # 连接标识
    connection_id: str
    connection_type: str  # "git" | "webhook" | "api" | "registry"

    # 前置条件
    required_permits: List[str]
    frozen_dependencies: List[str]

    # 接口规范
    request_schema: str
    response_schema: str

    # 错误分类
    error_classes: List[str]
```

## 硬约束总结

1. **不实现真实外部连接**: 只定义接口，不实现连接
2. **不生成 Permit**: 只声明依赖，不生成裁决
3. **不存储凭据**: 只定义引用方式，不存储敏感信息
4. **只读 Frozen 主线**: 不修改任何 frozen 对象
5. **只读 Evidence/AuditPack**: 不改写证据
6. **不进入 Runtime**: 执行控制由 Handler 层负责
7. **清晰的子面边界**: Connector ≠ Integration ≠ Secrets ≠ Policy
