# L3 封板任务调度单（AI军团协作）

任务日期：2026-02-25  
主控官：Codex  
模式：strict

## PreflightChecklist
- [x] Fail-Closed 风险检查：三项任务都直接作用于主链路门禁/发布/版本演化，必须先审查再执行。
- [x] 环境与开关检查：执行环境统一使用 `d:\GM-SkillForge`，CLI 入口统一 `python -m skillforge.src.cli`（workdir=`skillforge-spec-pack`）。
- [x] 副作用检查：涉及发布、DB 写入、门禁阻断逻辑，全部任务强制 `Compliance PASS` 才可执行。

## ExecutionContract
- 输入范围（只允许触达）：
  - `skillforge-spec-pack/skillforge/src/**`
  - `skillforge-spec-pack/skillforge/tests/**`
  - `scripts/l3_gap_closure/**`
  - `scripts/run_l3_gap_closure.py`
  - `docs/2026-02-25/verification/**`
- 禁止触达：
  - `docs/2026-02-25/压力测试------/**`
  - 与 T1/T2/T3 无关目录
- 自动化 Gate：
  - `python scripts/run_l3_gap_closure.py`
- 回滚策略：
  - 单任务回滚到该任务开始前的 patch；若任一任务 `DENY`，本波次不放行。

## RequiredChanges
1. T1（Hard Gate）必须把 `constitution_risk_gate` 结果写入 `gate_decisions` 并在违规时阻断 `pack_audit_and_publish`，同时产出 `Ruling` 字段或 `ruling_path`。
2. T2（Integrity）必须在发布前增加 Registry/Graph 完整性校验（hash/signature/append-only），篡改后返回 `DENY` 或 `REQUIRES_CHANGES`（含冲突证据）。
3. T3（Delta）必须把“增量需求”强制映射到版本演进，并输出 `UpdatedGraph` 与 `ReleaseManifest` 可追溯字段。

## 任务分配（严格三权分立）
| Task | Execution | Review | Compliance | Depends On |
|---|---|---|---|---|
| T1 Hard Gate 接入 publish 前 | Antigravity-1 | vs--cc3 | Antigravity-2 | - |
| T2 Registry/Graph 完整性校验 | vs--cc1 | Kior-A | Kior-B | T1=ALLOW |
| T3 Delta 强制机制 | vs--cc2 | Kior-C | Antigravity-2 | T1=ALLOW, T2=ALLOW |

## 一键转发指令（复制整段给对应执行者）

### 发送给 Antigravity-1（Execution / T1）
```text
你是任务 T1 的执行者 Antigravity-1。

只执行文件：
- skillforge-spec-pack/skillforge/src/orchestration/engine.py
- skillforge-spec-pack/skillforge/src/nodes/constitution_gate.py
- skillforge-spec-pack/skillforge/src/nodes/pack_publish.py
- skillforge-spec-pack/skillforge/tests/test_constitution_hard_gate_blocking.py（可新建）

目标：
1) 违规意图必须在 publish 前被 BLOCK/DENY。
2) gate_decisions 不能为空，必须记录裁决。
3) 输出中必须包含 ruling（对象或路径）。

禁止：
- 不得改 T2/T3 指定文件。
- 不得绕过 Compliance PASS。

完成后写：
- docs/2026-02-25/verification/T1_execution_report.yaml
```

### 发送给 vs--cc3（Review / T1）
```text
你是任务 T1 的审查者 vs--cc3。

输入：
- docs/2026-02-25/tasks/T1_Antigravity-1.md
- docs/2026-02-25/verification/T1_execution_report.yaml

输出：
- docs/2026-02-25/verification/T1_gate_decision.json

要求：
- 检查 BLOCK 是否真的阻断发布。
- 检查 gate_decisions 是否有结构化记录。
- 检查 ruling 是否存在且字段齐全。
```

### 发送给 Antigravity-2（Compliance / T1）
```text
你是任务 T1 的合规官 Antigravity-2。

输入：
- docs/2026-02-25/verification/T1_execution_report.yaml
- docs/2026-02-25/verification/T1_gate_decision.json

输出：
- docs/2026-02-25/verification/T1_compliance_attestation.json

硬规则：
- 只要存在“可绕过 Fail-Closed”的路径，decision=FAIL。
- 结论必须含 evidence_refs 与 violations（若有）。
```

### 发送给 vs--cc1（Execution / T2）
```text
你是任务 T2 的执行者 vs--cc1。

前置：仅在 T1=ALLOW 后执行。

只执行文件：
- skillforge-spec-pack/skillforge/src/storage/repository.py
- skillforge-spec-pack/skillforge/src/storage/schema.py
- skillforge-spec-pack/skillforge/src/nodes/pack_publish.py
- skillforge-spec-pack/skillforge/tests/test_registry_graph_integrity_blocking.py（可新建）

目标：
1) 发布前做 registry/graph hash or signature 校验。
2) 发现篡改时返回冲突裁决并阻断发布。
3) 冲突结果可被 `scripts/l3_gap_closure/test_registry_graph_integrity.py` 捕获。

完成后写：
- docs/2026-02-25/verification/T2_execution_report.yaml
```

### 发送给 Kior-A（Review / T2）
```text
你是任务 T2 的审查者 Kior-A。
输出：docs/2026-02-25/verification/T2_gate_decision.json
审查重点：篡改后是否必定阻断；是否存在 silent pass。
```

### 发送给 Kior-B（Compliance / T2）
```text
你是任务 T2 的合规官 Kior-B。
输出：docs/2026-02-25/verification/T2_compliance_attestation.json
硬规则：完整性冲突不得放行发布；必须给出证据定位。
```

### 发送给 vs--cc2（Execution / T3）
```text
你是任务 T3 的执行者 vs--cc2。

前置：仅在 T1=ALLOW 且 T2=ALLOW 后执行。

只执行文件：
- skillforge-spec-pack/skillforge/src/nodes/skill_composer.py
- skillforge-spec-pack/skillforge/src/nodes/pack_publish.py
- skillforge-spec-pack/skillforge/src/orchestration/engine.py
- skillforge-spec-pack/skillforge/tests/test_delta_artifacts_enforced.py（可新建）

目标：
1) 增量需求必须产生新版本（或子 skill）。
2) 输出包含 UpdatedGraph（或 graph_update）字段。
3) 输出包含 ReleaseManifest（或 manifest+rollback）字段。

完成后写：
- docs/2026-02-25/verification/T3_execution_report.yaml
```

### 发送给 Kior-C（Review / T3）
```text
你是任务 T3 的审查者 Kior-C。
输出：docs/2026-02-25/verification/T3_gate_decision.json
审查重点：是否仍重复发布同一 skill_id v0.1.0；是否有图谱与发布清单结构。
```

### 发送给 Antigravity-2（Compliance / T3）
```text
你是任务 T3 的合规官 Antigravity-2。
输出：docs/2026-02-25/verification/T3_compliance_attestation.json
硬规则：无版本演化证据/无图谱变更证据/无发布清单证据 -> FAIL。
```

## Final Gate（主控官）
- 汇总文件：
  - `docs/2026-02-25/verification/T1_*`
  - `docs/2026-02-25/verification/T2_*`
  - `docs/2026-02-25/verification/T3_*`
- 输出：`docs/2026-02-25/verification/final_gate_decision.json`
- 规则：任一任务缺三权记录或 compliance!=PASS => `REQUIRES_CHANGES/DENY`。