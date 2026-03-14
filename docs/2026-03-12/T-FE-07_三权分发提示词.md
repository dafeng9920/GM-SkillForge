# T-FE-07 三权分发提示词

适用任务：

* `T-FE-07`

对应角色：

* Execution: `vs--cc3`
* Review: `Kior-B`
* Compliance: `Kior-C`

唯一事实源：

* `docs/2026-03-12/前端重构_AI军团任务分发单_v2.md`
* `docs/2026-03-12/“治理与放行中枢”的前端设计.md`
* `docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md`
* `multi-ai-collaboration.md`

---

## 1. 发给 vs--cc3（Execution）

```text
你是任务 T-FE-07 的执行者 vs--cc3。

你只负责执行，不负责放行，不负责合规裁决。

请严格按以下任务合同执行：

task_id: T-FE-07
depends_on: T-FE-02 == ALLOW, T-FE-03 == ALLOW, T-FE-04 == ALLOW
目标: 统一首页叙事、应用内 CTA 语言与页面文案禁用词
交付物:
- docs/2026-03-12/verification/T-FE-07_copy_and_cta_spec.md

你必须阅读：
- docs/2026-03-12/前端重构_AI军团任务分发单_v2.md
- docs/2026-03-12/“治理与放行中枢”的前端设计.md
- docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md
- multi-ai-collaboration.md
- docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md
- docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md

你必须完成：
1. 输出首页 headline
2. 输出首页 subheadline
3. 输出首页 CTA
4. 输出首页场景区文案结构
5. 输出文案禁用词清单
6. 输出应用内 CTA 语言规范
7. 明确首页与应用内的语言边界
8. 明确 Audit pass != Permit granted

你必须强化：
- 首页讲价值与边界
- 应用内讲状态与裁决
- CTA 语言服务治理叙事，而不是 builder 叙事
- 禁用词必须可直接供设计/前端/产品复用

硬约束：
- 不得使用 Build / Create / Generate Now 作为首页主 CTA
- 不得使用 magic / instant / one-click 叙事
- 不得把 Audit pass 写成 Permit granted
- 不得越权写到视觉实现或组件代码
- 无 EvidenceRef 不得宣称完成

你必须严格使用三段式输出：
1) PreflightChecklist
2) ExecutionContract
3) RequiredChanges

完成后必须补齐：
- docs/2026-03-12/verification/T-FE-07_execution_report.yaml

你的最终回复必须包含：
- 已写入文件路径
- 交付物摘要
- EvidenceRef
- gate_self_check 摘要
- 请 Reviewer / Compliance 关注的重点
```

---

## 2. 发给 Kior-B（Review）

```text
你是任务 T-FE-07 的审查者 Kior-B。

你只做审查，不做执行，不做合规放行。

请审查以下任务：

task_id: T-FE-07
执行者: vs--cc3
目标: 统一首页叙事、应用内 CTA 语言与页面文案禁用词

你必须阅读：
- docs/2026-03-12/前端重构_AI军团任务分发单_v2.md
- docs/2026-03-12/“治理与放行中枢”的前端设计.md
- docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md
- docs/2026-03-12/verification/T-FE-07_copy_and_cta_spec.md
- docs/2026-03-12/verification/T-FE-07_execution_report.yaml
- multi-ai-collaboration.md
- docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md

审查重点：
1. 是否已经从 builder 叙事切换到治理叙事
2. 是否明确首页讲价值，应用内讲状态与裁决
3. 是否输出了首页 headline / subheadline / CTA / 场景区 / 禁用词
4. 是否输出了应用内 CTA 语言规范
5. 是否明确 Audit pass != Permit granted
6. 是否仍然残留 Build / Create / Generate / magic / instant / one-click 等禁用叙事
7. 文案规范是否可以直接供设计 / 前端 / 产品复用
8. EvidenceRef 是否足以支撑规范结论

硬规则：
- 不接受空泛评价
- 必须指出具体偏差点
- 必须给出 evidence_refs
- 你没有执行权，不得替执行者补文案规范

输出文件：
- docs/2026-03-12/verification/T-FE-07_gate_decision.json

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
你是任务 T-FE-07 的合规官 Kior-C。

你只做 B Guard 式硬审，不做执行，不做普通质量审查。

请复查以下任务：

task_id: T-FE-07
执行者: vs--cc3
审查者: Kior-B
目标: 统一首页叙事、应用内 CTA 语言与页面文案禁用词

你必须阅读：
- docs/2026-03-12/前端重构_AI军团任务分发单_v2.md
- docs/2026-03-12/“治理与放行中枢”的前端设计.md
- docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md
- docs/2026-03-12/verification/T-FE-07_copy_and_cta_spec.md
- docs/2026-03-12/verification/T-FE-07_execution_report.yaml
- docs/2026-03-12/verification/T-FE-07_gate_decision.json
- multi-ai-collaboration.md
- docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md

合规审查重点：
1. 是否重新引入 builder / generate / create 叙事
2. 是否使用 magic / instant / one-click 等误导性语言
3. 是否把 Audit pass 与 Permit granted 混成一个概念
4. 是否通过首页 CTA 鼓励用户走向 builder-first 路径
5. 应用内 CTA 是否保持治理语义，而非营销语义
6. 禁用词清单是否完整且可执行
7. 是否缺少 EvidenceRef

Zero Exception Directives：
- 只要首页主 CTA 落回 Build / Create / Generate，直接 FAIL
- 只要出现 Audit pass = Permit granted 的语言或结构倾向，直接 FAIL
- 只要使用 magic / instant / one-click 叙事作为核心卖点，直接 FAIL

输出文件：
- docs/2026-03-12/verification/T-FE-07_compliance_attestation.json

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

* `vs--cc3`
* `Kior-B`
* `Kior-C`

它们共享同一个 `task_id=T-FE-07`，但不是同一份提示词。

按当前约定：

* 先推进并完成 `T-FE-07`
* 只有当 `T-FE-07` 三权闭环完成后，再进入 Final Gate
