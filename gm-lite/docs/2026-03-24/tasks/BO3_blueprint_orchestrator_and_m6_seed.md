# 任务 BO3：BlueprintOrchestrator 与 M6 最小意图捕获样板

## Task Envelope
- `task_id`: `BO3`
- `module`: `gm_lite_blueprint_orchestrator_seed_implementation_v1`
- `task_type`: `seed_implementation`
- `objective`: `实现 BlueprintOrchestrator 与 M6 最小 noun anchor / checkpoint 样板`
- `parallel_group`: `wave_2`
- `depends_on`: `["BO1", "BO2"]`
- `source_of_truth`:
  - `gm-lite/docs/2026-03-24/GM_LITE_BLUEPRINT_ORCHESTRATOR_SEED_IMPLEMENTATION_V1_SCOPE.md`
  - `gm-lite/docs/2026-03-24/GM_LITE_BLUEPRINT_ORCHESTRATOR_SEED_IMPLEMENTATION_V1_BOUNDARY_RULES.md`
  - `gm-lite/docs/2026-03-23/GM_LITE_METADATA_ENTRY_FIREWALLS_V1.md`
- `acceptance_criteria`:
  - `M6 最小样板成立`
  - `控制台可输出最小 gate 进度`
- `hard_constraints`:
  - `不进入完整 M7-M9`
  - `不进入 auto-send`
  - `不跨库搜索`
- `next_hop`: `review`

## 发给 Execution 的提示词

你是任务 BO3 的执行者 Kior-B。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 实现 `BlueprintOrchestrator` 最小骨架
- 实现 `M6` 最小意图捕获 / noun anchors locked 样板
- 控制台至少可输出一轮最小 gate 打勾结果
- 预埋最小 redline 熔断位
- 不进入完整 M7-M9

必须写入：
- `gm-lite/docs/2026-03-24/verification/gm_lite_blueprint_orchestrator_seed_implementation/BO3_execution_report.md`

必须包含：
1. `task_id: BO3`
2. `executor: Kior-B`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. BlueprintOrchestrator / M6 样板实现结论
5. 最少 `EvidenceRef`

写回成功后下一跳：
- `review`
- 接棒者：`vs--cc3`
- 写回目标：
  - `gm-lite/docs/2026-03-24/verification/gm_lite_blueprint_orchestrator_seed_implementation/BO3_review_report.md`

## 发给 Review 的提示词

你是任务 BO3 的审查者 vs--cc3。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-24/verification/gm_lite_blueprint_orchestrator_seed_implementation/BO3_review_report.md`

必须包含：
1. `task_id: BO3`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. BlueprintOrchestrator / M6 审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-24/verification/gm_lite_blueprint_orchestrator_seed_implementation/BO3_compliance_attestation.md`

若给出 `FAIL`，必须升级主控官，不得自行判定结案。

## 发给 Compliance 的提示词

你是任务 BO3 的合规官 Kior-C。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-24/verification/gm_lite_blueprint_orchestrator_seed_implementation/BO3_compliance_attestation.md`

必须包含：
1. `task_id: BO3`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
