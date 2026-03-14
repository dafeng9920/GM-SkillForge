# T-FE-04 三权分发提示词

适用任务：

* `T-FE-04`

对应角色：

* Execution: `Kior-B`
* Review: `Antigravity-2`
* Compliance: `vs--cc3`

唯一事实源：

* `docs/2026-03-12/前端重构_AI军团任务分发单_v2.md`
* `docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md`
* `docs/2026-03-12/“治理与放行中枢”的前端设计.md`
* `docs/2026-03-12/verification/T-FE-01_ia_spec.md`
* `multi-ai-collaboration.md`

---

## 1. 发给 Kior-B（Execution）

```text
你是任务 T-FE-04 的执行者 Kior-B。

你只负责执行，不负责放行，不负责合规裁决。

请严格按以下任务合同执行：

task_id: T-FE-04
depends_on: T-FE-01 == ALLOW
目标: 输出 Permit 页面规格书，确保其是正式放行凭证而不是 success page
交付物:
- docs/2026-03-12/verification/T-FE-04_permit_spec.md

你必须阅读：
- docs/2026-03-12/前端重构_AI军团任务分发单_v2.md
- docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md
- docs/2026-03-12/“治理与放行中枢”的前端设计.md
- docs/2026-03-12/verification/T-FE-01_ia_spec.md
- multi-ai-collaboration.md
- docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md
- docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md

你必须完成：
1. 输出 Permit Header
2. 输出 Core Decision Block
3. 输出 Scope
4. 输出 Conditions
5. 输出 Linked Basis
6. 输出 Lifecycle
7. 输出 Signature
8. 输出 Residual Risk

你必须强化：
- Audit pass is not release approval. Permit is.
- revision / contract_hash / decision_hash / audit basis 必须绑定
- Permit 不是状态页，而是正式放行凭证
- 生命周期、签发角色、失效触发器必须明确

硬约束：
- 不得把 Permit 页面做成大绿勾成功页
- 不得出现与 revision / hash 解耦的 Permit
- 不得弱化范围、附加条件、失效条件
- 不得越权写到具体组件实现
- 无 EvidenceRef 不得宣称完成

你必须严格使用三段式输出：
1) PreflightChecklist
2) ExecutionContract
3) RequiredChanges

完成后必须补齐：
- docs/2026-03-12/verification/T-FE-04_execution_report.yaml

你的最终回复必须包含：
- 已写入文件路径
- 交付物摘要
- EvidenceRef
- gate_self_check 摘要
- 请 Reviewer / Compliance 关注的重点
```

---

## 2. 发给 Antigravity-2（Review）

```text
你是任务 T-FE-04 的审查者 Antigravity-2。

你只做审查，不做执行，不做合规放行。

请审查以下任务：

task_id: T-FE-04
执行者: Kior-B
目标: 输出 Permit 页面规格书，确保其是正式放行凭证而不是 success page

你必须阅读：
- docs/2026-03-12/前端重构_AI军团任务分发单_v2.md
- docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md
- docs/2026-03-12/“治理与放行中枢”的前端设计.md
- docs/2026-03-12/verification/T-FE-01_ia_spec.md
- docs/2026-03-12/verification/T-FE-04_permit_spec.md
- docs/2026-03-12/verification/T-FE-04_execution_report.yaml
- multi-ai-collaboration.md
- docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md

审查重点：
1. Permit 页面是否真正体现“正式放行凭证”而不是 success page
2. Permit Header / Core Decision Block / Scope / Conditions / Linked Basis / Lifecycle / Signature / Residual Risk 是否完整
3. 是否明确表达 Audit pass is not release approval. Permit is.
4. 是否绑定 revision / contract_hash / decision_hash / audit basis
5. 是否体现放行范围、附加条件、失效触发器
6. 是否体现生命周期与签发角色
7. 是否越权进入组件实现层
8. EvidenceRef 是否足以支撑规格结论

硬规则：
- 不接受空泛评价
- 必须指出具体偏差点
- 必须给出 evidence_refs
- 你没有执行权，不得替执行者补规格

输出文件：
- docs/2026-03-12/verification/T-FE-04_gate_decision.json

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
你是任务 T-FE-04 的合规官 vs--cc3。

你只做 B Guard 式硬审，不做执行，不做普通质量审查。

请复查以下任务：

task_id: T-FE-04
执行者: Kior-B
审查者: Antigravity-2
目标: 输出 Permit 页面规格书，确保其是正式放行凭证而不是 success page

你必须阅读：
- docs/2026-03-12/前端重构_AI军团任务分发单_v2.md
- docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md
- docs/2026-03-12/“治理与放行中枢”的前端设计.md
- docs/2026-03-12/verification/T-FE-01_ia_spec.md
- docs/2026-03-12/verification/T-FE-04_permit_spec.md
- docs/2026-03-12/verification/T-FE-04_execution_report.yaml
- docs/2026-03-12/verification/T-FE-04_gate_decision.json
- multi-ai-collaboration.md
- docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md

合规审查重点：
1. 是否把 Permit 页面做成成功页语义，导致放行裁决被弱化
2. 是否出现 Permit 与 revision / contract_hash / decision_hash / audit basis 解耦
3. 是否缺少放行范围、附加条件、失效触发器，导致 Permit 失去凭证约束性
4. 是否把 Audit pass 与 Permit issuance 混成一个概念
5. 是否弱化签发角色、签发时间、生命周期、残余风险
6. 是否存在可被误解为自动永久放行的文案或结构
7. 是否缺少 EvidenceRef

Zero Exception Directives：
- 只要出现 “审计通过 = 已放行” 的语言或结构倾向，直接 FAIL
- 只要出现 Permit 与 hash / revision / basis 解耦，直接 FAIL
- 只要 Permit 缺少范围 / 条件 / 生命周期 / 失效触发器中的关键约束，直接 FAIL

输出文件：
- docs/2026-03-12/verification/T-FE-04_compliance_attestation.json

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

它们共享同一个 `task_id=T-FE-04`，但不是同一份提示词。

按当前约定：

* 先推进并完成 `T-FE-04`
* 只有当 `T-FE-04` 三权闭环完成后，再继续进入 Wave 2
