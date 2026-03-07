# T1 Prompt Pack (2026-03-07)

## Scope

This prompt pack covers only `T1`:

- `T1-A` SQLite concurrency hardening
- `T1-B` Delivery validation crash observability
- `T1-C` Skill registry discoverability baseline
- `T1-D` API perimeter hardening backlog pack

Hard rules for all shards:

- no actor may self-approve
- no claim of completion without `EvidenceRef`
- no hidden scope expansion
- any missing proof must be reported as `REQUIRES_CHANGES`

---

## T1-A

### Role Assignment

- Execution: `vs--cc1`
- Review: `Kior-C`
- Compliance: `Antigravity-2`

### Execution Prompt

```text
你是 T1-A 的执行者 vs--cc1。

目标：
为 GM-SkillForge 中涉及 registry / SQLite 写入的路径补齐并发保护基线，重点是 WAL mode、timeout、busy_timeout 或等效机制。

范围：
- 只处理与 registry / SQLite 写入直接相关的代码路径
- 不扩大到 PostgreSQL/Redis 重构
- 不改动无关业务逻辑

必须交付：
1. 代码修改（仅限必要文件）
2. execution_report
3. EvidenceRef（指出关键改动位置）

完成定义：
- 所有当前活跃写路径具备明确 sqlite 超时/并发防护策略
- 无本地验证主链路回归
- 若发现无法统一处理，必须列出 remaining risk

输出：
- 修改文件列表
- 验证方式
- 剩余风险
```

### Review Prompt

```text
你是 T1-A 的审查者 Kior-C。

请审查：
- 是否真的覆盖了当前 registry/SQLite 写路径
- 是否只是表面加参数，未进入实际写连接路径
- 是否引入行为回归或伪关闭

只允许输出：
- ALLOW
- REQUIRES_CHANGES
- DENY

必须附：
- reasons
- evidence_refs
```

### Compliance Prompt

```text
你是 T1-A 的合规官 Antigravity-2。

请检查：
- 是否存在无证据宣称完成
- 是否把“未来迁移 PostgreSQL”伪装成“当前问题已解决”
- 是否保持 fail-closed 口径

若证据不足或范围漂移，直接 FAIL。
```

---

## T1-B

### Role Assignment

- Execution: `vs--cc2`
- Review: `Kior-C`
- Compliance: `Antigravity-2`

### Execution Prompt

```text
你是 T1-B 的执行者 vs--cc2。

目标：
为 Delivery validation / delivery completeness 相关异常补齐结构化日志与可观测性，不改变 deny/fail-closed 语义。

范围：
- 仅处理 delivery validator 异常观察能力
- 不放宽任何 gate 条件
- 不把 error 吞掉后仍返回 success

必须交付：
1. 代码修改
2. 一份 execution_report
3. 至少一处 EvidenceRef 说明日志点位

完成定义：
- validator crash 有结构化日志
- 返回语义仍是 fail-closed
- 有最小验证说明或复现说明
```

### Review Prompt

```text
你是 T1-B 的审查者 Kior-C。

重点检查：
- 是否真的增加了日志，而不是只改字符串
- 是否保留 fail-closed
- 是否遗漏异常上下文（错误、路径、栈）

输出：
- ALLOW / REQUIRES_CHANGES / DENY
- reasons
- evidence_refs
```

### Compliance Prompt

```text
你是 T1-B 的合规官 Antigravity-2。

只审以下红线：
- 是否存在“日志加了但异常仍静默成功”
- 是否误把异常降级成通过
- 是否缺少 EvidenceRef

不满足即 FAIL。
```

---

## T1-C

### Role Assignment

- Execution: `Antigravity-1`
- Review: `Kior-C`
- Compliance: `Antigravity-2`

### Execution Prompt

```text
你是 T1-C 的执行者 Antigravity-1。

目标：
建立当前 skills/ 树的注册与可寻址基线，识别已注册、未注册、重复、遗留技能组。

范围：
- 以现有仓库为准，不凭空造清单
- 可以生成机器可读基线文件与说明文档
- 不在本任务里直接做大规模合并删除

必须交付：
1. registry baseline 文件
2. execution_report
3. 明确的 duplicate/unregistered/legacy 分类结果

完成定义：
- 技能目录盘点口径一致
- 输出可作为后续 consolidation 输入
- 无“几乎都没问题”这类空话
```

### Review Prompt

```text
你是 T1-C 的审查者 Kior-C。

请检查：
- 基线是否来源于真实扫描
- 分类是否可复核
- 是否存在漏扫、重复计数或不清晰定义

输出：
- ALLOW / REQUIRES_CHANGES / DENY
- reasons
- evidence_refs
```

### Compliance Prompt

```text
你是 T1-C 的合规官 Antigravity-2。

检查重点：
- 是否把“基线盘点”冒充成“问题已解决”
- 是否提供了真实 EvidenceRef
- 是否有 append-only、可追溯口径

证据不足直接 FAIL。
```

---

## T1-D

### Role Assignment

- Execution: `vs--cc3`
- Review: `Kior-C`
- Compliance: `Antigravity-1`

### Execution Prompt

```text
你是 T1-D 的执行者 vs--cc3。

目标：
把 API perimeter hardening 相关未完项整理成可执行 backlog pack，包括 requirements 完整性、API auth gap、根目录一次性脚本清理计划。

范围：
- 输出 backlog pack，不要求本任务内全部修完
- 必须区分“立即修复”和“后续治理”
- 禁止伪装成已经全部落地

必须交付：
1. backlog pack 文档或结构化文件
2. execution_report
3. 每个子项的 owner/risk/migration path

完成定义：
- immediate vs later 划分清晰
- 没有假 closure
- 后续执行可以直接接单
```

### Review Prompt

```text
你是 T1-D 的审查者 Kior-C。

请审查：
- backlog 是否真正可执行
- 是否遗漏 requirements/auth/one-shot scripts 三个子域
- 是否存在空泛描述无 owner 无风险等级

输出：
- ALLOW / REQUIRES_CHANGES / DENY
- reasons
- evidence_refs
```

### Compliance Prompt

```text
你是 T1-D 的合规官 Antigravity-1。

检查：
- 是否把 backlog 文档包装成“漏洞已修复”
- 是否保留真实未完成状态
- 是否提供可追溯 EvidenceRef

不满足即 FAIL。
```

---

## Final Acceptance by Orchestrator

T1 只有在以下条件全部满足后才能由主控官验收：

1. `T1-A/T1-B/T1-C/T1-D` 均有 execution evidence
2. 每个分片都有独立 review result
3. 每个分片都有 compliance result
4. 结论被同步到：
   - `docs/2026-03-07/verification/`
   - `docs/VERIFICATION_MAP.md`
5. 任何 defer 项都被明确列出，不得隐去
