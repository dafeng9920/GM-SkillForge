结论：
下面直接给你一套可落地的 **Dashboard / Audit Detail / Permit** 三页文字线框图。
目标不是“看起来像 SaaS”，而是让这三页天然长成 **治理控制层**：先看状态，再看裁决，再看放行。
我按 **桌面端优先（1440 宽）** 来写，方便你后面直接交给 UI 设计或前端拆组件。

置信度：0.92

关键风险点：

1. 线框如果把图表做得太重，会稀释“决策与放行”的主线。
2. Audit Detail 如果信息顺序不对，用户会先看到细节，后看到结论，体验会散。
3. Permit 页如果不够正式，会掉成“成功提示页”而不是“放行凭证页”。
4. 如果把内部规则与执行机制暴露过多，会破坏“裁决权威”和系统保护边界。

---

# 零、合并后的总原则

这一版已经合并了 `docs/2026-03-12` 下今天两份文档，以及 `Gemini / Claude` 两版关于前端架构的共识，所以在三页线框图之前，先把统一原则钉死。

## 1）前端主定位

GM-SkillForge 的前端不应该被理解成：

* AI builder
* skill marketplace
* workflow canvas
* 普通生成器控制台

它更准确的定义是：

* 治理中枢
* 审计工作台
* 放行控制层

一句话总定义：

> **这个前端不是让用户“搭东西”的主舞台，而是让用户“接受裁决、查看证据、获得放行”的控制层。**

## 2）这是结构性矛盾，不是设计失误

这类系统天然同时承载两个相互冲突的目标：

* 建立信任：必须让用户相信 `Audit Decision / Final Accept / Permit` 不是拍脑袋给的
* 保护机制：不能把底层规则、阈值、权重、阻断逻辑、执行拓扑暴露出去

所以它不是普通 SaaS 那种“功能展示 vs 学习成本”的 UX 问题，而是：

**可信性展示 vs 核心机制保护**

这意味着不能靠“把所有内部逻辑都讲清楚”来换取信任，只能靠：

* 结论
* 证据
* 分层展示
* 权限隔离

## 3）前端真正卖的东西

这套系统前端真正卖的不是：

* 流程
* 编排体验
* 生成功能
* 炫技图形

而是：

**Adjudication Authority + Evidence Presence**

也就是：

* 系统有资格下结论
* 这个结论有证据支撑
* 但用户不能在前端反推出裁决机理本身

最适合作为设计规范首页总句的是：

> **前端只负责出示不容置疑的“判决书”与“证据链”，永远不要试图向用户解释“法官”的推理过程与调查手段。**

## 4）四层信息分层模型

### Layer 0：对外公示层

允许展示：

* 审计维度名称
* 系统级结果摘要
* Permit 状态
* 封板摘要
* 时间戳与统计量级

禁止展示：

* 规则细节
* 阈值
* 调度方式
* 阻断逻辑

### Layer 1：内部工作台

允许展示：

* 执行主链状态
* 审计通过/失败
* 当前 Gate
* 红线 / 可修复项分类
* Permit readiness

不应展示：

* 规则权重
* 底层模块拓扑
* 可被逆向的判定树

### Layer 2：受控详情层

允许展示：

* Evidence Bundle
* Metrics
* Hash
* Revision lineage
* Signoff 历史
* 受控证据包

仍不应展示：

* pre_absorb_check 规则树
* absorb 内部处理逻辑
* L3 评分算法与权重

### Layer 3：禁止前端呈现区

任何角色都不应看到：

* 判定阈值
* 算法权重
* 探针代码
* 阻断触发路径
* 绕过路径
* 内部执行拓扑
* API 调用依赖顺序图

## 5）四条强约束设计原则

### 原则 1：只出示探针结果，不出示探针代码

前端组件只能展示：

* 输入物
* 输出物
* 违规项 / 安全评级 / 结论

不得展示：

* regex
* rule expression
* 内部脚本引用
* 具体探针实现方式

### 原则 2：证据链必须快照化、不可变

对 `L4 Evidence / L5 Reproducibility / Signoff / Permit` 的 UI 语义必须偏：

* 只读
* 存档感
* 时间戳明确
* Hash 明确
* 不可编辑

### 原则 3：执行链只展示状态流转，不解释内部异常

`Permit -> pre_absorb_check -> absorb -> local_accept -> final_accept`
在前端上应展示：

* 当前阶段
* 用时
* 卡点
* 建议动作

而不是：

* 内部异常栈
* 模块级报错
* 系统实现细节

### 原则 4：权限决定信息密度，且必须在后端裁剪

不同角色看到的信息层级不同，但不能靠前端“隐藏字段”实现。

必须：

* 由 API 按角色返回不同 payload

不应：

* 在前端通过角色判断后再裁剪字段

## 6）三页统一语义

这三页的统一职责是：

* `Dashboard`：全局治理与放行总控
* `Audit Detail`：裁决解释与证据闭环
* `Permit`：正式放行凭证与生效边界

它们共同组成的语义链应该是：

**Governed Asset -> Audited Decision -> Permit-bound Release**

而不是：

**Idea -> Generate -> Success**

---

# 一、Dashboard 文字线框图

## 页面定位

全局治理总控页。
用户进入后先回答三件事：

* 现在有哪些资产卡住了
* 哪些资产已经接近放行
* 我下一步该处理什么

---

## 1）页面骨架

```text
┌──────────────────────────────────────────────────────────────────────┐
│ Top Nav                                                             │
│ [GM-SkillForge] [Overview] [Forge] [Audit] [Release] [Registry] ... │
│                                              [Search] [Alerts] [Me] │
├──────────────────────────────────────────────────────────────────────┤
│ Workspace Bar                                                       │
│ [Workspace: Default] [Project: All] [Time Range] [Filter] [Run Audit]│
├──────────────────────────────────────────────────────────────────────┤
│ Page Title                                                          │
│ Overview                                                            │
│ “Governed assets, audit status, permit readiness.”                  │
├──────────────────────────────────────────────────────────────────────┤
│ KPI Row                                                             │
│ [In Review] [Blocked] [Fix Required] [Ready for Permit] [Permitted] │
├──────────────────────────────────────────────────────────────────────┤
│ Main Grid Row 1                                                     │
│ ┌──────────────────────────────┐ ┌────────────────────────────────┐ │
│ │ 8 Gate Health / Funnel       │ │ Priority Queue                 │ │
│ │ pass/fail/warn distribution  │ │ assets needing action now      │ │
│ └──────────────────────────────┘ └────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────┤
│ Main Grid Row 2                                                     │
│ ┌──────────────────────────────┐ ┌────────────────────────────────┐ │
│ │ Evidence Coverage            │ │ Gap Hotspots                   │ │
│ │ completeness / weakness      │ │ common failures by rule/gate   │ │
│ └──────────────────────────────┘ └────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────┤
│ Main Grid Row 3                                                     │
│ ┌──────────────────────────────┐ ┌────────────────────────────────┐ │
│ │ Recent Permit Events         │ │ Revision Watch                 │ │
│ │ issued/revoked/expired       │ │ recent changes requiring review│ │
│ └──────────────────────────────┘ └────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 2）模块详细说明

## A. Top Nav

作用：建立系统气质。
不要出现 “Builder / Create / Magic”。

包含：

* Logo
* 一级导航：Overview / Intake / Forge / Audit / Release / Registry / History / Policies
* 全局搜索
* 通知
* 用户菜单

---

## B. Workspace Bar

作用：告诉用户“这是控制台，不是单页工具”。

字段：

* Workspace 切换
* Project 切换
* Time Range
* Filter
* 主 CTA：**Run Audit**

右侧也可以加：

* `Only blocked`
* `Only ready for permit`

---

## C. KPI Row

5 张核心状态卡，必须是首屏最高权重。

### 卡 1：In Review

* 数量
* 辅助文案：currently in audit flow

### 卡 2：Blocked

* 数量
* 辅助文案：critical issues triggered

### 卡 3：Fix Required

* 数量
* 辅助文案：repairable gaps found

### 卡 4：Ready for Permit

* 数量
* 辅助文案：audit passed, waiting release approval

### 卡 5：Permitted

* 数量
* 辅助文案：active release credentials

交互：

* 点击任一卡片，右侧列表或全页进入对应筛选结果

---

## D. 8 Gate Health / Funnel

布局建议：左侧图，右侧摘要。

内容：

* Gate 1 → Gate 8 的流转状态
* 每个 Gate 的 pass/warn/fail 数
* 当前最堵的 Gate
* top failure reason

展开项：

* Gate 名
* 阻断数量
* 通过率
* 触发规则数

交互：

* 点击 Gate 3，Priority Queue 自动筛到“卡在 Gate 3 的资产”

---

## E. Priority Queue

这是 Dashboard 最关键的业务列表。

列表字段建议：

* Asset Name
* Revision
* Current Status
* Current Gate
* Risk Level
* Next Action
* Owner
* Last Updated

每行右侧动作：

* `Open Audit`
* `Review Gaps`
* `Issue Permit`（仅 Ready for Permit）

排序建议：

1. Ready for Permit
2. Critical Blocked
3. Client-facing delivery
4. Recent changed revisions

---

## F. Evidence Coverage

内容：

* evidence completeness score
* weak evidence cases
* no evidence / summary-only / sufficient evidence 分布
* 证据不足的资产列表

价值：
这块会把“不是黑盒”这件事显出来。

---

## G. Gap Hotspots

内容：

* 最常见失败 Rule
* 对应 Gate
* 受影响资产数量
* 平均修复轮次

展示方式：

* Top 5 gap clusters
* 点击进入 Gap Analysis 列表

---

## H. Recent Permit Events

字段：

* Permit ID
* Asset
* Status：Issued / Revoked / Expired / Replaced
* Signed by
* Time

右侧动作：

* `View Permit`

---

## I. Revision Watch

字段：

* Asset
* New Revision
* Change Impact
* Audit Required?
* Permit invalidated?

作用：
告诉用户这个系统不是“一次性审完就算了”。

---

## 3）Dashboard 固定状态条

建议首屏 KPI 下方加一条动态提示条：

### 情况 1：存在阻断

`3 critical assets are blocked by Gate 4 / Gate 6 rules.`

### 情况 2：存在待签发

`2 assets passed audit and are waiting for permit issuance.`

### 情况 3：存在 Permit 失效

`1 active permit was invalidated by revision drift.`

---

# 二、Audit Detail 文字线框图

## 页面定位

这是全系统最重要的一页。
它必须像“裁决页 + 审计工作台 + 修复入口”。

---

## 1）页面骨架

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ Top Nav                                                                 │
├──────────────────────────────────────────────────────────────────────────┤
│ Breadcrumb                                                              │
│ Registry / Asset Name / Revision R-014                                  │
├──────────────────────────────────────────────────────────────────────────┤
│ Decision Header                                                         │
│ Asset: Skill A                Revision: R-014                           │
│ Status: [Blocked]             Audit Version: v1.0                       │
│ decision_hash: xxx...         audited at: 2026-03-12                    │
│ [Review Gaps] [Export AuditPack] [Re-run Audit] [Submit for Permit]     │
├──────────────────────────────────────────────────────────────────────────┤
│ Summary + Authority Boundary                                            │
│ ┌───────────────────────────────┐ ┌───────────────────────────────────┐ │
│ │ Decision Summary              │ │ Power Boundary                    │ │
│ │ why pass/fail                 │ │ Execution / Audit / Compliance    │ │
│ └───────────────────────────────┘ └───────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────┤
│ Main Content                                                            │
│ ┌──────────────────────────────────────────────┐ ┌────────────────────┐ │
│ │ 8 Gate Timeline / Gate Details              │ │ EvidenceRef Panel   │ │
│ │ gate status, rule triggers, explanations    │ │ source, strength... │ │
│ └──────────────────────────────────────────────┘ └────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────┤
│ Issue Breakdown                                                         │
│ ┌───────────────────────────────┐ ┌───────────────────────────────────┐ │
│ │ Red Lines                     │ │ Fixable Gaps                      │ │
│ │ must block                    │ │ can repair and resubmit          │ │
│ └───────────────────────────────┘ └───────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────┤
│ Governance Snapshot                                                     │
│ ┌───────────────────────────────┐ ┌───────────────────────────────────┐ │
│ │ Contract / Control Snapshot   │ │ Hash & Reproducibility            │ │
│ │ constitution, rules, controls │ │ demand/contract/decision hashes   │ │
│ └───────────────────────────────┘ └───────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────┤
│ Footer Action Bar                                                       │
│ [Go to Gap Analysis] [Assign Owner] [Re-run Audit] [Submit for Permit] │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 2）模块详细说明

## A. Breadcrumb

`Registry / Payment Agent Skill / Revision R-014`

好处：

* 强化“这是资产治理”，不是临时任务页
* revision 直接可见

---

## B. Decision Header

这是正式感的来源。

字段必须有：

* Asset Name
* Asset Type：Skill / Workflow / Agent Asset
* Revision ID
* Current Status
* Audit Version
* decision_hash
* audited at
* owner / reviewer（可选）

状态标签只建议用：

* Draft
* In Audit
* Passed
* Fix Required
* Blocked
* Ready for Permit

不要写：

* Success
* Done
* Completed

---

## C. Decision Summary

建议卡片中拆成 4 行：

1. **Final Decision**
   `Blocked`

2. **Primary Reason**
   `Execution boundary leakage detected under Gate 4.`

3. **Evidence Sufficiency**
   `Sufficient for rejection`

4. **Permit Readiness**
   `Not eligible until critical gaps are resolved`

底部再放三个小标签：

* Critical issues: 2
* Fixable gaps: 4
* Evidence refs: 11

---

## D. Power Boundary

这是你的特色，必须常驻可见。

推荐呈现：

```text
Execution
- Can run
- Can produce outputs
- Cannot approve release

Audit
- Can inspect evidence
- Can issue audit decision
- Cannot issue permit

Compliance
- Can issue or revoke permit
- Can define release conditions
- Cannot modify execution output
```

这块最好做成 3 列卡片，位置靠上，不要藏。

---

## E. 8 Gate Timeline / Gate Details

这是页面主体。

每个 Gate 卡片包含：

* Gate 名称
* Status
* Triggered rules
* Evidence count
* 1 行说明

展开后内容：

* What failed / passed
* Why it matters
* Which rules triggered
* Which evidence supports the finding
* What to fix next

建议展开态结构：

```text
Gate 4 — Boundary Integrity   [Fail]

Reason
Execution logic exceeded declared control scope.

Triggered Rules
- RULE-4.2
- RULE-4.7

Evidence
- EVD-003: runtime trace mismatch
- EVD-006: undeclared action path

Fix Suggestion
- tighten declared control boundaries
- update ControlSpec and resubmit
```

---

## F. EvidenceRef Panel

建议放右侧 sticky panel。

每条 EvidenceRef 字段：

* Evidence ID
* Source Type
* Summary
* Strength：Weak / Medium / Strong
* Visibility：Visible / Summary only / Restricted
* Linked Gate

点击某条 evidence 后：

* 中间内容联动高亮对应 Gate
* 下方出现 evidence 摘要说明

这会非常像“审计系统”，而不是“模型解释卡片”。

---

## G. Red Lines vs Fixable Gaps

必须分左右两栏。

### Red Lines

每条字段：

* Issue title
* Impact
* Triggered Gate
* Rule
* Why blocking
* Required disposition

### Fixable Gaps

每条字段：

* Gap title
* Severity
* Related Gate
* Suggested fix
* Expected re-review outcome

目的：
让用户明白哪些问题是“碰都不能碰”，哪些问题是“修了可过”。

---

## H. Contract / Control Snapshot

放一块中等权重卡片。

内容：

* Contract summary
* Constitution version
* Rule pack version
* ControlSpec version
* linked manifest
* audit scope

这是企业用户判断可信度的重要区域。

---

## I. Hash & Reproducibility

字段：

* demand_hash
* contract_hash
* decision_hash
* revision lineage
* linked manifest ID

右侧可放一句说明：
`This decision is bound to the current revision and policy context.`

---

## J. Footer Action Bar

固定底部，按状态变化。

### 状态 Blocked

* View critical fixes
* Export fix brief
* Re-run after changes

### 状态 Fix Required

* Go to Gap Analysis
* Assign owner
* Re-submit to audit

### 状态 Passed

* Export AuditPack
* Submit for Permit

### 状态 Ready for Permit

* Open Permit Draft
* Issue Permit

---

# 三、Permit 文字线框图

## 页面定位

正式放行页。
它不是“你通过了”，而是“你被允许在特定边界下发布”。

---

## 1）页面骨架

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ Top Nav                                                                 │
├──────────────────────────────────────────────────────────────────────────┤
│ Breadcrumb                                                              │
│ Release / Permit / PMT-2026-0312-014                                    │
├──────────────────────────────────────────────────────────────────────────┤
│ Permit Header                                                           │
│ Permit ID: PMT-2026-0312-014                                             │
│ Asset: Skill A            Revision: R-014                                │
│ Status: [Active]          Effective: 2026-03-12                          │
│ Signed by: Compliance-01 Scope: Production / Internal                    │
│ [Export Permit] [View Linked Audit] [Revoke Permit] [View History]       │
├──────────────────────────────────────────────────────────────────────────┤
│ Core Decision Block                                                     │
│ ┌──────────────────────────────────────────────────────────────────────┐ │
│ │ Permit granted                                                      │ │
│ │ Audit pass is not release approval. Permit is.                      │ │
│ │ This permit is bound to revision R-014 and current rulepack v1.0    │ │
│ └──────────────────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────┤
│ Main Grid                                                               │
│ ┌──────────────────────────────┐ ┌────────────────────────────────────┐ │
│ │ Release Scope                │ │ Conditions                         │ │
│ │ env / asset / boundary       │ │ must hold / invalidation triggers  │ │
│ └──────────────────────────────┘ └────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────┤
│ Linked Basis                                                            │
│ ┌──────────────────────────────┐ ┌────────────────────────────────────┐ │
│ │ Audit Basis                  │ │ Evidence / Policy Basis            │ │
│ │ linked auditpack, hashes     │ │ evidence summary, ruleset version  │ │
│ └──────────────────────────────┘ └────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────┤
│ Lifecycle + Signature                                                   │
│ ┌──────────────────────────────┐ ┌────────────────────────────────────┐ │
│ │ Permit Lifecycle             │ │ Compliance Signature               │ │
│ │ audit > ready > issued ...   │ │ signer, note, timestamp            │ │
│ └──────────────────────────────┘ └────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────┤
│ Residual Risk Reminder                                                  │
│ [Known operational risks] [Monitoring expectations] [Re-audit triggers] │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 2）模块详细说明

## A. Permit Header

必须像证书抬头。

字段：

* Permit ID
* Asset Name
* Revision
* Status
* Effective Date
* Signed by
* Scope

状态只建议：

* Pending
* Active
* Revoked
* Expired
* Superseded

---

## B. Core Decision Block

大卡片，视觉强调最强。

内容建议：

### 主结论

`Permit granted`

### 副说明

`Audit pass is not release approval. Permit is.`

### 绑定说明

`Bound to revision R-014, contract_hash xxx, decision_hash xxx`

### 当前动作建议

`Allowed for release within declared scope only`

---

## C. Release Scope

字段建议：

* Environment：Internal / Production / Client Delivery
* Asset Boundary：具体资产名
* Revision Scope：R-014 only
* Invocation Boundary：declared only
* Valid Use Context：例如 internal ops only

作用：
告诉用户“放行不是无限授权”。

---

## D. Conditions

字段建议：

* Must remain unchanged from certified revision
* Re-audit required on contract change
* Permit invalidates on rulepack mismatch
* Permit invalidates on undeclared execution path
* Monitoring expected for runtime drift

这块很关键，因为它体现“稳定治理”。

---

## E. Audit Basis

字段：

* Linked Audit ID
* Audit result
* decision_hash
* contract_hash
* audit version
* reviewed at

按钮：

* `Open Audit Detail`

---

## F. Evidence / Policy Basis

字段：

* Evidence summary count
* Evidence sufficiency level
* Rulepack version
* Constitution version
* Compliance note

---

## G. Permit Lifecycle

时间线建议：

```text
Audit Completed
↓
Passed Audit
↓
Ready for Permit
↓
Permit Issued
↓
Active
↓
[Optional] Revoked / Superseded / Expired
```

点击任一节点可看时间、操作者、说明。

---

## H. Compliance Signature

字段：

* signed by
* signed at
* signature note
* approval remarks
* release comments

即便 v0 没有电子签样式，也要把这块作为正式模块保留。

---

## I. Residual Risk Reminder

这里会增加可信度。

字段建议：

* Known residual risks
* Monitoring expectations
* Runtime drift triggers
* Mandatory re-audit triggers

目的：
告诉用户 Permit 不是“绝对没风险”，而是“在边界内可放行”。

---

# 四、三页共用的组件规范

## 1. 状态标签规范

统一使用：

* Draft
* In Audit
* Passed
* Fix Required
* Blocked
* Ready for Permit
* Permit Active
* Permit Revoked
* Permit Expired

不要混用 success / approved / done / live 这种偏营销词。

---

## 2. 右侧详情抽屉

三页都建议共用一个右侧抽屉，用来展示：

* rule detail
* evidence detail
* revision detail
* audit note
* permit note

这样信息密度高，但不炸页面。

---

## 3. 底部动作栏

Audit Detail 和 Permit 都建议有固定底部 action bar。
因为用户最后总会回到底部做决定。

---

## 4. hash 展示规范

统一展示方式：

* 前 8 位 + 省略 + hover 全量
* 可复制
* 可跳转 linked object

---

# 五、这三页最容易做歪的地方

## Dashboard

别做成“炫图表 BI 大屏”。
它首先是指挥台，不是展示墙。

## Audit Detail

别把 Evidence、Rule、Gate、Gap 混成一锅。
顺序必须是：**结论 → 原因 → 证据 → 修复**。

## Permit

别做成一个大绿勾加“Release allowed”。
必须有 **范围、条件、签发、生命周期**。

---

# 六、合并后的补充落地建议

这一节吸收今天两份文档里更偏产品架构与推进顺序的部分，用来约束后续 UI/UX 重构。

## 1）页面优先级重新确认

如果继续推进前端，建议优先级是：

1. `Audit Detail`
2. `Permit`
3. `Dashboard`

原因：

* `Audit Detail` 定义系统的可信裁决语言
* `Permit` 定义商业闭环和放行权威
* `Dashboard` 再把前两者组织成全局管理体验

## 2）首页与应用内叙事分工

首页负责：

* 讲价值
* 讲边界
* 讲治理流程

应用内负责：

* 讲状态
* 讲裁决
* 讲证据
* 讲放行

所以首页 CTA 应偏向：

* `Run an Audit`
* `See a Permit Example`

而不是：

* `Build a Skill`
* `Generate Now`

## 3）必须显式保留的系统独特性

后续视觉与组件设计里，以下内容必须常驻可见，不能埋太深：

* 三权分立
* 8 Gate
* EvidenceRef
* Permit as only release credential
* Revision + Hash 绑定
* Red Lines vs Fixable Gaps

## 4）当前阶段不要做重的部分

最容易把产品做歪的模块，应暂缓：

* 复杂 workflow canvas
* 模板市场 / skill 广场
* 社区化首页
* 炫技 BI 大屏
* 过早做重 RBAC 门户

当前最该做硬的是：

* 决策头部
* 审计主体
* Permit 凭证感
* Registry / History 的持续治理感

## 5）最终一句话定位

> **GM-SkillForge 的前端不是 AI builder 的操作面，而是治理系统的判决书、证据台和放行凭证层。**

---

## 配套执行文档

如果下一步要直接转给 AI 军团执行，请配合使用：

* `docs/2026-03-12/前端重构_AI军团执行指令提示词_v1.md`

该文档已经把本稿进一步压缩成：

* 主控官 Prompt
* IA 执行体 Prompt
* Page Spec 执行体 Prompt
* Frontend Mapping 执行体 Prompt
* Review Agent Prompt
* Compliance Agent Prompt

---


