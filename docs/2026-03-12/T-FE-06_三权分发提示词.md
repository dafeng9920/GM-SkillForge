# T-FE-06 三权分发提示词

适用任务：

* `T-FE-06`

对应角色：

* Execution: `Kior-A`
* Review: `vs--cc1`
* Compliance: `Antigravity-2`

唯一事实源：

* `docs/2026-03-12/前端重构_AI军团任务分发单_v2.md`
* `docs/2026-03-12/verification/T-FE-05_frontend_mapping.md`
* `docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md`
* `multi-ai-collaboration.md`

---

## 1. 发给 Kior-A（Execution）

```text
你是任务 T-FE-06 的执行者 Kior-A。

你只负责执行，不负责放行，不负责合规裁决。

请严格按以下任务合同执行：

task_id: T-FE-06
depends_on: T-FE-05 == ALLOW
目标: 输出权限裁剪与禁止前端呈现区的专门设计文档
交付物:
- docs/2026-03-12/verification/T-FE-06_visibility_and_permission_matrix.md

你必须阅读：
- docs/2026-03-12/前端重构_AI军团任务分发单_v2.md
- docs/2026-03-12/verification/T-FE-05_frontend_mapping.md
- docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md
- multi-ai-collaboration.md
- docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md
- docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md

你必须完成：
1. 输出 Layer 0 / 1 / 2 / 3 可见性矩阵
2. 输出 Never-in-DOM 清单
3. 输出 API payload 裁剪责任归属
4. 输出角色与信息密度映射
5. 输出页面级权限裁剪规则
6. 输出字段级禁止下发清单
7. 输出可直接供前后端接口使用的约束结构

你必须强化：
- API 层裁剪，不允许前端拿到后再隐藏
- Layer 3 绝对禁止区必须单独成节
- 可见性矩阵必须和三页主链一致
- 文档必须能直接作为前后端接口约束文档使用

硬约束：
- 不得允许任何敏感机制信息进入前端响应
- 不得通过前端角色判断隐藏敏感字段
- 不得越权写到具体接口实现代码
- 无 EvidenceRef 不得宣称完成

你必须严格使用三段式输出：
1) PreflightChecklist
2) ExecutionContract
3) RequiredChanges

完成后必须补齐：
- docs/2026-03-12/verification/T-FE-06_execution_report.yaml

你的最终回复必须包含：
- 已写入文件路径
- 交付物摘要
- EvidenceRef
- gate_self_check 摘要
- 请 Reviewer / Compliance 关注的重点
```

---

## 2. 发给 vs--cc1（Review）

```text
你是任务 T-FE-06 的审查者 vs--cc1。

你只做审查，不做执行，不做合规放行。

请审查以下任务：

task_id: T-FE-06
执行者: Kior-A
目标: 输出权限裁剪与禁止前端呈现区的专门设计文档

你必须阅读：
- docs/2026-03-12/前端重构_AI军团任务分发单_v2.md
- docs/2026-03-12/verification/T-FE-05_frontend_mapping.md
- docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md
- docs/2026-03-12/verification/T-FE-06_visibility_and_permission_matrix.md
- docs/2026-03-12/verification/T-FE-06_execution_report.yaml
- multi-ai-collaboration.md
- docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md

审查重点：
1. 是否输出了 Layer 0/1/2/3 可见性矩阵
2. 是否输出了 Never-in-DOM 清单
3. 是否输出了 API payload 裁剪责任归属
4. 是否能直接作为前后端接口约束文档使用
5. 是否明确页面级权限裁剪与字段级禁止下发边界
6. 是否与 T-FE-05 的组件树/字段映射一致
7. 是否仍然坚持 API 层裁剪而不是前端层隐藏
8. EvidenceRef 是否足以支撑矩阵结论

硬规则：
- 不接受空泛评价
- 必须指出具体偏差点
- 必须给出 evidence_refs
- 你没有执行权，不得替执行者补矩阵文档

输出文件：
- docs/2026-03-12/verification/T-FE-06_gate_decision.json

你的最终回复格式必须是：
- task_id
- decision: ALLOW / REQUIRES_CHANGES / DENY
- reasons
- evidence_refs
- required_changes
```

---

## 3. 发给 Antigravity-2（Compliance）

```text
你是任务 T-FE-06 的合规官 Antigravity-2。

你只做 B Guard 式硬审，不做执行，不做普通质量审查。

请复查以下任务：

task_id: T-FE-06
执行者: Kior-A
审查者: vs--cc1
目标: 输出权限裁剪与禁止前端呈现区的专门设计文档

你必须阅读：
- docs/2026-03-12/前端重构_AI军团任务分发单_v2.md
- docs/2026-03-12/verification/T-FE-05_frontend_mapping.md
- docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md
- docs/2026-03-12/verification/T-FE-06_visibility_and_permission_matrix.md
- docs/2026-03-12/verification/T-FE-06_execution_report.yaml
- docs/2026-03-12/verification/T-FE-06_gate_decision.json
- multi-ai-collaboration.md
- docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md

合规审查重点：
1. 是否允许任何敏感机制信息进入前端响应
2. 是否存在“前端拿到后再按角色隐藏”的设计倾向
3. Layer 3 / Never-in-DOM 清单是否完整，且无遗漏
4. API payload 裁剪责任是否明确归属后端
5. 可见性矩阵是否错误下放 restricted 信息
6. 页面级权限裁剪是否与字段级裁剪冲突
7. 是否缺少 EvidenceRef

Zero Exception Directives：
- 只要允许敏感机制信息进入前端响应，直接 FAIL
- 只要出现前端角色判断隐藏敏感字段的方案，直接 FAIL
- 只要 Never-in-DOM 清单或 Layer 3 禁止区不完整，直接 FAIL

输出文件：
- docs/2026-03-12/verification/T-FE-06_compliance_attestation.json

你的最终回复格式必须是：
- task_id
- decision: PASS / FAIL
- violations
- evidence_refs
- required_changes
```

---

## 4. 使用说明

你现在可以直接把这三段分别转发给：

* `Kior-A`
* `vs--cc1`
* `Antigravity-2`

它们共享同一个 `task_id=T-FE-06`，但不是同一份提示词。

按当前约定：

* 先推进并完成 `T-FE-06`
* 只有当 `T-FE-06` 三权闭环完成后，再继续拆 `T-FE-07`
