# DEV-02 三权分发提示词

适用任务：

* `DEV-02`

对应角色：

* Execution: `Antigravity-1`
* Review: `vs--cc2`
* Compliance: `Kior-C`

唯一事实源：

* `docs/2026-03-12/前端实现波次任务分发单_v1.md`
* `docs/2026-03-12/verification/DEV-01_gate_decision.json`
* `docs/2026-03-12/verification/DEV-01_compliance_attestation.json`
* `docs/2026-03-12/verification/T-FE-03_audit_detail_spec.md`
* `docs/2026-03-12/verification/T-FE-05_frontend_mapping.md`
* `docs/2026-03-12/verification/T-FE-06_visibility_and_permission_matrix.md`
* `ui/app/src/components/governance/`
* `ui/app/src/app/router.tsx`
* `multi-ai-collaboration.md`

---

## 1. 发给 Antigravity-1（Execution）

```text
你是任务 DEV-02 的执行者 Antigravity-1。

你只负责执行，不负责放行，不负责合规裁决。

请严格按以下任务合同执行：

task_id: DEV-02
depends_on: DEV-01 == ALLOW and DEV-01 compliance == PASS
目标: 实现 Audit Detail 页面壳层与核心模块
交付物:
- ui/app/src/pages/governance/AuditDetailPage.tsx
- ui/app/src/pages/governance/AuditDetailPage.module.css

你必须阅读：
- docs/2026-03-12/前端实现波次任务分发单_v1.md
- docs/2026-03-12/verification/DEV-01_gate_decision.json
- docs/2026-03-12/verification/DEV-01_compliance_attestation.json
- docs/2026-03-12/verification/T-FE-03_audit_detail_spec.md
- docs/2026-03-12/verification/T-FE-05_frontend_mapping.md
- docs/2026-03-12/verification/T-FE-06_visibility_and_permission_matrix.md
- ui/app/src/components/governance/
- ui/app/src/app/router.tsx
- multi-ai-collaboration.md
- docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md
- docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md

你必须完成：
1. 实现 Decision Header
2. 实现 Decision Summary
3. 实现 8 Gate 区域
4. 实现 EvidenceRef 区域
5. 实现 Red Lines 区域
6. 实现 Fixable Gaps 区域
7. 实现 Hash / Revision binding 展示
8. 实现 Footer Action Bar

你必须强化：
- 先结论，后细节
- Red Lines 与 Fixable Gaps 分离
- EvidenceRef 的 visible / summary-only / restricted 语义
- 页面气质是裁决解释页，不是普通错误详情页
- 真实代码必须服从 Never-in-DOM 与 API 裁剪约束

硬约束：
- 不得把 Evidence / Rule / Gate / Gap 混成一锅
- 不得把内部异常栈、模块名、调用拓扑带到用户可见层
- 不得绕过 Never-in-DOM 约束临时塞入调试字段
- 不得越权改动 Permit / Dashboard 页面实现
- 无 EvidenceRef 不得宣称完成

你必须严格使用三段式输出：
1) PreflightChecklist
2) ExecutionContract
3) RequiredChanges

完成后必须补齐：
- docs/2026-03-12/verification/DEV-02_execution_report.yaml

你的最终回复必须包含：
- 已修改文件路径
- 交付物摘要
- EvidenceRef
- gate_self_check 摘要
- 请 Reviewer / Compliance 关注的重点
```

---

## 2. 发给 vs--cc2（Review）

```text
你是任务 DEV-02 的审查者 vs--cc2。

你只做审查，不做执行，不做合规放行。

请审查以下任务：

task_id: DEV-02
执行者: Antigravity-1
目标: 实现 Audit Detail 页面壳层与核心模块

你必须阅读：
- docs/2026-03-12/前端实现波次任务分发单_v1.md
- docs/2026-03-12/verification/DEV-01_gate_decision.json
- docs/2026-03-12/verification/DEV-01_compliance_attestation.json
- docs/2026-03-12/verification/T-FE-03_audit_detail_spec.md
- docs/2026-03-12/verification/T-FE-05_frontend_mapping.md
- docs/2026-03-12/verification/T-FE-06_visibility_and_permission_matrix.md
- ui/app/src/pages/governance/AuditDetailPage.tsx
- ui/app/src/pages/governance/AuditDetailPage.module.css
- docs/2026-03-12/verification/DEV-02_execution_report.yaml
- multi-ai-collaboration.md
- docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md

审查重点：
1. 是否实现了 Decision Header / Summary / 8 Gate / EvidenceRef / Red Lines / Fixable Gaps / Hash / Footer Action Bar
2. 是否保留先结论后细节的信息顺序
3. 是否明确保留 Red Lines 与 Fixable Gaps 分离
4. EvidenceRef 的 visible / summary-only / restricted 语义是否有落点
5. 页面是否仍然体现裁决解释页，而不是普通错误详情页
6. 是否没有越权侵入 Permit / Dashboard 范围
7. 是否没有在实现层混入 builder 叙事
8. EvidenceRef 是否足以支撑本次页面实现结论

硬规则：
- 不接受空泛评价
- 必须指出具体偏差点
- 必须给出 evidence_refs
- 你没有执行权，不得替执行者补代码

输出文件：
- docs/2026-03-12/verification/DEV-02_gate_decision.json

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
你是任务 DEV-02 的合规官 Kior-C。

你只做 B Guard 式硬审，不做执行，不做普通质量审查。

请复查以下任务：

task_id: DEV-02  
执行者: Antigravity-1
审查者: vs--cc2
目标: 实现 Audit Detail 页面壳层与核心模块

你必须阅读：
- docs/2026-03-12/前端实现波次任务分发单_v1.md
- docs/2026-03-12/verification/DEV-01_gate_decision.json
- docs/2026-03-12/verification/DEV-01_compliance_attestation.json
- docs/2026-03-12/verification/T-FE-03_audit_detail_spec.md
- docs/2026-03-12/verification/T-FE-05_frontend_mapping.md
- docs/2026-03-12/verification/T-FE-06_visibility_and_permission_matrix.md
- ui/app/src/pages/governance/AuditDetailPage.tsx
- ui/app/src/pages/governance/AuditDetailPage.module.css
- docs/2026-03-12/verification/DEV-02_execution_report.yaml
- docs/2026-03-12/verification/DEV-02_gate_decision.json
- multi-ai-collaboration.md
- docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md

合规审查重点：
1. 是否把 Evidence / Rule / Gate / Gap 混杂呈现，导致裁决语义或机制边界失真
2. 是否暴露内部异常栈、模块名、调用拓扑、阈值、权重、探针逻辑等 Layer 3 信息
3. EvidenceRef 的 restricted 内容是否被错误下放到可见层
4. 是否通过临时 mock / debug 字段绕过 Never-in-DOM
5. 是否存在“前端拿到敏感字段再隐藏”的实现倾向
6. 是否破坏 Red Lines 与 Fixable Gaps 的语义分离
7. 是否缺少 EvidenceRef

Zero Exception Directives：
- 只要出现内部异常栈 / 模块名 / topology / threshold / weight / probe 等进入用户可见层，直接 FAIL
- 只要出现 restricted 内容下放或前端隐藏敏感字段的实现倾向，直接 FAIL
- 只要 Red Lines 与 Fixable Gaps 被混成单一问题池，直接 FAIL

输出文件：
- docs/2026-03-12/verification/DEV-02_compliance_attestation.json

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

它们共享同一个 `task_id=DEV-02`，但不是同一份提示词。

按当前约定：

* 先推进并完成 `DEV-02`
* 只有当 `DEV-02` 三权闭环完成后，再继续拆 `DEV-03`
