# R1: system_execution_preparation 残留引用盘点

**执行者**: vs--cc1
**任务**: 盘点 `skillforge/src/system_execution_preparation/` 的所有残留引用
**时间**: 2026-03-19
**范围**: 仅限当前分支，不扩展到 frozen 主线

---

## 执行摘要

| 类别 | 数量 | 状态 |
|------|------|------|
| **代码引用** | 76+ | 待清理 |
| **文档引用** | 7 | 待清理 |
| **自检脚本引用** | 5 | 待清理 |
| **历史报告引用** | 2 | 归档保留 |
| **脚本引用** | 1 | 待清理 |

---

## 1. 代码引用

### 1.1 system_execution_preparation 内部文件 (19个)

```
skillforge/src/system_execution_preparation/
├── __init__.py
├── README.md
├── api/
│   ├── __init__.py
│   ├── api_interface.py
│   ├── request_adapter.py
│   ├── response_builder.py
│   ├── verify_imports.py
│   └── CONNECTIONS.md
├── handler/
│   ├── __init__.py
│   ├── call_forwarder.py
│   ├── handler_interface.py
│   ├── input_acceptance.py
│   ├── verify_imports.py
│   └── BOUNDARIES.md
├── orchestrator/
│   ├── __init__.py
│   ├── acceptance_boundary.py
│   ├── internal_router.py
│   ├── orchestrator_interface.py
│   ├── verify_imports.py
│   └── CONNECTIONS.md
├── service/
│   └── __init__.py
└── workflow/
    ├── __init__.py
    ├── entry.py
    ├── orchestration.py
    ├── _self_check.py
    └── CONNECTIONS.md
```

### 1.2 system_execution 中的引用 (迁移遗留)

| 文件 | 行/引用类型 | 说明 |
|------|-------------|------|
| `workflow/_self_check.py` | L5 | 注释: "路径已从 system_execution_preparation 迁移到 system_execution" |
| `workflow/WORKFLOW_RESPONSIBILITIES.md` | L92-93 | 迁移对照表 |
| `workflow/CONNECTIONS.md` | L9,10,54,60,71,77,88,94 | 旧路径文档 |
| `api/verify_imports.py` | L6, L63 | 迁移标记注释 |
| `api/CONNECTIONS.md` | L11,26,39,54-57,83,84,97,143,155 | 旧路径示例 |
| `service/verify_imports.py` | L99, L103 | **导入引用** (实际代码依赖) |

**关键发现**:
- `system_execution/service/verify_imports.py` 包含**实际导入依赖**:
  ```python
  from skillforge.src.system_execution_preparation.orchestrator import (
      AcceptanceBoundary,
      InternalRouter,
  )
  ```

### 1.3 system_execution_preparation 内部导入

| 模块 | 导入目标 |
|------|----------|
| `api/verify_imports.py` | 本地 api 模块 + orchestrator_interface |
| `handler/verify_imports.py` | 本地 handler 模块 |
| `orchestrator/verify_imports.py` | 本地 orchestrator 模块 |
| `workflow/_self_check.py` | 本地 workflow.entry, workflow.orchestration |

---

## 2. 文档引用

### 2.1 模块文档 (docs/2026-03-19/)

| 文件 | 引用类型 |
|------|----------|
| `SYSTEM_EXECUTION_PREPARATION_RETIREMENT_MODULE_V1_PROMPTS.md` | 主题引用 |
| `SYSTEM_EXECUTION_PREPARATION_RETIREMENT_MODULE_V1_REPORT.md` | 主题引用 |
| `SYSTEM_EXECUTION_PREPARATION_RETIREMENT_MODULE_V1_ACCEPTANCE.md` | 主题引用 |
| `SYSTEM_EXECUTION_PREPARATION_RETIREMENT_MODULE_V1_BOUNDARY_RULES.md` | 主题引用 |
| `SYSTEM_EXECUTION_PREPARATION_RETIREMENT_MODULE_V1_TASK_BOARD.md` | 主题引用 |
| `SYSTEM_EXECUTION_PREPARATION_RETIREMENT_MODULE_V1_SCOPE.md` | 主题引用 |
| `SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_REWORK_PROMPTS.md` | 迁移对照 |

### 2.2 验证报告 (docs/2026-03-19/verification/)

| 文件 | 引用内容 |
|------|----------|
| `system_execution_minimal_landing/T5_execution_report.md` | L22: `from skillforge.src.system_execution_preparation.api` |
| `system_execution_minimal_landing/T4_execution_report.md` | L24: `from system_execution_preparation.handler` |
| `system_execution_minimal_landing/T2_execution_report.md` | L36-37: orchestrator 导入对照表 |
| `system_execution_minimal_landing/PATH_MIGRATION_REVIEW_REPORT.md` | 路径迁移记录 |

---

## 3. 自检脚本引用

### 3.1 system_execution_preparation 自检 (4个)

| 脚本 | 类型 |
|------|------|
| `workflow/_self_check.py` | `from skillforge.src.system_execution_preparation.workflow` |
| `api/verify_imports.py` | `from skillforge.src.system_execution_preparation.api` |
| `handler/verify_imports.py` | `from system_execution_preparation.handler` |
| `orchestrator/verify_imports.py` | `from system_execution_preparation.orchestrator` |

### 3.2 system_execution 自检

| 脚本 | 依赖 |
|------|------|
| `service/verify_imports.py` | `from skillforge.src.system_execution_preparation.orchestrator` |

---

## 4. 历史报告引用

| 文件 | 行 | 说明 |
|------|-----|------|
| `docs/compliance_reviews/review_latest.json` | 196 | 审查报告中的资源清单 |
| `docs/compliance_reviews/runs/latest/review.json` | 196 | 审查报告中的资源清单 |

**状态**: 归档保留，不应修改

---

## 5. 脚本引用

| 文件 | 行 | 内容 |
|------|-----|------|
| `scripts/run_3day_compliance_review.py` | 684 | `"system_execution_preparation_assets": _glob_existing(...)` |

---

## 6. 关键风险点

### 6.1 实际代码依赖 (阻塞删除)

| 位置 | 依赖 |
|------|------|
| `skillforge/src/system_execution/service/verify_imports.py` | `from skillforge.src.system_execution_preparation.orchestrator` |

**影响**: 必须先迁移或删除此依赖，才能安全删除 `system_execution_preparation/`

### 6.2 文档漂移

- `system_execution/api/CONNECTIONS.md` 仍使用旧路径示例
- 可能导致开发者误用已废弃的导入路径

---

## 7. 下一步行动建议

| 优先级 | 任务 | 依赖 |
|--------|------|------|
| P0 | 解除 `service/verify_imports.py` 的导入依赖 | - |
| P1 | 删除 `system_execution_preparation/` 目录 | P0 |
| P2 | 更新 `system_execution/CONNECTIONS.md` 中的路径示例 | - |
| P3 | 归档/清理文档引用 | - |

---

**报告生成时间**: 2026-03-19
**R1 签名**: vs--cc1
