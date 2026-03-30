# 任务 SV1：Happy Path 样板链验证

## Task Envelope
- `task_id`: `SV1`
- `module`: `gm_lite_sample_flow_validation_v1`
- `task_type`: `validation`
- `objective`: `验证一条最小 happy path 样板链`
- `parallel_group`: `wave_1`
- `depends_on`: `[]`
- `source_of_truth`:
  - `gm-lite/docs/2026-03-24/GM_LITE_SAMPLE_FLOW_VALIDATION_V1_SCOPE.md`
  - `gm-lite/docs/2026-03-24/GM_LITE_SAMPLE_FLOW_VALIDATION_V1_BOUNDARY_RULES.md`
  - `gm-lite/docs/2026-03-24/GM_LITE_DISPATCH_ASSIST_MINIMAL_IMPLEMENTATION_V1_REPORT.md`
- `acceptance_criteria`:
  - `happy path 可回放`
  - `RAW -> ENRICHED -> FROZEN -> GATE_READY` 样板成立
- `hard_constraints`:
  - `不进入 watcher`
  - `不进入 auto-send`
  - `不跨库搜索`
- `next_hop`: `review`

## 发给 Execution 的提示词

你是任务 SV1 的执行者 Antigravity-1。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 验证一条最小 happy path 样板链
- 用样板证明 `RAW -> ENRICHED -> FROZEN -> GATE_READY`
- 不进入 watcher / auto-send / runtime

必须写入：
- `gm-lite/docs/2026-03-24/verification/gm_lite_sample_flow_validation/SV1_execution_report.md`

必须包含：
1. `task_id: SV1`
2. `executor: Antigravity-1`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. happy path 样板链验证结论
5. 最少 `EvidenceRef`

写回成功后下一跳：
- `review`
- 接棒者：`Kior-A`
- 写回目标：
  - `gm-lite/docs/2026-03-24/verification/gm_lite_sample_flow_validation/SV1_review_report.md`

## 发给 Review 的提示词

你是任务 SV1 的审查者 Kior-A。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-24/verification/gm_lite_sample_flow_validation/SV1_review_report.md`

必须包含：
1. `task_id: SV1`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. happy path 样板链审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-24/verification/gm_lite_sample_flow_validation/SV1_compliance_attestation.md`

若给出 `FAIL`，必须升级主控官，不得自行判定结案。

## 发给 Compliance 的提示词

你是任务 SV1 的合规官 Kior-C。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-24/verification/gm_lite_sample_flow_validation/SV1_compliance_attestation.md`

必须包含：
1. `task_id: SV1`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
