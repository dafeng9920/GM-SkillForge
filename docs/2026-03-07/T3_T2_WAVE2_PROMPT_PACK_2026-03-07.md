# T3 + T2 Wave 2 Prompt Pack (2026-03-07)

## Scope

This prompt pack covers only:

- `T3-A` submit/status/fetch/verify stability closure
- `T3-B` overnight unattended runbook
- `T3-C` parallel cloud batch template
- `T3-D` cloud operator documentation normalization
- `T2W2-A` non-F1 migration-doc path normalization
- `T2W2-B` selective intent contract promotion shortlist
- `T2W2-C` Wave 2 execution preconditions

Hard rules for all shards:

- no actor may self-approve
- no claim of completion without `EvidenceRef`
- no hidden scope expansion
- any missing proof must be reported as `REQUIRES_CHANGES`
- every executor must write a completion record before handoff
- all completion records for this wave must use `docs/2026-03-07/T3_T2_WAVE2_任务回传模板_COMPLIANT_v1.md`

Start fact (must be preserved):

- `docs/2026-03-07/T2_EXTERNAL_ALIGNMENT_STATEMENT_2026-03-07.md`
- Do not reopen `T2 Wave 1` as unresolved work

---

## T3-A

### Role Assignment

- Execution: `Kior-B`
- Review: `Kior-C`
- Compliance: `Antigravity-1`

### Execution Prompt

```text
你是 T3-A 的执行者 Kior-B。

目标：
把当前 Lobster Console + lobsterctl 的 submit/status/fetch/verify 路径稳定下来，
让它从“能用”变成“可重复、少人工修补”的操作链。

范围：
- 只处理当前云端执行路径的操作稳定性
- 重点是 submit/status/fetch/verify
- 不扩大到新的云平台重构

必须交付：
1. execution_report
2. completion record（必须使用 `docs/2026-03-07/T3_T2_WAVE2_任务回传模板_COMPLIANT_v1.md`）
3. 至少一个 smoke task 的稳定执行证据
4. EvidenceRef（命令、日志、产物、状态输出）

完成定义：
- one-click 或最小可重复序列可跑通至少一个 smoke task
- status 输出有界并能正常退出
- fetch/verify 路径不需要临时 shell 修补
- operator sequence 被压缩成最小可复现步骤

输出：
- 实际执行序列
- 修复了哪些 friction
- 验证方式
- remaining risk
```

### Review Prompt

```text
你是 T3-A 的审查者 Kior-C。

请审查：
- 是否真的降低了人工修补依赖
- smoke task 证据是否完整
- status/fetch/verify 是否有可复现实操证据

输出：
- ALLOW / REQUIRES_CHANGES / DENY
- reasons
- evidence_refs
```

### Compliance Prompt

```text
你是 T3-A 的合规官 Antigravity-1。

请检查：
- 是否保持 closed-loop contract + receipt + dual-gate 口径
- 是否存在无证据的“稳定”宣称
- 是否引入绕过 permit/gate 的临时手法

证据不足直接 FAIL。
```

---

## T3-B

### Role Assignment

- Execution: `Kior-C`
- Review: `Antigravity-1`
- Compliance: `Antigravity-2`

### Execution Prompt

```text
你是 T3-B 的执行者 Kior-C。

目标：
产出一份真正可执行的 overnight unattended runbook，
让非 debug 流程也能按步骤完成“夜间运行 -> 早晨收口 -> 失败处理”。

范围：
- 只写当前现实操作链对应的 checklist
- 每一步必须能映射到现有按钮、命令、路径
- 不写理想化未来流程

必须交付：
1. runbook 文档
2. execution_report
3. completion record（必须使用 `docs/2026-03-07/T3_T2_WAVE2_任务回传模板_COMPLIANT_v1.md`）
4. EvidenceRef（每个关键步骤对应真实入口）

完成定义：
- pre-shutdown checklist 明确 → EvidenceRef: 验证报告路径
- morning fetch/verify checklist 明确 → EvidenceRef: 验证报告路径
- failure branch checklist 明确 → EvidenceRef: 验证报告路径
- 非调试人员也能照着执行 → EvidenceRef: 试运行记录
- remaining risk 挂载 EvidenceRef 或明确 NONE 并附 gate decision

输出：
- runbook 路径 → EvidenceRef: 文件路径
- 三段 checklist 概要 → EvidenceRef: 每段验证报告
- 验证方式 → EvidenceRef: self-check 日志 / 手工验证截图
- remaining risk → EvidenceRef: 风险分析报告 / [NONE + gate decision 路径]
```

### Review Prompt

```text
你是 T3-B 的审查者 Antigravity-1。

请审查：
- checklist 是否真能执行，而不是原则性空话
- 是否覆盖 pre-shutdown / morning / failure 三段
- 是否与当前现实工具链一致

输出：
- ALLOW / REQUIRES_CHANGES / DENY
- reasons
- evidence_refs
```

### Compliance Prompt

```text
你是 T3-B 的合规官 Antigravity-2。

请检查：
- 是否存在”无证据步骤”
- 每个 checklist 是否有验证报告/截图证据
- remaining risk 是否挂载 EvidenceRef
- 是否把未来能力写成当前能力
- 是否有明确的 block/remediation 路径

证据不足或遗漏即 FAIL。
发现问题时必须明确 block 点和 remediation 要求。
```

---

## T3-C

### Role Assignment

- Execution: `Antigravity-1`
- Review: `Kior-C`
- Compliance: `Antigravity-2`

### Execution Prompt

```text
你是 T3-C 的执行者 Antigravity-1。

目标：
产出并行云端批次模板，用于后续 M2/M3/M4 或同类批量 dispatch
（注：删除"稳定的"以避免无证据的稳定宣称）

范围：
- 只做模板和聚合路径
- review/compliance 必须保持本地集中
- 不直接启动新云批次

必须交付：
1. batch template 文档或结构化文件
2. execution_report
3. completion record（必须使用 `docs/2026-03-07/T3_T2_WAVE2_任务回传模板_COMPLIANT_v1.md`）
4. EvidenceRef（模板关键字段、归档目标、聚合路径）

完成定义：
- task ids / wave order / archive targets 明确 → EvidenceRef: 模板字段清单/结构化文件
- 无 executor self-approval 路径 → EvidenceRef: workflow 设计审查记录
- final aggregation path 明确 → EvidenceRef: 聚合脚本/文档路径
- 模板可执行性验证通过 → EvidenceRef: 模拟验证报告/试运行记录

输出：
- 模板路径 → EvidenceRef: 文件路径
- 关键字段 → EvidenceRef: 模板字段清单/截图
- 验证方式 → EvidenceRef: 验证报告/日志
- remaining risk → EvidenceRef: 风险分析报告 / [NONE + gate decision 路径]
```

### Review Prompt

```text
你是 T3-C 的审查者 Kior-C。

请审查：
- 模板是否真正可执行 → EvidenceRef: 试运行记录/模拟验证
- wave / archive / aggregation 路径是否明确 → EvidenceRef: 模板字段/文档
- 是否消除了 self-approval 风险 → EvidenceRef: workflow 设计审查

输出：
- ALLOW / REQUIRES_CHANGES / DENY
- reasons → 每条理由必须有 EvidenceRef
- evidence_refs
```

### Compliance Prompt

```text
你是 T3-C 的合规官 Antigravity-2。

请检查：
- 是否存在"无证据步骤"（每项宣称必须有 EvidenceRef）
- 是否存在无证据的"稳定"/"可执行"宣称
- remaining risk 是否挂载 EvidenceRef
- 是否把未来能力（实际未验证的功能）写成当前能力
- 是否有明确的 block/remediation 路径
- 三权分立是否在模板中体现（review/compliance 本地集中）
- 是否缺少 archive / final gate 路径定义

证据不足或遗漏即 FAIL。
发现问题时必须明确 block 点和 remediation 要求。
```

---

## T3-D

### Role Assignment

- Execution: `vs--cc3`
- Review: `Kior-C`
- Compliance: `Antigravity-2`

### Execution Prompt

```text
你是 T3-D 的执行者 vs--cc3。

目标：
清理当前云端 operator 文档中的过时口径，
让现行 runbook 只反映 Lobster Console + Antigravity-1 路径。

范围：
- 只处理 current-runbook / operator-facing docs
- 保留历史记录中的旧事实，不篡改历史
- 不扩大到无关文档全面清洗

必须交付：
1. 文档修改
2. execution_report
3. completion record（必须使用 `docs/2026-03-07/T3_T2_WAVE2_任务回传模板_COMPLIANT_v1.md`）
4. EvidenceRef（指出当前链路口径更新点）

完成定义：
- 当前 runbook 不再把 suspended executor 当 active dependency → EvidenceRef: 文档 diff/截图
- current cloud chain 与现实一致 → EvidenceRef: 链路验证报告
- history vs current-state distinction 被保留 → EvidenceRef: 文档结构审查

输出：
- 修改文件列表 → EvidenceRef: git diff / 文件路径清单
- 清理掉的旧口径 → EvidenceRef: before/after 对比
- 验证方式 → EvidenceRef: 审查报告/截图
- remaining risk → EvidenceRef: 风险分析报告 / [NONE + gate decision 路径]
```

### Review Prompt

```text
你是 T3-D 的审查者 Kior-C。

请审查：
- 当前文档是否已去除过时依赖 → EvidenceRef: 文档审查记录
- 是否误删历史事实 → EvidenceRef: 历史事实核对表
- 当前 operator 口径是否与现实路径一致 → EvidenceRef: 链路验证报告

输出：
- ALLOW / REQUIRES_CHANGES / DENY
- reasons → 每条理由必须有 EvidenceRef
- evidence_refs
```

### Compliance Prompt

```text
你是 T3-D 的合规官 Antigravity-2。

请检查：
- 是否存在"无证据步骤"（每项文档修改必须有 EvidenceRef）
- 是否存在历史与现状混写导致的误导
- 是否有当前 runbook 仍指向 suspended executor
- 是否缺少 EvidenceRef 支撑文档更新
- remaining risk 是否挂载 EvidenceRef
- 是否有明确的 block/remediation 路径

证据不足或遗漏即 FAIL。
发现问题时必须明确 block 点和 remediation 要求。
```

---

## T2W2-A

### Role Assignment

- Execution: `vs--cc2`
- Review: `Kior-C`
- Compliance: `Antigravity-2`

### Execution Prompt

```text
你是 T2W2-A 的执行者 vs--cc2。

目标：
梳理 intent_map 中剩余的非 F1 docs-backed entries，
并将它们分类为：
- promote now
- keep docs-backed with reason
- defer

范围：
- 只处理非 F1 scope、仍停留在 migration-doc path 的 entries
- 不在本任务内直接做全部主线化
- 重点是状态清晰，不是一次性修完

必须交付：
1. baseline 文档或结构化清单
2. execution_report
3. completion record（必须使用 `docs/2026-03-07/T3_T2_WAVE2_任务回传模板_COMPLIANT_v1.md`）
4. EvidenceRef（每个条目当前路径与分类理由）

完成定义：
- 每个 docs-backed entry 都有明确 disposition → EvidenceRef: baseline 清单/审查记录
- 无 ambiguous active path → EvidenceRef: 路径核对表
- 结果可作为 Wave 2 下一步输入 → EvidenceRef: stakeholder 确认记录

输出：
- 清单路径 → EvidenceRef: baseline 文件路径
- 分类结果 → EvidenceRef: 分类决策表
- owner path / next step → EvidenceRef: 任务分配记录
- remaining risk → EvidenceRef: 风险分析报告 / [NONE + gate decision 路径]
```

### Review Prompt

```text
你是 T2W2-A 的审查者 Kior-C。

请审查：
- 是否真的覆盖了剩余 docs-backed non-F1 entries → EvidenceRef: 覆盖范围核对表
- 分类是否可复核 → EvidenceRef: 分类依据文档
- 是否还存在”活跃但无人负责”的路径 → EvidenceRef: owner 映射表

输出：
- ALLOW / REQUIRES_CHANGES / DENY
- reasons → 每条理由必须有 EvidenceRef
- evidence_refs
```

### Compliance Prompt

```text
你是 T2W2-A 的合规官 Antigravity-2。

请检查：
- 是否存在”无证据步骤”（每项分类结论必须有 EvidenceRef）
- 是否把”docs-backed by design”误报成”已主线化”
- 是否有无证据的分类结论
- 是否有路径漂移被静默跳过
- remaining risk 是否挂载 EvidenceRef
- 是否有明确的 block/remediation 路径

证据不足或遗漏即 FAIL。
发现问题时必须明确 block 点和 remediation 要求。
```

---

## T2W2-B

### Role Assignment

- Execution: `Kior-A`
- Review: `Kior-C`
- Compliance: `Antigravity-1`

### Execution Prompt

```text
你是 T2W2-B 的执行者 Kior-A。

目标：
产出 Wave 2 selective intent contract promotion shortlist。

范围：
- 只做 shortlist 与排序
- 依据 fit + contribution + operational value
- 不在本任务里直接实现这些 intents

必须交付：
1. shortlist 文档
2. execution_report
3. completion record（必须使用 `docs/2026-03-07/T3_T2_WAVE2_任务回传模板_COMPLIANT_v1.md`）
4. EvidenceRef（每个 shortlisted intent 的理由）

完成定义：
- shortlist 明确且有顺序
- 每个 intent 有 rationale 和 owner path
- 低 fit intents 被明确 defer

输出：
- shortlist 路径
- ordered list
- rationale
- remaining risk
```

### Review Prompt

```text
你是 T2W2-B 的审查者 Kior-C。

请审查：
- shortlist 是否与 Wave 1 后现状一致
- 是否存在高分低值或低分高估问题
- 是否把 defer 项说明清楚

输出：
- ALLOW / REQUIRES_CHANGES / DENY
- reasons
- evidence_refs
```

### Compliance Prompt

```text
你是 T2W2-B 的合规官 Antigravity-1。

请检查：
- 是否存在无依据的 promotion 建议
- 是否把低 fit 项包装成当前必须迁移
- 是否有 fake closure 话术

不满足即 FAIL。
```

---

## T2W2-C

### Role Assignment

- Execution: `Antigravity-1`
- Review: `Kior-C`
- Compliance: `Antigravity-2`

### Execution Prompt

```text
你是 T2W2-C 的执行者 Antigravity-1。

目标：
定义 Wave 2 migration execution preconditions，
并明确它们与 T3 稳定化输出的依赖关系。

范围：
- 只写 preconditions，不启动 Wave 2 实施
- 必须把 cloud-lane dependency 写明
- 不允许“边迁边补条件”

必须交付：
1. preconditions 文档
2. execution_report
3. completion record（必须使用 `docs/2026-03-07/T3_T2_WAVE2_任务回传模板_COMPLIANT_v1.md`）
4. EvidenceRef（对应 T3 输出与启动条件）

完成定义：
- Wave 2 execution preconditions 明确 → EvidenceRef: preconditions 文档路径
- T3 dependency 明确 → EvidenceRef: T3 输出引用/依赖映射表
- 无 undefined operating condition → EvidenceRef: 条件覆盖完整性检查

输出：
- 文档路径 → EvidenceRef: preconditions 文件路径
- preconditions list → EvidenceRef: 条件清单/结构化文件
- dependency mapping → EvidenceRef: T3 依赖映射图
- remaining risk → EvidenceRef: 风险分析报告 / [NONE + gate decision 路径]
```

### Review Prompt

```text
你是 T2W2-C 的审查者 Kior-C。

请审查：
- preconditions 是否真的可执行 → EvidenceRef: 可执行性验证报告
- 是否把 T3 dependency 写清楚 → EvidenceRef: 依赖映射表
- 是否仍有含糊启动条件 → EvidenceRef: 条件明确性检查

输出：
- ALLOW / REQUIRES_CHANGES / DENY
- reasons → 每条理由必须有 EvidenceRef
- evidence_refs
```

### Compliance Prompt

```text
你是 T2W2-C 的合规官 Antigravity-2。

请检查：
- 是否存在"无证据步骤"（每个 precondition 必须有 EvidenceRef）
- 是否存在未定义条件下启动 Wave 2 的风险
- 是否把 cloud stabilization 依赖写成了软建议而不是硬前提
- 是否缺少 EvidenceRef
- remaining risk 是否挂载 EvidenceRef
- 是否有明确的 block/remediation 路径

证据不足或遗漏即 FAIL。
发现问题时必须明确 block 点和 remediation 要求。
```
