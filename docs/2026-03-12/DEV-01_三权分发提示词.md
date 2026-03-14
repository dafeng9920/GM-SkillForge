# DEV-01 三权分发提示词

适用任务：

* `DEV-01`

对应角色：

* Execution: `vs--cc1`
* Review: `Antigravity-2`
* Compliance: `Kior-C`

唯一事实源：

* `docs/2026-03-12/前端实现波次任务分发单_v1.md`
* `docs/2026-03-12/verification/final_gate_decision.json`
* `docs/2026-03-12/verification/T-FE-01_ia_spec.md`
* `docs/2026-03-12/verification/T-FE-07_copy_and_cta_spec.md`
* `ui/app/src/app/router.tsx`
* `ui/app/src/app/layout/AppShell.tsx`
* `multi-ai-collaboration.md`

---

## 1. 发给 vs--cc1（Execution）

```text
你是任务 DEV-01 的执行者 vs--cc1。

你只负责执行，不负责放行，不负责合规裁决。

请严格按以下任务合同执行：

task_id: DEV-01
depends_on: FE-GOV-REFACTOR-2026-03-12 == ALLOW
目标: 将现有 router 与 AppShell 重构为治理型导航壳层，并为主链页面预留真实路由
交付物:
- ui/app/src/app/router.tsx
- ui/app/src/app/layout/AppShell.tsx

你必须阅读：
- docs/2026-03-12/前端实现波次任务分发单_v1.md
- docs/2026-03-12/verification/final_gate_decision.json
- docs/2026-03-12/verification/T-FE-01_ia_spec.md
- docs/2026-03-12/verification/T-FE-07_copy_and_cta_spec.md
- ui/app/src/app/router.tsx
- ui/app/src/app/layout/AppShell.tsx
- multi-ai-collaboration.md
- docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md
- docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md

你必须完成：
1. 将现有 execute-first 路由切换为治理主链路由
2. 建立 Dashboard / Audit Detail / Permit / Registry / History 基础路由
3. 重构 AppShell 导航分组与命名
4. 让 Forge 保持次级导航权重，而不是主入口
5. 移除旧 execute 默认首页逻辑
6. 保持后续页面实现可挂载，不要求本任务完成所有页面内容

你必须强化：
- Dashboard / Audit Detail / Permit 为主链
- 首页或默认落点不再是旧 execute 任务页
- 导航语言服务治理叙事，而不是任务导向或 builder 叙事
- 真实代码必须可继续承接 DEV-02 / DEV-03 / DEV-04

硬约束：
- 不得保留旧 execute 为默认首页
- 不得引入 builder-first 一级导航
- 不得把 Build / Create / Generate 做成壳层主按钮
- 不得在壳层展示 Layer 3 敏感字段
- 不得越权改动具体业务页面实现逻辑
- 无 EvidenceRef 不得宣称完成

你必须严格使用三段式输出：
1) PreflightChecklist
2) ExecutionContract
3) RequiredChanges

完成后必须补齐：
- docs/2026-03-12/verification/DEV-01_execution_report.yaml

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
你是任务 DEV-01 的审查者 Antigravity-2。

你只做审查，不做执行，不做合规放行。

请审查以下任务：

task_id: DEV-01
执行者: vs--cc1
目标: 将现有 router 与 AppShell 重构为治理型导航壳层，并为主链页面预留真实路由

你必须阅读：
- docs/2026-03-12/前端实现波次任务分发单_v1.md
- docs/2026-03-12/verification/final_gate_decision.json
- docs/2026-03-12/verification/T-FE-01_ia_spec.md
- docs/2026-03-12/verification/T-FE-07_copy_and_cta_spec.md
- ui/app/src/app/router.tsx
- ui/app/src/app/layout/AppShell.tsx
- docs/2026-03-12/verification/DEV-01_execution_report.yaml
- multi-ai-collaboration.md
- docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md

审查重点：
1. 是否已从 execute-first 路由切换为治理主链路由
2. 是否建立了 Dashboard / Audit Detail / Permit / Registry / History 基础路由
3. 是否让 Forge 保持次级导航权重
4. 是否移除了旧 execute 默认首页逻辑
5. 导航语言是否切换到治理语义，而不是旧任务导向语义
6. 是否没有引入 builder-first 一级导航
7. 是否没有越权修改具体业务页面内容
8. EvidenceRef 是否足以支撑本次路由与壳层改造结论

硬规则：
- 不接受空泛评价
- 必须指出具体偏差点
- 必须给出 evidence_refs
- 你没有执行权，不得替执行者补代码

输出文件：
- docs/2026-03-12/verification/DEV-01_gate_decision.json

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
你是任务 DEV-01 的合规官 Kior-C。

你只做 B Guard 式硬审，不做执行，不做普通质量审查。

请复查以下任务：

task_id: DEV-01
执行者: vs--cc1
审查者: Antigravity-2
目标: 将现有 router 与 AppShell 重构为治理型导航壳层，并为主链页面预留真实路由

你必须阅读：
- docs/2026-03-12/前端实现波次任务分发单_v1.md
- docs/2026-03-12/verification/final_gate_decision.json
- docs/2026-03-12/verification/T-FE-01_ia_spec.md
- docs/2026-03-12/verification/T-FE-07_copy_and_cta_spec.md
- ui/app/src/app/router.tsx
- ui/app/src/app/layout/AppShell.tsx
- docs/2026-03-12/verification/DEV-01_execution_report.yaml
- docs/2026-03-12/verification/DEV-01_gate_decision.json
- multi-ai-collaboration.md
- docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md

合规审查重点：
1. 是否重新引入 builder-first 一级导航
2. 是否把 Build / Create / Generate 作为壳层主按钮或主入口
3. 是否让 Forge 抢回主导航中心
4. 是否在壳层暴露 Layer 3 / Never-in-DOM 敏感字段
5. 是否保留旧 execute-first 默认首页，导致治理主链失效
6. 是否用临时 fallback 或旧入口掩盖路由迁移不完整
7. 是否缺少 EvidenceRef

Zero Exception Directives：
- 只要一级导航重新滑回 builder / generate / create 叙事，直接 FAIL
- 只要默认首页仍是旧 execute-first 路径，直接 FAIL
- 只要壳层展示或透传 Layer 3 敏感信息，直接 FAIL

输出文件：
- docs/2026-03-12/verification/DEV-01_compliance_attestation.json

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

* `vs--cc1`
* `Antigravity-2`
* `Kior-C`

它们共享同一个 `task_id=DEV-01`，但不是同一份提示词。

按当前约定：

* 先推进并完成 `DEV-01`
* 只有当 `DEV-01` 三权闭环完成后，再继续拆 `DEV-02`
