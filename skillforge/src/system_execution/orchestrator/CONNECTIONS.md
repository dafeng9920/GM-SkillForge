# Orchestrator Interface Connection Guide

## 概述

本文档说明 Orchestrator 与 API / Service / Handler 层的接口连接方式。

## 导入路径

```python
# 从其他层导入 Orchestrator
from skillforge.src.system_execution.orchestrator import (
    InternalRouter,
    AcceptanceBoundary,
    OrchestratorInterface,
)
```

## 接口契约

### RoutingContext (输入)

```python
from skillforge.src.system_execution.orchestrator.orchestrator_interface import RoutingContext

context = RoutingContext(
    request_id="req-123",
    source="api",  # "api" | "handler" | "internal"
    intent="skill_execution",  # optional
    evidence_ref="audit_pack:abc123"  # optional
)
```

### RouteTarget (输出)

```python
from skillforge.src.system_execution.orchestrator.orchestrator_interface import RouteTarget

target = RouteTarget(
    layer="service",  # "service" | "handler" | "external"
    module="skill_service",
    action="execute"
)
```

## 使用示例

### 1. API 层 → Orchestrator

```python
# skillforge/src/api/routes/skill_routes.py
from skillforge.src.system_execution.orchestrator import InternalRouter
from skillforge.src.system_execution.orchestrator.orchestrator_interface import RoutingContext

router = InternalRouter(AcceptanceBoundary())

@router.post("/skills/execute")
async def execute_skill(request: SkillRequest):
    context = RoutingContext(
        request_id=request.request_id,
        source="api",
        intent="skill_execution",
        evidence_ref=request.evidence_ref
    )

    # 检查承接
    accepted, reasons = router.validate_acceptance(context)
    if not accepted:
        raise HTTPException(400, {"reasons": reasons})

    # 获取路由目标
    target = router.route_request(context)

    # 准备上下文
    enriched = router.prepare_context(context)

    # 转发到 service 层
    return await forward_to_service(target, enriched)
```

### 2. Handler 层 → Orchestrator

```python
# skillforge/src/system_execution/handler/governance_handler.py
from skillforge.src.system_execution.orchestrator import InternalRouter
from skillforge.src.system_execution.orchestrator.orchestrator_interface import RoutingContext

router = InternalRouter(AcceptanceBoundary())

def handle_governance_query(request: GovernanceQuery):
    context = RoutingContext(
        request_id=request.id,
        source="handler",
        intent="governance_query"
    )

    accepted, _ = router.validate_acceptance(context)
    if not accepted:
        return {"error": "request not accepted"}

    enriched = router.prepare_context(context)
    return query_governance_state(enriched)
```

### 3. Service 层接收 Orchestrator 上下文

```python
# skillforge/src/system_execution/service/skill_service.py
from typing import Dict, Any

def execute_skill(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Service 层接收由 Orchestrator 准备的上下文。

    Context 包含:
    - request_id: 请求 ID
    - source: 请求来源
    - intent: 意图类型
    - evidence_ref: 证据引用
    - route_target: 路由目标信息
    - routing_decision: 路由决策者
    """
    request_id = context.get("request_id")
    evidence_ref = context.get("evidence_ref")

    # Service 层执行业务逻辑
    return {"result": "processed", "request_id": request_id}
```

## 路由映射表

Orchestrator 维护的内部路由映射：

| Intent | Layer | Module | Action |
|--------|-------|--------|--------|
| governance_query | handler | governance_handler | query |
| governance_status | handler | governance_handler | status |
| skill_execution | service | skill_service | execute |
| data_processing | service | data_service | process |
| pipeline_submit | service | pipeline_service | submit |
| pipeline_status | service | pipeline_service | status |

## 承接检查规则

AcceptanceBoundary 检查：

1. `request_id` 必须非空
2. `source` 必须是 `api` / `handler` / `internal` 之一
3. `evidence_ref` (如果提供) 必须是字符串

**注意**: 这是结构检查，不是治理许可检查。

## 边界约束

| 约束 | 说明 |
|------|------|
| 无治理判断 | Gate 决策由 gate 层负责 |
| 无外部调用 | 外部集成由 service 层负责 |
| 无 Runtime 控制 | 执行控制由 handler 层负责 |
| 只读 Frozen 对象 | 不修改 frozen 主线 |

## 导入自检

运行以下命令验证连接：

```bash
# 验证导入
python -c "
from skillforge.src.system_execution.orchestrator import (
    InternalRouter,
    AcceptanceBoundary,
    OrchestratorInterface,
)
print('✓ Orchestrator imports OK')
"

# 验证接口
python -c "
from skillforge.src.system_execution.orchestrator.orchestrator_interface import (
    RoutingContext,
    RouteTarget,
    OrchestratorInterface,
)
ctx = RoutingContext(request_id='test', source='api')
print(f'✓ RoutingContext: {ctx}')
"
```
