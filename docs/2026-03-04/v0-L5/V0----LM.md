| 层级                   | 目标（北极星）                      | 范围（做什么）                                                                                                                                                                                                                                                                                                                    | 验收（怎么算达标）                                                                                                                      | 不做什么（硬禁止）                                                                                           | 商业化对应 Tier                                                                |
| -------------------- | ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| **v0：治理内核封板**        | **能裁决、能放行、能复核**（把“玄学”变成确定性）  | - Demand DSL（四件套）+ schema 校验  <br>- Manifest Schema v0 + `static_rules_v0.yml`（安全红线）<br>- 三哈希：`demand_hash/contract_hash/decision_hash`<br>- L3 AuditPack（manifest/decisions/policy_matrix/checksums）<br>- Permit Issuer（绑定三哈希 + `policy_hash` + `audit_pack_hash`）<br>- 合规运行终端最小接口（RunRequest/RunResult/ArtifactManifest） | - **同输入→三哈希一致**（需求复现）<br>- **篡改 pack/证据→校验失败**（不可篡改）<br>- **无 Permit→发布/整合被拦截**（不可绕过）                                          | - 不做跨模块污点分析/语义追踪<br>- 不做“无限生成”/无配额 API<br>- 不做真实生产外部动作（仅 tests-only/dry-run）<br>- 不做多 Agent 自治/动态规划 | **Free/Trial（受限）**：演示静态 L3 pack（少量）<br>**Pro（起步）**：有限额度完整 L3 + Permit（可选） |
| **v1：可用性与成功率**       | **能交付、能批量、能迭代提效**（硬度不变，体验上去） | - NL→Demand DSL 稳定化（blocking 澄清≤3）<br>- NL↔DSL/Contract 一致性校验<br>- Gap Analysis v0-min（可喂 AI 修复 + 可复核）<br>- 自动回炉重跑 Gate（N 次上限）<br>- 计量与配额（Build/Run/Storage credits）+ 幂等 request_id<br>- 对外受控 API：run/status/auditpack/permit                                                                                              | - **一次通过率 ≥ 80%（样本集）**<br>- FAIL 必产 Gap + required_changes（可执行）<br>- 迭代合规：哈希变化必带 diff+rationale+tombstone<br>- Permit 仍是唯一放行凭证 | - 不放松安全红线（BLOCKER 不可降级）<br>- 不开放“直接发布/上架”API<br>- 不引入复杂工程 IR（Blueprint/Plan）硬约束                     | **Pro（主力）**：高额度 Build + 中额度 Run + RAG 历史<br>**Team（初版）**：多人协作/共享宪法/批量队列   |
| **L4：规模化自动迭代与工程 IR** | **系统自己变强**（规模化治理+结构标准化）      | - Architecture Blueprint IR + PlanSpec（你定义的 IR）<br>- `blueprint_hash/plan_hash`（不混入 contract_hash）<br>- 代码↔蓝图一致性 Gate（接口/模块边界/拓扑）<br>- 黄金样例库与回归基准（fixtures 锁 commit）<br>- 批量生成/批量审查/队列化/重试<br>-（可选）多裁判：规则为主、模型为辅                                                                                                           | - 批量吞吐稳定（幂等+队列+可观测）<br>- 自动迭代降低人工介入（回炉次数下降）<br>- 工程复现：blueprint/plan hash 稳定<br>- 不破坏 v0 信任根（Permit/三哈希/证据）                    | - 不把 blueprint/plan 混进需求口径（contract_hash）<br>- 不让模型自判合规（裁决仍由 Gate+证据）                               | **Team（成熟）**：组织级审批、批量生产线、组织 Permit<br>**Enterprise（切入）**：定制 Gate/策略、审计留存  |
| **L5：执行级证明与企业级认证**   | **执行可证明、外部可审计**（合规护城河）       | - 强执行证明（环境指纹/依赖锁/可重复验证）<br>- 供应链治理（SBOM/依赖签名/漏洞/许可深化）<br>- Attestation Diff（模型自述 vs 系统裁决差异，证据化）<br>- 私有部署/SSO/不可篡改留存/白标认证/SLA                                                                                                                                                                                              | - 同 revision 在受信环境可重复验证（执行级复现）<br>- 外部审计可独立复核（少信任假设）<br>- 留存/权限/合规要求可配置并可证明                                                    | - 不为了通过率牺牲证明强度<br>- 不把“对比审计”做成无证据营销（必须 EvidenceRef）                                                 | **Enterprise（主战场）**：私有部署+合规证明+认证服务<br>**高端年费/SLA**：对标治理预算带宽               |
-------------------

整体路径建议走 **“先封板治理内核（v0）→ 提升生成成功率与对外可用性（v1）→ 规模化自动迭代与生态标准化（L4）→ 执行级证明与企业级合规认证（L5）”**。每一层都要有明确的“不可变接口+验收门禁”，否则一定返工。

置信度：0.87

关键风险点：

1. v0 未封板（hash/permit/evidence/rules）就上自动化与生态 → 口径漂移
2. 过早做 L4/L5（跨模块追踪/全执行证明）→ 工程量指数爆炸
3. 规则资产缺版本治理与申诉/tombstone → 规则债反噬

---

# 路径布局总览（v0 → v1 → L4 → L5）

## v0：治理内核封板（“能裁决、能放行、能复核”）

**北极星**：任何结果是否可上生产，只由 **GateDecision + EvidenceRef + AuditPack + Permit** 决定。
**范围**（你已基本定）：

* Demand DSL（四件套）+ schema 校验
* Manifest Schema v0 + static_rules_v0.yml（安全红线）
* 三哈希：demand_hash / contract_hash / decision_hash
* L3 AuditPack（manifest/decisions/policy_matrix/checksums）
* Permit Issuer（绑定三哈希 + policy_hash + audit_pack_hash）
* 合规运行终端最小接口（RunRequest/RunResult/ArtifactManifest），执行只产 artifacts

**封板验收（必须全过）**

* 同输入 → 三哈希一致（需求复现）
* 篡改 pack/证据 → 校验失败（不可篡改）
* 无 Permit → 发布/整合被拦截（不可绕过）

**产出资产**：规则库雏形、AuditPack 规范、Permit 信任根。

---

## v1：可用性与成功率（“能交付、能批量、能迭代提效”）

**北极星**：把 v0 的硬度保留不动，把体验与成功率做上去。
**重点能力**：

1. **NL→Demand DSL 稳定化**（少澄清、低漂移）

   * 4 模式题库化澄清（blocking ≤3）
   * 一致性校验（NL↔DSL/Contract）
2. **Gap Analysis v0-min**（可喂 AI 修复 + 审计可复核）

   * required_changes 结构化
   * 自动回炉重跑 Gate（最多 N 次）
3. **配额与计量**（Build/Run/Storage credits）

   * API 埋点与幂等 request_id
4. **对外 API v0**（受控）

   * run/status/auditpack/permit（不开放发布）

**v1 验收指标（建议）**

* 20 条样本一次通过率 ≥ 80%（在不放松红线的前提下）
* FAIL 都能产 Gap + required_changes（可执行）
* 迭代合规：hash 变化必带 diff+rationale+tombstone

**产出资产**：高纯度失败—修复语料、模板库、稳定需求口径。

---

## L4：规模化自动迭代与工程 IR（“系统自己变强”）

**北极星**：在不改 v0 信任根的前提下，实现**大规模自动化改进**与**工程结构标准化**。
**新增能力**：

1. **Blueprint IR + PlanSpec**（你刚要的两套 IR）

   * blueprint_hash / plan_hash（不混入 contract_hash）
   * 代码与蓝图一致性 Gate（接口/模块边界/拓扑）
2. **自动回归与黄金样例库**

   * 固定 repo fixtures + 锁 commit_sha + 稳定评测
3. **跨模型/多裁判机制**（可选）

   * 规则裁决为主，模型裁决为辅（避免黑箱）
4. **生态集成**

   * n8n/OpenClaw/MCP 适配器标准化
   * 组织级审批流（Team/Enterprise 核心）

**L4 验收指标（建议）**

* 批量任务稳定吞吐（队列化/重试/幂等）
* 自动迭代减少人工介入（平均回炉次数下降）
* blueprint_hash/plan_hash 稳定复现（工程复现成立）

**产出资产**：工程蓝图资产库、可复用计划库、批量治理能力。

---

## L5：执行级证明与企业级认证（“合规护城河”）

**北极星**：不仅“静态可裁决”，还要“执行可证明”；不仅内部可复核，还要外部可审计。
**新增能力**：

1. **强执行证明**

   * 受信执行环境（更严格的 runtime attestation）
   * 完整链路证据：运行产物、环境指纹、依赖锁、可再现执行
2. **供应链与依赖治理**

   * SBOM、依赖签名、漏洞扫描、许可审计深化
3. **Attestation Diff（你提的隔离层）**

   * 模型自述 vs 系统裁决差异，证据化、可对比基准化
4. **企业合规包**

   * SSO、审计留存、不可篡改存证、白标认证、SLA

**L5 验收指标（建议）**

* 同 revision 在受信环境中可重复验证（执行级复现）
* 外部审计可独立复核（无需信任你们服务端）
* 规则/证据留存满足合规要求（行业/地区差异化）

**产出资产**：行业级审计标准、认证服务、强信任执行与存证体系。

---

# 每一层的“不可变内核”与“可变外壳”

**不可变（从 v0 起就锁死，后面不返工）**

* 三哈希口径 + policy_hash
* EvidenceRef / AuditPack / Permit 结构
* 三权分立边界（执行不裁决、审计不发布、合规签 Permit）

**可变（每一层都可以迭代）**

* NL 解析器、模板库、RAG 策略
* 修复策略与回炉调度
* Blueprint/Plan 的丰富度
* 执行终端的适配与加速

---

