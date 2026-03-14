# DEV-03 三权分发提示词

适用任务：

* `DEV-03`

对应角色：

* Execution: `Kior-B`
* Review: `Antigravity-2`
* Compliance: `vs--cc3`

唯一事实源：

* `docs/2026-03-12/前端实现波次任务分发单_v1.md`
* `docs/2026-03-12/verification/DEV-01_gate_decision.json`
* `docs/2026-03-12/verification/DEV-01_compliance_attestation.json`
* `docs/2026-03-12/verification/T-FE-04_permit_spec.md`
* `docs/2026-03-12/verification/T-FE-05_frontend_mapping.md`
* `docs/2026-03-12/verification/T-FE-06_visibility_and_permission_matrix.md`
* `docs/2026-03-12/verification/T-FE-07_copy_and_cta_spec.md`
* `ui/app/src/app/router.tsx`
* `multi-ai-collaboration.md`

---

## 1. 发给 Kior-B（Execution）

```text
你是任务 DEV-03 的执行者 Kior-B。

你只负责执行，不负责放行，不负责合规裁决。

请严格按以下任务合同执行：

task_id: DEV-03
depends_on: DEV-01 == ALLOW and DEV-01 compliance == PASS
目标: 实现 Permit 页面壳层与凭证模块
交付物:
- ui/app/src/pages/governance/PermitPage.tsx
- ui/app/src/pages/governance/PermitPage.module.css

你必须阅读：
- docs/2026-03-12/前端实现波次任务分发单_v1.md
- docs/2026-03-12/verification/DEV-01_gate_decision.json
- docs/2026-03-12/verification/DEV-01_compliance_attestation.json
- docs/2026-03-12/verification/T-FE-04_permit_spec.md
- docs/2026-03-12/verification/T-FE-05_frontend_mapping.md
- docs/2026-03-12/verification/T-FE-06_visibility_and_permission_matrix.md
- docs/2026-03-12/verification/T-FE-07_copy_and_cta_spec.md
- ui/app/src/app/router.tsx
- multi-ai-collaboration.md
- docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md
- docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md

你必须完成：
1. 实现 Permit Header
2. 实现 Core Decision Block
3. 实现 Release Scope
4. 实现 Conditions
5. 实现 Linked Basis / Audit Basis
6. 实现 Lifecycle
7. 实现 Compliance Signature
8. 实现 Residual Risk

你必须强化：
- Audit pass is not release approval. Permit is.
- revision / contract_hash / decision_hash / audit basis 必须绑定
- Permit 页面气质是正式放行凭证，不是 success page
- 放行范围、附加条件、失效触发器必须有明确视觉落点

硬约束：
- 不得把 Permit 页面做成大绿勾 success page
- 不得出现与 revision / contract_hash / decision_hash 解耦的 Permit 展示
- 不得弱化 Scope / Conditions / Lifecycle / Signature / Residual Risk
- 不得越权改动 Audit Detail / Dashboard 页面实现
- 无 EvidenceRef 不得宣称完成

你必须严格使用三段式输出：
1) PreflightChecklist
2) ExecutionContract
3) RequiredChanges

完成后必须补齐：
- docs/2026-03-12/verification/DEV-03_execution_report.yaml

你的最终回复必须包含：
- 已修改文件路径
- 交付物摘要
- EvidenceRef
- gate_self_check 摘要
- 请 Reviewer / Compliance 关注的重点
```

---

## 2. 发给 Antigravity-2（Review）

```text
你是任务 DEV-03 的审查者 Antigravity-2。

你只做审查，不做执行，不做合规放行。

请审查以下任务：

task_id: DEV-03
执行者: Kior-B
目标: 实现 Permit 页面壳层与凭证模块

你必须阅读：
- docs/2026-03-12/前端实现波次任务分发单_v1.md
- docs/2026-03-12/verification/DEV-01_gate_decision.json
- docs/2026-03-12/verification/DEV-01_compliance_attestation.json
- docs/2026-03-12/verification/T-FE-04_permit_spec.md
- docs/2026-03-12/verification/T-FE-05_frontend_mapping.md
- docs/2026-03-12/verification/T-FE-07_copy_and_cta_spec.md
- ui/app/src/pages/governance/PermitPage.tsx
- ui/app/src/pages/governance/PermitPage.module.css
- docs/2026-03-12/verification/DEV-03_execution_report.yaml
- multi-ai-collaboration.md
- docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md

审查重点：
1. 是否实现了 Permit Header / Core Decision Block / Scope / Conditions / Linked Basis / Lifecycle / Signature / Residual Risk
2. 是否显式强化 Audit pass is not release approval. Permit is.
3. 是否保留 revision / contract_hash / decision_hash / audit basis 绑定
4. 是否体现放行范围、附加条件、失效触发器
5. 是否体现生命周期与签发角色
6. 页面是否保持正式凭证气质，而不是普通状态页
7. 是否没有越权侵入 Audit Detail / Dashboard 范围
8. EvidenceRef 是否足以支撑本次页面实现结论

硬规则：
- 不接受空泛评价
- 必须指出具体偏差点
- 必须给出 evidence_refs
- 你没有执行权，不得替执行者补代码

输出文件：
- docs/2026-03-12/verification/DEV-03_gate_decision.json

你的最终回复格式必须是：
- task_id
- decision: ALLOW / REQUIRES_CHANGES / DENY
- reasons
- evidence_refs
- required_changes
```

---

## 3. 发给 vs--cc3（Compliance）

```text
你是任务 DEV-03 的合规官 vs--cc3。

你只做 B Guard 式硬审，不做执行，不做普通质量审查。

请复查以下任务：

task_id: DEV-03
执行者: Kior-B
审查者: Antigravity-2
目标: 实现 Permit 页面壳层与凭证模块

你必须阅读：
- docs/2026-03-12/前端实现波次任务分发单_v1.md
- docs/2026-03-12/verification/DEV-01_gate_decision.json
- docs/2026-03-12/verification/DEV-01_compliance_attestation.json
- docs/2026-03-12/verification/T-FE-04_permit_spec.md
- docs/2026-03-12/verification/T-FE-05_frontend_mapping.md
- docs/2026-03-12/verification/T-FE-06_visibility_and_permission_matrix.md
- docs/2026-03-12/verification/T-FE-07_copy_and_cta_spec.md
- ui/app/src/pages/governance/PermitPage.tsx
- ui/app/src/pages/governance/PermitPage.module.css
- docs/2026-03-12/verification/DEV-03_execution_report.yaml
- docs/2026-03-12/verification/DEV-03_gate_decision.json
- multi-ai-collaboration.md
- docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md

合规审查重点：
1. 是否把 Permit 页面做成 success page 或弱状态页
2. 是否出现 Audit pass 与 Permit granted 混淆
3. 是否出现 Permit 与 revision / contract_hash / decision_hash / audit basis 解耦
4. 是否缺少 Scope / Conditions / Lifecycle / Signature / Residual Risk 中的关键约束
5. 是否存在会被误读为“永久自动放行”的结构或文案
6. 是否暴露 Layer 3 / Never-in-DOM 信息
7. 是否缺少 EvidenceRef

Zero Exception Directives：
- 只要出现 Audit pass = Permit granted 的语言或结构倾向，直接 FAIL
- 只要出现 Permit 与 revision/hash/basis 解耦，直接 FAIL
- 只要缺少范围、条件、生命周期、失效触发器中的关键约束，直接 FAIL

输出文件：
- docs/2026-03-12/verification/DEV-03_compliance_attestation.json

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

* `Kior-B`
* `Antigravity-2`
* `vs--cc3`

它们共享同一个 `task_id=DEV-03`，但不是同一份提示词。

按当前约定：

* 先推进并完成 `DEV-03`
* 只有当 `DEV-03` 三权闭环完成后，再继续拆 `DEV-04`
