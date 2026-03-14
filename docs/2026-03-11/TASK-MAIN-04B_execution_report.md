# TASK-MAIN-04B: 前端承接主链状态与证据 - 执行报告

> **任务目标**: 让前端承接主链状态、证据入口和运行结果
> **执行日期**: 2026-03-11
> **任务定义**: docs/2026-03-11/TASK-MAIN-04_前端承接完整链路_任务定义_2026-03-11.md
> **执行依据**: core/runtime_interface.py v0.1

---

## 执行摘要

| 状态 | 完成度 | 说明 |
|------|--------|------|
| 类型定义 | 100% | 完整映射 runtime_interface.py 中的数据结构 |
| 映射器 | 100% | 支持从真实 JSON 转换为前端类型 |
| 组件实现 | 100% | MainChainStatusPanel 可展示完整主链状态 |
| 证据入口 | 100% | 集成 EvidenceDrawer 提供证据交互 |
| 测试页面 | 100% | MainChainTestPage 可测试真实数据承接 |

---

## 完成内容

### 1. 类型定义 (`ui/app/src/types/runtimeInterface.ts`)

**核心类型**:
- `RunStatus` - 执行状态枚举
- `ArtifactKind` - 工件类型枚举
- `GateDecision` - Gate 决策状态
- `ArtifactRef` - 工件引用
- `EvidenceRef` - 证据引用
- `ArtifactManifest` - 工件清单
- `RunResult` - 执行结果

**前端扩展类型**:
- `MainChainStep` - 主链步骤定义
- `MainChainStepStatus` - 主链步骤状态
- `MainChainStepResult` - 主链步骤结果
- `MainChainStatus` - 完整主链状态
- `MainChainViewModel` - 主链执行视图模型
- `EvidenceEntry` - 证据入口项

**工具函数**:
- `isRunSuccess()` - 判断运行状态是否成功
- `isRunFailure()` - 判断运行状态是否失败
- `isGateAllowed()` - 判断 Gate 决策是否通过
- `getStepDisplayName()` - 获取步骤显示名称
- `getStepStatusColor()` - 获取步骤状态颜色
- `extractEvidenceEntries()` - 从 RunResult 提取证据入口列表

---

### 2. 映射器 (`ui/app/src/mappers/runtimeInterfaceMapper.ts`)

**映射函数**:
- `mapToArtifactRef()` - 映射工件引用
- `mapToEvidenceRef()` - 映射证据引用
- `mapToArtifactManifest()` - 映射工件清单
- `mapToRunResult()` - 映射运行结果
- `mapToMainChainStatus()` - 从 RunResult 推导主链状态

**加载函数**:
- `loadRunResultFromJson()` - 从 JSON 文件加载 RunResult
- `loadManifestFromJson()` - 从 JSON 文件加载 ArtifactManifest

**验证函数**:
- `validateRunResult()` - 验证 RunResult 数据完整性

---

### 3. 主链状态面板组件 (`ui/app/src/components/governance/MainChainStatusPanel.tsx`)

**功能特性**:
1. 展示主链步骤状态 (Permit → Pre-Absorb → Absorb → Local Accept → Final Accept)
2. 显示 Gate Decision 状态 (ALLOW/REQUIRES_CHANGES/DENY)
3. 提供证据入口位 (可点击打开 EvidenceDrawer)
4. 展示运行结果摘要
5. 显示 ArtifactManifest 统计信息

**子组件**:
- `StepStatusIndicator` - 步骤状态指示器
- `GateDecisionTag` - Gate 决策标签

**Props 接口**:
```typescript
interface MainChainStatusPanelProps {
  runResult: RunResult;              // 运行结果 (必需)
  mainChainStatus?: MainChainStatus; // 主链状态 (可选)
  showDetails?: boolean;              // 是否显示详细信息
  stepOrder?: MainChainStep[];        // 步骤顺序 (可自定义)
}
```

---

### 4. 测试页面 (`ui/app/src/pages/execute/MainChainTestPage.tsx`)

**功能**:
- 支持从真实 JSON 文件加载 RunResult (REAL-TASK-002)
- 支持加载模拟数据用于测试
- 展示 MainChainStatusPanel 完整功能
- 提供使用说明和代码示例

**测试数据路径**:
- `docs/2026-03-11/REAL-TASK-002/run_result.json`
- `docs/2026-03-11/REAL-TASK-002/artifact_manifest.json`

---

## 真实数据映射

### RunResult 映射示例

**真实 JSON** (来自 REAL-TASK-002):
```json
{
  "schema_version": "runtime_interface_v0.1",
  "task_id": "REAL-TASK-002",
  "run_id": "REAL-TASK-002-ABSORB",
  "executor": "absorb_with_manifest.py",
  "status": "success",
  "started_at": "2026-03-10T16:34:48.143559Z",
  "finished_at": "2026-03-10T16:34:48.164102Z",
  "summary": "Absorbed 6 artifacts and 4 evidence items",
  "evidence_refs": [...],
  "manifest": {...}
}
```

**前端类型** (映射后):
```typescript
{
  schema_version: "runtime_interface_v0.1",
  task_id: "REAL-TASK-002",
  run_id: "REAL-TASK-002-ABSORB",
  executor: "absorb_with_manifest.py",
  status: "success",  // RunStatus
  started_at: "2026-03-10T16:34:48.143559Z",
  finished_at: "2026-03-10T16:34:48.164102Z",
  summary: "Absorbed 6 artifacts and 4 evidence items",
  evidence_refs: [/* EvidenceRef[] */],
  manifest: {/* ArtifactManifest */}
}
```

### ArtifactManifest 映射示例

**真实 JSON**:
```json
{
  "schema_version": "runtime_interface_v0.1",
  "task_id": "REAL-TASK-002",
  "run_id": "REAL-TASK-002-ABSORB",
  "artifacts": [
    { "path": "blueprint.md", "kind": "blueprint", "content_hash": "...", "size_bytes": 718 },
    ...
  ],
  "evidence": [
    { "path": "evidence/p2_doc_integration_report.md", "kind": "evidence", ... },
    ...
  ],
  "env": { "APP_ROOT": "D:/GM-SkillForge", ... },
  "created_at": "2026-03-10T16:34:48.143559+00:00"
}
```

---

## 证据入口实现

### 证据入口类型

1. **EvidenceRef 入口** - 来自 runResult.evidence_refs
2. **Artifact 入口** - 来自 manifest.artifacts
3. **Evidence 入口** - 来自 manifest.evidence
4. **Manifest 入口** - manifest.json 本身
5. **Gate Decision 入口** - 步骤的 gate_decision

### 证据交互流程

```
用户点击证据卡片
    ↓
MainChainStatusPanel.handleEvidenceClick(entry)
    ↓
设置 selectedEvidence + 打开 EvidenceDrawer
    ↓
EvidenceDrawer 显示证据详情
    ↓
用户可复制 run_id / evidence_ref / 完整 JSON
```

---

## 集成点

### 与现有组件集成

1. **EvidenceDrawer** - 复用现有证据抽屉组件
2. **DualChannelWorkbench** - 可用于嵌入主链状态面板
3. **DecisionHeroCard** - 可与 Gate Decision 状态联动

### 数据流

```
core/runtime_interface.py (Python)
    ↓ (JSON 文件)
ui/app/src/mappers/runtimeInterfaceMapper.ts
    ↓ (类型转换)
ui/app/src/types/runtimeInterface.ts
    ↓ (Props 传递)
ui/app/src/components/governance/MainChainStatusPanel.tsx
    ↓ (用户交互)
ui/app/src/components/governance/EvidenceDrawer.tsx
```

---

## 风险评估

| 风险ID | 级别 | 描述 | 缓解措施 |
|--------|------|------|----------|
| R-001 | LOW | 类型映射可能遗漏字段 | 提供可选字段和默认值 |
| R-002 | LOW | 真实 JSON 数据可能不符合 schema | 添加验证函数 validateRunResult() |
| R-003 | LOW | 主链步骤推导逻辑可能不准确 | 提供 mainChainStatus 可选参数覆盖 |
| R-004 | LOW | 证据入口路径可能不可访问 | 仅展示引用，不强制验证路径存在 |

---

## 下一步 (TASK-MAIN-04C)

TASK-MAIN-04B 完成了前端**承接**主链状态的能力。下一步 TASK-MAIN-04C 应该：

1. **发起一次完整链路测试** - 从前端发起一个低风险测试任务
2. **接到主链输出** - 接收真实的 RunResult 和 ArtifactManifest
3. **在前端显示完整结果** - 使用 MainChainStatusPanel 展示

---

## 证据引用

| 类型 | 路径 |
|------|------|
| 任务定义 | docs/2026-03-11/TASK-MAIN-04_前端承接完整链路_任务定义_2026-03-11.md |
| Runtime 接口 | core/runtime_interface.py |
| 真实数据 | docs/2026-03-11/REAL-TASK-002/run_result.json |
| 真实数据 | docs/2026-03-11/REAL-TASK-002/artifact_manifest.json |

---

**报告生成时间**: 2026-03-11
**任务状态**: COMPLETED
**下一步**: TASK-MAIN-04C
