# Wave 3 约束文档：3D RAG 与数据飞轮

> Constitution SSOT: `docs/2026-02-16/constitution_v1.md`
> Contract: `skillforge/src/contracts/rag_3d.yaml`

## 0. 文档目的

固化 GM-SkillForge Wave 3 阶段的 3D RAG 与数据飞轮约束，作为实施与审计的不可回退边界。

## 1. 3D RAG 正确拆分

### 1.1 内核化（不可 Skill 取代）
- **at-time 复现口径**：同一 `repo@commit + at_time` 必须可复现同一 revision 与证据引用
- **tombstone 语义**：已下架条目不可绕过，检索时必须标记
- **system-of-record/index schema**：索引结构由内核定义，Skill 不可篡改

### 1.2 Skill 化（可替换）
- 抽取/切分策略
- 索引构建/更新
- 检索策略/重排
- 评测/优化

### 1.3 目标
- 历史可复现检索
- tombstone 不可绕过
- 证据链完整可追溯

## 2. 四条验收标准（Fail-Closed）

### AC-1: AtTimeReference 完整性
**条件**：任一 RAG 检索请求必须携带完整的 `AtTimeReference` 结构。

**字段要求**：
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| uri | string(URI) | 是 | 资源定位符 |
| commit_sha | string(40-char hex) | 是 | Git commit 指纹 |
| at_time | string(ISO-8601) | 是 | 时间点锚定 |
| tombstone | boolean | 是 | 下架标记（默认 false） |

**Fail-Closed 规则**：
- `FC-AC1-1`: uri 无效 -> REJECTED
- `FC-AC1-2`: commit_sha 非 40 位十六进制 -> REJECTED
- `FC-AC1-3`: at_time 非 ISO-8601 格式 -> REJECTED
- `FC-AC1-4`: tombstone 字段缺失 -> REJECTED

### AC-2: ExperienceEntry 结构合规
**条件**：每次 Experience Capture 必须产出符合规范的 `ExperienceEntry`。

**字段要求**：
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| issue_key | string | 是 | 问题键（如 GATE.FC-2 / RISK.L5） |
| evidence_ref | string | 是 | 证据引用路径或 URI |
| source_stage | string | 是 | 来源阶段（audit/fix/test） |
| summary | string | 是 | 经验摘要 |
| action | string | 是 | 修复/防御动作 |
| revision | string | 是 | 绑定 skill revision |
| created_at | string(ISO-8601) | 是 | 创建时间 |
| content_hash | string(SHA-256) | 是 | 经验内容哈希 |

**Fail-Closed 规则**：
- `FC-AC2-1`: issue_key 缺失 -> REJECTED
- `FC-AC2-2`: evidence_ref 缺失或无效 -> REJECTED
- `FC-AC2-3`: revision 不匹配 -> REJECTED
- `FC-AC2-4`: content_hash 校验失败 -> REJECTED

### AC-3: evolution.json 写入规则
**条件**：Experience Capture 产物必须正确写入 `evolution.json`。

**写入规则**：
1. **Append-Only**：不得覆盖历史项
2. **去重**：以 `content_hash` 为主键，命中同哈希仅增加引用计数
3. **固化时机**：在 `pack_audit_and_publish` Gate 时固化进 L3 AuditPack

**Fail-Closed 规则**：
- `FC-AC3-1`: 检测到覆盖操作 -> REJECTED
- `FC-AC3-2`: 去重逻辑失效 -> REJECTED
- `FC-AC3-3`: 固化进 AuditPack 失败 -> REJECTED
- `FC-AC3-4`: evolution.json 字段缺失 -> REJECTED

### AC-4: 闭环完整性
**条件**：从 RAG 检索到回灌 Input 必须形成完整闭环。

**闭环路径**：
```
AtTimeReference -> RAG Query -> ExperienceEntry -> evolution.json -> AuditPack -> 回灌 Input
```

**验证点**：
1. `AtTimeReference` 可追溯至原始 `repo@commit`
2. `ExperienceEntry` 绑定有效 `IssueKey + EvidenceRef`
3. `evolution.json` 已固化进 L3 AuditPack
4. 回灌数据可验证完整性

**Fail-Closed 规则**：
- `FC-AC4-1`: AtTimeReference 不可追溯 -> REJECTED
- `FC-AC4-2`: EvidenceRef 链断裂 -> REJECTED
- `FC-AC4-3`: AuditPack 缺失 evolution.json -> REJECTED
- `FC-AC4-4`: 回灌数据校验失败 -> REJECTED

## 3. 角色分工

### SkillForge（Governor/内核）
- at-time/tombstone 口径定义与执行
- system-of-record 索引管理
- Experience Capture 固化
- permit 签发

### n8n（Orchestrator）
- 触发/路由/重试/通知
- 外部系统集成
- 不参与裁决

### 硬约束
- n8n 不裁决
- 无 permit 不发布
- tombstone 不可绕过

## 4. 违规判定（Fail-Closed）

任一条违反即 `REJECTED`，不得"部分通过"：
1. AtTimeReference 字段缺失或格式错误
2. ExperienceEntry 缺少 IssueKey 或 EvidenceRef
3. evolution.json 覆盖历史或固化失败
4. 闭环链断裂或不可验证

## 5. 生效与优先级

1. 本文档生效后，任何 3D RAG 相关设计/实现与本文冲突时，以本文为准。
2. 优先级：`Constitution > 不可回退架构约束 v1 > Wave 3 约束 > 其他设计文档`

## 6. 版本与追溯

| 版本 | 日期 | 变更说明 | evidence_ref |
|------|------|----------|--------------|
| v1.0.0 | 2026-02-17 | 初始冻结 | T-W3-A:vs--cc1 |
