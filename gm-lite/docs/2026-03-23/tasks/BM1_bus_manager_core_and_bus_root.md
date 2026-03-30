# 任务 BM1：BusManager 核心类与 .gm_bus 目录读写骨架

## Task Envelope
- `task_id`: `BM1`
- `module`: `gm_bus_manager_seed_implementation_v1`
- `task_type`: `seed_implementation`
- `objective`: `实现 BusManager 最小核心类，定义 .gm_bus 根目录与最小读写骨架`
- `parallel_group`: `wave_1`
- `depends_on`: `[]`
- `source_of_truth`:
  - `gm-lite/docs/2026-03-23/GM_BUS_MANAGER_SEED_IMPLEMENTATION_V1_SCOPE.md`
  - `gm-lite/docs/2026-03-23/GM_BUS_MANAGER_SEED_IMPLEMENTATION_V1_BOUNDARY_RULES.md`
  - `gm-lite/docs/2026-03-20/GM_SHARED_TASK_BUS_FROZEN_JUDGMENT_V1_REPORT.md`
  - `gm-lite/docs/2026-03-23/GM_LITE_BUS_MANAGER_METADATA_GUARDRAILS_V1.md`
- `acceptance_criteria`:
  - `BusManager 核心类存在`
  - `.gm_bus` 根目录与最小读写骨架存在`
  - `无越界进入 runtime`
- `hard_constraints`:
  - `只做 seed implementation`
  - `不实现 watcher / auto-send / direct-connect`
  - `不跨库搜索`
- `escalation_trigger`:
  - `authority_path_conflict`
  - `scope_expansion`
  - `bus_root_conflict`
- `next_hop`: `review`

## 发给 Execution 的提示词

你是任务 BM1 的执行者 Antigravity-1。

你只做 execution，不做 review，不做 compliance。

权威项目树以 `D:\gm-lite` 为准。

唯一目标：
- 落 `BusManager` 最小核心类
- 定义 `.gm_bus` 根目录与最小读写骨架
- 只做到 seed implementation，不进入 watcher / runtime

必须写入：
- `gm-lite/docs/2026-03-23/verification/gm_bus_manager_seed_implementation/BM1_execution_report.md`

必须包含：
1. `task_id: BM1`
2. `executor: Antigravity-1`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. `BusManager` 核心类与目录骨架结论
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
  - `gm-lite/docs/2026-03-23/verification/gm_bus_manager_seed_implementation/BM1_review_report.md`

## 发给 Review 的提示词

你是任务 BM1 的审查者 Kior-A。
你只做 review，不做 execution，不做 compliance。

必须写入：
- `gm-lite/docs/2026-03-23/verification/gm_bus_manager_seed_implementation/BM1_review_report.md`

必须包含：
1. `task_id: BM1`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. 核心类 / 目录骨架审查重点
5. 最少 `EvidenceRef`

若 review_report 写回成功，默认下一跳：
- `compliance`
- 接棒者：`Kior-C`
- 写回目标：
  - `gm-lite/docs/2026-03-23/verification/gm_bus_manager_seed_implementation/BM1_compliance_attestation.md`

若给出 `FAIL`，必须升级主控官，不得自行判定结案。

## 发给 Compliance 的提示词

你是任务 BM1 的合规官 Kior-C。
你只做 B Guard 式硬审。

必须写入：
- `gm-lite/docs/2026-03-23/verification/gm_bus_manager_seed_implementation/BM1_compliance_attestation.md`

必须包含：
1. `task_id: BM1`
2. `compliance_officer / executor / reviewer`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. Zero Exception Directives 检查结果
5. 最少 `EvidenceRef`

若 compliance_attestation 写回成功，且三件套齐全，则任务进入：
- `GATE_READY`
