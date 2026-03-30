# 任务 DI3：Dispatch Packet Builder 与 BusManager 最小对接

## Task Envelope
- `task_id`: `DI3`
- `module`: `gm_lite_dispatch_assist_minimal_implementation_v1`
- `task_type`: `minimal_implementation`
- `objective`: `实现 dispatch packet builder 并与 BusManager 做最小对接`
- `parallel_group`: `wave_2`
- `depends_on`: `["DI1", "DI2"]`
- `source_of_truth`:
  - `gm-lite/docs/2026-03-24/GM_LITE_DISPATCH_ASSIST_MINIMAL_IMPLEMENTATION_V1_SCOPE.md`
  - `gm-lite/docs/2026-03-24/GM_LITE_DISPATCH_ASSIST_MINIMAL_IMPLEMENTATION_V1_BOUNDARY_RULES.md`
  - `gm-lite/docs/2026-03-23/GM_BUS_MANAGER_SEED_IMPLEMENTATION_V1_REPORT.md`
- `acceptance_criteria`:
  - `dispatch packet builder 可用`
  - `与 BusManager 最小对接成立`
- `hard_constraints`:
  - `依赖 DI1 / DI2`
  - `不进入 auto-send / runtime`
  - `不跨库搜索`
- `escalation_trigger`:
  - `bus_interface_conflict`
  - `packet_schema_conflict`
  - `scope_expansion`
- `next_hop`: `review`

## 发给 Execution 的提示词

你是任务 DI3 的执行者 Kior-B。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 实现 dispatch packet builder
- 与 BusManager 做最小对接
- 不进入 auto-send / runtime

必须写入：
- `gm-lite/docs/2026-03-24/verification/gm_lite_dispatch_assist_minimal_implementation/DI3_execution_report.md`

必须包含：
1. `task_id: DI3`
2. `executor: Kior-B`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. packet builder / BusManager 对接结论
5. 最少 `EvidenceRef`

写回要求：
- 只写核心结论、增量内容、必要 EvidenceRef
- 不复述整份任务卡
- 不进入 auto-send / direct-connect / watcher
- 不跨库搜索

写回成功后下一跳：
- `review`
- 接棒者：`vs--cc3`
- 写回目标：
  - `gm-lite/docs/2026-03-24/verification/gm_lite_dispatch_assist_minimal_implementation/DI3_review_report.md`

## 发给 Review 的提示词

你是任务 DI3 的审查者 vs--cc3。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-24/verification/gm_lite_dispatch_assist_minimal_implementation/DI3_review_report.md`

必须包含：
1. `task_id: DI3`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. packet builder / BusManager 对接审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-24/verification/gm_lite_dispatch_assist_minimal_implementation/DI3_compliance_attestation.md`

若给出 `FAIL`，必须升级主控官，不得自行判定结案。

## 发给 Compliance 的提示词

你是任务 DI3 的合规官 Kior-C。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-24/verification/gm_lite_dispatch_assist_minimal_implementation/DI3_compliance_attestation.md`

必须包含：
1. `task_id: DI3`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
