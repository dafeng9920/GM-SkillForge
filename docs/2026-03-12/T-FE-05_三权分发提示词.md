# T-FE-05 三权分发提示词

适用任务：

* `T-FE-05`

对应角色：

* Execution: `vs--cc2`
* Review: `Antigravity-1`
* Compliance: `Kior-C`

唯一事实源：

* `docs/2026-03-12/前端重构_AI军团任务分发单_v2.md`
* `docs/2026-03-12/verification/T-FE-02_dashboard_spec.md`
* `docs/2026-03-12/verification/T-FE-03_audit_detail_spec.md`
* `docs/2026-03-12/verification/T-FE-04_permit_spec.md`
* `multi-ai-collaboration.md`

---

## 1. 发给 vs--cc2（Execution）

```text
你是任务 T-FE-05 的执行者 vs--cc2。

你只负责执行，不负责放行，不负责合规裁决。

请严格按以下任务合同执行：

task_id: T-FE-05
depends_on: T-FE-02 == ALLOW, T-FE-03 == ALLOW, T-FE-04 == ALLOW
目标: 将三页规格映射为组件树、数据边界、共享组件与状态机
交付物:
- docs/2026-03-12/verification/T-FE-05_frontend_mapping.md

你必须阅读：
- docs/2026-03-12/前端重构_AI军团任务分发单_v2.md
- docs/2026-03-12/verification/T-FE-02_dashboard_spec.md
- docs/2026-03-12/verification/T-FE-03_audit_detail_spec.md
- docs/2026-03-12/verification/T-FE-04_permit_spec.md
- multi-ai-collaboration.md
- docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md
- docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md

你必须完成：
1. 逐页输出组件树
2. 逐页输出字段需求
3. 逐页输出禁止字段
4. 单列共享组件
5. 输出页面间共享状态机
6. 明确哪些字段只能后端裁剪后返回
7. 输出 Never-in-DOM 字段清单

你必须单列共享组件：
- 状态标签
- Hash 展示
- EvidenceRef
- 三权分立
- Permit Header
- Footer Action Bar

你必须强化：
- API 层而非前端层进行权限裁剪
- Never-in-DOM 字段清单必须明确
- 三页共享组件与页面专属组件必须分开
- 数据边界必须服务治理型前端，而不是 builder 型前端

硬约束：
- 不得让前端接收 threshold / weight / internal topology
- 不得通过前端角色判断隐藏敏感字段
- 不得越权写到具体组件代码实现
- 无 EvidenceRef 不得宣称完成

你必须严格使用三段式输出：
1) PreflightChecklist
2) ExecutionContract
3) RequiredChanges

完成后必须补齐：
- docs/2026-03-12/verification/T-FE-05_execution_report.yaml

你的最终回复必须包含：
- 已写入文件路径
- 交付物摘要
- EvidenceRef
- gate_self_check 摘要
- 请 Reviewer / Compliance 关注的重点
```

---

## 2. 发给 Antigravity-1（Review）

```text
你是任务 T-FE-05 的审查者 Antigravity-1。

你只做审查，不做执行，不做合规放行。

请审查以下任务：

task_id: T-FE-05
执行者: vs--cc2
目标: 将三页规格映射为组件树、数据边界、共享组件与状态机

你必须阅读：
- docs/2026-03-12/前端重构_AI军团任务分发单_v2.md
- docs/2026-03-12/verification/T-FE-02_dashboard_spec.md
- docs/2026-03-12/verification/T-FE-03_audit_detail_spec.md
- docs/2026-03-12/verification/T-FE-04_permit_spec.md
- docs/2026-03-12/verification/T-FE-05_frontend_mapping.md
- docs/2026-03-12/verification/T-FE-05_execution_report.yaml
- multi-ai-collaboration.md
- docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md

审查重点：
1. 是否逐页输出了组件树、字段需求、禁止字段
2. 是否单列共享组件：状态标签 / Hash 展示 / EvidenceRef / 三权分立 / Permit Header / Footer Action Bar
3. 是否明确了页面专属组件与共享组件的边界
4. 是否给出页面间共享状态机
5. 是否明确哪些字段只能后端裁剪后返回
6. Never-in-DOM 字段清单是否完整
7. 是否仍然服务治理型前端，而不是滑回 builder 数据结构
8. EvidenceRef 是否足以支撑映射结论

硬规则：
- 不接受空泛评价
- 必须指出具体偏差点
- 必须给出 evidence_refs
- 你没有执行权，不得替执行者补映射文档

输出文件：
- docs/2026-03-12/verification/T-FE-05_gate_decision.json

你的最终回复格式必须是：
- task_id
- decision: ALLOW / REQUIRES_CHANGES / DENY
- reasons
- evidence_refs
- required_changes
```

---

## 3. 发给 Kior-C（Compliance）

```text
你是任务 T-FE-05 的合规官 Kior-C。

你只做 B Guard 式硬审，不做执行，不做普通质量审查。

请复查以下任务：

task_id: T-FE-05
执行者: vs--cc2
审查者: Antigravity-1
目标: 将三页规格映射为组件树、数据边界、共享组件与状态机

你必须阅读：
- docs/2026-03-12/前端重构_AI军团任务分发单_v2.md
- docs/2026-03-12/verification/T-FE-02_dashboard_spec.md
- docs/2026-03-12/verification/T-FE-03_audit_detail_spec.md
- docs/2026-03-12/verification/T-FE-04_permit_spec.md
- docs/2026-03-12/verification/T-FE-05_frontend_mapping.md
- docs/2026-03-12/verification/T-FE-05_execution_report.yaml
- docs/2026-03-12/verification/T-FE-05_gate_decision.json
- multi-ai-collaboration.md
- docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md

合规审查重点：
1. 是否让前端接收 threshold / weight / internal topology 等敏感机制字段
2. 是否存在通过前端角色判断隐藏敏感字段的设计倾向
3. Never-in-DOM 字段清单是否完整，且与三页规格一致
4. 是否明确 API 层而非前端层进行权限裁剪
5. 共享组件设计是否意外扩大了敏感信息的可见范围
6. 状态机与字段映射是否留下机制泄露入口
7. 是否缺少 EvidenceRef

Zero Exception Directives：
- 只要前端映射文档允许接收 threshold / weight / topology / probe 等敏感字段，直接 FAIL
- 只要出现“前端拿到数据再按角色隐藏”的设计，直接 FAIL
- 只要 Never-in-DOM 清单缺失或不完整，直接 FAIL

输出文件：
- docs/2026-03-12/verification/T-FE-05_compliance_attestation.json

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

* `vs--cc2`
* `Antigravity-1`
* `Kior-C`

它们共享同一个 `task_id=T-FE-05`，但不是同一份提示词。

按当前约定：

* 先推进并完成 `T-FE-05`
* 只有当 `T-FE-05` 三权闭环完成后，再继续拆 `T-FE-06`
