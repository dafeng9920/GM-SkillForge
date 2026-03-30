# 任务 BM2：总线对象模型与双层状态设计

## Task Envelope
- `task_id`: `BM2`
- `module`: `gm_bus_manager_seed_implementation_v1`
- `task_type`: `seed_implementation`
- `objective`: `定义总线对象最小模型与 lifecycle_status + gate_levels 双层状态模型`
- `parallel_group`: `wave_1`
- `depends_on`: `[]`
- `source_of_truth`:
  - `gm-lite/docs/2026-03-23/GM_BUS_MANAGER_SEED_IMPLEMENTATION_V1_SCOPE.md`
  - `gm-lite/docs/2026-03-23/GM_BUS_MANAGER_SEED_IMPLEMENTATION_V1_BOUNDARY_RULES.md`
  - `gm-lite/docs/2026-03-23/GM_LITE_BUS_MANAGER_METADATA_GUARDRAILS_V1.md`
- `acceptance_criteria`:
  - `对象模型存在`
  - `双层状态模型存在`
  - `不混用生命周期与门禁状态`
- `hard_constraints`:
  - `只做 seed implementation`
  - `不进入完整 runtime`
  - `不跨库搜索`
- `escalation_trigger`:
  - `state_model_conflict`
  - `scope_expansion`
  - `object_boundary_conflict`
- `next_hop`: `review`

## 发给 Execution 的提示词

你是任务 BM2 的执行者 Antigravity-2。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 定义总线对象最小模型
- 定义 `lifecycle_status + gate_levels` 双层状态设计
- 为后续 L1/L2/L3 火控状态位预留标准结构

必须写入：
- `gm-lite/docs/2026-03-23/verification/gm_bus_manager_seed_implementation/BM2_execution_report.md`

必须包含：
1. `task_id: BM2`
2. `executor: Antigravity-2`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. 对象模型清单
5. 双层状态模型结论
6. 最少 `EvidenceRef`

写回要求：
- 只写核心结论、增量内容、必要 EvidenceRef
- 不复述整份任务卡
- 不进入 watcher / auto-send / direct-connect
- 不跨库搜索

写回成功后下一跳：
- `review`
- 接棒者：`vs--cc1`
- 写回目标：
  - `gm-lite/docs/2026-03-23/verification/gm_bus_manager_seed_implementation/BM2_review_report.md`

## 发给 Review 的提示词

你是任务 BM2 的审查者 vs--cc1。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-23/verification/gm_bus_manager_seed_implementation/BM2_review_report.md`

必须包含：
1. `task_id: BM2`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. 对象模型 / 状态模型审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-23/verification/gm_bus_manager_seed_implementation/BM2_compliance_attestation.md`

若给出 `FAIL`，必须升级主控官，不得自行判定结案。

## 发给 Compliance 的提示词

你是任务 BM2 的合规官 Kior-C。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-23/verification/gm_bus_manager_seed_implementation/BM2_compliance_attestation.md`

必须包含：
1. `task_id: BM2`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
