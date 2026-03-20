# Service Layer - 职责文档

## 概述

Service 层是 System Execution 子面中的 **内部服务承接层**，负责定义业务逻辑服务的接口和结构边界。

## 核心职责 (DOES)

### 1. 内部服务承接 (Internal Service Acceptance)
- 接收来自 Orchestrator 的已路由请求
- 验证上下文结构的完整性
- 为未来业务逻辑实现预留接口

### 2. 只读访问 Frozen 主线 (Read-Only Frozen Access)
- 以只读方式访问 frozen governance 对象
- 不修改任何 frozen 主线数据
- 保持 frozen 主线的不可变性

### 3. 服务接口定义 (Service Interface Definition)
- 定义 Service 层的标准接口契约
- 规范上下文验证规则
- 明确只读依赖声明

## 明确边界 (DOES NOT)

| 行为 | 是否属于 Service | 理由 |
|------|----------------|------|
| 承接 orchestrator 请求 | ✅ 是 | 内部服务承接 |
| 验证上下文结构 | ✅ 是 | 接口契约要求 |
| 只读 frozen 对象 | ✅ 是 | 治理数据引用 |
| 实现业务逻辑 | ❌ 否 | 最小骨架阶段 |
| 执行外部调用 | ❌ 否 | Handler 层职责 |
| Runtime 控制 | ❌ 否 | Handler 层职责 |
| 修改 frozen 数据 | ❌ 否 | 违反只读约束 |

## 与 Handler 层的边界

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR Layer                       │
│  (内部路由决策 → service 或 handler)                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
           ┌───────────────┴───────────────┐
           ▼                               ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│      SERVICE Layer       │  │      HANDLER Layer       │
│  ┌────────────────────┐  │  │  ┌────────────────────┐ │
│  │ 接口定义           │  │  │  │ Runtime 控制       │ │
│  │ 上下文验证         │  │  │  │ 执行调度           │ │
│  │ 只读 Frozen 访问   │  │  │  │ 超时管理           │ │
│  │ (无业务逻辑实现)   │  │  │  │ 资源隔离           │ │
│  └────────────────────┘  │  │  └────────────────────┘ │
└──────────────────────────┘  └──────────────────────────┘
```

**关键区别**：
- **Service**: 接口定义 + 上下文验证 + 只读访问
- **Handler**: Runtime 控制 + 执行调度 + 资源管理

## 与 Orchestrator 层的关系

```
API Layer
    │
    ▼
Orchestrator (InternalRouter)
    │ route_request() → RouteTarget(layer="service", ...)
    │ prepare_context() → enriched_context
    ▼
Service (BaseService)
    │ validate_context() → 检查结构
    │ get_read_dependencies() → 声明只读依赖
    ▼
[业务逻辑实现预留 - 当前不实现]
```

## Frozen 主线使用方式

### 只读访问原则

```python
# ✅ 正确：只读访问
from skillforge.src.contracts import skill_spec

def read_frozen_spec(skill_id: str) -> Optional[Dict]:
    """只读方式读取 frozen skill spec"""
    return skill_spec.get_spec(skill_id)  # 假设提供只读接口

# ❌ 错误：修改 frozen 数据
def modify_frozen_spec(skill_id: str, changes: Dict):
    skill_spec.update_spec(skill_id, changes)  # 禁止！
```

### 只读依赖声明

```python
class BaseService(ServiceInterface):
    def get_read_dependencies(self) -> List[str]:
        return [
            "skillforge.src.contracts.skill_spec",
            "skillforge.src.contracts.intake_request",
            # 其他 frozen 主线模块
        ]
```

## 硬约束总结

1. **不实现真实业务逻辑**: 当前阶段仅定义接口，不实现具体业务
2. **不执行外部调用**: 外部集成由 Handler 层负责
3. **不进入 Runtime 控制**: 执行控制由 Handler 层负责
4. **只读 Frozen 主线**: 不修改任何 frozen governance 对象
5. **清晰的层边界**: Service ≠ Handler ≠ Orchestrator
