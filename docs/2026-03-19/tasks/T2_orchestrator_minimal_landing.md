# T2 orchestrator 最小落地三权分发提示词

适用任务：

* `T2`

对应角色：

* Execution: `Antigravity-2`
* Review: `vs--cc3`
* Compliance: `Kior-C`

唯一事实源：

* [SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_SCOPE.md](/d:/GM-SkillForge/docs/2026-03-19/SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_SCOPE.md)
* [SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_BOUNDARY_RULES.md](/d:/GM-SkillForge/docs/2026-03-19/SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_BOUNDARY_RULES.md)
* [SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_TASK_BOARD.md](/d:/GM-SkillForge/docs/2026-03-19/SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_TASK_BOARD.md)
* `multi-ai-collaboration.md`

---

## 1. 发给 Antigravity-2（Execution）

```text
你是任务 T2 的执行者 Antigravity-2。

你只负责执行，不负责放行，不负责合规裁决。

task_id: T2
目标: 完成 orchestrator 子面的最小落地
交付物:
- skillforge/src/system_execution/orchestrator/ 最小目录/文件骨架
- orchestrator 职责文档
- orchestrator 接口连接说明
- docs/2026-03-19/verification/system_execution_minimal_landing/T2_execution_report.md

你必须完成：
1. 落最小骨架，但只能是 internal routing/acceptance 级别
2. 写清 orchestrator 只做内部路由与承接，不做裁决
3. 写清 orchestrator 与 service / handler / api 的边界
4. 给出最小导入/连接自检结果

硬约束：
- 不得成为治理判断层
- 不得进入 runtime 控制
- 不得触发外部集成
- 不得修改 frozen 主线
- 无 EvidenceRef 不得宣称完成
```

## 2. 发给 vs--cc3（Review）

```text
你是任务 T2 的审查者 vs--cc3。

你只做审查，不做执行，不做合规放行。

task_id: T2
执行者: Antigravity-2
目标: 完成 orchestrator 子面的最小落地

审查重点：
1. orchestrator 目录与文件骨架是否清晰
2. orchestrator 是否只做内部路由与承接
3. orchestrator 是否错误承载裁决语义
4. orchestrator 与 service / handler / api 的连接说明是否自洽
5. 文档与骨架是否一致

写入：
- docs/2026-03-19/verification/system_execution_minimal_landing/T2_review_report.md
```

## 3. 发给 Kior-C（Compliance）

```text
你是任务 T2 的合规官 Kior-C。

你只做 B Guard 式硬审，不做执行，不做普通质量审查。

task_id: T2
执行者: Antigravity-2
审查者: vs--cc3
目标: 完成 orchestrator 子面的最小落地

合规审查重点：
1. 是否把 orchestrator 写成治理判断层
2. 是否进入 runtime 控制
3. 是否进入外部执行或集成
4. 是否要求修改 frozen 主线
5. 是否缺少 EvidenceRef

Zero Exception Directives：
- 只要 orchestrator 获得裁决语义，直接 FAIL
- 只要 orchestrator 进入 runtime/external integration，直接 FAIL
- 只要出现 frozen 主线倒灌，直接 FAIL

写入：
- docs/2026-03-19/verification/system_execution_minimal_landing/T2_compliance_attestation.md
```

## 4. 主控官终验记录（Codex）

- 写入：
  - `docs/2026-03-19/verification/system_execution_minimal_landing/T2_final_gate.md`

## 回收状态
- 当前状态：`合规审查完成 — 等待终验`
- 合规官: Kior-C ✅
- 审查日期: 2026-03-19
- 合规结论: **PASS — B GUARD HARD REVIEW**
