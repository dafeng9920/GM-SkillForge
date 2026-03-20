# T4 handler 最小落地三权分发提示词

适用任务：

* `T4`

对应角色：

* Execution: `Kior-B`
* Review: `vs--cc1`
* Compliance: `Kior-C`

唯一事实源：

* [SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_SCOPE.md](/d:/GM-SkillForge/docs/2026-03-19/SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_SCOPE.md)
* [SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_BOUNDARY_RULES.md](/d:/GM-SkillForge/docs/2026-03-19/SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_BOUNDARY_RULES.md)
* [SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_TASK_BOARD.md](/d:/GM-SkillForge/docs/2026-03-19/SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_TASK_BOARD.md)
* `multi-ai-collaboration.md`

---

## 1. 发给 Kior-B（Execution）

```text
你是任务 T4 的执行者 Kior-B。

你只负责执行，不负责放行，不负责合规裁决。

task_id: T4
目标: 完成 handler 子面的最小落地
交付物:
- skillforge/src/system_execution/handler/ 最小目录/文件骨架
- handler 职责文档
- handler 调用边界说明
- docs/2026-03-19/verification/system_execution_minimal_landing/T4_execution_report.md

你必须完成：
1. 落最小骨架，但只能是输入承接与调用转发级别
2. 写清 handler 只做输入承接与调用转发，不做裁决、不做 runtime
3. 写清 handler 与 api / service 的职责差异
4. 给出最小导入/连接自检结果

硬约束：
- 不得触发副作用动作
- 不得进入 runtime 分支控制
- 不得进入外部集成
- 不得修改 frozen 主线
- 无 EvidenceRef 不得宣称完成
```

## 2. 发给 vs--cc1（Review）

```text
你是任务 T4 的审查者 vs--cc1。

你只做审查，不做执行，不做合规放行。

task_id: T4
执行者: Kior-B
目标: 完成 handler 子面的最小落地

审查重点：
1. handler 目录与文件骨架是否清晰
2. handler 是否只做输入承接与调用转发
3. handler 是否错误承载裁决或 runtime 职责
4. handler 与 api / service 的边界是否清晰
5. 文档与骨架是否一致

写入：
- docs/2026-03-19/verification/system_execution_minimal_landing/T4_review_report.md
```

## 3. 发给 Kior-C（Compliance）

```text
你是任务 T4 的合规官 Kior-C。

你只做 B Guard 式硬审，不做执行，不做普通质量审查。

task_id: T4
执行者: Kior-B
审查者: vs--cc1
目标: 完成 handler 子面的最小落地

合规审查重点：
1. 是否触发副作用动作
2. 是否进入 runtime 分支控制
3. 是否进入外部集成
4. 是否要求修改 frozen 主线
5. 是否缺少 EvidenceRef

Zero Exception Directives：
- 只要 handler 触发真实业务动作，直接 FAIL
- 只要 handler 进入 runtime/external integration，直接 FAIL
- 只要出现 frozen 主线倒灌，直接 FAIL

写入：
- docs/2026-03-19/verification/system_execution_minimal_landing/T4_compliance_attestation.md
```

## 4. 主控官终验记录（Codex）

- 写入：
  - `docs/2026-03-19/verification/system_execution_minimal_landing/T4_final_gate.md`

## 回收状态
- 当前状态：`路径修正完成 — 等待审查`
- 执行者: Kior-B ✅
- 执行日期: 2026-03-19
- 路径修正: **COMPLETED**
- 正确路径: `skillforge/src/system_execution/handler/`
- 原路径: `skillforge/src/system_execution_preparation/handler/`
