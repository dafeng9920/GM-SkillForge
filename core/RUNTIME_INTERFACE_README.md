# GM-SkillForge 统一最小运行接口 v0.1

> Task: T-ASM-02 统一最小运行接口
> Date: 2026-03-10
> Status: 完成

## 一、接口定义位置

```
core/runtime_interface.py
```

这是本地主线的**统一最小运行接口**模块，提供：

- `RunRequest` - 执行请求
- `RunResult` - 执行结果
- `ArtifactManifest` - 工件清单
- `RuntimeSession` - 运行时会话

## 二、与现有系统的对应关系

### 2.1 RunRequest 对应现有结构

| 现有结构 | 路径 | 对应关系 |
|---------|------|---------|
| `CloudTaskContract` | `schemas/openclaw_cloud_task_contract.schema.json` | 完全覆盖，RunRequest 是更通用的版本 |
| `IntakeRequest` | `skillforge/src/skills/gates/gate_intake.py` | 兼容 input_data 格式 |
| `TaskSpec.input` | `multi-ai-collaboration.md` | 兼容 task 书写格式 |

### 2.2 RunResult 对应现有结构

| 现有结构 | 路径 | 对应关系 |
|---------|------|---------|
| `ExecutionReceipt` | `schemas/openclaw_execution_receipt.schema.json` | 完全覆盖，RunResult 是更通用的版本 |
| `GateResult` | 各 gate 文件 | 兼容 gate_decision/evidence_refs 格式 |
| `ExecutionReport` | `multi-ai-collaboration.md` | 兼容执行报告格式 |

### 2.3 ArtifactManifest 对应现有结构

| 现有结构 | 路径 | 对应关系 |
|---------|------|---------|
| `dropzone manifest.json` | `dropzone/*/manifest.json` | 完全兼容，提供 `from_dropzone_manifest()` 方法 |
| `AuditPack.manifest` | `core/pack_and_permit.py` | 可互相转换 |
| `TaskSpec.output.deliverables` | `multi-ai-collaboration.md` | 兼容交付物清单格式 |

## 三、统一接口与主链的关系

```
┌─────────────────────────────────────────────────────────────────┐
│                     本地主线统一入口                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │   Permit     │ ──>  │ pre_absorb   │ ──>  │    absorb    │  │
│  │              │      │    _check    │      │              │  │
│  └──────────────┘      └──────────────┘      └──────────────┘  │
│         │                      │                      │         │
│         v                      v                      v         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              core/runtime_interface.py                      │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │ │
│  │  │ RunRequest   │  │ ArtifactManifest│ │  RunResult   │    │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │ │
│  └────────────────────────────────────────────────────────────┘ │
│         │                      │                      │         │
│         v                      v                      v         │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │  local       │      │   final      │      │   Receipt    │  │
│  │  accept      │      │   accept     │      │   Chain      │  │
│  └──────────────┘      └──────────────┘      └──────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 四、接口使用示例

### 4.1 创建执行请求

```python
from core.runtime_interface import RunRequest, RuntimeSession

# 方式1: 直接创建
request = RunRequest(
    task_id="T-ASM-02",
    run_id="RUN-12345678",
    objective="统一最小运行接口",
    executor="Antigravity-1",
    contract_ref="contracts/task_T_ASM_02.yml",
    permit_ref="permits/default/tg1_baseline_permit.json",
    required_artifacts=["blueprint.md", "code.diff"],
    required_evidence=["test_report.md"],
)

# 方式2: 通过 RuntimeSession 创建
session = RuntimeSession(task_id="T-ASM-02", executor="Antigravity-1")
request = session.create_request(
    objective="统一最小运行接口",
    parameters={"output_dir": "/tmp/output"},
    constraints={"max_duration_sec": 3600},
    contract_ref="contracts/task_T_ASM_02.yml",
)
```

### 4.2 创建工件清单

```python
from core.runtime_interface import ArtifactManifest, ArtifactKind
from pathlib import Path

# 方式1: 直接创建
manifest = ArtifactManifest(
    task_id="T-ASM-02",
    run_id="RUN-12345678",
)
manifest.add_artifact("core/runtime_interface.py", ArtifactKind.CODE)
manifest.add_evidence("docs/T-ASM-02_report.md")

# 方式2: 从 dropzone manifest 加载
manifest = ArtifactManifest.from_dropzone_manifest(
    manifest_path=Path("dropzone/REAL-TASK-002/manifest.json"),
    run_id="RUN-12345678",
)
```

### 4.3 创建执行结果

```python
from core.runtime_interface import RunResult, RunStatus

# 方式1: 直接创建
result = RunResult(
    task_id="T-ASM-02",
    run_id="RUN-12345678",
    executor="Antigravity-1",
    status=RunStatus.SUCCESS,
    started_at="2026-03-10T10:00:00Z",
    finished_at="2026-03-10T10:30:00Z",
    summary="统一接口创建完成",
    manifest=manifest,
)

# 方式2: 通过工厂方法
result = RunResult.success_result(
    task_id="T-ASM-02",
    run_id="RUN-12345678",
    executor="Antigravity-1",
    started_at="2026-03-10T10:00:00Z",
    finished_at="2026-03-10T10:30:00Z",
    summary="统一接口创建完成",
    manifest=manifest,
)
```

### 4.4 完整会话流程

```python
from core.runtime_interface import RuntimeSession, RunStatus

# 1. 创建会话
session = RuntimeSession(task_id="T-ASM-02", executor="Antigravity-1")

# 2. 创建请求
request = session.create_request(
    objective="统一最小运行接口",
    contract_ref="contracts/task_T_ASM_02.yml",
)

# 3. 开始执行
started_at = session.start_run()

# 4. 创建工件清单
manifest = session.create_manifest()
manifest.add_artifact("core/runtime_interface.py", ArtifactKind.CODE)
manifest.add_evidence("docs/T-ASM-02_report.md")

# 5. 完成执行
result = session.complete_run(
    status=RunStatus.SUCCESS,
    summary="统一接口创建完成",
    executed_commands=["python -m core.runtime_interface"],
)

# 6. 导出 JSON
request_json = json.dumps(session.request.to_dict(), indent=2)
result_json = json.dumps(session.result.to_dict(), indent=2)
manifest_json = json.dumps(session.manifest.to_dict(), indent=2)
```

## 五、兼容性说明

### 5.1 与现有 Permit 系统兼容

```python
from core.runtime_interface import RunRequest
from core.pack_and_permit import Permit

# RunRequest 可引用 Permit
request = RunRequest(
    task_id="T-ASM-02",
    run_id="RUN-12345678",
    objective="...",
    executor="Antigravity-1",
    permit_ref="permits/default/tg1_baseline_permit.json",
)

# 或直接关联 Permit 对象的 hash
permit = Permit(...)
request.permit_ref = permit.audit_pack_hash
```

### 5.2 与现有 AuditPack 系统兼容

```python
from core.runtime_interface import ArtifactManifest
from core.pack_and_permit import AuditPack

# ArtifactManifest 可转换为 AuditPack.manifest
manifest = ArtifactManifest(task_id="T-ASM-02", run_id="RUN-12345678")
manifest_dict = manifest.to_dict()

# 可直接用于构建 AuditPack
audit_pack = AuditPack(
    pack_id="AP-...",
    schema_version="pack_and_permit_v0",
    manifest=manifest_dict,  # 直接使用
    gate_decisions=[...],
    policy_matrix={...},
    checksums={...},
    created_at="...",
)
```

### 5.3 与现有 Gate 系统兼容

```python
from core.runtime_interface import RunResult, EvidenceRef

# RunResult.evidence_refs 兼容 gate EvidenceRef
result = RunResult(...)
result.evidence_refs.append(EvidenceRef(
    issue_key="T-ASM-02",
    source_locator="file://docs/T_ASM_02_report.md",
    content_hash="sha256:abc123...",
    tool_revision="runtime_interface_v0.1",
    timestamp="2026-03-10T10:30:00Z",
    kind="FILE",
))
```

## 六、后续迁移路径

### 6.1 本轮已完成

- ✅ 创建统一接口定义 (`core/runtime_interface.py`)
- ✅ 定义核心数据结构 (RunRequest, RunResult, ArtifactManifest)
- ✅ 提供与现有系统的兼容方法
- ✅ 创建本说明文档

### 6.2 下一轮可迁移（T-ASM-03 及之后）

以下组件可逐步迁移到使用统一接口，但**本轮不修改**：

1. **dropzone manifest.json**
   - 当前: 简单的 `{task_id, artifacts[], evidence[], env{}}`
   - 迁移: 使用 `ArtifactManifest` 替代，增加 `kind`, `content_hash` 等字段

2. **scripts/absorb.sh**
   - 当前: 直接读取 manifest.json 并复制文件
   - 迁移: 使用 `ArtifactManifest.from_dropzone_manifest()` 加载

3. **core/pack_and_permit.py**
   - 当前: 使用自己的 `AuditPack` 结构
   - 迁移: `AuditPack.manifest` 可接受 `ArtifactManifest.to_dict()` 输出

4. **scripts/validate_delivery_completeness.py**
   - 当前: 固定检查 6 种交付物
   - 迁移: 使用 `ArtifactManifest.artifacts` 动态检查

### 6.3 暂不迁移的部分

以下组件**暂不迁移**，保持现有实现：

1. **Gate 系统** (`skillforge/src/skills/gates/*.py`)
   - 原因: Gate 系统已有稳定的 `GateResult` 结构
   - 保持: 继续使用现有接口，通过 `EvidenceRef` 做桥接

2. **Permit 签发** (`core/pack_and_permit.py`)
   - 原因: 已有完整的 Permit/AuditPack 结构
   - 保持: 继续使用现有结构，通过 manifest 字段对接

3. **现有 Schema 文件** (`schemas/*.json`)
   - 原因: 已有稳定的 JSON Schema 定义
   - 保持: 继续使用，统一接口提供转换方法

## 七、风险与限制

### 7.1 风险

| 风险 | 缓解措施 |
|-----|---------|
| 新接口与现有系统不一致 | 提供兼容方法和转换函数 |
| 迁移过程中出现兼容性问题 | 保持现有接口不变，新接口并行存在 |
| 多 Agent 使用时版本冲突 | 使用 `schema_version` 字段标识版本 |

### 7.2 限制

1. **不修改现有业务逻辑**
   - 本轮只创建新接口，不修改现有代码
   - 现有系统继续使用原有接口

2. **不引入新抽象层**
   - 本轮只做接口统一，不做架构改造
   - 不引入新的中间件或代理

3. **兼容性优先**
   - 新接口设计以兼容现有结构为前提
   - 不强制现有系统迁移

## 八、验收标准

- [x] 接口定义位于 `core/runtime_interface.py`
- [x] 定义了 `RunRequest`, `RunResult`, `ArtifactManifest`
- [x] 提供了 `RuntimeSession` 统一入口
- [x] 与现有 manifest/permit/absorb 链有对应关系
- [x] 文档说明了后续迁移路径（但本轮不动）
- [x] 不修改无关业务逻辑
- [x] 不引入与主线无关的新抽象

## 九、证据引用

- 接口定义: `core/runtime_interface.py`
- 说明文档: `core/RUNTIME_INTERFACE_README.md`
- 现有 Permit: `permits/default/tg1_baseline_permit.json`
- 现有 Manifest 示例: `dropzone/REAL-TASK-002/manifest.json`
- Pack And Permit: `core/pack_and_permit.py`
