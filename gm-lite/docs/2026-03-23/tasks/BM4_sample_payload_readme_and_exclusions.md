# 任务 BM4：样板 Payload / README / Exclusions / Change Control

## Task Envelope
- `task_id`: `BM4`
- `module`: `gm_bus_manager_seed_implementation_v1`
- `task_type`: `seed_implementation`
- `objective`: `补全 sample payload、README、使用说明与 exclusions / change control，确保 seed implementation 可被后续模块消费`
- `parallel_group`: `wave_3`
- `depends_on`: `["BM3"]`
- `source_of_truth`:
  - `gm-lite/docs/2026-03-23/GM_BUS_MANAGER_SEED_IMPLEMENTATION_V1_SCOPE.md`
  - `gm-lite/docs/2026-03-23/GM_BUS_MANAGER_SEED_IMPLEMENTATION_V1_BOUNDARY_RULES.md`
  - `gm-lite/docs/2026-03-23/GM_BUS_MANAGER_SEED_IMPLEMENTATION_V1_CHANGE_CONTROL_RULES.md`
- `acceptance_criteria`:
  - `sample payload 存在`
  - `README / usage 存在`
  - `exclusions / change control 冻结`
- `hard_constraints`:
  - `依赖 BM3`
  - `只做 seed implementation`
  - `不进入 watcher / runtime`
- `escalation_trigger`:
  - `documentation_gap`
  - `scope_expansion`
  - `change_control_conflict`
- `next_hop`: `review`

## 发给 Execution 的提示词

你是任务 BM4 的执行者 vs--cc1。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 补齐 sample payload
- 补齐 README / usage
- 冻结 exclusions / change control
- 让后续 dispatch assist minimal implementation 能直接消费这一层 seed 基座

必须写入：
- `gm-lite/docs/2026-03-23/verification/gm_bus_manager_seed_implementation/BM4_execution_report.md`

必须包含：
1. `task_id: BM4`
2. `executor: vs--cc1`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. sample payload / README / exclusions 核心结论
5. 最少 `EvidenceRef`

写回要求：
- 只写核心结论、增量内容、必要 EvidenceRef
- 不复述整份任务卡
- 不进入 watcher / auto-send / direct-connect
- 不跨库搜索

写回成功后下一跳：
- `review`
- 接棒者：`Kior-A`
- 写回目标：
  - `gm-lite/docs/2026-03-23/verification/gm_bus_manager_seed_implementation/BM4_review_report.md`

## 发给 Review 的提示词

你是任务 BM4 的审查者 Kior-A。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-23/verification/gm_bus_manager_seed_implementation/BM4_review_report.md`

必须包含：
1. `task_id: BM4`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. sample payload / README / exclusions 审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-23/verification/gm_bus_manager_seed_implementation/BM4_compliance_attestation.md`

若给出 `FAIL`，必须升级主控官，不得自行判定结案。

## 发给 Compliance 的提示词

你是任务 BM4 的合规官 Kior-C。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-23/verification/gm_bus_manager_seed_implementation/BM4_compliance_attestation.md`

必须包含：
1. `task_id: BM4`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
