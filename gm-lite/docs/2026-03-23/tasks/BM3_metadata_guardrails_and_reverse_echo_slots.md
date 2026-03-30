# 任务 BM3：Metadata 护栏字段与 Reverse Echo 槽位预埋

## Task Envelope
- `task_id`: `BM3`
- `module`: `gm_bus_manager_seed_implementation_v1`
- `task_type`: `seed_implementation`
- `objective`: `预埋 metadata 护栏字段、intent_trace/history/noun anchors、reverse echo/vote array/validation status 槽位`
- `parallel_group`: `wave_2`
- `depends_on`: `["BM1", "BM2"]`
- `source_of_truth`:
  - `gm-lite/docs/2026-03-23/GM_LITE_BUS_MANAGER_METADATA_GUARDRAILS_V1.md`
  - `gm-lite/docs/2026-03-23/GM_LITE_METADATA_ORIGIN_AND_COMPLETION_MODEL_V1.md`
  - `gm-lite/docs/2026-03-23/GM_LITE_METADATA_ENTRY_FIREWALLS_V1.md`
- `acceptance_criteria`:
  - `护栏字段骨架存在`
  - `reverse echo 槽位存在`
  - `validation_status / intent_trace_id / noun anchors 存在`
- `hard_constraints`:
  - `依赖 BM1 / BM2`
  - `只做 seed implementation`
  - `不进入完整 runtime`
- `escalation_trigger`:
  - `metadata_boundary_conflict`
  - `scope_expansion`
  - `firewall_field_missing`
- `next_hop`: `review`

## 发给 Execution 的提示词

你是任务 BM3 的执行者 Kior-B。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 预埋 metadata 护栏字段
- 预埋 reverse echo / vote_array / purified_intent_payload / explicit_nouns / intent_trace_id / validation_status 等槽位
- 确保后续 BusManager 能承载 RAW/ENRICHED/FROZEN 与 L1/L2/L3 火控语义

必须写入：
- `gm-lite/docs/2026-03-23/verification/gm_bus_manager_seed_implementation/BM3_execution_report.md`

必须包含：
1. `task_id: BM3`
2. `executor: Kior-B`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. metadata 字段骨架清单
5. reverse echo 槽位清单
6. 最少 `EvidenceRef`

写回要求：
- 只写核心结论、增量内容、必要 EvidenceRef
- 不复述整份任务卡
- 不进入 watcher / auto-send / direct-connect
- 不跨库搜索

写回成功后下一跳：
- `review`
- 接棒者：`vs--cc3`
- 写回目标：
  - `gm-lite/docs/2026-03-23/verification/gm_bus_manager_seed_implementation/BM3_review_report.md`

## 发给 Review 的提示词

你是任务 BM3 的审查者 vs--cc3。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-23/verification/gm_bus_manager_seed_implementation/BM3_review_report.md`

必须包含：
1. `task_id: BM3`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. metadata / reverse echo 槽位审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-23/verification/gm_bus_manager_seed_implementation/BM3_compliance_attestation.md`

若给出 `FAIL`，必须升级主控官，不得自行判定结案。

## 发给 Compliance 的提示词

你是任务 BM3 的合规官 Kior-C。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-23/verification/gm_bus_manager_seed_implementation/BM3_compliance_attestation.md`

必须包含：
1. `task_id: BM3`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
