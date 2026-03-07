# T2 Follow-up Prompt Pack (2026-03-07)

## Scope

This prompt pack covers only `T2 follow-up`:

- `F1` lifecycle and audit canonical contract normalization
- `F2` selective mainline promotion
- `F3` parity regression and replay evidence pack

Hard rules for all shards:

- no actor may self-approve
- no claim of completion without `EvidenceRef`
- no hidden scope expansion
- no old migration-doc asset may silently remain authoritative if a production contract is introduced
- any missing proof must be reported as `REQUIRES_CHANGES`
- every executor must write a completion record in daily docs before handoff

---

## F1

### Role Assignment

- Execution: `vs--cc2`
- Review: `Kior-C`
- Compliance: `Antigravity-2`

### Execution Prompt

```text
你是 T2 follow-up F1 的执行者 vs--cc2。

目标：
把以下 intent 的 canonical 合同命名统一到当前调度口径，并落到生产可引用位置：
- generate_skill_from_repo
- upgrade_skill_revision
- tombstone_skill
- audit_repo_skill

范围：
- 只处理 canonical intent_id / contract filename / contract authoritative location / intent_map 对齐
- 必要时更新引用路径、注释、文档说明
- 不扩大到新建无关功能，不做额外平台重构

必须交付：
1. 代码或合同文件修改（仅限必要文件）
2. execution_report
3. EvidenceRef（指出 canonical 命名统一后的关键位置）
4. completion record（写入每日文档，供主控官统一回收）

完成定义：
- 四个 intent 均有唯一 canonical 名称
- dispatch / contract / intent_map 三层命名一致
- docs 迁移副本若保留，必须明确标注非主 authoritative
- 无活动路径继续引用旧 alias 造成歧义

输出：
- 修改文件列表
- canonical naming 对照表（before -> after）
- 验证方式
- remaining risk
- completion record 文档位置
```

### Review Prompt

```text
你是 T2 follow-up F1 的审查者 Kior-C。

请审查：
- 是否真的统一了 canonical 命名，而不是只改了文档标题
- intent_map、合同路径、调度口径是否仍有分叉
- 是否留下“两个都算主版本”的歧义

只允许输出：
- ALLOW
- REQUIRES_CHANGES
- DENY

必须附：
- reasons
- evidence_refs
- 是否确认 execution completion record 已存在
```

### Compliance Prompt

```text
你是 T2 follow-up F1 的合规官 Antigravity-2。

请检查：
- 是否把 docs 侧迁移草稿伪装成生产合同
- 是否存在无证据宣称“已统一”
- 是否因命名统一引入边界放宽或口径漂移

若证据不足或 authoritative 边界不清，直接 FAIL。
```

---

## F2

### Role Assignment

- Execution: `Antigravity-1`
- Review: `Kior-C`
- Compliance: `Antigravity-2`

### Execution Prompt

```text
你是 T2 follow-up F2 的执行者 Antigravity-1。

目标：
把以下两个已判定为 migrate now 的 selective intents 从 planned 状态提升到 mainline：
- outer_intent_ingest
- outer_contract_freeze

范围：
- 仅处理当前仓库中的 mainline 合同、intent_map、gate path、evidence requirements
- 必须绑定现有 contracts-first + gate + evidence 口径
- 不引入 full-copy old GM OS 实现

必须交付：
1. 代码/合同修改
2. execution_report
3. EvidenceRef（指出 planned -> mainline 的关键变化）
4. completion record（写入每日文档，供主控官统一回收）

完成定义：
- 两个 intent 均不再停留于 l42_planned
- 有明确 contract_path / gate_path / evidence_required
- migration_status 与 integration_level 可被复核
- 不存在只改状态标签、没有实际主线落点的假提升

输出：
- 修改文件列表
- gate/evidence 对照
- 验证方式
- remaining risk
- completion record 文档位置
```

### Review Prompt

```text
你是 T2 follow-up F2 的审查者 Kior-C。

重点检查：
- 是否真的进入 mainline，而不只是把 planned 改名
- gate_path 与 evidence_required 是否符合当前主线
- 是否引入了无合同约束的“空 intent”

输出：
- ALLOW / REQUIRES_CHANGES / DENY
- reasons
- evidence_refs
- 是否确认 execution completion record 已存在
```

### Compliance Prompt

```text
你是 T2 follow-up F2 的合规官 Antigravity-2。

只审以下红线：
- 是否存在 full-copy old GM OS 逻辑的倾向
- 是否绕过 contracts-first 直接用 runtime 口径冒充 mainline
- 是否缺少 EvidenceRef 就宣称完成

不满足即 FAIL。
```

---

## F3

### Role Assignment

- Execution: `vs--cc1`
- Review: `Kior-C`
- Compliance: `Antigravity-2`

### Execution Prompt

```text
你是 T2 follow-up F3 的执行者 vs--cc1。

目标：
补齐以下三项的 replay/parity 可复核证据：
- constitutional default-deny stop behavior
- evidence-first publish chain
- time_semantics at_time replay discipline

范围：
- 只处理测试、验证脚本、最小文档化证据产物
- 必须绑定当前 archive/verification 流程
- 不修改无关业务逻辑

必须交付：
1. 测试或验证产物
2. execution_report
3. 至少一处 EvidenceRef 指向每个目标项
4. completion record（写入每日文档，供主控官统一回收）

完成定义：
- 三个目标均有可复现的 parity/replay artifact
- artifact 可归档并被 Verification Map 或 follow-up gate 引用
- 不再只靠 narrative claim 支撑 parity

输出：
- 新增/修改文件
- 执行结果
- each target 对应的 EvidenceRef
- remaining risk
- completion record 文档位置
```

### Review Prompt

```text
你是 T2 follow-up F3 的审查者 Kior-C。

重点检查：
- artifact 是否真的可复现，而非描述性文档
- default-deny / evidence-first / time_semantics 三项是否都覆盖
- 是否与当前 archive flow 对齐

输出：
- ALLOW / REQUIRES_CHANGES / DENY
- reasons
- evidence_refs
- 是否确认 execution completion record 已存在
```

### Compliance Prompt

```text
你是 T2 follow-up F3 的合规官 Antigravity-2。

请检查：
- 是否存在“加了文档但没有 replay/parity 证据”的假闭环
- 是否放宽 fail-closed 语义
- 是否缺少可追溯 EvidenceRef

证据不足直接 FAIL。
```
