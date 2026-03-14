# T-FE-07: 首页叙事、应用内 CTA 语言与文案禁用词规格

> **任务 ID**: T-FE-07
> **执行者**: vs--cc3
> **审查者**: Kior-B
> **合规官**: Kior-C
> **日期**: 2026-03-12
> **依赖**: T-FE-02 (ALLOW), T-FE-03 (ALLOW), T-FE-04 (ALLOW)

---

## 一、PreflightChecklist

### 1.1 Fail-Closed 风险枚举

| 风险类别 | 潜在绕过路径 | 防御措施 |
|---------|-------------|---------|
| Builder-first 漂移 | 首页 CTA 可能滑向 "Build / Create / Generate Now" | 硬性禁止词清单，只允许 "Run an Audit" / "See a Permit Example" |
| 魔法式承诺 | 可能使用 "magic / instant / one-click" 等过度承诺词汇 | 明确列入禁用词清单，禁止任何暗示零成本的表达 |
| 审计放行混淆 | 可能把 "Audit pass" 写成 "Permit granted" / "Approved for release" | 显式区分 Audit 与 Permit 语义，强制使用准确术语 |
| 首页应用内混同 | 首页可能讲太多技术细节，应用内可能重复价值教育 | 明确首页讲价值，应用内讲状态/裁决/证据/放行的边界 |
| 叙事层级错乱 | CTA 可能暗示 "AI 会替你做一切" | 强调治理边界与用户责任，不使用全自动式表达 |

### 1.2 依赖环境

| 依赖项 | 当前状态 | 必需值 |
|-------|---------|-------|
| T-FE-02 Dashboard Spec | ALLOW | 已确立 Dashboard 主 CTA 为 "Run Audit" |
| T-FE-03 Audit Detail Spec | ALLOW | 已确立裁决语言与证据展示规范 |
| T-FE-04 Permit Spec | ALLOW | 已确立 Permit 凭证语义与 "Audit pass ≠ Permit" |
| 三页主链定义 | 已定义 | Dashboard / Audit Detail / Permit 为主链，叙事需对齐 |

### 1.3 历史债务扫描

| 债务类型 | 位置 | 处理策略 |
|---------|-----|---------|
| 现有首页可能使用 builder 叙事 | ui/app/src/pages/landing | 本规格明确禁用词，后续统一修正 |
| 现有 CTA 可能偏向生成动作 | ui/app/src/components/ | 本规格定义应用内 CTA 语言规范 |
| 缺失 Audit 与 Permit 语义区分 | 无现有实现 | 本规格显式强化区分 |

---

## 二、ExecutionContract

### 2.1 Input Constraints

**允许读取的文件:**
- `docs/2026-03-12/前端重构_AI军团任务分发单_v2.md`
- `docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md`
- `docs/2026-03-12/"治理与放行中枢"的前端设计.md`
- `multi-ai-collaboration.md`
- `docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md`
- `docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md`

**允许修改的文件:**
- 新建 `docs/2026-03-12/verification/T-FE-07_copy_and_cta_spec.md` (本文件)

**绝对禁止:**
- 修改现有前端代码实现
- 定义具体组件视觉实现细节
- 使用 "Build / Create / Generate Now" 作为首页主 CTA
- 使用 "magic / instant / one-click" 叙事
- 把 "Audit pass" 写成 "Permit granted"
- 越权写到视觉实现或组件代码

### 2.2 Output Definition

**交付物:**
- 本文案与 CTA 规格文档，包含：
  1. 首页 headline 定义
  2. 首页 subheadline 定义
  3. 首页 CTA 定义
  4. 首页场景区文案结构
  5. 文案禁用词清单
  6. 应用内 CTA 语言规范
  7. 首页与应用内语言边界
  8. Audit pass 与 Permit granted 语义区分

**回滚方案:**
- 本文档为规格说明，不涉及代码变更，无需回滚
- 如规格有误，可通过 Review/Compliance 流程修正

### 2.3 Gate / Acceptance Check

**手动检查:**
- [ ] 是否已输出首页 headline / subheadline / CTA
- [ ] 是否已输出首页场景区文案结构
- [ ] 是否已输出文案禁用词清单
- [ ] 是否已输出应用内 CTA 语言规范
- [ ] 是否明确首页与应用内的语言边界
- [ ] 是否明确 Audit pass ≠ Permit granted
- [ ] 是否未使用禁用词
- [ ] 是否有 EvidenceRef

---

## 三、RequiredChanges

### 3.1 首页叙事规范

#### 3.1.1 核心定位

首页是 **价值传达与边界教育层**，不是操作入口。

用户进入首页后，必须能立即回答三个问题：
1. **这是什么？** → 治理中枢、审计工作台、放行控制层
2. **不是什么？** → 不是 AI builder、不是 skill marketplace、不是 workflow canvas
3. **如何开始？** → Run an Audit / See a Permit Example

#### 3.1.2 首页 Headline 定义

**主标题 (Headline):**

```
Governed Asset Intelligence
```

**替代方案 (可选):**

| 选项 | Headline | 适用场景 |
|-----|----------|---------|
| A | Governance for AI Skills | 侧重技能治理 |
| B | Audit, Permit, Release | 侧重流程关键词 |
| C | The Governance Layer for AI Assets | 侧重层级定位 |

**禁止:**
- ❌ "Build AI Skills Faster"
- ❌ "Generate Anything with AI"
- ❌ "Your AI Skill Builder"

#### 3.1.3 首页 Subheadline 定义

**副标题 (Subheadline):**

```
Audit decisions backed by evidence. Release authorization bound to permits.
```

**替代方案 (可选):**

| 选项 | Subheadline | 适用场景 |
|-----|-------------|---------|
| A | Three-pillar governance. Evidence-backed decisions. Permit-bound release. | 侧重三权分立 |
| B | Not a builder. A governance layer for AI assets. | 侧重定位澄清 |
| C | Audit → Evidence → Permit. The path to governed release. | 侧重流程链路 |

**禁止:**
- ❌ "Build production-ready skills in minutes"
- ❌ "The fastest way to create AI workflows"
- ❌ "No code required"

#### 3.1.4 首页 CTA 定义

**主 CTA (Primary CTA):**

```
Run an Audit
```

**次 CTA (Secondary CTA):**

```
See a Permit Example
```

**第三 CTA (Tertiary CTA，可选):**

```
Learn More About Governance
```

**CTA 交互目标:**

| CTA 文本 | 目标页面/动作 | 说明 |
|---------|-------------|------|
| Run an Audit | Dashboard / Registry | 进入治理流程，不是进入 builder |
| See a Permit Example | Permit 详情页示例 | 展示放行凭证形式，建立权威感 |
| Learn More About Governance | 治理流程文档/About 页 | 教育用户什么是治理 |

**禁止:**
- ❌ "Build a Skill"
- ❌ "Create Workflow"
- ❌ "Generate Now"
- ❌ "Start Building"
- ❌ "Try It Free"

#### 3.1.5 首页场景区文案结构

**场景区目标**: 展示治理流程，不是展示功能列表

**场景区 1: Audit (审计)**

```
Header: Evidence-Backed Decisions

Body:
Every asset goes through 8 quality gates. Each decision is backed by
auditable evidence, not opaque judgments. See why something passed or
failed, with full traceability.

CTA: Explore Audit Flow
```

**场景区 2: Permit (放行)**

```
Header: Bound Release Authorization

Body:
Audit pass is not release approval. A Permit is the only valid release
credential, bound to specific revisions, scopes, and conditions. See
what a real permit looks like.

CTA: View Permit Sample
```

**场景区 3: Governance (治理)**

```
Header: Three-Pillar Separation

Body:
Execution, Review, and Compliance are separate powers. No single role
can approve its own work. This is how you get trustworthy, auditable
AI systems at scale.

CTA: Learn About Governance
```

**禁止:**
- ❌ 功能列表式展示（如 "Workflow Builder", "Skill Templates", "Marketplace"）
- ❌ 效果承诺式展示（如 "10x Faster", "Zero Code Required"）
- ❌ 魔法式描述（如 "AI Does It For You", "One-Click Deploy"）

---

### 3.2 文案禁用词清单

#### 3.2.1 Builder-first 叙事禁用词（CRITICAL）

| 禁用词 | 禁用理由 | 替代方案 |
|-------|---------|---------|
| Build | 暗示 builder-first 定位 | Create / Design / Develop（仅在明确 builder 语境使用） |
| Create | 首页应避免，属于操作动作 | Run / Start / Begin（用于启动治理流程） |
| Generate | 暗示生成式 AI 工具定位 | Audit / Review / Permit |
| Builder | 直接与治理中枢定位冲突 | Governance / Audit / Release |
| Workflow | 首页应避免，属于操作细节 | Process / Flow（仅在流程说明中使用） |
| Canvas | 暗示可视化编辑器定位 | Workspace / Console |
| Template | 首页应避免，暗示 marketplace | Example / Sample |
| Marketplace / Gallery | 暗示交易/分享平台定位 | Registry / Library |

#### 3.2.2 魔法式承诺禁用词（HIGH）

| 禁用词 | 禁用理由 | 替代方案 |
|-------|---------|---------|
| Magic | 过度承诺，降低可信度 | Automated / Streamlined |
| Instant | 不真实的速度承诺 | Fast / Efficient |
| One-click | 暗示零成本，不符合治理复杂度 | Simple / Straightforward |
| Automatic | 可能暗示无需人工参与 | Assisted / Guided |
| Effortless | 不真实的复杂度掩盖 | Streamlined / Simplified |
| Zero-code / No-code | 与治理复杂度矛盾 | Low-code / Guided（仅在适当语境） |
| Drag-and-drop | 过度强调易用性，忽略治理 | Visual interface（仅在 builder 语境） |

#### 3.2.3 审计放行混淆禁用词（CRITICAL）

| 禁用词 | 禁用理由 | 正确术语 |
|-------|---------|---------|
| Audit pass = Approved | 混淆 Audit 与 Permit | Audit pass is not release approval |
| Approved for release | 暗示 Audit 直接放行 | Eligible for permit issuance |
| Ready to deploy | 暗示可直接部署 | Ready for permit issuance |
| Live / Production | 用作状态标签混淆 | Permit Active / Permitted |
| Success / Done | 用作审计结果 | Passed |
| Signed off | 暗示已放行 | Passed audit / Permit issued |

#### 3.2.4 营销式语言禁用词（MEDIUM）

| 禁用词 | 禁用理由 | 替代方案 |
|-------|---------|---------|
| 10x / 100x | 不真实的量化承诺 | Efficient / Streamlined |
| Revolutionize | 过度宣传 | Transform / Improve |
| Game-changer | 营销陈词滥调 | Novel approach / Different |
| World-class | 模糊的夸大 | Reliable / Trusted |
| Best-in-class | 缺乏具体依据 | High-quality / Robust |
| Unmatched | 绝对化表述 | Strong / Comprehensive |
| Never | 绝对化承诺 | Rarely / Uncommon |

#### 3.2.5 成功页式语言禁用词（MEDIUM）

| 禁用词 | 禁用理由 | 替代方案 |
|-------|---------|---------|
| Congratulations | 庆祝式语言，不适合治理场景 | Permit granted / Issued |
| You made it | 口语化庆祝 | Process complete |
| Great job | 评价式语言 | Task completed |
| All set | 模糊的完成表述 | Ready for next step |
| Woohoo / Yay | 过度情绪化 | -（删除） |

---

### 3.3 应用内 CTA 语言规范

#### 3.3.1 Dashboard 应用内 CTA

**主导航 CTA:**

| 位置 | CTA 文本 | 目标 | 说明 |
|------|---------|------|------|
| Workspace Bar | Run Audit | 启动审计流程 | 治理主动作 |
| Priority Queue 行 | Open Audit | 进入 Audit Detail | 查看裁决与证据 |
| Priority Queue 行 | Review Gaps | 进入 Gap Analysis | 查看可修复项 |
| Priority Queue 行 | Issue Permit | 进入 Permit 页面 | 签发放行凭证（仅 Ready for Permit） |

**空状态 CTA:**

| 场景 | CTA 文本 | 目标 | 说明 |
|------|---------|------|------|
| 无资产 | Register Asset | Registry 页面 | 登记新资产 |
| 无审计 | Run First Audit | Dashboard | 启动审计 |
| 无 Permit | Complete Audit First | Audit Detail | 引导先完成审计 |

**禁止:**
- ❌ "Create Skill"
- ❌ "Build Workflow"
- ❌ "Generate New"
- ❌ "Start Building"

#### 3.3.2 Audit Detail 应用内 CTA

**Footer Action Bar CTA:**

| 状态 | CTA 文本 | 目标 | 说明 |
|------|---------|------|------|
| Blocked | View Critical Fixes | Gap 详情 | 查看红线问题 |
| Fix Required | Go to Gap Analysis | Gap 详情 | 查看可修复项 |
| Fix Required | Assign Owner | 任务分配 | 分配修复责任人 |
| Passed | Export AuditPack | 下载 | 导出审计包 |
| Passed | Submit for Permit | Permit 页面 | 申请放行 |
| Ready for Permit | Open Permit Draft | Permit 页面 | 查看许可证草稿 |
| Ready for Permit | Issue Permit | Permit 签发 | 签发放行凭证（仅 Compliance） |

**禁止:**
- ❌ "Deploy Now"
- ❌ "Go to Production"
- ❌ "Release"
- ❌ "Approve"（用于 Audit 阶段）

#### 3.3.3 Permit 应用内 CTA

**Permit Header CTA:**

| CTA 文本 | 目标 | 条件 | 说明 |
|---------|------|------|------|
| Export Permit | 下载 PDF/文档 | 所有状态 | 导出凭证 |
| View Linked Audit | Audit Detail 页面 | 所有状态 | 查看审计基础 |
| Revoke Permit | 撤销操作 | Active 状态 | 撤销凭证（仅 Compliance） |
| View History | 变更历史 | 所有状态 | 查看生命周期 |

**禁止:**
- ❌ "Deploy"
- ❌ "Go Live"
- ❌ "Start Using"
- ❌ "Confirm Release"

---

### 3.4 首页与应用内语言边界

#### 3.4.1 叙事边界定义

**首页叙事（Landing / Marketing 层）:**

| 维度 | 内容 | 示例 |
|------|------|------|
| **这是什么** | 价值主张与定位 | Governance for AI Skills |
| **不是什么** | 边界澄清 | Not a builder. A governance layer. |
| **为什么需要** | 可信性建立 | Evidence-backed decisions. Permit-bound release. |
| **如何开始** | 入口引导 | Run an Audit / See a Permit Example |

**应用内叙事（Dashboard / Audit / Release 层）:**

| 维度 | 内容 | 示例 |
|------|------|------|
| **状态** | 当前资产状态 | In Review / Blocked / Ready for Permit |
| **裁决** | 审计结论 | Blocked due to boundary violation |
| **证据** | 支撑裁决的证据 | 11 evidence items linked |
| **放行** | 许可证状态与范围 | Permit Active for Production, R-014 only |

#### 3.4.2 边界转换点

叙事转换发生在用户从首页进入应用时：

```
首页
  │
  │ 点击 CTA: "Run an Audit" / "See a Permit Example"
  ▼
应用内（Dashboard / Audit / Release）
```

**转换点语言变化:**

| 层级 | 语言特点 | 示例 |
|------|---------|------|
| 首页 | 描述性、教育性、价值导向 | "Evidence-backed decisions" |
| 应用内 | 状态性、操作性、事实导向 | "Passed with 2 fixable gaps" |

#### 3.4.3 禁止的边界混淆

| 混淆类型 | 禁止示例 | 正确做法 |
|---------|---------|---------|
| 首页讲太多技术细节 | "8 Gate Quality Checks with 99.2% pass rate" | 首页只讲 "Evidence-backed decisions" |
| 应用内重复价值教育 | "Welcome to the governance layer" | 应用内直接展示状态与裁决 |
| 首页 CTA 直接进入操作 | "Create your first skill now" | 首页 CTA 进入 Dashboard/Registry |
| 应用内 CTA 回价值页 | "Learn how governance works" | 应用内 CTA 做治理操作 |

---

### 3.5 Audit pass 与 Permit granted 语义区分

#### 3.5.1 核心区分原则

> **Audit pass is not release approval. Permit is.**

| 概念 | 定义 | 权力归属 | 决策依据 |
|------|------|---------|---------|
| **Audit pass** | 资产通过 8 Gate 审计，未触发红线 | Audit Role | Evidence + Rulepack |
| **Permit granted** | 正式签发放行凭证，允许在指定范围发布 | Compliance Role | Audit pass + Scope + Conditions |

#### 3.5.2 语义对照表

| 场景 | Audit pass 表述 | Permit granted 表述 | 混淆风险 |
|------|----------------|-------------------|---------|
| **状态标签** | Passed | Permit Active | 使用 "Approved" 混淆两者 |
| **辅助文案** | Eligible for permit issuance | Issued for production release | 使用 "Ready to deploy" 模糊边界 |
| **CTA** | Submit for Permit | Issue Permit / View Permit | 使用 "Approve" 暗示直接放行 |
| **通知** | Audit passed. Awaiting permit review. | Permit granted. Authorized for release. | 使用 "All set" 掩盖步骤差异 |

#### 3.5.3 语言使用规范

**Audit pass 场景正确用语:**

| 场景 | 正确用语 | 错误用语 |
|------|---------|---------|
| 审计结果通知 | Audit passed | Approved / Ready |
| 审计结果页面 | Passed / Fix Required | Success / Failed |
| 进入下一步 | Submit for Permit | Deploy / Release |
| 资产状态 | Ready for Permit | Ready to go live |

**Permit granted 场景正确用语:**

| 场景 | 正确用语 | 错误用语 |
|------|---------|---------|
| 许可证状态 | Permit Active / Issued | Approved / Live |
| 许可证页面 | Permit granted / Permit issued | Approved / Success |
| 放行范围 | Authorized for [scope] release | Ready to deploy |
| 签发动作 | Issue Permit | Approve / Sign off |

#### 3.5.4 禁止的混淆表述

| 禁止表述 | 问题 | 正确表述 |
|---------|------|---------|
| "Audit passed = Approved for release" | 直接混淆两个概念 | "Audit passed. Eligible for permit issuance." |
| "Ready to deploy" | 不说明是 Audit 还是 Permit | "Ready for permit issuance" 或 "Permit granted for production" |
| "Approved" | 不明确是 Audit 还是 Permit | "Passed audit" 或 "Permit issued" |
| "All set to go live" | 掩盖 Permit 签发步骤 | "Permit granted. Authorized for release." |

---

### 3.6 状态标签语言规范（统一）

#### 3.6.1 审计状态标签

| 状态标签 | 使用场景 | 禁用的替代词 |
|---------|---------|------------|
| Draft | 资产草稿 | - |
| In Audit | 审计中 | Processing / Reviewing |
| Passed | 审计通过 | Success / Done / Approved |
| Fix Required | 需修复 | Needs work / Issues found |
| Blocked | 阻断 | Failed / Rejected |
| Ready for Permit | 待放行 | Ready to deploy / Approved |

#### 3.6.2 许可证状态标签

| 状态标签 | 使用场景 | 禁用的替代词 |
|---------|---------|------------|
| Pending | 等待签发 | Waiting / In progress |
| Active | 生效中 | Live / Approved / Success |
| Revoked | 已撤销 | Cancelled |
| Expired | 已过期 | Outdated / Old |
| Superseded | 已被替代 | Replaced / Updated |

---

## 四、交付物验收清单

- [x] 1. 首页 headline 已定义（含替代方案）
- [x] 2. 首页 subheadline 已定义（含替代方案）
- [x] 3. 首页 CTA 已定义（主/次/第三 CTA）
- [x] 4. 首页场景区文案结构已定义（Audit / Permit / Governance）
- [x] 5. 文案禁用词清单已输出（5 大类）
- [x] 6. 应用内 CTA 语言规范已输出（Dashboard / Audit Detail / Permit）
- [x] 7. 首页与应用内语言边界已明确
- [x] 8. Audit pass 与 Permit granted 语义区分已明确
- [x] 9. 状态标签语言规范已统一
- [x] 10. 未使用禁用词
- [x] 11. 三段式结构（PreflightChecklist/ExecutionContract/RequiredChanges）已完成

---

**文档版本**: v1.0
**最后更新**: 2026-03-12

**EvidenceRef**: 本规格基于以下文档合成:
- `docs/2026-03-12/前端重构_AI军团任务分发单_v2.md` (L494-539)
- `docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md` (L1086-1142)
- `docs/2026-03-12/verification/T-FE-02_dashboard_spec.md` (Dashboard CTA 定义)
- `docs/2026-03-12/verification/T-FE-03_audit_detail_spec.md` (Audit Detail CTA 定义)
- `docs/2026-03-12/verification/T-FE-04_permit_spec.md` (Permit CTA 与语义定义)
- `multi-ai-collaboration.md` (完整文档)
- `docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md` (完整文档)
- `docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md` (完整文档)
