# 任务 DA1：Dispatch Assist 职责边界定义

## Task Envelope
- `task_id`: `DA1`
- `module`: `gm_lite_dispatch_assist_preparation_v1`
- `task_type`: `preparation`
- `objective`: `定义 dispatch assist 的职责边界、与 controller console/.gm_bus/verification 的关系，以及 Light 版不负责的内容`
- `parallel_group`: `wave_1`
- `depends_on`: `[]`
- `source_of_truth`:
  - `gm-lite/docs/2026-03-23/GM_LITE_DISPATCH_ASSIST_PREPARATION_V1_SCOPE.md`
  - `gm-lite/docs/2026-03-23/GM_LITE_DISPATCH_ASSIST_PREPARATION_V1_BOUNDARY_RULES.md`
  - `gm-lite/docs/2026-03-20/GM_SHARED_TASK_BUS_FROZEN_JUDGMENT_V1_REPORT.md`
  - `gm-lite/docs/2026-03-20/GM_LITE_CONTROLLER_CONSOLE_MINIMAL_IMPLEMENTATION_V1_REPORT.md`
- `acceptance_criteria`:
  - `dispatch assist 职责边界清晰`
  - `明确与 .gm_bus / controller console / verification 的关系`
  - `明确不负责自动发送 / direct-connect / timeout runtime`
- `hard_constraints`:
  - `只做 preparation`
  - `不进入实现`
  - `不改 shared task bus frozen 事实`
  - `不跨库搜索`
- `escalation_trigger`:
  - `boundary_conflict`
  - `scope_expansion`
  - `authority_path_conflict`
- `next_hop`: `review`

## 发给 Execution 的提示词

你是任务 DA1 的执行者 Antigravity-1。

你只做 execution，不做 review，不做 compliance。

唯一目标：
- 定义 `dispatch assist` 在 GM-LITE Light 中的职责边界
- 说明它与 `.gm_bus`、controller console、verification 的关系
- 明确它不承担什么

必须写入：
- `gm-lite/docs/2026-03-23/verification/gm_lite_dispatch_assist_preparation/DA1_execution_report.md`

必须包含：
1. `task_id: DA1`
2. `executor: Antigravity-1`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. dispatch assist 职责边界核心结论
5. 与 `.gm_bus` / controller console / verification 的关系
6. 不在本轮承担的内容
7. 最少 `EvidenceRef`

写回要求：
- 只写核心结论、增量内容、必要 EvidenceRef
- 不复述整份任务卡
- 不跨库搜索
- 不进入实现层

写回成功后下一跳：
- `review`
- 接棒者：`Kior-A`
- 写回目标：
  - `gm-lite/docs/2026-03-23/verification/gm_lite_dispatch_assist_preparation/DA1_review_report.md`

## 发给 Review 的提示词

你是任务 DA1 的审查者 Kior-A。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-23/verification/gm_lite_dispatch_assist_preparation/DA1_review_report.md`

必须包含：
1. `task_id: DA1`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. 职责边界审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-23/verification/gm_lite_dispatch_assist_preparation/DA1_compliance_attestation.md`

若给出 `FAIL`，必须升级主控官，不得自行判定结案。

## 发给 Compliance 的提示词

你是任务 DA1 的合规官 Kior-C。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-23/verification/gm_lite_dispatch_assist_preparation/DA1_compliance_attestation.md`

必须包含：
1. `task_id: DA1`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
