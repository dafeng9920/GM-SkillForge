# API Layer (System Execution Layer)

## Purpose

API 层是 system execution 层的 **最小接口层承接** 模块。

## 核心职责 (DOES)

1. **接口层承接 (Interface Acceptance)**
   - 接收外部风格的请求结构（占位符，非真实 HTTP）
   - 检查请求的结构完整性
   - 拒绝格式错误的请求

2. **请求适配 (Request Adaptation)**
   - 将 API 请求转换为 orchestrator 路由上下文
   - 保留原始引用 (evidence_ref)
   - 添加来源标记 (source="api")

3. **响应构造 (Response Building)**
   - 从路由结果构造响应结构
   - 提供接受/拒绝/待处理状态
   - 不实现真实 HTTP 协议

## 明确边界 (DOES NOT)

| 行为 | 是否属于 API Layer | 理由 |
|------|-------------------|------|
| 检查 request_id 非空 | ✅ 是 | 结构验证 |
| 转换为 RoutingContext | ✅ 是 | 请求适配 |
| 构造 ApiResponse | ✅ 是 | 响应准备 |
| 真实 HTTP 协议处理 | ❌ 否 | 本模块不实现 |
| 真实对外 API 暴露 | ❌ 否 | 本模块不实现 |
| Webhook/Queue 接入 | ❌ 否 | 外部集成，禁止 |
| 数据库操作 | ❌ 否 | 外部集成，禁止 |
| Slack/Email/Repo 操作 | ❌ 否 | 外部集成，禁止 |

## 与其他层的边界

```
┌─────────────────────────────────────────────────────────────┐
│                    External (Placeholder)                   │
│  (Future: HTTP/Webhook - NOT implemented in this module)    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                        API Layer                            │
│  ┌────────────────┐  ┌──────────────────────────────────┐  │
│  │ RequestAdapter │  │ ResponseBuilder                  │  │
│  │                │  │ (structure only, no HTTP)        │  │
│  └────────────────┘  └──────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   ORCHESTRATOR Layer                        │
│  (Internal routing and context preparation)                 │
└─────────────────────────────────────────────────────────────┘
```

## 模块说明

- `api_interface.py`: 定义 API 层接口契约
- `request_adapter.py`: 请求适配实现 (API 请求 → RoutingContext)
- `response_builder.py`: 响应构造实现 (路由结果 → API 响应)

## 硬约束

1. **不得暴露真实外部协议**: 所有 HTTP/Webhook 等实现不在本模块
2. **不得进入外部集成**: 无真实数据库、队列、外部 API 调用
3. **不得进入 Runtime**: 执行逻辑由 handler 层负责
4. **不得修改 frozen 主线**: 只读取，不修改 governance 对象
