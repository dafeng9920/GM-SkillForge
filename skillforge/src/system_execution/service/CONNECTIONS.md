# Service Layer - 连接关系说明

## 概述

本文档说明 Service 层与 Orchestrator / Handler 层的连接方式和职责边界。

## 层级连接关系

```
┌─────────────────────────────────────────────────────────────┐
│                        API Layer                            │
│  (FastAPI routes, HTTP validation)                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR Layer                       │
│  ┌────────────────┐  ┌──────────────────────────────────┐  │
│  │ InternalRouter │  │ AcceptanceBoundary               │  │
│  │ - route_request│  │ - validate()                     │  │
│  │ - prepare_ctx  │  │                                 │  │
│  └────────────────┘  └──────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
           ┌───────────────┴───────────────┐
           │ route_request() 决策          │
           ▼                               ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│      SERVICE Layer       │  │      HANDLER Layer       │
│  ┌────────────────────┐  │  │  ┌────────────────────┐ │
│  │ ServiceInterface   │  │  │  │ Runtime 控制器      │ │
│  │ - get_service_info │  │  │  │ - 执行调度         │ │
│  │ - validate_context │  │  │  │ - 超时管理         │ │
│  │ - get_read_deps    │  │  │  │ - 资源隔离         │ │
│  │ (无业务逻辑实现)   │  │  │  └────────────────────┘ │
│  └────────────────────┘  │  │                          │
└──────────────────────────┘  └──────────────────────────┘
```

## 与 Orchestrator 的连接

### Orchestrator → Service (单向)

```python
# Orchestrator 层准备上下文
from skillforge.src.system_execution.orchestrator import InternalRouter
from skillforge.src.system_execution.orchestrator.orchestrator_interface import RoutingContext

router = InternalRouter(AcceptanceBoundary())

context = RoutingContext(
    request_id="req-123",
    source="api",
    intent="skill_execution",
    evidence_ref="audit_pack:abc123"
)

# 路由决策
target = router.route_request(context)
# → RouteTarget(layer="service", module="skill_service", action="execute")

# 准备上下文
enriched = router.prepare_context(context)
# → {
#       "request_id": "req-123",
#       "source": "api",
#       "intent": "skill_execution",
#       "evidence_ref": "audit_pack:abc123",
#       "route_target": {"layer": "service", "module": "skill_service", "action": "execute"},
#       "routing_decision": "internal_router"
#    }
```

### Service 接收上下文

```python
# Service 层接收并验证
from skillforge.src.system_execution.service import BaseService

service = BaseService()

# 验证上下文结构
valid, reasons = service.validate_context(enriched)
if not valid:
    raise ValueError(f"Invalid context: {reasons}")

# 获取服务信息
info = service.get_service_info()
# → {
#       "service_name": "BaseService",
#       "service_type": "internal_service",
#       "accepts_context": True,
#       "reads_frozen_only": True,
#       "has_business_logic": False
#    }

# 声明只读依赖
deps = service.get_read_dependencies()
# → [] (最小骨架，暂无依赖)
```

## 与 Handler 的边界

### Service ≠ Handler

| 维度 | Service | Handler |
|------|---------|---------|
| **职责** | 服务接口定义 | Runtime 控制 |
| **输入** | Orchestrator 上下文 | Orchestrator 上下文 |
| **验证** | 上下文结构完整性 | 执行环境就绪性 |
| **访问** | 只读 Frozen 对象 | 读写 Runtime 状态 |
| **控制** | 无执行控制 | 超时/隔离/重试 |
| **外部调用** | 无 | 有（通过 adapters） |
| **业务逻辑** | 接口定义（最小骨架） | 执行调度 |

### 示例：同一个请求的不同处理

```python
# Service 层视角（最小骨架阶段）
from skillforge.src.system_execution.service import BaseService

class SkillService(BaseService):
    """仅定义接口，不实现业务逻辑"""

    def get_service_info(self):
        return {
            "service_name": "SkillService",
            "service_type": "skill_execution",
            "accepts_context": True,
            "reads_frozen_only": True,
            "has_business_logic": False,  # 最小骨架
        }

# Handler 层视角（如有实现）
class SkillExecutionHandler:
    """Runtime 控制与执行调度"""

    def execute_with_timeout(self, context: Dict, timeout: int):
        """执行超时控制"""
        # 1. 环境就绪检查
        # 2. 资源隔离
        # 3. 执行业务逻辑
        # 4. 超时处理
        pass
```

## 导入路径

### 从 Service 层导入

```python
# 导入 Service 接口
from skillforge.src.system_execution.service import (
    ServiceInterface,
    BaseService,
)

# 导入具体服务（未来扩展）
from skillforge.src.system_execution.service.skill_service import SkillService
```

### 从其他层导入 Service

```python
# Orchestrator 层引用 Service
from skillforge.src.system_execution.service.service_interface import ServiceInterface

# Handler 层引用 Service
from skillforge.src.system_execution.service.base_service import BaseService
```

## 路由映射（Orchestrator → Service）

| Intent | Layer | Module | Action |
|--------|-------|--------|--------|
| skill_execution | service | skill_service | execute |
| data_processing | service | data_service | process |
| pipeline_submit | service | pipeline_service | submit |
| pipeline_status | service | pipeline_service | status |

**注意**: 当前最小骨架阶段，这些服务仅定义接口，不实现业务逻辑。

## 上下文传递流程

```
1. API Layer
   ↓
2. Orchestrator.validate_acceptance() → 检查结构
   ↓
3. Orchestrator.route_request() → 决定路由到 service
   ↓
4. Orchestrator.prepare_context() → 准备上下文
   ↓
5. Service.validate_context() → 验证上下文完整性
   ↓
6. Service.get_read_dependencies() → 声明只读依赖
   ↓
7. [业务逻辑实现预留 - 当前最小骨架不实现]
```

## 硬约束

1. **单向数据流**: Orchestrator → Service，Service 不反向调用 Orchestrator
2. **结构验证**: Service 只验证上下文结构，不做业务判断
3. **只读依赖**: Service 只读访问 Frozen 主线，不修改
4. **无 Runtime 控制**: Service 不涉及执行调度、超时管理等 Runtime 逻辑
