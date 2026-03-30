# 任务 BO4：MirrorSealer / Frozen Seal / README / Exclusions

## Task Envelope
- `task_id`: `BO4`
- `module`: `gm_lite_blueprint_orchestrator_seed_implementation_v1`
- `task_type`: `seed_implementation`
- `objective`: `实现 MirrorSealer 最小封印规则、.frozen_seal 样板与 README / exclusions`
- `parallel_group`: `wave_3`
- `depends_on`: `["BO3"]`
- `source_of_truth`:
  - `gm-lite/docs/2026-03-24/GM_LITE_BLUEPRINT_ORCHESTRATOR_SEED_IMPLEMENTATION_V1_SCOPE.md`
  - `gm-lite/docs/2026-03-24/GM_LITE_BLUEPRINT_ORCHESTRATOR_SEED_IMPLEMENTATION_V1_BOUNDARY_RULES.md`
  - `gm-lite/docs/2026-03-24/GM_LITE_AUTHORITY_PATH_RULES_V1.md`
- `acceptance_criteria`:
  - `.frozen_seal` 样板成立`
  - `MirrorSealer` 规则与说明完整`
- `hard_constraints`:
  - `不进入完整镜像守护系统`
  - `不进入 auto-send`
  - `不跨库搜索`
- `next_hop`: `review`

## 发给 Execution 的提示词

你是任务 BO4 的执行者 vs--cc1。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 实现 `MirrorSealer` 最小封印规则
- 生成 `.frozen_seal` 样板与 README / exclusions
- 解决“什么是资产 / 如何保护资产”的问题
- 不进入完整镜像守护系统

必须写入：
- `gm-lite/docs/2026-03-24/verification/gm_lite_blueprint_orchestrator_seed_implementation/BO4_execution_report.md`

必须包含：
1. `task_id: BO4`
2. `executor: vs--cc1`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. MirrorSealer / frozen seal / README 结论
5. 最少 `EvidenceRef`

写回成功后下一跳：
- `review`
- 接棒者：`Kior-A`
- 写回目标：
  - `gm-lite/docs/2026-03-24/verification/gm_lite_blueprint_orchestrator_seed_implementation/BO4_review_report.md`

## 发给 Review 的提示词

你是任务 BO4 的审查者 Kior-A。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-24/verification/gm_lite_blueprint_orchestrator_seed_implementation/BO4_review_report.md`

必须包含：
1. `task_id: BO4`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. MirrorSealer / frozen seal / README 审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-24/verification/gm_lite_blueprint_orchestrator_seed_implementation/BO4_compliance_attestation.md`

若给出 `FAIL`，必须升级主控官，不得自行判定结案。

## 发给 Compliance 的提示词

你是任务 BO4 的合规官 Kior-C。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-24/verification/gm_lite_blueprint_orchestrator_seed_implementation/BO4_compliance_attestation.md`

必须包含：
1. `task_id: BO4`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
