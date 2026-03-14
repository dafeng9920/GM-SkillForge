# T-FE-04: Permit 页面规格书

> **任务 ID**: T-FE-04
> **执行者**: Kior-B
> **审查者**: Antigravity-2
> **合规官**: vs--cc3
> **日期**: 2026-03-12
> **依赖**: T-FE-01 (ALLOW)

---

## 一、PreflightChecklist

### 1.1 Fail-Closed 风险枚举

| 风险类别 | 潜在绕过路径 | 防御措施 |
|---------|-------------|---------|
| 成功页化 | Permit 页面可能被设计成大绿勾成功页，弱化正式凭证感 | 强制"证书抬头"设计，使用正式文档语言，禁止使用营销式成功表达 |
| 语义混淆 | 可能暗示"Audit pass = Release approved" | 在 Core Decision Block 中显式强调"Audit pass is not release approval. Permit is." |
| 绑定缺失 | Permit 可能与 revision/hash 解耦，失去可追溯性 | 强制绑定 revision / contract_hash / decision_hash / audit basis |
| 范围弱化 | 可能弱化放行范围、附加条件、失效触发器 | 明确 Release Scope / Conditions / Lifecycle 为必填模块 |
| 角色模糊 | 可能弱化签发角色、生命周期状态 | 明确 Compliance Signature 为必填，Permit Lifecycle 为可视化时间线 |

### 1.2 依赖环境

| 依赖项 | 当前状态 | 必需值 |
|-------|---------|-------|
| T-FE-01 IA Spec | ALLOW | 已确立 Permit 页面角色与职责边界 |
| 三页主链定义 | 已定义 | Permit 为正式放行凭证页面 |
| Audit Detail 规格 | 已定义 | Audit Basis 关联关系 |

### 1.3 历史债务扫描

| 债务类型 | 位置 | 处理策略 |
|---------|-----|---------|
| 现有 Permit 可能偏向成功页 | ui/app/src/pages/ | 本规格明确禁止项，后续 T-FE-06 裁剪 |
| 缺失 revision/hash 绑定 | 无现有实现 | 本规格强制绑定 |

---

## 二、ExecutionContract

### 2.1 Input Constraints

**允许读取的文件:**
- `docs/2026-03-12/前端重构_AI军团任务分发单_v2.md`
- `docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md`
- `docs/2026-03-12/"治理与放行中枢"的前端设计.md`
- `docs/2026-03-12/verification/T-FE-01_ia_spec.md`
- `multi-ai-collaboration.md`
- `docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md`
- `docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md`

**允许修改的文件:**
- 新建 `docs/2026-03-12/verification/T-FE-04_permit_spec.md` (本文件)

**绝对禁止:**
- 修改现有前端代码实现
- 定义具体组件视觉实现细节
- 把 Permit 页面做成大绿勾成功页
- 出现与 revision/hash 解耦的 Permit
- 弱化范围、附加条件、失效条件
- 越权写到具体组件实现
- 暗示 "Audit pass = Release approved"

### 2.2 Output Definition

**交付物:**
- 本 Permit 规格文档，包含：
  1. Permit 页面目标
  2. Permit 页面骨架
  3. 模块列表与模块优先级
  4. 核心模块详细规格 (8 个必填模块)
  5. 状态设计与交互
  6. 禁止展示项
  7. Hash 绑定要求

**回滚方案:**
- 本文档为规格说明，不涉及代码变更，无需回滚
- 如规格有误，可通过 Review/Compliance 流程修正

### 2.3 Gate / Acceptance Check

**手动检查:**
- [ ] 是否体现放行范围、附加条件、失效触发器
- [ ] 是否体现生命周期与签发角色
- [ ] 是否未把 Permit 页面做成大绿勾成功页
- [ ] 是否未出现与 revision/hash 解耦的 Permit
- [ ] 是否显式强调 "Audit pass is not release approval. Permit is."

---

## 三、RequiredChanges

### 3.1 Permit 页面目标

#### 3.1.1 核心定位

Permit 是 **正式放行凭证页面**，不是成功提示页，不是状态页。

用户进入 Permit 页面后，必须能立即回答四个问题：
1. **这个 Permit 允许什么？** → Release Scope
2. **这个 Permit 有什么条件？** → Conditions
3. **这个 Permit 基于什么审计结论？** → Audit Basis
4. **这个 Permit 什么时候会失效？** → Lifecycle + Residual Risk

#### 3.1.2 设计原则

| 原则 | 说明 | 禁止 |
|-----|------|-----|
| **凭证优先** | Permit 必须像正式证书，有证书抬头、签名、印章 | 使用成功页/状态页样式 |
| **边界明确** | 必须明确放行范围、附加条件、失效触发器 | 模糊表述"已批准" |
| **追溯完整** | 必须绑定 revision / contract_hash / decision_hash / audit basis | 出现解耦的 Permit |
| **语义清晰** | 必须区分 Audit pass 与 Permit issuance | 暗示"审计通过即放行" |
| **风险透明** | 必须告知残余风险、监控期望、重审触发器 | 掩盖风险或限制 |

#### 3.1.3 与其他页面的职责边界

| 页面 | 职责 | 不在此页 |
|-----|------|---------|
| **Permit** | 正式放行凭证、范围、条件、生命周期、签名 | 审计详情、裁决解释、证据链 |
| **Audit Detail** | 单资产裁决详情、证据链、红线/可修复项 | 放行凭证、范围条件 |
| **Dashboard** | 总览状态、优先队列、门禁健康 | 单资产放行凭证详情 |

---

### 3.2 Permit 页面骨架

```
┌──────────────────────────────────────────────────────────────────────────┐
│ Top Nav                                                                 │
├──────────────────────────────────────────────────────────────────────────┤
│ Breadcrumb                                                              │
│ Release / Permit / PMT-2026-0312-014                                    │
├──────────────────────────────────────────────────────────────────────────┤
│ Permit Header (证书抬头)                                                  │
│ Permit ID: PMT-2026-0312-014                                             │
│ Asset: Skill A            Revision: R-014                                │
│ Status: [Active]          Effective: 2026-03-12                          │
│ Signed by: Compliance-01 Scope: Production / Internal                    │
│ [Export Permit] [View Linked Audit] [Revoke Permit] [View History]       │
├──────────────────────────────────────────────────────────────────────────┤
│ Core Decision Block (核心决策块 - 最高视觉权重)                            │
│ ┌──────────────────────────────────────────────────────────────────────┐ │
│ │ Permit granted                                                      │ │
│ │ Audit pass is not release approval. Permit is.                      │ │
│ │ This permit is bound to revision R-014 and current rulepack v1.0    │ │
│ │ Allowed for release within declared scope only                      │ │
│ └──────────────────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────┤
│ Main Grid Row 1                                                         │
│ ┌──────────────────────────────┐ ┌────────────────────────────────────┐ │
│ │ Release Scope                │ │ Conditions                         │ │
│ │ env / asset / boundary       │ │ must hold / invalidation triggers  │ │
│ └──────────────────────────────┘ └────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────┤
│ Main Grid Row 2                                                         │
│ ┌──────────────────────────────┐ ┌────────────────────────────────────┐ │
│ │ Audit Basis                  │ │ Evidence / Policy Basis            │ │
│ │ linked auditpack, hashes     │ │ evidence summary, ruleset version  │ │
│ └──────────────────────────────┘ └────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────┤
│ Main Grid Row 3                                                         │
│ ┌──────────────────────────────┐ ┌────────────────────────────────────┐ │
│ │ Permit Lifecycle             │ │ Compliance Signature               │ │
│ │ audit > ready > issued ...   │ │ signer, note, timestamp            │ │
│ └──────────────────────────────┘ └────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────┤
│ Residual Risk Reminder (残余风险提醒)                                     │
│ [Known operational risks] [Monitoring expectations] [Re-audit triggers] │
└──────────────────────────────────────────────────────────────────────────┘
```

---

### 3.3 模块列表与模块优先级

#### 3.3.1 P0 模块 (MUST - 必填)

| 模块名称 | 优先级 | 核心字段 | 位置 |
|---------|-------|---------|------|
| **Permit Header** | P0 | Permit ID, Asset, Revision, Status, Effective, Signed by, Scope | 页面顶部 |
| **Core Decision Block** | P0 | 主结论, 副说明, 绑定说明, 动作建议 | Header 下方，最高视觉权重 |
| **Release Scope** | P0 | Environment, Asset Boundary, Revision Scope, Invocation Boundary, Valid Use Context | Main Grid Row 1 左侧 |
| **Conditions** | P0 | Must hold, Invalidation triggers, Monitoring requirements | Main Grid Row 1 右侧 |
| **Audit Basis** | P0 | Linked Audit ID, decision_hash, contract_hash, audit version | Main Grid Row 2 左侧 |
| **Evidence / Policy Basis** | P0 | Evidence summary, Rulepack version, Constitution version | Main Grid Row 2 右侧 |
| **Permit Lifecycle** | P0 | 时间线: Audit → Ready → Issued → Active → [Revoked/Expired/Superseded] | Main Grid Row 3 左侧 |
| **Compliance Signature** | P0 | signed by, signed at, signature note, approval remarks | Main Grid Row 3 右侧 |

#### 3.3.2 P1 模块 (SHOULD - 强烈建议)

| 模块名称 | 优先级 | 核心字段 | 位置 |
|---------|-------|---------|------|
| **Residual Risk Reminder** | P1 | Known risks, Monitoring expectations, Re-audit triggers | 页面底部 |
| **Breadcrumb** | P1 | Release / Permit / Permit ID | Header 上方 |

---

### 3.4 核心模块详细规格

#### 3.4.1 Permit Header (证书抬头)

**位置**: 页面顶部，Breadcrumb 下方

**设计要求**: 必须像正式证书抬头，使用正式文档语言，禁止使用营销式表达

**核心字段:**

| 字段 | 说明 | 示例 |
|-----|------|-----|
| **Permit ID** | 许可证唯一标识 | PMT-2026-0312-014 |
| **Asset Name** | 资产名称 | Payment Agent Skill |
| **Revision** | 版本号 | R-014 |
| **Status** | 当前状态 | Active / Pending / Revoked / Expired / Superseded |
| **Effective Date** | 生效日期 | 2026-03-12 |
| **Signed by** | 签发者 | Compliance-01 |
| **Scope** | 放行范围 | Production / Internal / Client Delivery |

**右侧动作:**

| CTA 文本 | 目标 | 条件 |
|---------|------|-----|
| **Export Permit** | 导出 Permit 为 PDF/文档 | 所有状态 |
| **View Linked Audit** | 跳转 Audit Detail 页面 | 所有状态 |
| **Revoke Permit** | 撤销当前 Permit | Active 状态 |
| **View History** | 查看 Permit 变更历史 | 所有状态 |

**禁止:**
- ❌ 使用"已批准"、"通过"、"成功"等营销式表达
- ❌ 使用大绿勾、庆祝动画等成功页样式
- ❌ 隐藏 Revision 或 Permit ID

---

#### 3.4.2 Core Decision Block (核心决策块)

**位置**: Permit Header 下方，首屏最高视觉权重

**设计要求**: 大卡片，视觉强调最强，必须显式强调"Audit pass is not release approval. Permit is."

**内容结构:**

```
┌──────────────────────────────────────────────────────────────────────┐
│ Permit granted                                                        │
│                                                                      │
│ Audit pass is not release approval. Permit is.                       │
│                                                                      │
│ This permit is bound to revision R-014 and current rulepack v1.0     │
│                                                                      │
│ Allowed for release within declared scope only                       │
└──────────────────────────────────────────────────────────────────────┘
```

**字段说明:**

| 字段 | 说明 | 语言要求 |
|-----|------|---------|
| **主结论** | Permit granted / Permit denied / Permit revoked | 使用正式凭证语言 |
| **副说明** | Audit pass is not release approval. Permit is. | 必须显式区分 Audit 与 Permit |
| **绑定说明** | Bound to revision R-014, contract_hash xxx, decision_hash xxx | 必须包含 revision 与 hash 绑定 |
| **动作建议** | Allowed for release within declared scope only | 强调"within declared scope" |

**禁止:**
- ❌ 省略副说明 "Audit pass is not release approval. Permit is."
- ❌ 省略绑定说明中的 revision 或 hash
- ❌ 使用"You can now deploy"等口语化表达
- ❌ 使用"恭喜"、"成功"等营销式语言

---

#### 3.4.3 Release Scope (放行范围)

**位置**: Main Grid Row 1 左侧

**核心字段:**

| 字段 | 说明 | 示例 |
|-----|------|-----|
| **Environment** | 放行环境 | Production / Internal / Client Delivery |
| **Asset Boundary** | 资产边界 | Payment Agent Skill (R-014 only) |
| **Revision Scope** | 版本范围 | R-014 only (不得覆盖其他版本) |
| **Invocation Boundary** | 调用边界 | Declared only (仅声明的调用路径) |
| **Valid Use Context** | 有效使用上下文 | Internal operations only / Client-facing delivery |

**设计要求:**
- 告诉用户"放行不是无限授权"
- 每个字段必须有明确值，不得为空
- 使用列表或卡片形式展示，清晰易读

**禁止:**
- ❌ 使用"所有环境"、"不限"等模糊表述
- ❌ 省略 Revision Scope
- ❌ 隐藏 Invocation Boundary

---

#### 3.4.4 Conditions (生效条件)

**位置**: Main Grid Row 1 右侧

**核心字段:**

| 字段 | 说明 | 示例 |
|-----|------|-----|
| **Must hold conditions** | 必须保持的条件 | Must remain unchanged from certified revision |
| **Re-audit triggers** | 重审触发器 | Re-audit required on contract change |
| **Invalidation triggers** | 失效触发器 | Permit invalidates on rulepack mismatch |
| **Undeclared execution** | 未声明执行路径 | Permit invalidates on undeclared execution path |
| **Monitoring requirements** | 监控要求 | Monitoring expected for runtime drift |

**设计要求:**
- 体现"稳定治理"原则
- 明确告知 Permit 的边界与限制
- 使用条件列表形式，每个条件独立一行

**禁止:**
- ❌ 省略失效触发器
- ❌ 使用"无特殊条件"等模糊表述
- ❌ 隐藏监控要求

---

#### 3.4.5 Audit Basis (审计基础)

**位置**: Main Grid Row 2 左侧

**核心字段:**

| 字段 | 说明 | 示例 |
|-----|------|-----|
| **Linked Audit ID** | 关联的审计 ID | AUD-2026-0312-014 |
| **Audit result** | 审计结果 | Passed / Conditional pass |
| **decision_hash** | 决策哈希 | sha256:a1b2c3d4... |
| **contract_hash** | 合同哈希 | sha256:e5f6g7h8... |
| **audit version** | 审计版本 | v1.0 |
| **reviewed at** | 审计时间 | 2026-03-12T10:00:00Z |

**右侧动作:**
- `Open Audit Detail` - 跳转 Audit Detail 页面

**设计要求:**
- 必须包含 decision_hash 和 contract_hash
- 必须关联到具体的 Audit ID
- 提供"查看审计详情"的入口

**禁止:**
- ❌ 省略 decision_hash 或 contract_hash
- ❌ 出现解耦的 Permit (无 Audit Basis)
- ❌ 使用"审计通过"简化表述，必须使用具体 Audit ID

---

#### 3.4.6 Evidence / Policy Basis (证据与策略基础)

**位置**: Main Grid Row 2 右侧

**核心字段:**

| 字段 | 说明 | 示例 |
|-----|------|-----|
| **Evidence summary count** | 证据摘要数量 | 11 evidence items |
| **Evidence sufficiency level** | 证据充分性等级 | Sufficient / Conditional |
| **Rulepack version** | 规则包版本 | v1.0 |
| **Constitution version** | 宪法版本 | v2.1 |
| **Compliance note** | 合规备注 | Additional monitoring required for runtime drift |

**设计要求:**
- 展示 Permit 的策略依据
- 体现"有证据支撑"的放行决策
- 提供规则包版本的可追溯性

**禁止:**
- ❌ 省略 Rulepack version 或 Constitution version
- ❌ 隐藏 Evidence sufficiency level
- ❌ 使用"符合所有规则"等模糊表述

---

#### 3.4.7 Permit Lifecycle (许可证生命周期)

**位置**: Main Grid Row 3 左侧

**时间线设计:**

```
Audit Completed (2026-03-10T15:00:00Z)
    ↓
Passed Audit (2026-03-11T10:00:00Z)
    ↓
Ready for Permit (2026-03-11T14:00:00Z)
    ↓
Permit Issued (2026-03-12T09:00:00Z) ← Compliance-01
    ↓
Active (2026-03-12T10:00:00Z)
    ↓
[Optional] Revoked / Superseded / Expired
```

**交互:**
- 点击任一节点可查看详细时间、操作者、说明
- 当前状态节点高亮显示
- 已完成节点显示时间戳
- 未发生节点显示"(Optional)"标记

**设计要求:**
- 必须体现 Permit 的生命周期流转
- 必须显示"Permit Issued"的签发者与时间
- 必须区分"Ready for Permit"与"Permit Issued"

**禁止:**
- ❌ 省略"Permit Issued"节点
- ❌ 混淆"Ready for Permit"与"Permit Issued"
- ❌ 隐藏当前状态

---

#### 3.4.8 Compliance Signature (合规签名)

**位置**: Main Grid Row 3 右侧

**核心字段:**

| 字段 | 说明 | 示例 |
|-----|------|-----|
| **signed by** | 签发者 | Compliance-01 |
| **signed at** | 签发时间 | 2026-03-12T09:00:00Z |
| **signature note** | 签名备注 | Approved for production release |
| **approval remarks** | 批准备注 | Subject to runtime monitoring |
| **release comments** | 放行评论 | Contact compliance-01 for revocation |

**设计要求:**
- 即便 v0 没有电子签样式，也要把这块作为正式模块保留
- 体现"合规官签字"的权威性
- 提供"联系合规官"的入口

**禁止:**
- ❌ 省略 signed by 或 signed at
- ❌ 使用"系统自动签发"等弱化角色表述
- ❌ 隐藏签名模块或折叠到次要位置

---

### 3.5 Residual Risk Reminder (残余风险提醒)

**位置**: 页面底部，Main Grid 下方

**核心字段:**

| 字段 | 说明 | 示例 |
|-----|------|-----|
| **Known operational risks** | 已知运营风险 | Rate limiting may trigger under high load |
| **Monitoring expectations** | 监控期望 | Monitor error rates for 72 hours post-release |
| **Re-audit triggers** | 重审触发器 | Re-audit required if incident severity ≥ High |

**设计要求:**
- 增加 Permit 的可信度
- 告知用户 Permit 不是"绝对没风险"
- 明确"在边界内可放行"

**禁止:**
- ❌ 省略残余风险提醒
- ❌ 使用"无风险"等绝对化表述
- ❌ 隐藏监控期望

---

### 3.6 状态设计

#### 3.6.1 状态标签规范

**统一使用 (禁止混用营销词):**

| 状态标签 | 使用场景 | 禁用的替代词 |
|---------|---------|------------|
| Pending | 等待签发 | Waiting, In Progress |
| Active | 生效中 | Live, Approved, Success |
| Revoked | 已撤销 | Cancelled |
| Expired | 已过期 | Outdated |
| Superseded | 已被替代 | Replaced |

**禁止:**
- ❌ 使用 "Success", "Approved", "Live" 等营销词
- ❌ 使用 "Done", "Completed" 等任务完成词

---

### 3.7 Hash 绑定要求 (CRITICAL)

#### 3.7.1 强制绑定字段

**Permit 必须绑定以下字段，不得解耦:**

| 字段 | 用途 | 禁止操作 |
|-----|------|---------|
| **revision** | 版本追溯 | ❌ 不得出现无 revision 的 Permit |
| **contract_hash** | 合同哈希 | ❌ 不得出现无 contract_hash 的 Permit |
| **decision_hash** | 决策哈希 | ❌ 不得出现无 decision_hash 的 Permit |
| **audit_basis** | 审计基础 | ❌ 不得出现无 Audit Basis 的 Permit |
| **rulepack_version** | 规则包版本 | ❌ 不得出现无规则包版本的 Permit |

#### 3.7.2 Hash 展示规范

**统一展示方式:**
- 前 8 位 + 省略号 (如: `sha256:a1b2c3d4...`)
- hover 显示全量
- 可复制
- 可跳转 linked object

**禁止:**
- ❌ 只显示哈希值的前几位而不标注省略
- ❌ 禁止复制哈希值
- ❌ 不提供跳转 linked object 的入口

---

### 3.8 禁止展示项

#### 3.8.1 Permit 页面特定禁止项

| 禁止项 | 说明 | 替代方案 |
|-------|------|---------|
| 大绿勾成功页 | 不得使用大绿勾、庆祝动画 | 使用正式凭证样式 |
| 营销式语言 | 不得使用"恭喜"、"成功"、"通过"等 | 使用"Permit granted"、"Permit issued" |
| 口语化表达 | 不得使用"You can now deploy" | 使用"Allowed for release within declared scope only" |
| 模糊范围 | 不得使用"所有环境"、"不限" | 明确具体环境与边界 |
| 解耦的 Permit | 不得出现无 revision/hash 的 Permit | 强制绑定所有必填字段 |
| 语义混淆 | 不得暗示"Audit pass = Release approved" | 显式强调"Audit pass is not release approval. Permit is." |

---

### 3.9 交互与导航

#### 3.9.1 Breadcrumb (面包屑)

**位置**: Top Nav 下方，Permit Header 上方

**格式:**
```
Release / Permit / PMT-2026-0312-014
```

**交互:**
- 点击 "Release" → 跳转 Release 主页
- 点击 "Permit" → 跳转 Permit 列表页
- 点击 "PMT-2026-0312-014" → 当前页

#### 3.9.2 Top Nav (顶部导航)

**一级导航项** (按 T-FE-01 IA Spec):
1. Overview
2. Forge
3. Audit
4. Release (当前页)
5. Registry
6. Policies
7. History

**导航禁忌:**
- ❌ 不得使用 "Builder / Create / Magic" 作为导航项
- ❌ 不得将 Forge 置于导航首位

---

### 3.10 响应式与交互摘要

#### 3.10.1 响应式断点 (桌面优先)

| 断点 | 布局调整 |
|-----|---------|
| ≥ 1440px | 完整双列布局 |
| 1024-1440px | 保持双列，间距压缩 |
| < 1024px | 单列布局，模块堆叠 |

#### 3.10.2 关键交互

| 交互 | 行为 |
|-----|------|
| 点击 Permit ID | 复制 Permit ID 到剪贴板 |
| 点击 decision_hash | 复制哈希值到剪贴板，hover 显示全量 |
| 点击 View Linked Audit | 跳转 Audit Detail 页面 |
| 点击 Revoke Permit | 弹出确认对话框，确认后撤销 Permit |
| 点击 Lifecycle 节点 | 显示该节点的详细时间、操作者、说明 |

---

## 四、交付物验收清单

- [x] 1. Permit 页面目标已定义 (正式放行凭证，非成功页)
- [x] 2. Permit 页面骨架已绘制
- [x] 3. 模块列表与模块优先级已明确 (8 个 P0 必填模块)
- [x] 4. 核心模块详细规格已输出 (Permit Header / Core Decision Block / Scope / Conditions / Linked Basis / Lifecycle / Signature / Residual Risk)
- [x] 5. 强化 "Audit pass is not release approval. Permit is."
- [x] 6. revision / contract_hash / decision_hash / audit basis 绑定要求已明确
- [x] 7. 生命周期、签发角色、失效触发器已明确
- [x] 8. 未把 Permit 页面做成大绿勾成功页
- [x] 9. 未出现与 revision/hash 解耦的 Permit
- [x] 10. 未弱化范围、附加条件、失效条件
- [x] 11. 未越权写到具体组件实现
- [x] 12. Hash 绑定要求已明确 (CRITICAL)
- [x] 13. 状态标签规范已统一
- [x] 14. 禁止展示项已列出
- [x] 15. 三段式结构 (PreflightChecklist/ExecutionContract/RequiredChanges) 已完成

---

**文档版本**: v1.0
**最后更新**: 2026-03-12

**EvidenceRef**: 本规格基于以下文档合成:
- `docs/2026-03-12/前端重构_AI军团任务分发单_v2.md` (L347-392)
- `docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md` (L781-995)
- `docs/2026-03-12/"治理与放行中枢"的前端设计.md` (完整文档)
- `docs/2026-03-12/verification/T-FE-01_ia_spec.md` (L250-267)
- `multi-ai-collaboration.md` (完整文档)
- `docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md` (完整文档)
- `docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md` (完整文档)
