# API Layer Interface Connection Guide

## 概述

本文档说明 API 层与 Orchestrator / Handler / Service 层的接口连接方式。

## 导入路径

```python
# 从其他层导入 API 层
from skillforge.src.system_execution.api import (
    ApiInterface,
    ApiRequest,
    ApiResponse,
    RequestContext,
    RequestAdapter,
    ResponseBuilder,
)
```

## 接口契约

### ApiRequest (输入)

```python
from skillforge.src.system_execution.api.api_interface import ApiRequest

request = ApiRequest(
    request_id="api-req-123",
    request_type="governance_query",
    payload={"query": "..."},
    evidence_ref="audit_pack:abc123"  # optional
)
```

### ApiResponse (输出)

```python
from skillforge.src.system_execution.api.api_interface import ApiResponse

response = ApiResponse(
    request_id="api-req-123",
    status="accepted",  # "pending" | "accepted" | "rejected"
    message="Request accepted and routed",
    routing_target={"layer": "handler", "module": "governance_handler", "action": "query"}
)
```

## 使用示例

### 1. API 层 → Orchestrator

```python
# skillforge/src/system_execution/api/api_handler.py
from skillforge.src.system_execution.api import RequestAdapter, ResponseBuilder
from skillforge.src.system_execution.orchestrator import InternalRouter
from skillforge.src.system_execution.api.api_interface import ApiRequest

adapter = RequestAdapter()
router = InternalRouter(AcceptanceBoundary())
builder = ResponseBuilder()

def handle_api_request(request: ApiRequest) -> ApiResponse:
    # 1. 验证请求结构
    accepted, reasons = adapter.validate_request_structure(request)
    if not accepted:
        return builder.build_rejected(request.request_id, reasons)

    # 2. 转换为路由上下文
    context = adapter.adapt(request)

    # 3. 调用 orchestrator 路由
    target = router.route_request(context)
    enriched = router.prepare_context(context)

    # 4. 返回响应
    return builder.build_accepted(request.request_id, enriched)
```

### 2. Orchestrator 接收 API 上下文

```python
# skillforge/src/system_execution/orchestrator/internal_router.py
from skillforge.src.system_execution.orchestrator.orchestrator_interface import RoutingContext

def route_request(self, context: RoutingContext) -> RouteTarget:
    # context.source == "api" 表示来自 API 层
    if context.source == "api":
        # 路由到相应的 handler 或 service
        pass
    return self._ROUTE_MAP.get(context.intent, self._FALLBACK)
```

### 3. Handler 层处理

```python
# skillforge/src/system_execution/handler/governance_handler.py
def handle_governance_query(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler 层接收由 Orchestrator 准备的上下文。

    Context 包含:
    - request_id: 请求 ID
    - source: "api" | "handler" | "internal"
    - intent: 意图类型
    - evidence_ref: 证据引用
    - route_target: 路由目标信息
    """
    request_id = context.get("request_id")
    # Handler 层执行调用转发
    return {"status": "processed", "request_id": request_id}
```

## 请求类型映射

API 层支持的请求类型（占位符）：

| request_type | 路由目标 | 说明 |
|-------------|---------|------|
| governance_query | handler | 治理查询 |
| governance_status | handler | 治理状态 |
| skill_execution | service | 技能执行 |
| data_processing | service | 数据处理 |
| pipeline_submit | service | 流程提交 |
| pipeline_status | service | 流程状态 |

## 边界约束

| 约束 | 说明 |
|------|------|
| 无真实 HTTP | 所有 HTTP/Webhook 实现不在本模块 |
| 无外部调用 | 外部集成由未来模块负责 |
| 无 Runtime | 执行控制由 handler 层负责 |
| 只读 Frozen 对象 | 不修改 frozen 主线 |

## 导入自检

运行以下命令验证连接：

```bash
# 验证 API 层导入
python -c "
from skillforge.src.system_execution.api import (
    ApiInterface,
    ApiRequest,
    ApiResponse,
    RequestAdapter,
    ResponseBuilder,
)
print('✓ API Layer imports OK')
"

# 验证接口创建
python -c "
from skillforge.src.system_execution.api.api_interface import ApiRequest
req = ApiRequest(request_id='test', request_type='governance_query', payload={})
print(f'✓ ApiRequest: {req}')
"
```

## 与 Orchestrator 的集成

API 层通过 `RequestContext` 与 Orchestrator 层集成：

```python
# API 层创建
request_context = RequestContext(
    request_id=request.request_id,
    source="api",
    intent=request.request_type,
    evidence_ref=request.evidence_ref,
)

# Orchestrator 层接收
routing_context: RoutingContext = request_context  # 兼容
```
