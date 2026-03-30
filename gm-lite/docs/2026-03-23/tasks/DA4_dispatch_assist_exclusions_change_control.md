# 任务 DA4：Dispatch Assist Exclusions / Change Control 定义

## Task Envelope
- `task_id`: `DA4`
- `module`: `gm_lite_dispatch_assist_preparation_v1`
- `task_type`: `preparation`
- `objective`: `冻结 dispatch assist 的禁止项、升级条件与 change control，防止其膨胀为自动发送或 runtime 系统`
- `parallel_group`: `wave_3`
- `depends_on`: `["DA1", "DA2", "DA3"]`
- `source_of_truth`:
  - `gm-lite/docs/2026-03-23/GM_LITE_DISPATCH_ASSIST_PREPARATION_V1_SCOPE.md`
  - `gm-lite/docs/2026-03-23/GM_LITE_DISPATCH_ASSIST_PREPARATION_V1_BOUNDARY_RULES.md`
  - `gm-lite/docs/2026-03-23/GM_LITE_DISPATCH_ASSIST_PREPARATION_V1_CHANGE_CONTROL_RULES.md`
- `acceptance_criteria`:
  - `禁止项冻结`
  - `升级条件冻结`
  - `不与 controller console / runtime 混职`
- `hard_constraints`:
  - `依赖 DA1 / DA2 / DA3`
  - `只做 preparation`
  - `不进入实现`
- `escalation_trigger`:
  - `boundary_expansion`
  - `runtime_leakage`
  - `change_control_conflict`
- `next_hop`: `review`

## 发给 Execution 的提示词

你是任务 DA4 的执行者 vs--cc1。

你只做 execution，不做 review，不做 compliance。

唯一目标：
- 冻结 dispatch assist 的禁止项
- 冻结升级条件
- 冻结 change control
- 明确它不会膨胀成自动发送或 runtime 系统

必须写入：
- `gm-lite/docs/2026-03-23/verification/gm_lite_dispatch_assist_preparation/DA4_execution_report.md`

必须包含：
1. `task_id: DA4`
2. `executor: vs--cc1`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. exclusions / change control 核心结论
5. 禁止项与升级条件清单
6. 最少 `EvidenceRef`

写回要求：
- 只写核心结论、增量内容、必要 EvidenceRef
- 不复述整份任务卡
- 不进入实现层
- 不跨库搜索

写回成功后下一跳：
- `review`
- 接棒者：`Kior-A`
- 写回目标：
  - `gm-lite/docs/2026-03-23/verification/gm_lite_dispatch_assist_preparation/DA4_review_report.md`

## 发给 Review 的提示词

你是任务 DA4 的审查者 Kior-A。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-23/verification/gm_lite_dispatch_assist_preparation/DA4_review_report.md`

必须包含：
1. `task_id: DA4`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. exclusions / change control 审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-23/verification/gm_lite_dispatch_assist_preparation/DA4_compliance_attestation.md`

若给出 `FAIL`，必须升级主控官，不得自行判定结案。

## 发给 Compliance 的提示词

你是任务 DA4 的合规官 Kior-C。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-23/verification/gm_lite_dispatch_assist_preparation/DA4_compliance_attestation.md`

必须包含：
1. `task_id: DA4`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
