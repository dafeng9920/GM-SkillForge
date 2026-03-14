# T-FE-02: Dashboard 页面规格书

> **任务 ID**: T-FE-02
> **执行者**: vs--cc1
> **审查者**: Kior-A
> **合规官**: Kior-B
> **日期**: 2026-03-12
> **依赖**: T-FE-01 (ALLOW)

---

## 一、PreflightChecklist

### 1.1 Fail-Closed 风险枚举

| 风险类别 | 潜在绕过路径 | 防御措施 |
|---------|-------------|---------|
| BI 大屏化 | Dashboard 可能被设计成炫图表的大屏展示，弱化治理总控定位 | 明确禁止炫图表，强制"先看状态，再看风险，再看可执行动作"的信息层次 |
| Builder 叙事渗透 | 可能出现 Generate/Build/Create 作为主 CTA | 强制主 CTA 为 Run Audit/Review Gaps/Issue Permit/View Audit Trail |
| 机制信息泄漏 | 可能通过图表/统计暴露阈值、权重、判定逻辑 | 严格限制展示层级，只展示结果态，不展示判定机理 |
| 视觉权重错配 | 可能把 Forge 或生成动作放在最高视觉权重 | 明确 Dashboard 主视觉权重为 KPI Row + Priority Queue + 8 Gate Health |

### 1.2 依赖环境

| 依赖项 | 当前状态 | 必需值 |
|-------|---------|-------|
| T-FE-01 IA Spec | ALLOW | 已确立首页讲价值、应用内讲裁决原则 |
| 三页主链定义 | 已定义 | Dashboard/Audit Detail/Permit 角色 |
| 四层信息分层 | 已定义 | Layer 0/1/2 可展示范围 |

### 1.3 历史债务扫描

| 债务类型 | 位置 | 处理策略 |
|---------|-----|---------|
| 现有 Dashboard 可能偏向 BI | ui/app/src/pages/ | 本规格明确禁止项，后续 T-FE-06 裁剪 |

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
- 新建 `docs/2026-03-12/verification/T-FE-02_dashboard_spec.md` (本文件)

**绝对禁止:**
- 修改现有前端代码实现
- 定义具体组件视觉实现细节
- 把 Dashboard 做成炫图表 BI 大屏
- 把 Generate/Build/Create 做成主 CTA
- 把生成动作放到 Dashboard 的最高视觉权重
- 越权写到具体组件实现

### 2.2 Output Definition

**交付物:**
- 本 Dashboard 规格文档，包含：
  1. Dashboard 页面目标
  2. Dashboard 页面骨架
  3. 模块列表与模块优先级
  4. CTA 列表
  5. 空状态/高风险状态/待签发状态
  6. 禁止展示项

**回滚方案:**
- 本文档为规格说明，不涉及代码变更，无需回滚
- 如规格有误，可通过 Review/Compliance 流程修正

### 2.3 Gate / Acceptance Check

**手动检查:**
- [ ] 是否先看状态，再看风险，再看可执行动作
- [ ] 是否保留 8 Gate/Priority Queue/Evidence Coverage/Permit Events/Revision Watch
- [ ] 是否未把 Dashboard 做成炫图表 BI 大屏
- [ ] 是否未把 Generate/Build/Create 做成主 CTA

---

## 三、RequiredChanges

### 3.1 Dashboard 页面目标

#### 3.1.1 核心定位

Dashboard 是 **全局治理总控台**，不是 BI 大屏，不是 Builder 控制台。

用户进入 Dashboard 后，必须能立即回答三个问题：
1. **现在有哪些资产卡住了？** → KPI Row + Priority Queue
2. **哪些资产已经接近放行？** → KPI Row (Ready for Permit)
3. **我下一步该处理什么？** → Priority Queue + 主 CTA

#### 3.1.2 设计原则

| 原则 | 说明 | 禁止 |
|-----|------|-----|
| **状态先行** | 首屏最高权重是五态 KPI 卡片 | 先展示图表或操作按钮 |
| **风险优先** | Blocked/Critical 必须视觉突出 | 平铺展示所有状态 |
| **动作收敛** | 每个资产只保留 1-2 个核心动作 | 暴露过多次要操作 |
| **证据可见** | Evidence Coverage 必须常驻 | 隐藏证据完整性信息 |
| **门禁透明** | 8 Gate 健康度必须可见 | 仅展示最终通过率 |

#### 3.1.3 与其他页面的职责边界

| 页面 | 职责 | 不在此页 |
|-----|------|---------|
| **Dashboard** | 总览状态、优先队列、门禁健康、证据覆盖、许可事件 | 单资产详情、具体裁决解释 |
| **Audit Detail** | 单资产裁决详情、证据链、红线/可修复项 | 全局状态总览 |
| **Permit** | 单资产放行凭证、范围、条件、生命周期 | 门禁健康、证据覆盖 |

---

### 3.2 Dashboard 页面骨架

```
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
│ "Governed assets, audit status, permit readiness."                  │
├──────────────────────────────────────────────────────────────────────┤
│ KPI Row (最高视觉权重)                                                │
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
│ │ completeness / weakness      │ │ common failures by rule/gate   │
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

### 3.3 模块列表与模块优先级

#### 3.3.1 P0 模块 (MUST)

| 模块名称 | 优先级 | 核心字段 | 位置 |
|---------|-------|---------|------|
| **KPI Row** | P0 | In Review / Blocked / Fix Required / Ready for Permit / Permitted | 首屏最高位置 |
| **Priority Queue** | P0 | Asset Name, Revision, Current Status, Current Gate, Risk Level, Next Action, Owner, Last Updated | Main Grid Row 1 右侧 |
| **8 Gate Health** | P0 | Gate 名称, pass/warn/fail 数, 当前最堵的 Gate, top failure reason | Main Grid Row 1 左侧 |

#### 3.3.2 P1 模块 (SHOULD)

| 模块名称 | 优先级 | 核心字段 | 位置 |
|---------|-------|---------|------|
| **Evidence Coverage** | P1 | evidence completeness score, weak evidence cases, no evidence/summary-only/sufficient evidence 分布 | Main Grid Row 2 |
| **Recent Permit Events** | P1 | Permit ID, Asset, Status (Issued/Revoked/Expired/Replaced), Signed by, Time | Main Grid Row 3 |

#### 3.3.3 P2 模块 (NICE)

| 模块名称 | 优先级 | 核心字段 | 位置 |
|---------|-------|---------|------|
| **Gap Hotspots** | P2 | 最常见失败 Rule, 对应 Gate, 受影响资产数量, 平均修复轮次 | Main Grid Row 2 |
| **Revision Watch** | P2 | Asset, New Revision, Change Impact, Audit Required?, Permit invalidated? | Main Grid Row 3 |

---

### 3.4 核心模块详细规格

#### 3.4.1 KPI Row (五态卡片)

**位置**: Workspace Bar 下方，首屏最高视觉权重

**五张卡片规格:**

| 卡片名称 | 显示内容 | 辅助文案 | 点击行为 |
|---------|---------|---------|---------|
| **In Review** | 数量 | currently in audit flow | 筛选 Priority Queue 显示 In Review 状态 |
| **Blocked** | 数量 | critical issues triggered | 筛选 Priority Queue 显示 Blocked 状态 |
| **Fix Required** | 数量 | repairable gaps found | 筛选 Priority Queue 显示 Fix Required 状态 |
| **Ready for Permit** | 数量 | audit passed, eligible for permit issuance | 筛选 Priority Queue 显示 Ready for Permit 状态 |
| **Permitted** | 数量 | active release credentials | 筛选 Priority Queue 显示 Permitted 状态 |

**视觉强调规则:**
- Blocked 卡片使用红色/警告色
- Ready for Permit 卡片使用绿色/成功色
- 其他卡片使用中性色

---

#### 3.4.2 8 Gate Health / Funnel

**位置**: Main Grid Row 1 左侧

**核心字段:**
- Gate 1 → Gate 8 的流转状态
- 每个 Gate 的 pass/warn/fail 数
- 当前最堵的 Gate
- top failure reason

**展开项 (安全治理摘要，仅结果态):**
- Gate 名
- 阻断数量
- 通过率
- 受影响资产数量

**交互:**
- 点击 Gate 3, Priority Queue 自动筛到"卡在 Gate 3 的资产"

**禁止展示 (机制泄露防御 - CRITICAL):**
- 规则阈值 (threshold)
- 规则权重 (weight)
- 规则细节或规则表达式 (rule expression)
- 判定逻辑说明 (decision logic)
- 触发规则详情 (triggered rule details)
- 规则与 Gate 的映射关系 (rule-to-gate mapping)
- 探针代码或探针信息 (probe code/info)
- 判定路径可视化 (decision path visualization)

**允许展示 (仅纯数字统计):**
- 规则触发数量 (triggered rule count) - 仅纯数字，不关联具体规则内容
- 资产通过/失败数量 (pass/fail count) - 仅数量统计

---

#### 3.4.3 Priority Queue

**位置**: Main Grid Row 1 右侧 (Dashboard 最关键的业务列表)

**列表字段:**

| 字段 | 说明 | 示例 |
|-----|------|-----|
| Asset Name | 资产名称 | Payment Agent Skill |
| Revision | 版本号 | R-014 |
| Current Status | 当前状态 | Blocked / Fix Required / Ready for Permit |
| Current Gate | 当前卡在哪个门禁 | Gate 4 |
| Risk Level | 风险等级 | Critical / High / Medium / Low |
| Next Action | 下一步操作 | Review Gaps / Issue Permit |
| Owner | 负责人 | vs--cc1 |
| Last Updated | 最后更新时间 | 2 hours ago |

**每行右侧动作:**

| 状态 | 可用动作 |
|-----|---------|
| 所有状态 | `Open Audit` (链接到 Audit Detail) |
| 有 Gap 的状态 | `Review Gaps` (展开 Gap 列表) |
| Ready for Permit | `Issue Permit` (跳转 Permit 页面) |

**排序规则:**
1. Ready for Permit (优先)
2. Critical Blocked
3. Client-facing delivery
4. Recent changed revisions

---

#### 3.4.4 Evidence Coverage

**位置**: Main Grid Row 2 左侧

**核心字段:**
- evidence completeness score (0-100)
- weak evidence cases 数量
- no evidence / summary-only / sufficient evidence 分布 (仅结果态分类，不得展示分类依据)
- 证据不足的资产列表 (最多 5 条)

**价值:**
- 把"不是黑盒"这件事显出来
- 让用户了解裁决的可信度

**禁止展示 (机制泄露防御 - CRITICAL):**
- Evidence 内部内容 (摘要之外)
- 证据收集方法 (evidence collection method)
- 证据权重计算方式 (evidence weight calculation)
- 证据来源探针信息 (evidence source probe info)
- 证据分类依据 (evidence classification criteria)
- 证据强度判定逻辑 (evidence strength decision logic)
- 证据收集路径可视化 (evidence collection path visualization)

**允许展示 (仅充分性/完整性层):**
- evidence completeness score (0-100) - 仅最终评分
- weak evidence cases 数量 - 仅数量统计
- 证据充分性等级 (evidence sufficiency level) - 仅等级标签

---

#### 3.4.5 Recent Permit Events

**位置**: Main Grid Row 3 左侧

**字段:**

| 字段 | 说明 |
|-----|------|
| Permit ID | 许可证 ID |
| Asset | 资产名称 |
| Status | Issued / Revoked / Expired / Replaced |
| Signed by | 签发者 |
| Time | 时间戳 |

**右侧动作:**
- `View Permit` (跳转 Permit 页面)

---

### 3.5 CTA 列表

#### 3.5.1 Workspace Bar 主 CTA

| CTA 文本 | 目标 | 优先级 |
|---------|------|-------|
| **Run Audit** | 触发新的审计流程 | 最高 |
| Filter | 筛选显示内容 | 中 |
| Only blocked | 仅显示阻断项 | 低 |
| Only ready for permit | 仅显示待签发项 | 低 |

#### 3.5.2 Priority Queue 行内 CTA

| CTA 文本 | 目标 | 条件 |
|---------|------|-----|
| **Open Audit** | 跳转 Audit Detail | 所有状态 |
| **Review Gaps** | 展开/跳转 Gap 列表 | 有 Gap 的状态 |
| **Issue Permit** | 跳转 Permit 页面 | Ready for Permit |

#### 3.5.3 强化 CTA (硬约束)

**必须强化的 CTA:**
1. **Run Audit** - Workspace Bar 主 CTA
2. **Review Gaps** - Priority Queue 中有 Gap 时
3. **Issue Permit** - Ready for Permit 状态时
4. **View Audit Trail** - 可作为次要 CTA

**禁止的 CTA:**
- ❌ Generate
- ❌ Build
- ❌ Create
- ❌ Generate Now
- ❌ Create Skill
- ❌ Build Workflow

---

### 3.6 状态设计

#### 3.6.1 空状态 (Empty State)

**场景**: 无任何资产时

**显示内容:**
- 标题: "No governed assets yet"
- 副标题: "Learn about the governance process or review audit guidelines"
- 主 CTA: `Read Governance Guidelines`
- 次要 CTA: `View Audit Examples`

**禁止:**
- ❌ 使用 "Create your first skill" 类 builder 叙事
- ❌ 使用 "Go to Registry" 直接引导进入创建流程
- ❌ 使用空插图/插画掩盖治理定位

---

#### 3.6.2 高风险状态 (High Risk State)

**触发条件**: 存在 Critical Blocked 资产

**固定状态条显示:**
```
"N critical assets are blocked by Gate X / Gate Y rules."
```

**视觉处理:**
- 状态条使用红色/警告色
- Blocked KPI 卡片强调显示
- Priority Queue 自动筛到 Blocked 项置顶

---

#### 3.6.3 待签发状态 (Ready for Permit State)

**触发条件**: 存在 Ready for Permit 资产

**固定状态条显示:**
```
"N assets passed audit and are waiting for permit issuance."
```

**视觉处理:**
- 状态条使用绿色/提示色
- Ready for Permit KPI 卡片强调显示
- Priority Queue 自动筛到 Ready for Permit 项置顶

---

#### 3.6.4 Permit 失效状态 (Permit Invalidated State)

**触发条件**: 存在因 Revision drift 导致 Permit 失效

**固定状态条显示:**
```
"N active permit(s) were invalidated by revision drift."
```

**视觉处理:**
- 状态条使用警告色
- Recent Permit Events 高亮显示 Revoked 状态
- Revision Watch 自动显示受影响资产

---

### 3.7 禁止展示项

#### 3.7.1 绝对禁止前端呈现 (Layer 3)

| 类别 | 禁止项 | 原因 |
|-----|-------|------|
| 规则细节 | threshold (阈值) | 防止逆向判定逻辑 |
| 规则细节 | weight (权重) | 防止逆向评分算法 |
| 规则细节 | rule expression (规则表达式) | 防止绕过判定 |
| 规则细节 | 探针代码 | 防止逆向检测方法 |
| 执行细节 | 内部异常栈 | 防止系统信息泄漏 |
| 执行细节 | 模块名 | 防止拓扑暴露 |
| 执行细节 | 调用链 | 防止流程逆向 |
| 拓扑细节 | API 调用依赖顺序图 | 防止架构暴露 |

#### 3.7.2 未来扩展约束 (Future Expansion Constraints) - HARD REQUIREMENT

**本节为硬约束，不得以建议语气实施。任何未来扩展必须遵守以下条款：**

| 约束类别 | 禁止事项 | 违规后果 |
|---------|---------|---------|
| **渐进式机制暴露禁止** | 不得通过"渐进式添加细节"的方式逐步暴露机制信息 | 直接 FAIL |
| **规则详情禁止** | 永远不得在 Dashboard 中添加"规则详情"展开或页面 | 直接 FAIL |
| **判定逻辑可视化禁止** | 永远不得在 Dashboard 中添加"判定逻辑"可视化或流程图 | 直接 FAIL |
| **探针过程禁止** | 永远不得在 Dashboard 中添加"探针过程"或"探针执行路径"展示 | 直接 FAIL |
| **权重与阈值禁止** | 永远不得在 Dashboard 中添加"权重"或"阈值"的数值展示或可视化 | 直接 FAIL |
| **B Guard 复审要求** | 任何新增的"详情"展开功能必须先通过 B Guard 复审 | 未经复审直接 FAIL |

**硬约束说明:**
1. **禁止渐进式滑向机制暴露**: 不允许通过"先展示摘要，后续逐步添加细节"的方式渐进式暴露机制信息
2. **任何"详情"展开必须先定义禁止清单**: 在设计任何展开功能时，必须同步明确列出禁止展示项清单，未经 B Guard 审核不得实施
3. **三权分立可视化优先于"透明度"追求**: 任何以"提高透明度"为理由要求展示机制细节的请求，都必须被三权分立可视化原则优先拦截
4. **Dashboard 的边界是固定的**: Dashboard 的职责是"总览状态、优先队列、门禁健康、证据覆盖、许可事件"，任何超出此范围的扩展需求都应重新评估是否属于其他页面职责

**违规示例 (禁止):**
- ❌ "点击 8 Gate Health 后展示触发规则的规则 ID 和表达式"
- ❌ "点击 Evidence Coverage 后展示证据来源探针名称和收集路径"
- ❌ "在 v1.1 中添加规则阈值配置的只读展示"
- ❌ "添加判定逻辑流程图帮助用户理解审计结果"

**合规示例 (允许):**
- ✅ "点击 8 Gate Health 后跳转到 Audit Detail 页面查看该 Gate 的资产列表"
- ✅ "在 Evidence Coverage 中展示 evidence completeness score (0-100)，但不展示评分依据"
- ✅ "在 Permit Events 中展示 Permit 签发状态和时间，但不展示签发决策细节"

---

#### 3.7.3 Dashboard 页面特定禁止项

#### 3.7.2 Dashboard 页面特定禁止项

| 禁止项 | 说明 | 替代方案 |
|-------|------|---------|
| 炫图表 BI 大屏 | 不得使用过多动画、图表、可视化 | 使用简洁的数字+状态标签 |
| 生成类 CTA 作为主入口 | 不得把 Generate/Build/Create 放在主 CTA | 使用 Run Audit/Review Gaps |
| 规则阈值可视化 | 不得展示具体的 pass/fail 阈值 | 展示 pass/fail 数量和比例 |
| 算法权重展示 | 不得展示评分算法权重 | 展示最终评分结果 |
| 执行拓扑图 | 不得展示内部模块调用关系 | 展示 Gate 流转状态 |
| Builder 叙事文案 | 不得出现 "Create skill", "Build workflow" 等 | 使用 "Register asset", "Run audit" |

---

### 3.8 Dashboard 固定状态条规范

**位置**: KPI Row 下方，Main Grid 上方

**状态类型:**

| 状态 | 显示文案 | 色彩 |
|-----|---------|------|
| 存在阻断 | "N critical assets are blocked by Gate X / Gate Y rules." | 红色 |
| 存在待签发 | "N assets passed audit and are waiting for permit issuance." | 绿色 |
| Permit 失效 | "N active permit(s) were invalidated by revision drift." | 橙色 |
| 系统正常 | "All assets are within normal operating parameters." | 中性 |

**交互:**
- 点击状态条 → 自动筛选 Priority Queue 显示相关项

---

### 3.9 导航与面包屑

#### 3.9.1 Top Nav

**一级导航项** (按 T-FE-01 IA Spec):
1. Overview (当前页)
2. Forge
3. Audit
4. Release
5. Registry
6. Policies
7. History

**导航视觉权重分级:**
- **最高视觉权重**: Overview / Audit / Release (三页主链)
- **次级视觉权重**: Forge / Registry / Policies / History (通过颜色、位置、大小区分主次)
- **UI 层处理要求**: Forge 必须在视觉上弱化，不得与三页主链使用同等视觉强调

**导航禁忌:**
- ❌ 不得使用 "Builder / Create / Magic" 作为导航项
- ❌ 不得将 Forge 置于导航首位
- ❌ 不得将 Forge 的视觉权重提升至与 Overview/Audit/Release 同等

#### 3.9.2 Workspace Bar

**字段:**
- Workspace 切换器
- Project 切换器
- Time Range 选择器
- Filter 按钮
- 主 CTA: **Run Audit**

**右侧可选:**
- Only blocked toggle
- Only ready for permit toggle

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
| 点击 KPI 卡片 | 筛选 Priority Queue |
| 点击 Gate | 筛选卡在该 Gate 的资产 |
| 点击状态条 | 筛选相关资产 |
| 点击 Permit Event | 跳转 Permit 页面 |
| Open Audit | 跳转 Audit Detail |
| Issue Permit | 跳转 Permit 页面 |

---

## 四、R1 合规返工修订记录

### 4.1 修复的问题点

| 问题 | 修复内容 | 位置 |
|-----|---------|------|
| SF_FE02_001 (CRITICAL) | 8 Gate Health 展开项删除"触发规则数"，新增"受影响资产数量"；强化禁止展示项，明确禁止规则细节/阈值/权重/判定逻辑等 9 项 | Section 3.4.2 |
| SF_FE02_002 (CRITICAL) | Evidence Coverage 新增 7 项禁止展示项，明确禁止证据收集方法/权重计算/探针信息等，限定为仅展示充分性/完整性层 | Section 3.4.4 |
| SF_FE02_003 (HIGH) | 新增 Section 3.7.2 "未来扩展约束"，明确禁止渐进式机制暴露、规则详情、判定逻辑可视化等 6 类硬约束 | Section 3.7.2 |
| SF_FE02_004 (MEDIUM) | 修正 Ready for Permit 辅助文案，从"waiting release approval"改为"eligible for permit issuance"，明确区分 readiness 与 issuance | Section 3.4.1 |
| SF_FE02_005 (LOW) | Top Nav 新增"导航视觉权重分级"，明确 Forge 为次级视觉权重，UI 层需弱化处理 | Section 3.9.1 |
| SF_FE02_006 (LOW) | 空状态 CTA 从"Go to Registry"改为"Read Governance Guidelines"，避免隐性引导进入创建流程 | Section 3.6.1 |

### 4.2 版本信息

**文档版本**: v1.1 (R1 合规返工修订)
**最后更新**: 2026-03-12
**返工执行者**: vs--cc1
**返工触发者**: Kior-B (Compliance)

---

## 五、交付物验收清单

- [x] 1. Dashboard 页面目标已定义 (治理总控台，非 BI 大屏)
- [x] 2. Dashboard 页面骨架已绘制
- [x] 3. 模块列表与模块优先级已明确 (P0/P1/P2)
- [x] 4. CTA 列表已定义 (强化 Run Audit/Review Gaps/Issue Permit/View Audit Trail)
- [x] 5. 空状态/高风险状态/待签发状态已设计
- [x] 6. 禁止展示项已列出 (Layer 3 + Dashboard 特定禁止项)
- [x] 7. 未把 Dashboard 做成炫图表 BI 大屏
- [x] 8. 未把 Generate/Build/Create 做成主 CTA
- [x] 9. 未把生成动作放到最高视觉权重
- [x] 10. 未越权写到具体组件实现
- [x] 11. 保留 8 Gate/Priority Queue/Evidence Coverage/Permit Events/Revision Watch
- [x] 12. 先看状态，再看风险，再看可执行动作的信息层次已确立

---

**文档版本**: v1.1 (R1 合规返工修订)
**最后更新**: 2026-03-12

**EvidenceRef**: 本规格基于以下文档合成:
- `docs/2026-03-12/前端重构_AI军团任务分发单_v2.md` (L1-696)
- `docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md` (L1-1163)
- `docs/2026-03-12/"治理与放行中枢"的前端设计.md` (完整文档)
- `docs/2026-03-12/verification/T-FE-01_ia_spec.md` (L1-544)
- `multi-ai-collaboration.md` (L1-451)
- `docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md` (L1-29)
- `docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md` (L1-30)
