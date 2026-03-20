# Orchestrator (System Execution Layer)

## Purpose

Orchestrator 是 system execution 层的 **内部路由与承接** 模块。

## 核心职责 (DOES)

1. **内部路由 (Internal Routing)**
   - 根据 request_type 将请求路由到 service/handler 层
   - 维护路由映射表 (intent → target)
   - 准备下游层需要的上下文

2. **承接检查 (Acceptance)**
   - 检查请求的结构完整性 (request_id, source)
   - 拒绝格式错误或来源未知的请求
   - 不做业务规则判断

3. **上下文准备 (Context Preparation)**
   - 为 service/handler 层准备 enriched context
   - 添加路由元数据
   - 保留原始引用 (evidence_ref)

## 明确边界 (DOES NOT)

| 行为 | 是否属于 Orchestrator | 理由 |
|------|---------------------|------|
| 路由请求到 service | ✅ 是 | 内部路由 |
| 检查 request_id 非空 | ✅ 是 | 结构验证 |
| 检查来源是否已知 | ✅ 是 | 承接检查 |
| 许可证发放 | ❌ 否 | Gate 层职责 |
| 治理决策 | ❌ 否 | Gate/Contracts 层职责 |
| 外部集成 | ❌ 否 | Service 层职责 |
| Runtime 控制 | ❌ 否 | Handler 层职责 |

## 与其他层的边界

```
┌─────────────────────────────────────────────────────────────┐
│                        API Layer                            │
│  (FastAPI routes, request validation)                       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR Layer                       │
│  ┌────────────────┐  ┌──────────────────────────────────┐  │
│  │ InternalRouter │  │ AcceptanceBoundary               │  │
│  │                │  │ (structural validation only)     │  │
│  └────────────────┘  └──────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
           ┌───────────────┴───────────────┐
           ▼                               ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│      SERVICE Layer       │  │      HANDLER Layer       │
│  (Business logic)        │  │  (Request/dispatch)      │
└──────────────────────────┘  └──────────────────────────┘
```

## 模块说明

- `orchestrator_interface.py`: 定义 OrchestratorInterface 接口契约
- `internal_router.py`: 内部路由实现 (路由表 + 上下文准备)
- `acceptance_boundary.py`: 承接检查 (结构验证，非治理判断)

## 硬约束

1. **不得成为治理判断层**: 所有 permit/gate 决策由 gate 层负责
2. **不得进入 runtime 控制**: runtime execution 由 handler 层负责
3. **不得触发外部集成**: 外部调用由 service 层负责
4. **不得修改 frozen 主线**: 只读取，不修改 governance 对象
