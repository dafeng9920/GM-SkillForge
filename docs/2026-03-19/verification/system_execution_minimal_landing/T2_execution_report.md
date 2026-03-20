# T2 Execution Report: Orchestrator Minimal Landing

**Task ID**: T2
**Executor**: Antigravity-2
**Date**: 2026-03-19
**Status**: COMPLETED (返工后)

---

## 任务目标

完成 orchestrator 子面的最小落地：
- skillforge/src/system_execution/orchestrator/ 最小目录/文件骨架
- orchestrator 职责文档
- orchestrator 接口连接说明
- 最小导入/连接自检结果

---

## 路径迁移记录

### 返工原因
主控官终验退回：落位路径错误

### 路径变更

| 项目 | 旧路径 | 新路径 |
|------|--------|--------|
| **根目录** | `system_execution_preparation/` | `system_execution/` |
| **完整路径** | `skillforge/src/system_execution_preparation/orchestrator/` | `skillforge/src/system_execution/orchestrator/` |

### 导入路径变更

| 旧导入 | 新导入 |
|--------|--------|
| `from skillforge.src.system_execution_preparation.orchestrator import ...` | `from skillforge.src.system_execution.orchestrator import ...` |
| `from system_execution_preparation.orchestrator import ...` | `from system_execution.orchestrator import ...` |

---

## 交付物清单

### 1. 文件骨架

| 文件 | 路径 | 说明 |
|------|------|------|
| `__init__.py` | `skillforge/src/system_execution/orchestrator/__init__.py` | 模块导出定义 |
| `orchestrator_interface.py` | `skillforge/src/system_execution/orchestrator/orchestrator_interface.py` | 接口契约定义 |
| `internal_router.py` | `skillforge/src/system_execution/orchestrator/internal_router.py` | 内部路由实现 |
| `acceptance_boundary.py` | `skillforge/src/system_execution/orchestrator/acceptance_boundary.py` | 承接检查实现 |
| `verify_imports.py` | `skillforge/src/system_execution/orchestrator/verify_imports.py` | 导入自检脚本 |
| `README.md` | `skillforge/src/system_execution/orchestrator/README.md` | 职责文档 |
| `CONNECTIONS.md` | `skillforge/src/system_execution/orchestrator/CONNECTIONS.md` | 接口连接说明 |

### 2. 文档

- **README.md**: 明确 Orchestrator 的核心职责 (DOES) 和边界 (DOES NOT)
- **CONNECTIONS.md**: 详细的接口连接指南和使用示例（已更新所有路径引用）

### 3. 自检结果

```
==================================================
SUMMARY
==================================================
Imports: PASS
Interface Creation: PASS
Routing: PASS
Boundary Conditions: PASS

✓ All checks passed
```

---

## 核心职责明确

### Orchestrator DOES (做)

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

### Orchestrator DOES NOT (不做)

| 行为 | 是否 | 理由 |
|------|------|------|
| 许可证发放 | ❌ 否 | Gate 层职责 |
| 治理决策 | ❌ 否 | Gate/Contracts 层职责 |
| 外部集成 | ❌ 否 | Service 层职责 |
| Runtime 控制 | ❌ 否 | Handler 层职责 |

---

## 边界清晰

### 与 API 层边界
- API 层接收 HTTP 请求
- Orchestrator 接收 RoutingContext (结构化上下文)
- Orchestrator 不解析 HTTP 协议

### 与 Service 层边界
- Orchestrator 路由到 service
- Service 执行业务逻辑
- Orchestrator 不执行业务逻辑

### 与 Handler 层边界
- Orchestrator 路由到 handler
- Handler 执行 runtime 控制
- Orchestrator 不控制 runtime

### 与 Gate 层边界
- Orchestrator 做结构验证
- Gate 层做治理许可判断
- Orchestrator 不做 permit 检查

---

## 硬约束遵守

| 约束 | 状态 | Evidence |
|------|------|----------|
| 不得成为治理判断层 | ✅ 遵守 | `acceptance_boundary.py` 只检查结构，不检查 permit |
| 不得进入 runtime 控制 | ✅ 遵守 | `internal_router.py` 只返回路由目标，不执行 |
| 不得触发外部集成 | ✅ 遵守 | 无外部导入，无 HTTP 调用 |
| 不得修改 frozen 主线 | ✅ 遵守 | 只读取 context，不修改任何状态 |
| 不得借返工扩模块 | ✅ 遵守 | 仅迁移路径，无新增功能 |
| 无 EvidenceRef 不得宣称完成 | ✅ 遵守 | 本报告作为执行证据 |

---

## 接口契约

### 输入: RoutingContext

```python
@dataclass(frozen=True)
class RoutingContext:
    request_id: str
    source: str  # "api" | "handler" | "internal"
    intent: Optional[str] = None
    evidence_ref: Optional[str] = None
```

### 输出: RouteTarget

```python
@dataclass(frozen=True)
class RouteTarget:
    layer: str  # "service" | "handler" | "external"
    module: str
    action: str
```

### 方法签名

```python
class OrchestratorInterface(ABC):
    @abstractmethod
    def route_request(self, context: RoutingContext) -> RouteTarget: ...

    @abstractmethod
    def validate_acceptance(self, context: RoutingContext) -> tuple[bool, List[str]]: ...

    @abstractmethod
    def prepare_context(self, context: RoutingContext) -> Dict[str, Any]: ...
```

---

## 路由映射表

| Intent | Layer | Module | Action |
|--------|-------|--------|--------|
| governance_query | handler | governance_handler | query |
| governance_status | handler | governance_handler | status |
| skill_execution | service | skill_service | execute |
| data_processing | service | data_service | process |
| pipeline_submit | service | pipeline_service | submit |
| pipeline_status | service | pipeline_service | status |

---

## EvidenceRef

本交付物的证据引用：

1. **代码骨架**: `skillforge/src/system_execution/orchestrator/*.py`
2. **职责文档**: `skillforge/src/system_execution/orchestrator/README.md`
3. **连接说明**: `skillforge/src/system_execution/orchestrator/CONNECTIONS.md`
4. **自检结果**: 上述 "自检结果" 章节（新路径验证通过）
5. **执行报告**: `docs/2026-03-19/verification/system_execution_minimal_landing/T2_execution_report.md`

---

## 审查响应

### 审查结论
- **状态**: CONDITIONAL PASS — WITH CLARIFICATION
- **Python 后端 orchestrator**: ✅ 完全符合要求
- **UI 端命名混淆**: ✅ 已澄清完成

### 澄清操作

审查指出 `ui/app/src/features/governanceInteraction/orchestrator.ts` 存在命名混淆：
- 该文件包含的是**交互决策逻辑** (inferIntent, resolveInteractionDecision)
- 这是**前端交互决策服务**，不是内部路由 orchestrator

已执行澄清操作：

| 操作 | 详情 | Evidence |
|------|------|----------|
| 重命名文件 | `orchestrator.ts` → `interactionDecision.ts` | `ui/app/src/features/governanceInteraction/interactionDecision.ts` |
| 更新引用 (10个文件) | ✅ 全部完成 | 无残留引用 |

### 命名区分

| 名称 | 层级 | 职责 |
|------|------|------|
| `orchestrator/` (Python) | 后端 system_execution | 内部路由与承接 |
| `interactionDecision.ts` (前端) | UI governanceInteraction | 前端交互决策服务 |

---

## 执行者声明

我是 Antigravity-2，T2 执行者。

我只负责执行，不负责放行，不负责合规裁决。

本报告所述交付物已完成（路径已修正），等待 Gate 审核。

---

**报告结束**
