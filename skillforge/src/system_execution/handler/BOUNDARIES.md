# Handler Boundary & Connection Guide

## 概述

本文档说明 Handler 与 API / Service / Orchestrator 层的边界与连接方式。

## 导入路径

```python
# 从其他层导入 Handler
from skillforge.src.system_execution.handler import (
    HandlerInterface,
    InputAcceptance,
    CallForwarder,
)
```

## 接口契约

### HandlerInput (输入)

```python
from skillforge.src.system_execution.handler.handler_interface import HandlerInput

handler_input = HandlerInput(
    request_id="handler-req-123",
    source="api",  # "api" | "orchestrator" | "service"
    action="query",  # "query" | "status" | "forward" | "dispatch"
    payload={"key": "value"},
    evidence_ref="audit_pack:abc123"  # optional
)
```

### ForwardTarget (输出)

```python
from skillforge.src.system_execution.handler.handler_interface import ForwardTarget

target = ForwardTarget(
    layer="service",  # "service" | "orchestrator"
    module="query_service",
    method="execute"
)
```

## 使用示例

### 1. API 层 → Handler

```python
# skillforge/src/api/routes/query_routes.py
from skillforge.src.system_execution.handler import CallForwarder
from skillforge.src.system_execution.handler.handler_interface import HandlerInput

forwarder = CallForwarder(InputAcceptance())

@router.post("/query")
async def handle_query(request: QueryRequest):
    handler_input = HandlerInput(
        request_id=request.request_id,
        source="api",
        action="query",
        payload=request.params,
        evidence_ref=request.evidence_ref
    )

    # 检查输入承接
    accepted, reasons = forwarder.accept_input(handler_input)
    if not accepted:
        raise HTTPException(400, {"reasons": reasons})

    # 获取转发目标
    target = forwarder.forward_call(handler_input)

    # 准备上下文
    context = forwarder.prepare_forward_context(handler_input)

    # 转发到 service 层执行
    return await forward_to_service(target, context)
```

### 2. Orchestrator → Handler

```python
# skillforge/src/system_execution/orchestrator/internal_router.py
from skillforge.src.system_execution.handler import CallForwarder
from skillforge.src.system_execution.handler.handler_interface import HandlerInput

forwarder = CallForwarder(InputAcceptance())

def route_to_handler(context: RoutingContext):
    handler_input = HandlerInput(
        request_id=context.request_id,
        source="orchestrator",
        action="forward",
        payload={"context": context},
        evidence_ref=context.evidence_ref
    )

    accepted, _ = forwarder.accept_input(handler_input)
    if not accepted:
        return {"error": "input not accepted"}

    target = forwarder.forward_call(handler_input)
    return target
```

### 3. Service 层接收 Handler 上下文

```python
# skillforge/src/system_execution/service/query_service.py
from typing import Dict, Any

def execute_query(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Service 层接收由 Handler 准备的上下文。

    Context 包含:
    - request_id: 请求 ID
    - source: 请求来源
    - action: 动作类型
    - payload: 原始数据
    - evidence_ref: 证据引用
    - forward_target: 转发目标信息
    - forward_decision: 转发决策者
    """
    request_id = context.get("request_id")
    payload = context.get("payload")

    # Service 层执行业务逻辑
    return {"result": "queried", "request_id": request_id}
```

## 边界约束

| 约束 | 说明 |
|------|------|
| 无副作用 | Handler 不执行任何副作用（由 Service 负责） |
| 无 runtime 控制 | Runtime 控制由 Orchestrator 负责 |
| 无业务判断 | 业务规则由 Service/Gate 负责 |
| 只读 Frozen 对象 | 不修改 frozen 主线 |

## 职责对比表

| 行为 | API | Handler | Service | Orchestrator |
|------|-----|---------|---------|--------------|
| HTTP 协议解析 | ✅ | ❌ | ❌ | ❌ |
| 输入结构验证 | ❌ | ✅ | ❌ | ❌ |
| 调用转发决策 | ❌ | ✅ | ❌ | ❌ |
| 内部路由 | ❌ | ❌ | ❌ | ✅ |
| 业务逻辑执行 | ❌ | ❌ | ✅ | ❌ |
| 副作用触发 | ❌ | ❌ | ✅ | ❌ |
| 外部集成 | ❌ | ❌ | ✅ | ❌ |

## 导入自检

运行以下命令验证连接：

```bash
# 验证导入
python -c "
from skillforge.src.system_execution.handler import (
    HandlerInterface,
    InputAcceptance,
    CallForwarder,
)
print('✓ Handler imports OK')
"

# 验证接口
python -c "
from skillforge.src.system_execution.handler.handler_interface import (
    HandlerInput,
    ForwardTarget,
)
inp = HandlerInput(request_id='test', source='api', action='query', payload={})
print(f'✓ HandlerInput: {inp}')
"
```

## 典型调用链

```
User Request
    ↓
API Layer (parse HTTP)
    ↓
Handler Layer (accept_input + forward_call)
    ↓
    ├→ Service Layer (execute business logic)
    └→ Orchestrator Layer (route_request)
```

## 关键设计原则

1. **Handler 是透明的**: 它不保留状态，每次调用都是独立的
2. **Handler 不执行**: 它只返回转发目标，不实际调用
3. **Handler 不判断**: 它只做结构验证，不做业务决策
