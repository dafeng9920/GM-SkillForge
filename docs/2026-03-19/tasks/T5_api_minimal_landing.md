# T5 api 最小落地三权分发提示词

适用任务：

* `T5`

对应角色：

* Execution: `vs--cc3`
* Review: `Kior-A`
* Compliance: `Kior-C`

唯一事实源：

* [SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_SCOPE.md](/d:/GM-SkillForge/docs/2026-03-19/SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_SCOPE.md)
* [SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_BOUNDARY_RULES.md](/d:/GM-SkillForge/docs/2026-03-19/SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_BOUNDARY_RULES.md)
* [SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_TASK_BOARD.md](/d:/GM-SkillForge/docs/2026-03-19/SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_TASK_BOARD.md)
* `multi-ai-collaboration.md`

---

## 1. 发给 vs--cc3（Execution）

```text
你是任务 T5 的执行者 vs--cc3。

你只负责执行，不负责放行，不负责合规裁决。

task_id: T5
目标: 完成 api 子面的最小落地
交付物:
- skillforge/src/system_execution/api/ 最小目录/文件骨架
- api 职责文档
- api 与 handler / service 的连接说明
- docs/2026-03-19/verification/system_execution_minimal_landing/T5_execution_report.md

你必须完成：
1. 落最小骨架，但只能是最小接口层承接级别
2. 写清 api 只做最小接口层承接，不做真实对外集成
3. 写清 api 与 handler / service 的连接说明
4. 给出最小导入/连接自检结果

硬约束：
- 不得暴露真实外部协议
- 不得进入外部集成
- 不得进入 runtime
- 不得修改 frozen 主线
- 无 EvidenceRef 不得宣称完成
```

## 2. 发给 Kior-A（Review）

```text
你是任务 T5 的审查者 Kior-A。

你只做审查，不做执行，不做合规放行。

task_id: T5
执行者: vs--cc3
目标: 完成 api 子面的最小落地

审查重点：
1. api 目录与文件骨架是否清晰
2. api 是否只做最小接口层承接
3. api 是否错误承载真实对外集成职责
4. api 与 handler / service 的连接说明是否清晰
5. 文档与骨架是否一致

写入：
- docs/2026-03-19/verification/system_execution_minimal_landing/T5_review_report.md
```

## 3. 发给 Kior-C（Compliance）

```text
你是任务 T5 的合规官 Kior-C。

你只做 B Guard 式硬审，不做执行，不做普通质量审查。

task_id: T5
执行者: vs--cc3
审查者: Kior-A
目标: 完成 api 子面的最小落地

合规审查重点：
1. 是否暴露真实外部协议
2. 是否进入外部集成
3. 是否进入 runtime
4. 是否要求修改 frozen 主线
5. 是否缺少 EvidenceRef

Zero Exception Directives：
- 只要 api 成为真实对外集成层，直接 FAIL
- 只要 api 进入 runtime/external integration，直接 FAIL
- 只要出现 frozen 主线倒灌，直接 FAIL

写入：
- docs/2026-03-19/verification/system_execution_minimal_landing/T5_compliance_attestation.md
```

## 4. 主控官终验记录（Codex）

- 写入：
  - `docs/2026-03-19/verification/system_execution_minimal_landing/T5_final_gate.md`

## 回收状态
- 当前状态：`未开始`
