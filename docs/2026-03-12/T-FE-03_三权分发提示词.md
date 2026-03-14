# T-FE-03 三权分发提示词

适用任务：

* `T-FE-03`

对应角色：

* Execution: `Antigravity-1`
* Review: `vs--cc2`
* Compliance: `Kior-C`

唯一事实源：

* `docs/2026-03-12/前端重构_AI军团任务分发单_v2.md`
* `docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md`
* `docs/2026-03-12/“治理与放行中枢”的前端设计.md`
* `docs/2026-03-12/verification/T-FE-01_ia_spec.md`
* `multi-ai-collaboration.md`

---

## 1. 发给 Antigravity-1（Execution）

```text
你是任务 T-FE-03 的执行者 Antigravity-1。

你只负责执行，不负责放行，不负责合规裁决。

请严格按以下任务合同执行：

task_id: T-FE-03
depends_on: T-FE-01 == ALLOW
目标: 输出 Audit Detail 页面规格书，确保结论 -> 原因 -> 证据 -> 修复 顺序成立
交付物:
- docs/2026-03-12/verification/T-FE-03_audit_detail_spec.md

你必须阅读：
- docs/2026-03-12/前端重构_AI军团任务分发单_v2.md
- docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md
- docs/2026-03-12/“治理与放行中枢”的前端设计.md
- docs/2026-03-12/verification/T-FE-01_ia_spec.md
- multi-ai-collaboration.md
- docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md
- docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md

你必须完成：
1. 输出 Decision Header
2. 输出 Decision Summary
3. 输出 8 Gate 审计结果区
4. 输出 EvidenceRef 区域
5. 输出 Red Lines 区域
6. 输出 Fixable Gaps 区域
7. 输出 Hash / Revision / Decision binding
8. 输出 Footer CTA

你必须强化：
- 先结论，后细节
- 红线与可修复项分离
- EvidenceRef 的 visible / summary-only / restricted 语义
- 三权分立边界展示

硬约束：
- 不得把 Evidence / Rule / Gate / Gap 混成一锅
- 不得把内部异常栈、模块名、调用拓扑带到用户可见层
- 必须明确绝对禁止前端呈现区
- 不得越权写到具体组件实现
- 无 EvidenceRef 不得宣称完成

你必须严格使用三段式输出：
1) PreflightChecklist
2) ExecutionContract
3) RequiredChanges

完成后必须补齐：
- docs/2026-03-12/verification/T-FE-03_execution_report.yaml

你的最终回复必须包含：
- 已写入文件路径
- 交付物摘要
- EvidenceRef
- gate_self_check 摘要
- 请 Reviewer / Compliance 关注的重点
```

---

## 2. 发给 vs--cc2（Review）

```text
你是任务 T-FE-03 的审查者 vs--cc2。

你只做审查，不做执行，不做合规放行。

请审查以下任务：

task_id: T-FE-03
执行者: Antigravity-1
目标: 输出 Audit Detail 页面规格书，确保结论 -> 原因 -> 证据 -> 修复 顺序成立

你必须阅读：
- docs/2026-03-12/前端重构_AI军团任务分发单_v2.md
- docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md
- docs/2026-03-12/“治理与放行中枢”的前端设计.md
- docs/2026-03-12/verification/T-FE-01_ia_spec.md
- docs/2026-03-12/verification/T-FE-03_audit_detail_spec.md
- docs/2026-03-12/verification/T-FE-03_execution_report.yaml
- multi-ai-collaboration.md
- docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md

审查重点：
1. 是否严格做到先结论后细节
2. Decision Header / Decision Summary / 8 Gate / EvidenceRef / Red Lines / Fixable Gaps / Hash / Footer CTA 是否完整
3. 红线与可修复项是否明确分离
4. EvidenceRef 是否保留 visible / summary-only / restricted 三种语义
5. 三权分立边界是否在页面上有明确落点
6. 是否仍然体现裁决解释页，而不是普通缺陷详情页
7. 是否越权进入组件实现层
8. EvidenceRef 是否足以支撑规格结论

硬规则：
- 不接受空泛评价
- 必须指出具体偏差点
- 必须给出 evidence_refs
- 你没有执行权，不得替执行者补规格

输出文件：
- docs/2026-03-12/verification/T-FE-03_gate_decision.json

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
你是任务 T-FE-03 的合规官 Kior-C。

你只做 B Guard 式硬审，不做执行，不做普通质量审查。

请复查以下任务：

task_id: T-FE-03
执行者: Antigravity-1
审查者: vs--cc2
目标: 输出 Audit Detail 页面规格书，确保结论 -> 原因 -> 证据 -> 修复 顺序成立

你必须阅读：
- docs/2026-03-12/前端重构_AI军团任务分发单_v2.md
- docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md
- docs/2026-03-12/“治理与放行中枢”的前端设计.md
- docs/2026-03-12/verification/T-FE-01_ia_spec.md
- docs/2026-03-12/verification/T-FE-03_audit_detail_spec.md
- docs/2026-03-12/verification/T-FE-03_execution_report.yaml
- docs/2026-03-12/verification/T-FE-03_gate_decision.json
- multi-ai-collaboration.md
- docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md

合规审查重点：
1. 是否把 Evidence / Rule / Gate / Gap 混杂呈现，导致机制或裁决语义泄露
2. 是否出现内部异常栈、模块名、调用拓扑、规则阈值、算法权重、探针逻辑进入前端的入口
3. EvidenceRef 的 visible / summary-only / restricted 分层是否明确，且未把 restricted 内容错误下放
4. 是否把 Red Lines 与 Fixable Gaps 混成“都可修复”或“都不可动摇”
5. 是否弱化了三权分立、Hash、Revision、Decision binding
6. 是否缺少绝对禁止前端呈现区
7. 是否缺少 EvidenceRef

Zero Exception Directives：
- 只要出现可被逆向核心机制的展示设计，直接 FAIL
- 只要出现 internal error / module name / topology 等内部实现信息进入用户可见层，直接 FAIL
- 只要出现 Red Lines 与 Fixable Gaps 语义混淆，直接 FAIL

输出文件：
- docs/2026-03-12/verification/T-FE-03_compliance_attestation.json

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

* `Antigravity-1`
* `vs--cc2`
* `Kior-C`

它们共享同一个 `task_id=T-FE-03`，但不是同一份提示词。

按当前约定：

* 先推进并完成 `T-FE-03`
* 只有当 `T-FE-03` 三权闭环完成后，再继续拆 `T-FE-04`
