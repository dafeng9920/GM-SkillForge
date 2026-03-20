# Workflow 连接说明

> **证据级别**: PREPARATION | **任务**: T1 | **日期**: 2026-03-19 (返工)

## 路径迁移记录 (T1 返工)

| 项目 | 迁移状态 |
|------|----------|
| workflow 模块 | 已迁移至 `skillforge/src/system_execution/workflow/` |
| 导入路径 | 已迁移至 `skillforge.src.system_execution.workflow` |

**注**: `system_execution_preparation/` 目录已退役，所有引用已更新至 `system_execution/`。

## 层级连接图

```
┌───────────────────────────────────────────────────────────────────┐
│                         External Request                          │
└───────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌───────────────────────────────────────────────────────────────────┐
│                       Workflow Layer                              │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  entry.py: WorkflowEntry.route(context)                     │  │
│  │    └─> 接收请求，确定处理路径                                │  │
│  └─────────────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  orchestration.py: WorkflowOrchestrator.coordinate_stage()  │  │
│  │    └─> 连接各层，传递上下文                                  │  │
│  └─────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        ▼                         ▼                         ▼
┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
│   Orchestrator    │   │     Service       │   │     Handler       │
│   (编排协调)      │   │    (业务逻辑)     │   │    (资源操作)     │
│  ../orchestrator/ │   │   ../service/     │   │   ../handler/     │
│  __init__.py      │   │  __init__.py      │   │  __init__.py      │
└───────────────────┘   └───────────────────┘   └───────────────────┘
        │                         │                         │
        └─────────────────────────┼─────────────────────────┘
                                  ▼
                        ┌───────────────────┐
                        │       Gate        │
                        │   (治理裁决)      │
                        │  skills/gates/    │
                        └───────────────────┘
```

## 各层连接说明

### 1. Workflow → Orchestrator

**模块路径**: `skillforge/src/system_execution/orchestrator/`

**连接方式**:
```python
# 在 workflow/orchestration.py 中
workflow_orchestrator.connect_to_orchestrator(
    "skillforge.src.system_execution.orchestrator"
)
```

**调用边界**:
- Workflow 传递: `WorkflowContext` (上下文对象)
- Orchestrator 返回: `StageResult` (阶段结果)
- **不传递**: 治理决策权

### 2. Workflow → Service

**模块路径**: `skillforge/src/system_execution/service/`

**连接方式**:
```python
# 在 workflow/orchestration.py 中
workflow_orchestrator.connect_to_service(
    "skillforge.src.system_execution.service"
)
```

**调用边界**:
- Workflow 传递: 业务参数
- Service 返回: 业务结果
- **不传递**: 治理决策上下文

### 3. Workflow → Handler

**模块路径**: `skillforge/src/system_execution/handler/`

**连接方式**:
```python
# 在 workflow/orchestration.py 中
workflow_orchestrator.connect_to_handler(
    "skillforge.src.system_execution.handler"
)
```

**调用边界**:
- Workflow 传递: 资源操作请求
- Handler 返回: 操作结果
- **不传递**: 治理验证逻辑

### 4. Workflow → API

**模块路径**: `skillforge/src/api/`

**连接方式**:
```python
# 在 workflow/orchestration.py 中
workflow_orchestrator.connect_to_api(
    "skillforge.src.api"
)
```

**调用边界**:
- Workflow 传递: 协议适配请求
- API 返回: 协议响应
- **不传递**: 治理裁决结果

## 与现有 API 的集成

### 现有 API 端点

| 端点 | 文件 | Workflow 连接点 |
|------|------|----------------|
| POST /cognition/generate | api/l4_api_fixed.py | WorkflowEntry.route() |
| POST /work/adopt | api/l4_api_fixed.py | WorkflowEntry.route() |
| POST /work/execute | api/l4_api_fixed.py | WorkflowEntry.route() |

### 集成方式 (PREPARATION 级别)

```python
# PREPARATION 级别: 只定义接口，不建立实际连接
# 在 workflow/entry.py 中

class WorkflowEntry:
    def route(self, context: WorkflowContext) -> str:
        # TODO: Runtime implementation
        # 1. 解析 context.request_id
        # 2. 路由到对应的 orchestrator/service/handler
        # 3. 返回路由目标
        raise NotImplementedError("Preparation only")
```

## 连接验证

### 静态连接检查
```bash
# 检查模块导入是否正确 (新路径)
python -m skillforge.src.system_execution.workflow._self_check
```

### 期望输出
```
✓ WorkflowEntry imported
✓ WorkflowOrchestrator imported
✓ All protocol types defined
✓ No runtime dependencies detected
✓ Correct module path: skillforge.src.system_execution.workflow
```

## 禁止的连接

| 连接类型 | 原因 |
|---------|------|
| Workflow → Gate | 治理裁决不由 Workflow 负责 |
| Workflow → Database | 资源操作由 Handler 负责 |
| Workflow → External API | 外部集成由 API 层负责 |
| Workflow 直接实现业务逻辑 | 业务逻辑由 Service 负责 |

## 证据要求

完成连接后必须提供:
1. 各层模块路径清单
2. 导入自检结果
3. 连接接口定义
4. 无运行时依赖证明
