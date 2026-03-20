# T2 Review Report: Orchestrator Minimal Landing

**Review ID**: T2-REV-20260319
**Reviewer**: vs--cc3
**Executor**: Antigravity-2
**Review Date**: 2026-03-19
**Status**: **PASS — FINAL**
**路径迁移状态**: ✅ 已迁移到 `skillforge/src/system_execution/orchestrator/`
**返工审查**: 见 [PATH_MIGRATION_REVIEW_REPORT.md](./PATH_MIGRATION_REVIEW_REPORT.md)

---

## Executive Summary

T2 任务 **Python 后端 orchestrator 骨架** 符合要求，职责边界清晰，但 **UI 端 "orchestrator.ts" 存在命名混淆**。

### 审查结论

| 维度 | Python 后端 | UI 端 orchestrator.ts |
|------|------------|----------------------|
| 目录骨架 | ✅ PASS | ⚠️ 命名混淆 |
| 内部路由职责 | ✅ PASS | ❌ 包含决策逻辑 |
| 裁决语义隔离 | ✅ PASS | ⚠️ 承载推断决策 |
| 连接说明自洽 | ✅ PASS | ⚠️ 需澄清 |
| 文档一致性 | ✅ PASS | N/A (UI 端无对应文档) |

---

## 1. 目录与文件骨架清晰度

### 1.1 Python 后端骨架 ✅

```
skillforge/src/system_execution_preparation/orchestrator/
├── __init__.py                 # 模块导出
├── orchestrator_interface.py   # 接口契约定义
├── internal_router.py          # 内部路由实现
├── acceptance_boundary.py      # 承接检查实现
├── verify_imports.py           # 导入自检脚本
├── README.md                   # 职责文档
└── CONNECTIONS.md              # 接口连接说明
```

**评估**: 结构清晰，职责分离明确，接口定义完整。

### 1.2 UI 端文件位置 ⚠️

```
ui/app/src/features/governanceInteraction/
├── orchestrator.ts      # ⚠️ 包含决策逻辑
├── interaction.tsx      # React Context Provider
└── governanceOrchestrationAdapter.ts  # 服务适配器
```

**评估**: `orchestrator.ts` 文件名与 T2 任务要求的 "orchestrator" 概念重叠，但实际内容是 **交互决策服务**，非内部路由。

---

## 2. Orchestrator 是否只做内部路由与承接

### 2.1 Python 后端 ✅

**`internal_router.py` 分析**:
```python
class InternalRouter(OrchestratorInterface):
    # Route mapping: request_type -> (layer, module, action)
    _ROUTE_MAP: Dict[str, RouteTarget] = {
        "governance_query": RouteTarget("handler", "governance_handler", "query"),
        "skill_execution": RouteTarget("service", "skill_service", "execute"),
        # ...
    }

    def route_request(self, context: RoutingContext) -> RouteTarget:
        # 纯路由映射，无业务逻辑
        if request_type in self._ROUTE_MAP:
            return self._ROUTE_MAP[request_type]
        return RouteTarget("handler", "fallback_handler", "accept")
```

**评估**: 符合要求，只做路由映射。

**`acceptance_boundary.py` 分析**:
```python
class AcceptanceBoundary:
    def validate(self, context: RoutingContext) -> tuple[bool, List[str]]:
        # 只检查结构完整性：request_id, source, evidence_ref
        # 无 permit 检查，无业务规则
```

**评估**: 符合要求，只做结构验证。

### 2.2 UI 端 orchestrator.ts ⚠️

**包含的决策逻辑**:
```typescript
// inferIntent: 意图推断（NLP 决策）
export const inferIntent = (value: string): IntentState => {
  // 根据输入内容推断 intent
  if (normalized.includes('外部') || normalized.includes('import')) {
    return 'vetting';
  }
  // ...
}

// resolveInteractionDecision: 决策构造
export const resolveInteractionDecision = (
  value: string,
  intentHint: IntentState = 'unknown',
): InteractionDecision => {
  return {
    intent,
    canvas,
    confidence: requiresClarification ? 'low' : 'high',  // ← 置信度决策
    requiresClarification,  // ← 是否需要澄清的决策
    reason: ...,  // ← 决策理由
    nextActions: ...,  // ← 决策动作
  };
}
```

**评估**: **超出 orchestrator 职责范围**。这不是内部路由，而是 **前端交互决策服务**。

---

## 3. Orchestrator 是否错误承载裁决语义

### 3.1 Python 后端 ✅

| 检查项 | 结果 | Evidence |
|--------|------|----------|
| 是否包含 permit 检查 | ❌ 否 | `acceptance_boundary.py` 只检查结构 |
| 是否包含 governance 决策 | ❌ 否 | 所有代码注释明确说明 "Does NOT make governance decisions" |
| 是否包含业务规则 | ❌ 否 | 只有路由映射表 |
| 是否修改状态 | ❌ 否 | 使用 `@dataclass(frozen=True)` |

### 3.2 UI 端 orchestrator.ts ⚠️

| 检查项 | 结果 | Evidence |
|--------|------|----------|
| 是否包含决策 | ✅ 是 | `inferIntent`, `resolveInteractionDecision` |
| 是否判断置信度 | ✅ 是 | `confidence: 'high' | 'low'` |
| 是否判断是否澄清 | ✅ 是 | `requiresClarification: boolean` |

**评估**: UI 端文件承载了**决策语义**，但这属于 **前端交互决策层**，非 orchestrator 路由层。

---

## 4. 接口连接说明自洽性

### 4.1 Python 后端 ✅

**`CONNECTIONS.md` 提供了完整的连接指南**:
- 导入路径说明
- 接口契约定义 (`RoutingContext`, `RouteTarget`)
- 使用示例 (API → Orchestrator, Handler → Orchestrator, Service 接收)
- 路由映射表

**评估**: 自洽完整。

### 4.2 UI 端连接 ⚠️

**调用链**:
```
interaction.tsx → governanceOrchestrationAdapter → (后端服务)
                ↑
        orchestrator.ts (仅用于类型定义和常量)
```

**评估**: 连接存在，但 `orchestrator.ts` 的命名与其在调用链中的角色不匹配。

---

## 5. 文档与骨架一致性

### 5.1 Python 后端 ✅

| 文档声称 | 骨架实现 | 一致性 |
|---------|---------|--------|
| 内部路由 | `internal_router.py` | ✅ |
| 承接检查 | `acceptance_boundary.py` | ✅ |
| 无治理判断 | 无 permit/governance 代码 | ✅ |
| 无外部集成 | 无 HTTP 调用 | ✅ |

### 5.2 UI 端 ⚠️

UI 端没有对应的 README/CONNECTIONS 文档说明其职责范围。

---

## 问题清单

### P1 — 命名混淆 ⚠️

**问题描述**: UI 端 `orchestrator.ts` 文件名与 T2 任务交付的 "orchestrator" 概念重叠，但实际功能不同。

**影响**:
- 文档阅读者可能混淆 Python 后端 orchestrator（内部路由）与 UI 端 orchestrator（交互决策）
- 未来维护者可能误将决策逻辑放入 Python orchestrator

**建议**:
1. 将 UI 端 `orchestrator.ts` 重命名为 `interactionDecision.ts` 或 `governanceRouting.ts`
2. 或者添加清晰的注释说明这是 **UI 交互决策层**，非 Python orchestrator

### P2 — 文档缺失 ⚠️

**问题描述**: UI 端缺少职责说明文档。

**建议**: 在 `ui/app/src/features/governanceInteraction/README.md` 中明确说明：
- 该模块负责 **交互决策**（intent 推断、canvas 解析）
- 与 Python 后端 **orchestrator**（内部路由）的区别

---

## EvidenceRef

本审查报告基于以下证据：

1. **Python 骨架**: `skillforge/src/system_execution_preparation/orchestrator/*.py`
2. **UI 实现**: `ui/app/src/features/governanceInteraction/orchestrator.ts`
3. **职责文档**: `skillforge/src/system_execution_preparation/orchestrator/README.md`
4. **连接说明**: `skillforge/src/system_execution_preparation/orchestrator/CONNECTIONS.md`
5. **执行报告**: `docs/2026-03-19/verification/system_execution_minimal_landing/T2_execution_report.md`

---

## 审查者声明

我是 vs--cc3，T2 审查者。

我已完成对 Antigravity-2 交付物的审查。

**审查结论**: Python 后端 orchestrator 骨架符合所有要求，UI 端命名澄清操作已完成。

---

## 审查响应最终更新 (2026-03-19)

### 澄清操作状态：完成 ✅

| 操作 | 状态 | Evidence |
|------|------|----------|
| 重命名文件 | ✅ 完成 | `interactionDecision.ts` 存在 |
| 更新组件引用 (6个) | ✅ 完成 | 所有组件引用已更新 |
| 更新特性引用 (4个) | ✅ 完成 | 所有特性引用已更新 |
| 验证无残留 | ✅ 通过 | `grep -r "from.*orchestrator"` 无结果 |

### 命名区分（最终状态）

| 层级 | 文件 | 职责 |
|------|------|------|
| Python 后端 | `skillforge/src/system_execution_preparation/orchestrator/` | 内部路由与承接 |
| UI 前端 | `ui/app/src/features/governanceInteraction/interactionDecision.ts` | 交互决策服务 |

### 最终评估

| 组件 | 状态 |
|------|------|
| Python 后端 orchestrator | ✅ PASS |
| UI 端澄清操作 | ✅ COMPLETE |

---

**移交合规官**: 报告已完整，交付 Kior-C 进行合规审查。

---

**报告结束**
