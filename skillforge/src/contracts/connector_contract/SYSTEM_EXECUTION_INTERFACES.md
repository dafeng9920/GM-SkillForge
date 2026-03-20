# Connector Contract - System Execution 接口关系

## 概述

本文档定义 Connector Contract 子面与 system_execution 模块的接口承接关系。

## 接口关系架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    system_execution 模块                        │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ API Layer (request_adapter, response_builder)             │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ Orchestrator Layer (internal_router, prepare_context)     │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                  │
│  ┌───────────────────────┬─────────────────────────────────┐ │
│  │   Service Layer       │     Handler Layer                │ │
│  │ (service_interface)   │ (handler_interface)              │ │
│  └───────────────────────┴─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ 查询接口契约
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Connector Contract Layer                        │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ 1. 返回连接接口契约                                        │ │
│  │ 2. 声明 permit 依赖                                        │ │
│  │ 3. 声明 frozen 依赖                                        │ │
│  │ 4. 定义数据结构规范                                        │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ (有 permit 后)
┌─────────────────────────────────────────────────────────────────┐
│                 Integration Gateway (执行连接)                  │
└─────────────────────────────────────────────────────────────────┘
```

## 接口查询流程

### 1. system_execution 查询连接契约
```python
# system_execution 中需要外部连接时
from skillforge.src.contracts.connector_contract import get_connection_contract

def prepare_external_connection(connection_type: str, target: str):
    """准备外部连接"""
    # 1. 查询连接契约
    contract = get_connection_contract(connection_type, target)

    # 2. 检查 permit 前置条件
    if not verify_permits(contract.required_permits):
        raise PermitMissingError(contract.required_permits)

    # 3. 准备 frozen 依赖
    frozen_context = load_frozen_dependencies(contract.frozen_dependencies)

    # 4. 准备请求数据
    request_data = prepare_request(contract.request_schema, frozen_context)

    return request_data
```

### 2. Connector Contract 返回接口规范
```python
# connector_contract 返回契约
@dataclass(frozen=True)
class ExternalConnectionContract:
    """外部连接接口契约"""

    # 连接标识
    connection_type: str  # "git" | "webhook" | "api" | "registry"
    target: str

    # 前置条件（不生成，只声明）
    required_permits: List[str]
    frozen_dependencies: List[str]

    # 数据结构规范
    request_schema: Dict[str, Any]
    response_schema: Dict[str, Any]

    # 错误分类
    error_classes: Dict[str, str]
```

## 接口调用约束

### 1. 单向调用规则
```
system_execution → Connector Contract: ✅ 允许
Connector Contract → system_execution: ❌ 禁止
```

### 2. 无状态规则
- Connector Contract 不维护调用状态
- 每次查询返回独立的契约对象
- 不缓存 system_execution 的上下文

### 3. 只读规则
- Connector Contract 不修改传入参数
- 返回的契约对象不可变 (frozen=True)

## Service 层承接关系

### Service Interface 扩展
```python
# system_execution Service 层可以扩展以支持外部连接
class ServiceInterface(ABC):
    @abstractmethod
    def get_external_connection_contract(
        self,
        connection_type: str,
        target: str
    ) -> Optional[ExternalConnectionContract]:
        """
        获取外部连接契约

        Args:
            connection_type: 连接类型
            target: 连接目标

        Returns:
            ExternalConnectionContract 或 None
        """
        pass
```

### Service 使用示例
```python
class ExternalIntegrationService(ServiceInterface):
    def get_external_connection_contract(
        self,
        connection_type: str,
        target: str
    ) -> Optional[ExternalConnectionContract]:
        from skillforge.src.contracts.connector_contract import (
            get_connection_contract
        )
        return get_connection_contract(connection_type, target)
```

## Handler 层承接关系

### Handler 在 permit 验证后调用 Integration Gateway
```python
# Handler 层流程
class ExternalIntegrationHandler(HandlerInterface):
    def handle_external_action(self, action: ExternalAction):
        # 1. 查询连接契约
        contract = get_connection_contract(action.connection_type, action.target)

        # 2. 验证 permit (在 Orchestrator 层已完成)
        # permit 验证不在此层重复

        # 3. 调用 Integration Gateway 执行连接
        gateway = IntegrationGateway(contract)
        result = gateway.execute(action)

        return result
```

## Orchestrator 层承接关系

### Orchestrator 路由到外部连接
```python
# Orchestrator 层路由决策
class InternalRouter(OrchestratorInterface):
    def route_request(self, context: RoutingContext) -> RouteTarget:
        if context.intent == "external_integration":
            # 路由到 Handler 层的外部集成处理器
            return RouteTarget(
                layer="handler",
                module="external_integration",
                action="handle_external_action"
            )
        # 其他路由...
```

## 接口规范示例（通用、协议无关）

### 通用连接契约结构

**重要**: Connector Contract 只定义通用、协议无关的接口结构。具体协议（Git、Webhook 等）的专用字段由 Integration Gateway 处理。

```python
# 通用连接契约示例（协议无关）
GENERIC_CONNECTION_CONTRACT = ExternalConnectionContract(
    connection_type="generic",
    target="external_system",

    required_permits=[
        "external.action.execute",
    ],

    frozen_dependencies=[
        FrozenDependencyDeclaration(
            module="skillforge.src.contracts.normalized_skill_spec",
            object_type="NormalizedSkillSpec",
            access_pattern="read",
            purpose="获取技能规范用于外部操作"
        ),
    ],

    # 通用请求结构（协议无关）
    request_schema={
        "type": "object",
        "properties": {
            "target_ref": {
                "type": "string",
                "description": "目标引用标识（协议无关）"
            },
            "action_type": {
                "type": "string",
                "description": "动作类型（协议无关）"
            },
            "payload": {
                "type": "object",
                "description": "载荷数据（具体协议内容由 Integration Gateway 处理）"
            },
            "metadata": {
                "type": "object",
                "description": "元数据（用于追踪和审计）"
            },
        },
    },

    # 通用响应结构（协议无关）
    response_schema={
        "type": "object",
        "properties": {
            "success": {
                "type": "boolean",
                "description": "操作是否成功"
            },
            "result_ref": {
                "type": "string",
                "description": "结果引用标识（协议无关）"
            },
            "error_code": {
                "type": "string",
                "description": "错误代码（如有）"
            },
        },
    },

    error_classes={
        "PERMIT_MISSING": "缺少操作许可",
        "TARGET_UNREACHABLE": "目标不可达",
        "PAYLOAD_INVALID": "载荷无效",
    },
)
```

### 协议专用字段处理

**Git 专用字段** (repository_url, branch, commit_message) 由 Integration Gateway 处理：
- Connector Contract 不定义这些字段
- Integration Gateway 在执行时将 payload 映射到 Git 专用字段

**Webhook 专用字段** (endpoint_url, event_type) 由 Integration Gateway 处理：
- Connector Contract 不定义这些字段
- Integration Gateway 在执行时将 payload 映射到 Webhook 专用字段

**原因**: Connector Contract 应该保持协议无关，便于扩展新协议而不修改契约定义。

## 边界规则

### Connector Contract 不做的：
1. 不执行连接
2. 不管理连接状态
3. 不处理网络异常
4. 不实现重试逻辑
5. 不生成 permit
6. 不存储凭据

### 上述行为归属：
- 执行连接 → Integration Gateway
- 管理连接状态 → Handler 层
- 处理网络异常 → Handler 层
- 重试逻辑 → Retry Boundary (E5)
- 生成 permit → Governor
- 存储凭据 → Secrets Boundary (E3)
