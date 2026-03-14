# T-FE-03: Audit Detail 页面规格书

> **任务 ID**: T-FE-03
> **执行者**: Antigravity-1
> **审查者**: vs--cc2
> **合规官**: Kior-C
> **日期**: 2026-03-12
> **状态**: Execution Phase

---

## 一、PreflightChecklist

### 1.1 Fail-Closed 风险枚举

| 风险类别 | 潜在绕过路径 | 防御措施 |
|---------|-------------|---------|
| 信息顺序失真 | 细节先行、结论后置，导致用户先看到技术细节而非裁决结果 | 强制"结论 → 原因 → 证据 → 修复"不可逆顺序 |
| 概念混淆 | Evidence/Rule/Gate/Gap 混成一锅，用户无法区分证据源、触发规则、阻断门禁、修复项 | 四者必须使用独立视觉容器和明确标签 |
| 权限泄漏 | 内部异常栈、模块名、调用拓扑泄漏到用户可见层 | 明确定义 Layer 3 绝对禁止前端呈现区 |
| 红线弱化 | Red Lines 与 Fixable Gaps 视觉权重相同，用户无法区分致命问题与可修复项 | 必须左右分栏，Red Lines 使用阻断态视觉，Fixable Gaps 使用修复态视觉 |
| 证据滥用 | EvidenceRef 未区分可见性级别，敏感证据全量展示 | 必须区分 visible / summary-only / restricted 三级 |

### 1.2 依赖环境

| 依赖项 | 当前状态 | 必需值 |
|-------|---------|-------|
| T-FE-01 IA 规格 | 已完成 (ALLOW) | 必须确认导航结构、页面边界 |
| 后端 Audit API | 需支持 | 必须支持按角色裁剪 payload，不返回 Layer 3 数据 |
| 三权分立可视化 | 无现有实现 | 本规格新增 |

### 1.3 历史债务扫描

| 债务类型 | 位置 | 处理策略 |
|---------|-----|---------|
| 缺失结论先行设计 | 无现有实现 | 本规格强制 |
| 缺失 EvidenceRef 语义 | 无现有实现 | 本规格新增 |
| 缺失三权分立可视化 | 无现有实现 | 本规格新增 |

---

## 二、ExecutionContract

### 2.1 Input Constraints

**允许读取的文件:**
- `docs/2026-03-12/前端重构_AI军团任务分发单_v2.md`
- `docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md`
- `docs/2026-03-12/T-FE-03_三权分发提示词.md`
- `docs/2026-03-12/verification/T-FE-01_ia_spec.md`
- `docs/2026-03-12/verification/T-FE-03_gate_decision.json` (R1 复审)
- `docs/2026-03-12/verification/T-FE-03_compliance_attestation.json` (R1 复审)
- `multi-ai-collaboration.md`
- `docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md`
- `docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md`

**允许创建的文件:**
- 本规格文档 `docs/2026-03-12/verification/T-FE-03_audit_detail_spec.md`
- 执行报告 `docs/2026-03-12/verification/T-FE-03_execution_report.yaml`

**绝对禁止:**
- 写具体组件实现代码
- 把 Evidence/Rule/Gate/Gap 混成一锅
- 把内部异常栈、模块名、调用拓扑带到用户可见层
- 越权写到 T-FE-05/T-FE-06 范围（组件树、权限矩阵）
- 无 EvidenceRef 宣称完成

### 2.2 Output Definition

**交付物:**
- 本 Audit Detail 页面规格，包含：
  1. Decision Header
  2. Decision Summary
  3. 8 Gate 审计结果区
  4. EvidenceRef 区域
  5. Red Lines 区域
  6. Fixable Gaps 区域
  7. Hash / Revision / Decision binding
  8. Footer CTA
  9. 三权分立边界展示
  10. 绝对禁止前端呈现区定义

**回滚方案:**
- 本文档为规格说明，不涉及代码变更
- 如规格有误，可通过 Review/Compliance 流程修正

### 2.3 Gate / Acceptance Check

**自动检查:**
```bash
# 检查是否出现 builder-first 禁用词
rg -n "builder|canvas|marketplace" docs/2026-03-12/verification/T-FE-03_audit_detail_spec.md
# 预期: 仅出现在 deny 或禁用语境
```

**手动检查:**
- [ ] 是否先结论后细节
- [ ] 是否明确红线与可修复项分离
- [ ] 是否保留 EvidenceRef 的 visible / summary-only / restricted 语义
- [ ] 是否保留三权分立边界展示
- [ ] 是否明确绝对禁止前端呈现区

---

## 三、页面规格

### 3.1 页面定位

**Audit Detail 是全系统最重要的一页。**

它必须像"裁决页 + 审计工作台 + 修复入口"，是用户理解"为什么这个资产被通过/阻断"的核心场所。

**核心价值主张:**
> **这不是一个普通的详情页，而是一个具有裁决权威的判决书展示场所。**
> **用户来到这里，是为了理解裁决、查看证据、确定下一步行动。**

**页面职责:**
1. 出示不容置疑的裁决结论
2. 解释裁决背后的原因
3. 展示支撑裁决的证据链
4. 明确哪些是致命红线，哪些是可修复缺口
5. 提供明确的下一步动作

### 3.2 页面骨架

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ Top Nav                                                                 │
├──────────────────────────────────────────────────────────────────────────┤
│ Breadcrumb                                                              │
│ Registry / Asset Name / Revision R-014                                  │
├──────────────────────────────────────────────────────────────────────────┤
│ [1] Decision Header                                                      │
│ Asset: Skill A                Revision: R-014                           │
│ Status: [Blocked]             Audit Version: v1.0                       │
│ decision_hash: xxx...         audited at: 2026-03-12                    │
│ [Review Gaps] [Export AuditPack] [Re-run Audit] [Submit for Permit]     │
├──────────────────────────────────────────────────────────────────────────┤
│ [2] Decision Summary + [3] Power Boundary                                │
│ ┌───────────────────────────────┐ ┌───────────────────────────────────┐ │
│ │ Decision Summary              │ │ Power Boundary                    │ │
│ │ why pass/fail                 │ │ Execution / Audit / Compliance    │ │
│ └───────────────────────────────┘ └───────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────┤
│ Main Content                                                            │
│ ┌──────────────────────────────────────────────┐ ┌────────────────────┐ │
│ │ [4] 8 Gate Timeline / Gate Details          │ │ [5] EvidenceRef    │ │
│ │ gate status, rule triggers, explanations    │ │ Panel              │ │
│ └──────────────────────────────────────────────┘ └────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────┤
│ [6] Issue Breakdown                                                       │
│ ┌───────────────────────────────┐ ┌───────────────────────────────────┐ │
│ │ Red Lines                     │ │ Fixable Gaps                      │ │
│ │ must block                    │ │ can repair and resubmit          │ │
│ └───────────────────────────────┘ └───────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────┤
│ Governance Snapshot                                                     │
│ ┌───────────────────────────────┐ ┌───────────────────────────────────┐ │
│ │ Contract / Control Snapshot   │ │ [7] Hash & Reproducibility        │ │
│ │ constitution, rules, controls │ │ demand/contract/decision hashes   │ │
│ └───────────────────────────────┘ └───────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────┤
│ [8] Footer Action Bar                                                     │
│ [Go to Gap Analysis] [Assign Owner] [Re-run Audit] [Submit for Permit] │
└──────────────────────────────────────────────────────────────────────────┘
```

### 3.3 模块详细规格

#### [1] Decision Header

**视觉权重:** 最高，必须像证书抬头

**字段要求:**

| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| Asset Name | string | Y | 资产名称 |
| Asset Type | enum | Y | Skill / Workflow / Agent Asset |
| Revision ID | string | Y | 例如 R-014 |
| Current Status | enum | Y | 见状态标签规范 |
| Audit Version | string | Y | 例如 v1.0 |
| decision_hash | string(hash) | Y | 前 8 位 + 省略 + hover 全量 |
| audited_at | timestamp | Y | 审计完成时间 |
| owner | string | N | 资产负责人 |
| reviewer | string | N | 审查人 |

**状态标签规范:**

```
允许使用:
- Draft
- In Audit
- Passed
- Fix Required
- Blocked
- Ready for Permit

禁止使用:
- Success
- Done
- Completed
- Approved
```

**禁止事项:**
- ❌ 不得使用营销语言（Success / Done / Approved）
- ❌ 不得混用状态标签
- ❌ 不得省略 decision_hash

#### [2] Decision Summary

**视觉权重:** 最高，必须结论先行

**核心原则:**
> **用户第一眼看到的是"通过/阻断"的明确结论，而不是技术细节。**

**卡片结构:**

```
┌─────────────────────────────────────┐
│ Final Decision                      │
│ [Blocked]                           │  ← 最大字号，阻断态红色
├─────────────────────────────────────┤
│ Primary Reason                      │
│ Execution boundary leakage detected │
│ under Gate 4.                       │
├─────────────────────────────────────┤
│ Evidence Sufficiency                │
│ Sufficient for rejection            │
├─────────────────────────────────────┤
│ Permit Readiness                    │
│ Not eligible until critical gaps    │
│ are resolved                        │
├─────────────────────────────────────┤
│ [Critical: 2] [Fixable: 4] [EVD: 11]│
└─────────────────────────────────────┘
```

**字段定义:**

| 字段 | 类型 | 说明 |
|-----|------|-----|
| Final Decision | enum | Passed / Blocked / Fix Required |
| Primary Reason | text | 一句话解释为什么是此结论 |
| Evidence Sufficiency | enum | Sufficient for approval / Sufficient for rejection / Insufficient |
| Permit Readiness | text | 说明当前是否具备 Permit 申请资格 |

**禁止事项:**
- ❌ 不得先细节后结论
- ❌ 不得混用技术术语与用户语言
- ❌ 不得暗示"审计通过即放行"

#### [3] Power Boundary

**视觉权重:** 高，必须常驻可见

**核心原则:**
> **三权分立必须在 Audit Detail 页面显式展示，让用户明白谁负责什么。**

**推荐呈现:**

```
┌───────────────────┬───────────────────┬───────────────────┐
│ Execution         │ Audit             │ Compliance        │
├───────────────────┼───────────────────┼───────────────────┤
│ ✓ Can run         │ ✓ Can inspect     │ ✓ Can issue       │
│ ✓ Can produce     │ ✓ Can issue       │   permit          │
│   outputs         │   audit decision  │                   │
│ ✗ Cannot approve  │ ✗ Cannot issue    │ ✓ Can define      │
│   release         │   permit          │   conditions      │
│                   │                   │                   │
│                   │                   │ ✗ Cannot modify   │
│                   │                   │   execution       │
│                   │                   │   output          │
└───────────────────┴───────────────────┴───────────────────┘
```

**展示要求:**
- 必须用三列卡片形式
- 位置靠上，不要藏在折叠区
- 必须明确每个权力的"能做什么"和"不能做什么"

**禁止事项:**
- ❌ 不得弱化或隐藏三权分立
- ❌ 不得暗示执行者可以批准放行

#### [4] 8 Gate Timeline / Gate Details

**视觉权重:** 中高，是页面主体

**核心原则:**
> **8 Gate 必须按时间线或列表展示，每个 Gate 清晰表明状态和触发规则。**

**Gate 卡片结构:**

```
Gate 4 — Boundary Integrity   [Fail]

Reason
Execution logic exceeded declared control scope.

Triggered Rules
- RULE-4.2: Undeclared action path detected
- RULE-4.7: Control scope violation

Evidence
- EVD-003: runtime trace mismatch
- EVD-006: undeclared action path

Fix Suggestion
- tighten declared control boundaries
- update ControlSpec and resubmit
```

**字段定义:**

| 字段 | 类型 | 说明 |
|-----|------|-----|
| Gate Name | string | 例如 "Boundary Integrity" |
| Gate Status | enum | Pass / Fail / Warn / Skip |
| Reason | text | 简要说明 |
| Triggered Rules | list[RuleRef] | 触发的规则引用 |
| Evidence | list[EvidenceRef] | 支撑证据 |
| Fix Suggestion | text | 修复建议（可选） |

**禁止事项:**
- ❌ 不得展示规则阈值、权重、探针代码
- ❌ 不得暴露内部执行拓扑
- ❌ 不得把 Rule / Gate / Evidence 混成一锅

#### [5] EvidenceRef Panel

**视觉权重:** 中，右侧 sticky 面板

**核心原则:**
> **EvidenceRef 必须区分可见性级别，敏感证据不得全量展示。**

**EvidenceRef 字段结构:**

| 字段 | 类型 | 说明 |
|-----|------|-----|
| Evidence ID | string | 例如 EVD-003 |
| Source Type | enum | Log / File / Metric / Snapshot |
| Summary | text | 证据摘要 |
| Strength | enum | Weak / Medium / Strong |
| Visibility | enum | visible / summary-only / restricted |
| Linked Gate | string | 关联的 Gate |

**可见性级别语义:**

```
visible:        完整可见，支持展开全量内容
summary-only:   仅显示摘要，详情隐藏，点击可请求授权
restricted:     需额外权限验证，当前角色不可见
```

**交互设计:**
- 点击某条 evidence 后，中间内容联动高亮对应 Gate
- 下方出现 evidence 摘要说明
- restricted 级别显示"需权限验证"提示

**禁止事项:**
- ❌ 不得把所有证据全量展示
- ❌ 不得忽略 visibility 级别
- ❌ 不得让受限证据绕过权限验证

#### [6] Issue Breakdown

**核心原则:**
> **Red Lines 与 Fixable Gaps 必须左右分栏，视觉权重有明显区分。**

**布局:**

```
┌───────────────────────────────┬───────────────────────────────────┐
│ Red Lines (阻断项)            │ Fixable Gaps (可修复项)           │
├───────────────────────────────┼───────────────────────────────────┤
│ [阻] Execution boundary       │ [修] Missing required annotation  │
│ leakage detected              │                                   │
│ Impact: CRITICAL              │ Severity: Medium                 │
│ Gate: 4                       │ Gate: 2                           │
│ Rule: RULE-4.2, RULE-4.7      │ Suggested fix: Add annotation...  │
│ Why blocking: 超出声明控制边界│ Expected outcome: Pass after fix  │
│ Required disposition: 必须修复│                                   │
└───────────────────────────────┴───────────────────────────────────┘
```

**Red Lines 字段:**

| 字段 | 类型 | 说明 |
|-----|------|-----|
| Issue title | string | 问题描述 |
| Impact | enum | CRITICAL / HIGH |
| Triggered Gate | string | 触发的 Gate |
| Rule | list[string] | 触发的规则 |
| Why blocking | text | 为什么这是红线 |
| Required disposition | text | 必须的处理方式 |

**Fixable Gaps 字段:**

| 字段 | 类型 | 说明 |
|-----|------|-----|
| Gap title | string | 缺口描述 |
| Severity | enum | Low / Medium / High |
| Related Gate | string | 相关的 Gate |
| Suggested fix | text | 建议的修复方式 |
| Expected re-review outcome | text | 修复后的预期结果 |

**禁止事项:**
- ❌ 不得混同 Red Lines 与 Fixable Gaps
- ❌ 不得让两者的视觉权重相同
- ❌ 不得暗示 Red Lines 可以绕过

#### [7] Hash & Reproducibility

**视觉权重:** 中低，但必须保留

**核心原则:**
> **Hash 展示是建立信任的关键，必须明确每个裁决都是可重现的。**

**字段定义:**

| 字段 | 类型 | 说明 |
|-----|------|-----|
| demand_hash | string(hash) | 需求哈希 |
| contract_hash | string(hash) | 合同哈希 |
| decision_hash | string(hash) | 决策哈希 |
| revision lineage | string | 版本谱系 |
| linked manifest ID | string | 关联清单 ID |

**Hash 展示规范:**
- 前 8 位 + 省略 + hover 全量
- 可复制
- 可跳转 linked object

**辅助说明文本:**
```
This decision is bound to the current revision and policy context.
Any change in revision or policy context will invalidate this audit result.
```

**禁止事项:**
- ❌ 不得省略任一 Hash 字段
- ❌ 不得让 Permit 与 Hash 解耦

#### [8] Footer Action Bar

**视觉权重:** 中，固定底部

**核心原则:**
> **Footer CTA 必须根据当前状态动态变化，引导用户进行下一步动作。**

**CTA 状态机:**

```
状态 Blocked:
- [View Critical Fixes]
- [Export Fix Brief]
- [Re-run After Changes]

状态 Fix Required:
- [Go to Gap Analysis]
- [Assign Owner]
- [Re-submit to Audit]

状态 Passed:
- [Export AuditPack]
- [Submit for Permit]

状态 Ready for Permit:
- [Open Permit Draft]
- [Issue Permit]
```

**禁止事项:**
- ❌ 不得在 Blocked 状态显示"提交 Permit"
- ❌ 不得暗示"审计通过即放行"

#### [7.5] Contract / Control Snapshot

**视觉权重:** 中低， Governance Snapshot 区域左侧

**核心原则:**
> **企业用户需要判断裁决的可信度，必须知道本次审计依据的合同版本、规则包版本、控制规格版本。**

**页面位置:**
- 位于 Governance Snapshot 区域左侧
- 与 Hash & Reproducibility 并列
- 在 Footer Action Bar 之前

**字段定义:**

| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| Contract Summary | text | Y | 合同摘要，简述资产治理合同的核心内容 |
| Constitution Version | string | Y | 宪法版本号，例如 v2.1 |
| Rule Pack Version | string | Y | 规则包版本号，例如 v1.0.3 |
| ControlSpec Version | string | Y | 控制规格版本号，例如 v3.5 |
| Linked Manifest | string(ref) | Y | 关联清单 ID |
| Audit Scope | text | Y | 审计范围说明 |

**模块作用:**
- 告诉用户本次裁决依据的治理框架版本
- 让企业用户能够追溯审计依据的合同与规则
- 建立裁决的可信度和可审计性

**展示方式:**

```
┌─────────────────────────────────────┐
│ Contract / Control Snapshot         │
├─────────────────────────────────────┤
│ Contract Summary                    │
│ 资产治理合同: 技能类资产需要通过 8   │
│ Gate 审计，确保执行边界、控制规格、  │
│ 证据完整性符合要求。                 │
├─────────────────────────────────────┤
│ Constitution Version: v2.1          │
│ Rule Pack Version: v1.0.3           │
│ ControlSpec Version: v3.5           │
├─────────────────────────────────────┤
│ Linked Manifest: manifest-2026-012  │
│ Audit Scope: 全量 8 Gate 审计       │
└─────────────────────────────────────┘
```

**与其他模块的关系:**
- **与 Decision Summary**: Decision Summary 说明裁决结果，Contract/Control Snapshot 说明裁决依据
- **与 8 Gate Details**: 8 Gate 说明具体哪道门被阻断，Contract/Control Snapshot 说明这些门的规则版本
- **与 Hash & Reproducibility**: Hash 说明裁决的唯一性，Contract/Control Snapshot 说明裁决的治理框架
- **与 Permit Readiness**: Permit Readiness 说明是否可以申请放行，Contract/Control Snapshot 说明审计框架状态

**禁止事项:**
- ❌ 不得展示规则具体内容（Rule 规则细节属于 Layer 3）
- ❌ 不得展示判定阈值和权重（属于 Layer 3）
- ❌ 不得展示内部模块拓扑（属于 Layer 3）
- ❌ 不得让 Contract/Control Snapshot 与 Hash 解耦

**注意事项:**
- 本模块只展示版本号和摘要，不展开规则细节
- 规则详情如需查看，应通过独立入口（如 Policies 页面）
- 版本号应可点击跳转到对应的版本详情页

---

## 四、绝对禁止前端呈现区（Layer 3）

### 4.1 禁止内容清单

**任何角色都不应看到:**

| 类别 | 禁止内容 | 风险 |
|-----|---------|------|
| 规则机制 | 判定阈值、算法权重 | 可逆向规则逻辑 |
| 探针实现 | 探针代码、检测逻辑 | 可绕过检测 |
| 执行细节 | 阻断触发路径、绕过路径 | 可设计绕过 |
| 系统架构 | 内部执行拓扑、API 调用依赖顺序 | 可攻击系统 |
| 异常信息 | 内部异常栈、模块名、调用链 | 暴露实现细节 |

### 4.2 API 层裁剪责任

**必须:**
- 由 API 按角色返回不同 payload
- 敏感字段不得进入前端响应

**不应:**
- 在前端通过角色判断后再裁剪字段
- 全量下发给前端再隐藏

---

## 五、EvidenceRef 规范

### 5.1 可见性级别

| 级别 | 含义 | 展示方式 | 示例 |
|-----|------|---------|------|
| visible | 完整可见 | 全量展示，支持展开 | 执行日志摘要 |
| summary-only | 仅摘要 | 仅显示摘要，详情隐藏 | 内部探针结果 |
| restricted | 受限访问 | 需额外权限验证 | 生产环境凭证 |

### 5.2 EvidenceRef 字段结构

```
EvidenceRef:
  - id: string              # Evidence ID
  - source_type: enum       # Log / File / Metric / Snapshot
  - summary: text           # 证据摘要
  - strength: enum          # Weak / Medium / Strong
  - visibility: enum        # visible / summary-only / restricted
  - linked_gate: string     # 关联的 Gate
```

---

## 六、交付物验收清单

- [x] 1. Decision Header 规格已定义
- [x] 2. Decision Summary 规格已定义（结论先行）
- [x] 3. 8 Gate 审计结果区规格已定义
- [x] 4. EvidenceRef 区域规格已定义（含可见性级别）
- [x] 5. Red Lines 区域规格已定义
- [x] 6. Fixable Gaps 区域规格已定义（左右分栏）
- [x] 7. Hash / Revision / Decision binding 规格已定义
- [x] 8. Footer CTA 规格已定义（含状态机）
- [x] 9. 三权分立边界展示已定义
- [x] 10. 绝对禁止前端呈现区已明确定义
- [x] 11. "结论 → 原因 → 证据 → 修复"顺序已强制
- [x] 12. EvidenceRef visible/summary-only/restricted 语义已保留
- [x] 13. **[R1 新增] Contract / Control Snapshot 规格已定义**（参考线框图 L719-735）

---

## 七、强化要点摘要

### 7.1 先结论，后细节

```
Decision Summary (结论)
    ↓
8 Gate Details (原因)
    ↓
EvidenceRef Panel (证据)
    ↓
Red Lines / Fixable Gaps (修复)
```

### 7.2 红线与可修复项分离

```
Red Lines (左侧，阻断态视觉)
- 必须阻断
- Impact: CRITICAL / HIGH
- Required disposition 明确

Fixable Gaps (右侧，修复态视觉)
- 可以修复后重新提交
- Severity: Low / Medium / High
- Expected re-review outcome 明确
```

### 7.3 三权分立边界展示

```
Execution: ✓ Can run, ✓ Can produce outputs, ✗ Cannot approve release
Audit: ✓ Can inspect, ✓ Can issue audit decision, ✗ Cannot issue permit
Compliance: ✓ Can issue permit, ✗ Cannot modify execution output
```

---

**文档版本:** v1.1 (R1 返工修订)
**最后更新:** 2026-03-12 (R1)

**R1 返工修订记录:**
- 修复 FE03-002 (HIGH): 补齐 Contract / Control Snapshot 模块完整规格（Section 3.3 [7.5]）
- 修复 FE03-001 (MEDIUM): 更新 Input Constraints，增加 gate_decision 和 compliance_attestation 引用

**EvidenceRef:** 本规格基于以下文档合成:
- `docs/2026-03-12/前端重构_AI军团任务分发单_v2.md` (L1-696)
- `docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md` (L1-1163, **L719-735 Contract/Control Snapshot**)
- `docs/2026-03-12/verification/T-FE-01_ia_spec.md` (L1-544)
- `docs/2026-03-12/verification/T-FE-03_gate_decision.json` (R1 Review)
- `docs/2026-03-12/verification/T-FE-03_compliance_attestation.json` (R1 Compliance)
- `multi-ai-collaboration.md` (L1-451)
- `docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md` (L1-29)
- `docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md` (L1-30)
