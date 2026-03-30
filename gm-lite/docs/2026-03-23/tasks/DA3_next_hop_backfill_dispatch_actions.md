# 任务 DA3：Next Hop / Backfill / Dispatch Assist 动作与视图定义

## Task Envelope
- `task_id`: `DA3`
- `module`: `gm_lite_dispatch_assist_preparation_v1`
- `task_type`: `preparation`
- `objective`: `定义 next hop assist、missing piece backfill assist、dispatch packet build assist 的最小动作清单与主控视图关系`
- `parallel_group`: `wave_2`
- `depends_on`: `["DA1", "DA2"]`
- `source_of_truth`:
  - `gm-lite/docs/2026-03-23/GM_LITE_DISPATCH_ASSIST_PREPARATION_V1_SCOPE.md`
  - `gm-lite/docs/2026-03-23/GM_LITE_DISPATCH_ASSIST_PREPARATION_V1_BOUNDARY_RULES.md`
  - `gm-lite/docs/2026-03-20/GM_LITE_CONTROLLER_CONSOLE_MINIMAL_IMPLEMENTATION_V1_REPORT.md`
- `acceptance_criteria`:
  - `assist 动作清单清晰`
  - `next hop / missing piece / dispatch packet 的最小输出定义清晰`
  - `与 controller console 视图关系清晰`
- `hard_constraints`:
  - `依赖 DA1 / DA2`
  - `只做 preparation`
  - `不进入实现`
- `escalation_trigger`:
  - `dependency_not_ready`
  - `scope_expansion`
  - `action_boundary_conflict`
- `next_hop`: `review`

## 发给 Execution 的提示词

你是任务 DA3 的执行者 Kior-B。

你只做 execution，不做 review，不做 compliance。

唯一目标：
- 定义 dispatch assist 的三类动作：
  - `next_hop_assist`
  - `missing_piece_backfill_assist`
  - `dispatch_packet_build_assist`
- 定义这些动作与 controller console 主控视图的关系

必须写入：
- `gm-lite/docs/2026-03-23/verification/gm_lite_dispatch_assist_preparation/DA3_execution_report.md`

必须包含：
1. `task_id: DA3`
2. `executor: Kior-B`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. assist 动作清单
5. 每类 assist 的最小输出对象
6. 与 controller console 视图关系
7. 最少 `EvidenceRef`

写回要求：
- 只写核心结论、增量内容、必要 EvidenceRef
- 不复述整份任务卡
- 不进入实现层
- 不跨库搜索

写回成功后下一跳：
- `review`
- 接棒者：`vs--cc3`
- 写回目标：
  - `gm-lite/docs/2026-03-23/verification/gm_lite_dispatch_assist_preparation/DA3_review_report.md`

## 发给 Review 的提示词

你是任务 DA3 的审查者 vs--cc3。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-23/verification/gm_lite_dispatch_assist_preparation/DA3_review_report.md`

必须包含：
1. `task_id: DA3`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. next hop / backfill / dispatch packet 动作审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-23/verification/gm_lite_dispatch_assist_preparation/DA3_compliance_attestation.md`

若给出 `FAIL`，必须升级主控官，不得自行判定结案。

## 发给 Compliance 的提示词

你是任务 DA3 的合规官 Kior-C。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-23/verification/gm_lite_dispatch_assist_preparation/DA3_compliance_attestation.md`

必须包含：
1. `task_id: DA3`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
