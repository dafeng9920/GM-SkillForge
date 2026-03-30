# 任务 DA2：Dispatch Assist 输入输出与读源定义

## Task Envelope
- `task_id`: `DA2`
- `module`: `gm_lite_dispatch_assist_preparation_v1`
- `task_type`: `preparation`
- `objective`: `定义 dispatch assist 的最小输入对象、最小输出对象、权威读源与路径判定规则`
- `parallel_group`: `wave_1`
- `depends_on`: `[]`
- `source_of_truth`:
  - `gm-lite/docs/2026-03-23/GM_LITE_DISPATCH_ASSIST_PREPARATION_V1_SCOPE.md`
  - `gm-lite/docs/2026-03-23/GM_LITE_DISPATCH_ASSIST_PREPARATION_V1_BOUNDARY_RULES.md`
  - `gm-lite/docs/2026-03-20/GM_SHARED_TASK_BUS_FROZEN_JUDGMENT_V1_REPORT.md`
  - `gm-lite/docs/2026-03-20/GM_LITE_CONTROLLER_CONSOLE_MINIMAL_IMPLEMENTATION_V1_REPORT.md`
- `acceptance_criteria`:
  - `assist 输入对象定义清晰`
  - `assist 输出对象定义清晰`
  - `权威路径判定规则清晰`
- `hard_constraints`:
  - `只做 preparation`
  - `不进入实现`
  - `不跨库搜索`
- `escalation_trigger`:
  - `authority_path_conflict`
  - `object_boundary_conflict`
  - `scope_expansion`
- `next_hop`: `review`

## 发给 Execution 的提示词

你是任务 DA2 的执行者 Antigravity-2。

你只做 execution，不做 review，不做 compliance。

唯一目标：
- 定义 dispatch assist 的最小输入对象
- 定义 dispatch assist 的最小输出对象
- 定义权威路径、读源和冲突判定规则

必须写入：
- `gm-lite/docs/2026-03-23/verification/gm_lite_dispatch_assist_preparation/DA2_execution_report.md`

必须包含：
1. `task_id: DA2`
2. `executor: Antigravity-2`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. assist 输入对象清单
5. assist 输出对象清单
6. 权威读源 / 路径冲突判定规则
7. 最少 `EvidenceRef`

写回要求：
- 只写核心结论、增量内容、必要 EvidenceRef
- 不复述整份任务卡
- 不进入实现层
- 不跨库搜索

写回成功后下一跳：
- `review`
- 接棒者：`vs--cc1`
- 写回目标：
  - `gm-lite/docs/2026-03-23/verification/gm_lite_dispatch_assist_preparation/DA2_review_report.md`

## 发给 Review 的提示词

你是任务 DA2 的审查者 vs--cc1。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-23/verification/gm_lite_dispatch_assist_preparation/DA2_review_report.md`

必须包含：
1. `task_id: DA2`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. 输入输出与读源边界审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-23/verification/gm_lite_dispatch_assist_preparation/DA2_compliance_attestation.md`

若给出 `FAIL`，必须升级主控官，不得自行判定结案。

## 发给 Compliance 的提示词

你是任务 DA2 的合规官 Kior-C。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-23/verification/gm_lite_dispatch_assist_preparation/DA2_compliance_attestation.md`

必须包含：
1. `task_id: DA2`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
