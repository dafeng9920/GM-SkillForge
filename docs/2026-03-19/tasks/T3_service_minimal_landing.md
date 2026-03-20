# T3 service 最小落地三权分发提示词

适用任务：

* `T3`

对应角色：

* Execution: `vs--cc2`
* Review: `Kior-A`
* Compliance: `Kior-C`

唯一事实源：

* [SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_SCOPE.md](/d:/GM-SkillForge/docs/2026-03-19/SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_SCOPE.md)
* [SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_BOUNDARY_RULES.md](/d:/GM-SkillForge/docs/2026-03-19/SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_BOUNDARY_RULES.md)
* [SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_TASK_BOARD.md](/d:/GM-SkillForge/docs/2026-03-19/SYSTEM_EXECUTION_MINIMAL_LANDING_MODULE_V1_TASK_BOARD.md)
* `multi-ai-collaboration.md`

---

## 1. 发给 vs--cc2（Execution）

```text
你是任务 T3 的执行者 vs--cc2。

你只负责执行，不负责放行，不负责合规裁决。

task_id: T3
目标: 完成 service 子面的最小落地
交付物:
- skillforge/src/system_execution/service/ 最小目录/文件骨架
- service 职责文档
- service 与 handler / orchestrator 的关系说明
- docs/2026-03-19/verification/system_execution_minimal_landing/T3_execution_report.md

你必须完成：
1. 落最小骨架，但只能是内部服务承接级别
2. 写清 service 只做内部服务层承接，不做 handler/api/runtime 混合职责
3. 写清 service 对 frozen 主线的只读使用方式
4. 给出最小导入/连接自检结果

硬约束：
- 不得实现真实业务逻辑
- 不得外部调用
- 不得进入 runtime
- 不得修改 frozen 主线
- 无 EvidenceRef 不得宣称完成
```

## 2. 发给 Kior-A（Review）

```text
你是任务 T3 的审查者 Kior-A。

你只做审查，不做执行，不做合规放行。

task_id: T3
执行者: vs--cc2
目标: 完成 service 子面的最小落地

审查重点：
1. service 目录与文件骨架是否清晰
2. service 是否只做内部服务层承接
3. service 是否错误承载 handler/api/runtime 混合职责
4. service 对 frozen 主线的只读使用方式是否清晰
5. 文档与骨架是否一致

写入：
- docs/2026-03-19/verification/system_execution_minimal_landing/T3_review_report.md
```

## 3. 发给 Kior-C（Compliance）

```text
你是任务 T3 的合规官 Kior-C。

你只做 B Guard 式硬审，不做执行，不做普通质量审查。

task_id: T3
执行者: vs--cc2
审查者: Kior-A
目标: 完成 service 子面的最小落地

合规审查重点：
1. 是否实现真实业务逻辑
2. 是否发起外部调用
3. 是否进入 runtime
4. 是否要求修改 frozen 主线
5. 是否缺少 EvidenceRef

Zero Exception Directives：
- 只要 service 进入真实业务执行，直接 FAIL
- 只要 service 进入 runtime/external integration，直接 FAIL
- 只要出现 frozen 主线倒灌，直接 FAIL

写入：
- docs/2026-03-19/verification/system_execution_minimal_landing/T3_compliance_attestation.md
```

## 4. 主控官终验记录（Codex）

- 写入：
  - `docs/2026-03-19/verification/system_execution_minimal_landing/T3_final_gate.md`

## 回收状态
- 当前状态：`未开始`
