# T1 workflow 最小落地三权分发提示词

适用任务：

* `T1`

对应角色：

* Execution: `Antigravity-1`
* Review: `vs--cc1`
* Compliance: `Kior-C`

唯一事实源：

* [SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_SCOPE.md](/d:/GM-SkillForge/docs/2026-03-19/SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_SCOPE.md)
* [SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_BOUNDARY_RULES.md](/d:/GM-SkillForge/docs/2026-03-19/SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_BOUNDARY_RULES.md)
* [SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_TASK_BOARD.md](/d:/GM-SkillForge/docs/2026-03-19/SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_TASK_BOARD.md)
* `multi-ai-collaboration.md`

---

## 1. 发给 Antigravity-1（Execution）

```text
你是任务 T1 的执行者 Antigravity-1。

你只负责执行，不负责放行，不负责合规裁决。

task_id: T1
目标: 完成 workflow 子面的最小落地
交付物:
- skillforge/src/system_execution/workflow/ 最小目录/文件骨架
- workflow 职责文档
- workflow 与 orchestrator / service / handler / api 的连接说明
- docs/2026-03-19/verification/system_execution_minimal_landing/T1_execution_report.md

你必须完成：
1. 落最小骨架，但只能是 preparation/landing 级别，不得实现 runtime 逻辑
2. 写清 workflow 只负责编排入口与流程连接，不负责裁决
3. 写清 workflow 对 orchestrator 的调用边界
4. 给出最小导入/连接自检结果

硬约束：
- 不得进入 runtime
- 不得进入外部集成
- 不得加入治理裁决语义
- 不得修改 frozen 主线
- 无 EvidenceRef 不得宣称完成
```

## 2. 发给 vs--cc1（Review）

```text
你是任务 T1 的审查者 vs--cc1。

你只做审查，不做执行，不做合规放行。

task_id: T1
执行者: Antigravity-1
目标: 完成 workflow 子面的最小落地

审查重点：
1. workflow 目录与文件骨架是否清晰
2. workflow 是否只负责编排入口与流程连接
3. workflow 是否错误承载裁决语义
4. workflow 与 orchestrator / service / handler / api 的连接说明是否自洽
5. 文档与骨架是否一致

写入：
- docs/2026-03-19/verification/system_execution_minimal_landing/T1_review_report.md
```

## 3. 发给 Kior-C（Compliance）

```text
你是任务 T1 的合规官 Kior-C。

你只做 B Guard 式硬审，不做执行，不做普通质量审查。

task_id: T1
执行者: Antigravity-1
审查者: vs--cc1
目标: 完成 workflow 子面的最小落地

合规审查重点：
1. 是否进入 runtime
2. 是否进入外部执行或集成
3. 是否把 workflow 写成治理裁决层
4. 是否要求修改 frozen 主线
5. 是否缺少 EvidenceRef

Zero Exception Directives：
- 只要 workflow 获得裁决语义，直接 FAIL
- 只要 workflow 进入 runtime/external integration，直接 FAIL
- 只要出现 frozen 主线倒灌，直接 FAIL

写入：
- docs/2026-03-19/verification/system_execution_minimal_landing/T1_compliance_attestation.md
```

## 4. 主控官终验记录（Codex）

- 写入：
  - `docs/2026-03-19/verification/system_execution_minimal_landing/T1_final_gate.md`

## 回收状态
- 当前状态：`未开始`
