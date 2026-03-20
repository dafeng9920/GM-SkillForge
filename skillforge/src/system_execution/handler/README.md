# Handler (System Execution Layer)

## Purpose

Handler 是 system execution 层的 **输入承接与调用转发** 模块。

## 核心职责 (DOES)

1. **输入承接 (Input Acceptance)**
   - 接收来自 API/Orchestrator/Service 的结构化输入
   - 检查输入的结构完整性 (request_id, source, action, payload)
   - 拒绝格式错误的输入
   - 不做业务规则判断

2. **调用转发 (Call Forwarding)**
   - 根据输入 action 确定转发目标
   - 维护转发映射表 (action → target)
   - 准备下游层需要的上下文
   - 返回转发信息，不执行实际调用

3. **上下文准备 (Context Preparation)**
   - 为 service/orchestrator 层准备 enriched context
   - 添加转发元数据
   - 保留原始引用 (evidence_ref)

## 明确边界 (DOES NOT)

| 行为 | 是否属于 Handler | 理由 |
|------|-----------------|------|
| 检查 request_id 非空 | ✅ 是 | 结构验证 |
| 检查 action 是否已知 | ✅ 是 | 结构验证 |
| 确定转发目标 | ✅ 是 | 调用转发 |
| 触发副作用 | ❌ 否 | Service 层职责 |
| Runtime 分支控制 | ❌ 否 | Orchestrator 层职责 |
| 业务规则判断 | ❌ 否 | Service/Gate 层职责 |
| 外部集成 | ❌ 否 | Service 层职责 |

## 与其他层的边界

```
┌─────────────────────────────────────────────────────────────┐
│                        API Layer                            │
│  (FastAPI routes, HTTP requests)                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      HANDLER Layer                          │
│  ┌────────────────┐  ┌──────────────────────────────────┐  │
│  │ InputAcceptance│  │ CallForwarder                    │  │
│  │ (struct check) │  │ (forward info, no actual call)   │  │
│  └────────────────┘  └──────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
           ┌───────────────┴───────────────┐
           ▼                               ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│      SERVICE Layer       │  │   ORCHESTRATOR Layer     │
│  (Business logic)        │  │  (Internal routing)      │
└──────────────────────────┘  └──────────────────────────┘
```

## 与 API 层的差异

| 层级 | 输入类型 | 职责 |
|------|---------|------|
| API | HTTP Request (raw) | 协议解析、HTTP 验证 |
| Handler | HandlerInput (structured) | 输入承接、调用转发 |

**关键区别**:
- API 层处理 HTTP 协议细节（headers, cookies, content-type）
- Handler 层处理已解析的结构化数据
- Handler 不感知 HTTP 协议

## 与 Service 层的差异

| 层级 | 职责 |
|------|------|
| Handler | 承接输入 + 转发调用（不执行） |
| Service | 执行业务逻辑 + 触发副作用 |

**关键区别**:
- Handler 返回转发目标信息 (`ForwardTarget`)
- Service 执行实际业务动作并返回结果
- Handler 不触发副作用（无数据库写入、无外部调用）

## 模块说明

- `handler_interface.py`: 定义 HandlerInterface 接口契约
- `input_acceptance.py`: 输入验证实现（结构检查，非业务规则）
- `call_forwarder.py`: 调用转发实现（返回目标，不实际调用）
- `verify_imports.py`: 导入自检脚本

## 硬约束

1. **不得触发副作用动作**: 所有副作用由 service 层负责
2. **不得进入 runtime 分支控制**: runtime 控制由 orchestrator 层负责
3. **不得触发外部集成**: 外部调用由 service 层负责
4. **不得修改 frozen 主线**: 只读取，不修改 governance 对象

## 转发映射表

| Action | Layer | Module | Method |
|--------|-------|--------|--------|
| query | service | query_service | execute |
| status | service | status_service | get |
| forward | orchestrator | internal_router | route_request |
| dispatch | service | dispatch_service | process |

## 输入检查规则

InputAcceptance 检查：

1. `request_id` 必须非空
2. `source` 必须是 `api` / `orchestrator` / `service` 之一
3. `action` 必须是已知 action
4. `payload` 必须是字典
5. `evidence_ref` (如果提供) 必须是字符串

**注意**: 这是结构检查，不是业务规则检查。
