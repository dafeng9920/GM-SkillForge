# T2 Remediation Prompt Pack (2026-03-07)

## Scope

This prompt pack covers only:

- `F1-R` canonical contract restoration remediation
- `F3-R` evidence-first temporal semantics remediation
- `F2-C` independent compliance attestation replacement

Hard rules for all shards:

- no actor may self-approve
- no claim of completion without `EvidenceRef`
- remediation must answer the existing fail attestation directly
- do not widen scope beyond the cited findings

---

## F1-R

### Role Assignment

- Execution: `vs--cc2`
- Review: `Kior-C`
- Compliance: `Antigravity-2`

### Execution Prompt

```text
你是 T2 remediation F1-R 的执行者 vs--cc2。

目标：
修复 T2-F1 在合规报告中指出的 contract erosion 问题。

唯一权威问题来源：
- docs/2026-03-07/verification/T2-F1_compliance_attestation_FAIL.json

必须修复的核心问题：
1. 恢复 contracts/intents/ 中缺失的 validation_rules
2. 恢复 architecture_boundary / fail-closed 边界声明
3. 恢复 source_doc_ref / 证据链引用
4. 修正 execution_report 中不真实的“已一致”宣称
5. 处理 intent_map 中仍残留的迁移文档 contract_path

范围：
- 只修复 F1 fail attestation 指出的具体问题
- 保留 canonical naming 成果
- 不扩大到新功能开发或 unrelated contract redesign

必须交付：
1. 修复后的合同/映射文件
2. execution_report
3. completion record
4. EvidenceRef（必须能证明恢复了被削掉的约束）

完成定义：
- production contracts 不再比 migration draft 少关键治理字段
- canonical naming 仍成立，但不以削弱约束为代价
- fail attestation 中列出的 critical violations 都有对应修复
- remaining risk 如有，必须精确写明

输出：
- 修改文件列表
- 每个修复点对应哪条 fail finding
- 验证方式
- remaining risk
```

### Review Prompt

```text
你是 T2 remediation F1-R 的审查者 Kior-C。

请审查：
- 是否真的补回了 validation_rules / architecture_boundary / source_doc_ref
- 是否只是表面“补标题”，没有恢复治理能力
- execution_report 是否修正了虚假完成声明

只允许输出：
- ALLOW
- REQUIRES_CHANGES
- DENY

必须附：
- reasons
- evidence_refs
- 对 fail finding 的逐项核对结果
```

### Compliance Prompt

```text
你是 T2 remediation F1-R 的合规官 Antigravity-2。

请检查：
- contracts/intents/ 新文件是否已恢复 fail-closed 核心约束
- 是否仍存在 authoritative boundary erosion
- 是否还有未处理的 active intent_map 路径漂移

若未正面修复 fail attestation，直接 FAIL。
```

---

## F3-R

### Role Assignment

- Execution: `vs--cc1`
- Review: `Kior-C`
- Compliance: `Antigravity-2`

### Execution Prompt

```text
你是 T2 remediation F3-R 的执行者 vs--cc1。

目标：
修复 T2-F3 中 “evidence-first publish chain 只验证 evidence exists、未验证时间顺序” 的问题。

唯一权威问题来源：
- docs/2026-03-07/verification/T2-F3_compliance_attestation_FAIL.json

必须修复的核心问题：
1. 保存 gate decision timestamp / decision_time 到 evidence chain 或等效可追溯字段
2. 修正 test_evidence_collected_before_publish_decision，使其验证时间顺序
3. 修正 execution_report / completion record 中关于 evidence-first 的语义描述
4. 视情况补充 fail-closed 边界测试

范围：
- 只修复 F3 fail attestation 指向的时间顺序与可追溯性问题
- 不扩大为大规模审计引擎重构

必须交付：
1. 代码修复
2. 测试修复
3. execution_report
4. completion record
5. EvidenceRef（明确指出 decision_time 与 evidence timing 的落点）

完成定义：
- evidence-first 成为可验证的时间顺序语义
- 测试不再只验证 evidence 存在
- fail attestation 中的关键问题都有明确修复
- 对仍未覆盖的边界情况必须诚实列 remaining risk

输出：
- 修改文件列表
- 每个修复点对应哪条 fail finding
- 测试结果
- remaining risk
```

### Review Prompt

```text
你是 T2 remediation F3-R 的审查者 Kior-C。

重点检查：
- 是否真正保存并验证了 decision timestamp / decision_time
- 测试是否验证顺序关系，而不是换个名字继续测存在性
- completion/execution 报告是否去掉旧的虚假语义

输出：
- ALLOW / REQUIRES_CHANGES / DENY
- reasons
- evidence_refs
- 对 fail finding 的逐项核对结果
```

### Compliance Prompt

```text
你是 T2 remediation F3-R 的合规官 Antigravity-2。

请检查：
- evidence-first 的核心语义是否已从 narrative 变成可追溯时序事实
- 是否仍缺失 gate decision timestamp 等关键字段
- 是否还有 fake closure 话术

若没有把“先于决策”做成可验证事实，直接 FAIL。
```

---

## F3-R2

### Role Assignment

- Execution: `vs--cc1`
- Review: `Kior-C`
- Compliance: `Antigravity-2`

### Execution Prompt

```text
你是 T2 remediation F3-R2 的执行者 vs--cc1。

目标：
只修复 F3-R 本次 FAIL 的三条明确问题，不做任何额外扩展：
1. evidence-first 的核心语义（“先于决策”）必须成为可验证的时序事实
2. 测试必须真的验证时间顺序，不能只验证 evidence exists
3. 移除或修正所有虚假闭环话术（包括 docstring / report / completion record）

唯一权威问题来源：
- Antigravity-2 最新 F3-R FAIL 结论（2026-03-07T16:45:00Z）
- docs/2026-03-07/verification/T2-F3_compliance_attestation_FAIL.json

允许做的事，仅限：
1. 给 gate decision / publish decision 增加可追溯的 decision_time / gate_timestamp / equivalent field
2. 把该时间字段持久化到 evidence chain 或可引用输出
3. 修改测试，显式断言“证据先于决策”所需的时序关系
4. 修正文档、docstring、execution_report、completion record 中不真实的验证声明

禁止做的事：
- 不得扩大为审计引擎整体重构
- 不得新增无关测试包
- 不得只改文案不改时序事实
- 不得只改代码不改测试断言

必须交付：
1. 代码修改
2. 测试修改
3. execution_report（修订版）
4. completion record（修订版）
5. EvidenceRef（必须直接指向 timing 字段落点和顺序断言）

完成定义：
- evidence-first 不再是 narrative claim，而是可断言的时序事实
- 测试明确检查 timing ordering
- 所有虚假“已验证 evidence-first”措辞被清理或改成真实表述
- remaining risk 若有，必须只写尚未覆盖的边界，而不是回避核心问题

输出：
- 修改文件列表
- timing 字段存储位置
- 测试中的顺序断言位置
- 修正过的文案位置
- remaining risk
```

### Review Prompt

```text
你是 T2 remediation F3-R2 的审查者 Kior-C。

只审三件事：
1. 代码里是否真的出现了可追溯 decision_time / gate_timestamp / equivalent field
2. 测试里是否真的断言了时序关系
3. 文案里是否还残留“已验证 evidence-first”但代码未证明的说法

输出：
- ALLOW / REQUIRES_CHANGES / DENY
- reasons
- evidence_refs
- 对上面三项逐条核对结果
```

### Compliance Prompt

```text
你是 T2 remediation F3-R2 的合规官 Antigravity-2。

你只检查这三条红线：
1. “先于决策”是否已经成为可验证时序事实
2. 测试是否真的验证了顺序而不是存在性
3. 是否还有虚假闭环话术

如果任一条仍不成立，直接 FAIL。

输出限制：
- PASS / FAIL
- reasons
- evidence_refs
- 若 FAIL，必须指出哪一条仍未满足
```

---

## F3-R4

### Role Assignment

- Execution: `vs--cc1`
- Review: `Kior-C`
- Compliance: `Antigravity-2`

### Execution Prompt

```text
你是 T2 remediation F3-R4 的执行者 vs--cc1。

目标：
不要硬造当前架构中并不存在的“evidence-first = 证据先于决策”时序语义。
本次修复的目标是：正式降级术语，并把相关代码、测试、报告、完成记录统一改成真实可证明的语义口径。

唯一问题背景：
- F3-R / F3-R2 / F3-R3 连续失败的根因，不是“没有时间字段”，而是“当前实现无法真实证明 evidence-first 的时序含义”
- 因此本轮不再强行证明“先于决策”，而是统一改成当前代码真正能证明的语义

建议目标语义（执行时可采用同义但必须单一一致）：
- `evidence-recorded decision chain`
- 或 `decision-evidence traceability`
- 或其他等价、真实、可证明的术语

必须完成的事：
1. 从测试、docstring、execution_report、completion record 中移除或替换 `evidence-first` 的时序性表述
2. 统一改成当前代码真实能证明的语义口径
3. 保证测试只声称并验证“已记录决策链 / 可追溯时间戳 / 字段存在且匹配”的事实
4. 若保留 `evidence-first` 字样，必须明确标注为“历史术语/非严格时序术语”，不得再写成已验证的强语义

范围：
- 只处理语义降级、术语统一、文案与测试口径对齐
- 不扩大到新的时序架构改造
- 不重构 publish pipeline

禁止：
- 不得继续声称“证据先于决策”已被验证
- 不得通过模糊语言保留双重解释
- 不得新增与本轮目标无关的代码改造

必须交付：
1. 修改后的测试文件
2. 修改后的 execution_report
3. 修改后的 completion record
4. EvidenceRef（指出术语替换和真实语义落点）
5. 明确说明“新统一术语是什么、旧术语如何处理”

完成定义：
- 仓库内与本 shard 相关的表述不再把 `evidence-first` 当作已验证的时序语义
- 测试、报告、完成记录三者口径一致
- 当前系统真实可证明的能力被准确命名
- 无 fake closure 话术残留

输出：
- 修改文件列表
- 统一后的术语
- 旧术语处理策略
- EvidenceRef
- remaining risk
```

### Review Prompt

```text
你是 T2 remediation F3-R4 的审查者 Kior-C。

只审四件事：
1. 是否彻底移除了“evidence-first 已被验证为时序语义”的说法
2. 是否建立了单一、一致、真实的替代术语
3. 测试是否只验证当前代码真实可证明的事实
4. execution_report / completion record / docstring 是否已经统一口径

输出：
- ALLOW / REQUIRES_CHANGES / DENY
- reasons
- evidence_refs
- 对上面四项逐条核对结果
```

### Compliance Prompt

```text
你是 T2 remediation F3-R4 的合规官 Antigravity-2。

请检查：
1. 是否已停止把 `evidence-first` 当作已验证的强时序语义
2. 是否存在新的统一语义口径，且该口径与代码事实一致
3. 是否还有 fake closure 或双重含义表述

如果术语仍会误导为“先于决策已被证明”，直接 FAIL。

输出限制：
- PASS / FAIL
- reasons
- evidence_refs
- 若 FAIL，必须指出残留误导位置
```

---

## F2-C

### Role Assignment

- Compliance: `Antigravity-2`

### Compliance Prompt

```text
你是 T2 remediation F2-C 的合规官 Antigravity-2。

目标：
为 T2-F2 重新出具一份合法、独立的 ComplianceAttestation。

唯一审查输入：
- docs/2026-03-07/T2-F2_completion_record.md
- docs/2026-03-07/verification/T2-F2_execution_report.yaml
- docs/2026-03-07/verification/T2-F2_review_decision.json
- contracts/intents/outer_intent_ingest.yml
- contracts/intents/outer_contract_freeze.yml
- skillforge/src/orchestration/intent_map.yml

必须检查：
1. Compliance 与 Execution 是否角色独立
2. 是否引入 old GM OS full-copy implementation
3. mainline promotion 是否有真实合同落点，不是空状态标签
4. gate_path / evidence_required 是否与当前主线契约一致
5. constitution alignment 是否成立，尤其 outer_contract_freeze

输出限制：
- 只允许输出 PASS 或 FAIL
- 必须附 reasons
- 必须附 evidence_refs
- 若 FAIL，必须给 required_remediation

产出文件：
- docs/2026-03-07/verification/T2-F2_compliance_attestation.json
```
