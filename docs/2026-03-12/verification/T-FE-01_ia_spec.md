# T-FE-01: 前端信息架构与导航重构规格

> **任务 ID**: T-FE-01
> **执行者**: Antigravity-2
> **审查者**: vs--cc3
> **合规官**: Kior-C
> **日期**: 2026-03-12
> **状态**: Execution Phase

---

## 一、PreflightChecklist

### 1.1 Fail-Closed 风险枚举

| 风险类别 | 潜在绕过路径 | 防御措施 |
|---------|-------------|---------|
| 叙事漂移 | 前端视觉设计可能回归 builder-first 体验，弱化治理中枢定位 | 在 IA 层面强制首页与应用内叙事分离，禁止 Generate/Build/Create 作为主导航入口 |
| 主链侵蚀 | Forge/Canvas/Marketplace 模块可能成为视觉中心 | 明确 Dashboard/Audit Detail/Permit 为三页主链，Forge 作为次级入口 |
| 权限泄漏 | 敏感机制信息可能通过前端可见层暴露 | 定义四层信息分层模型，Layer 3 为绝对禁止前端呈现区 |
| 审计混淆 | Audit Pass 与 Permit Granted 可能被混同 | 在 IA 层面明确分离审计与放行的语义边界 |

### 1.2 依赖环境

| 依赖项 | 当前状态 | 必需值 |
|-------|---------|-------|
| 前端框架 | React (现有) | - |
| 后端 API | 治理放行 API | 必须支持按角色裁剪 payload |
| 认证系统 | 基于角色的权限控制 | 不得依赖前端隐藏敏感字段 |

### 1.3 历史债务扫描

| 债务类型 | 位置 | 处理策略 |
|---------|-----|---------|
| Builder-first 叙事 | ui/app/src/pages/ | 在 T-FE-07 中统一修正 |
| 缺失三权分立可视化 | 无现有实现 | 本规格新增 |
| 缺失 EvidenceRef 语义 | 无现有实现 | 本规格新增 |

---

## 二、ExecutionContract

### 2.1 Input Constraints

**允许读取的文件:**
- `docs/2026-03-12/前端重构_AI军团任务分发单_v2.md`
- `docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md`
- `multi-ai-collaboration.md`
- `docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md`
- `docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md`

**允许修改的文件:**
- 新建 `docs/2026-03-12/verification/T-FE-01_ia_spec.md` (本文件)

**绝对禁止:**
- 修改现有前端代码实现
- 定义具体组件视觉实现细节
- 输出 builder-first 叙事
- 让 Forge 成为主导航中心
- 把 canvas/marketplace 放入 v0 核心路径

### 2.2 Output Definition

**交付物:**
- 本 IA 规格文档，包含：
  1. 一级导航结构
  2. 页面职责边界
  3. 三类用户路径
  4. 页面优先级
  5. 暂缓模块清单

**回滚方案:**
- 本文档为规格说明，不涉及代码变更，无需回滚
- 如规格有误，可通过 Review/Compliance 流程修正

### 2.3 Gate / Acceptance Check

**自动检查:**
```bash
# 检查是否出现禁用词在非禁用语境
rg -n "builder|canvas|marketplace" docs/2026-03-12/verification/T-FE-01_ia_spec.md
# 预期: 仅出现在 deny 或禁用语境
```

**手动检查:**
- [x] 是否明确首页讲价值，应用内讲状态/裁决/证据/放行
- [ ] 是否明确 Dashboard/Audit Detail/Permit 为主链
- [ ] 是否保留三权分立、EvidenceRef、Hash、Revision、Permit 绑定关系

### 2.4 首页 vs 应用内叙事分离原则 (R1 新增)

**核心设计原则:**

> **首页讲价值与边界**
> **应用内讲状态、裁决、证据与放行**

这是一条不可混同的叙事边界，由参考文档 `治理与放行中枢的前端设计.md` 在开头即明确指出。

#### 2.4.1 首页叙事范围

首页负责向潜在客户/访客传达:

- **价值主张**: 治理中枢、审计工作台、放行控制层
- **系统边界**: 什么是被治理的、什么是可放行的、什么是受控的
- **治理流程**: 从登记到审计到放行的完整流程概览
- **可信性建立**: 为什么这个系统的裁决值得信赖

首页 CTA 应当是:
- `Run an Audit`
- `See a Permit Example`
- `Learn More About Governance`

首页 CTA 禁止:
- ❌ `Build a Skill`
- ❌ `Generate Now`
- ❌ `Create Workflow`

#### 2.4.2 应用内叙事范围

用户进入应用后，叙事切换为:

- **状态**: 当前资产在哪个 Gate、审计进度如何
- **裁决**: Audit Decision 是什么、为什么通过/阻断
- **证据**: 哪些 Evidence 支撑这个裁决、证据强度如何
- **放行**: Permit 是否签发、放行范围是什么、条件有哪些

应用内 CTA 应当是:
- `Open Audit Detail`
- `Review Gaps`
- `Issue Permit`
- `View Evidence`

应用内不再重复"价值教育"，而是直接进入治理操作。

#### 2.4.3 叙事转换边界

叙事转换发生在用户从首页进入应用时:
- **首页**: Landing Page / Marketing Site 层面
- **应用内**: Dashboard / Audit / Release 层面

转换点: 用户点击首页 CTA 或登录进入 Dashboard

---

## 三、RequiredChanges

### 3.1 一级导航结构

#### 3.1.1 导航裁剪说明 (R1 新增)

**参考文档 9 项导航 vs 本规格 7 项导航:**

根据参考文档 `治理与放行中枢的前端设计.md`，完整导航定义包含 9 项:
1. Overview (概览)
2. **Intake / Prompt Pack** (承接输入态和孵化态) ← **v1 暂缓**
3. Registry (登记)
4. Audit (审计)
5. Release (放行)
6. Forge (构建)
7. **Team / Approval** (团队交付、企业审批、合规签发) ← **v1 暂缓**
8. Policies (策略)
9. History (历史)

**v0 导航裁剪决策:**

| 导航项 | v0 状态 | 裁剪理由 |
|-------|---------|---------|
| Intake / Prompt Pack | **暂缓** | 属于输入管理与孵化场景，非治理主链核心。v0 专注治理三页主链 (Dashboard/Audit/Permit)，输入态可通过 Registry 或外部工作流承接 |
| Team / Approval | **暂缓** | 属于企业协作与审批流程，依赖组织架构与权限体系。v0 使用简化角色权限 (Executor/Reviewer/Compliance)，重 RBAC 门户已在暂缓模块清单中 |

**不破坏主链的原因:**
- Dashboard/Audit/Release 三页主链完整保留
- 治理裁决流程不受影响
- 暂缓项可在 v1+ 按需补入，不破坏 v0 IA 结构

#### 3.1.2 视觉权重与页面优先级的语义差异 (R1 新增)

**概念澄清:**
- **视觉权重**: 界面设计的视觉层次，主导航项的视觉强调程度
- **页面优先级**: v0 开发顺序，哪个页面先实现

**差异解释:**
- Overview 标记为 **最高视觉权重**，因为它是用户进入应用后的第一印象，需要承载治理总控的视觉权威
- 但 Overview 开发优先级为 **P1**，因为它的正确性依赖 Audit Detail 和 Permit 的语义先行确立
- Audit Detail 和 Permit 是 **P0**，因为它们定义系统的裁决语言和放行权威，是治理体验的基石

**统一表述:**
```
视觉权重: Overview = Audit = Release (最高，三者共同构成治理体验视觉权威)
开发优先级: Audit Detail = Permit (P0) > Dashboard (P1)
```

#### 3.1.3 v0 导航结构 (按优先级排序)

| 导航项 | 英文标识 | 页面职责 | 视觉权重 | 开发优先级 |
|-------|---------|---------|---------|-----------|
| 概览 | Overview | 全局治理总控，Dashboard 主页 | **最高** | P1 |
| 登记 | Registry | 资产登记与版本管理 | 高 | P2 |
| 审计 | Audit | 审计工作台与裁决详情 | **最高** | P0 |
| 放行 | Release | Permit 管理与放行控制 | **最高** | P0 |
| 构建 | Forge | 构建/编辑环境 | 中 (次级入口) | P4 |
| 策略 | Policies | 规则包与策略配置 | 低 | P3 |
| 历史 | History | 审计历史与记录查询 | 低 | P3 |

**导航禁忌:**
- ❌ 不得使用 "Builder / Create / Magic" 作为主导航项
- ❌ 不得将 Forge 置于导航首位或最高视觉权重
- ❌ 不得出现 "Marketplace / Canvas / Gallery" 作为一级导航

### 3.2 页面职责边界

#### 3.2.1 Dashboard (Overview)
**页面定位:** 全局治理总控台

**核心职责:**
1. 状态总览: 展示 In Review / Blocked / Fix Required / Ready for Permit / Permitted 五态
2. 八门监控: 8 Gate Health / Funnel 实时状态
3. 优先队列: Priority Queue 展示需立即处理的资产
4. 证据覆盖: Evidence Coverage 完整性监控
5. 缺口热点: Gap Hotspots 统计
6. 许可事件: Recent Permit Events 记录
7. 版本监视: Revision Watch 变更追踪

**禁止事项:**
- ❌ 不得做成炫图表 BI 大屏
- ❌ 不得把 Generate/Build/Create 做成主 CTA
- ❌ 不得把生成动作放到最高视觉权重

#### 3.2.2 Audit Detail
**页面定位:** 裁决解释与证据闭环页面

**核心职责:**
1. 决策头部: Decision Header 展示 Asset/Revision/Status/Hash
2. 决策摘要: Decision Summary 结论先行
3. 权力边界: Power Boundary 三权分立可视化
4. 门禁详情: 8 Gate Timeline / Gate Details
5. 证据引用: EvidenceRef Panel
6. 红线划分: Red Lines vs Fixable Gaps 分离
7. 治理快照: Contract / Control Snapshot
8. 可重现性: Hash & Reproducibility

**信息顺序 (不可逆):**
结论 → 原因 → 证据 → 修复

**禁止事项:**
- ❌ 不得把 Evidence/Rule/Gate/Gap 混成一锅
- ❌ 不得把内部异常栈、模块名、调用拓扑带到用户可见层
- ❌ 不得先细节后结论

#### 3.2.3 Permit
**页面定位:** 正式放行凭证页面

**核心职责:**
1. 许可头部: Permit Header 证书抬头
2. 核心决策: Core Decision Block
3. 放行范围: Release Scope 边界定义
4. 生效条件: Conditions 必须保持/失效触发
5. 审计基础: Audit Basis 关联审计
6. 生命周期: Permit Lifecycle 时间线
7. 合规签名: Compliance Signature
8. 残余风险: Residual Risk Reminder

**禁止事项:**
- ❌ 不得做成大绿勾成功页
- ❌ 不得出现与 revision/hash 解耦的 Permit
- ❌ 不得暗示 "Audit pass = Release approved"

### 3.3 四类用户路径

#### 3.3.0 首页访问者 / 潜在客户路径 (R1 新增)
**目标:** 了解价值、理解边界、决定尝试

**首页访问者场景:**
```
1. Landing Page / 首页
   ↓
   看到什么: 价值主张、治理流程概览、系统边界说明
   ↓
2. CTA 点击
   - "Run an Audit" → 进入应用 Registry 或 Dashboard
   - "See a Permit Example" → 查看 Permit 示例页面
   - "Learn More" → 阅读治理流程文档
```

**首页价值传达要点:**
- **这是什么**: 治理中枢、审计工作台、放行控制层
- **不是什么**: AI builder、skill marketplace、workflow canvas
- **为什么需要**: 三权分立、证据闭环、正式放行凭证
- **如何开始**: Run an Audit / See a Permit Example

#### 3.3.1 执行者 (Executor) 路径
**目标:** 提交资产、查看审计结果、修复问题

```
1. Registry → 登记新资产/创建新版本
   ↓
2. Audit Detail (In Audit) → 查看审计进度
   ↓
3. Audit Detail (Fix Required) → 修复 Fixable Gaps
   ↓
4. Audit Detail (Passed) → 提交 Permit 申请
   ↓
5. Permit (Pending) → 等待放行
```

#### 3.3.2 审查者 (Reviewer) 路径
**目标:** 审查资产、检查质量、给出意见

```
1. Dashboard → 查看待审查队列
   ↓
2. Audit Detail → 查看审计结果与证据
   ↓
3. EvidenceRef Panel → 检查证据链完整性
   ↓
4. 提交审查意见 (三权分立)
```

#### 3.3.3 合规官 (Compliance) 路径
**目标:** 审计合规、签发/撤销 Permit

```
1. Dashboard → 查看待放行资产
   ↓
2. Audit Detail → 确认审计通过
   ↓
3. Permit → 签发/拒绝 Permit
   ↓
4. Permit History → 管理 Permit 生命周期
```

### 3.4 页面优先级

| 优先级 | 页面 | 理由 |
|-------|-----|------|
| **P0** | Audit Detail | 定义系统可信裁决语言，是治理体验的核心 |
| **P0** | Permit | 定义商业闭环和放行权威，是价值实现的终点 |
| **P1** | Dashboard | 组织全局管理体验，依赖前两者 |
| **P2** | Registry | 资产管理入口，可复用现有表单模式 |
| **P3** | Policies | 策略配置，中低频操作 |
| **P3** | History | 历史查询，低频操作 |
| **P4** | Forge | 次级入口，不作为 v0 核心路径 |

### 3.5 暂缓模块清单

**v0 阶段暂缓，未来考虑:**

| 模块 | 暂缓原因 | 未来条件 |
|-----|---------|---------|
| Workflow Canvas | 复杂度高，易偏离治理定位 | 核心治理链稳定后 |
| Template Marketplace | 属于 builder-first 叙事 | 需求明确且治理链成熟 |
| Community/Social | 非核心治理场景 | 用户规模化后 |
|炫技 BI 大屏 | 冲击治理中枢定位 | 治理数据积累后 |
| 重 RBAC 门户 | 当前阶段可简化为角色权限 | 多租户需求明确后 |

**明确排除:**
- ❌ Canvas 编辑器不放入 v0 核心路径
- ❌ Marketplace 不作为主导航入口
- ❌ 社区化首页不纳入当前版本

---

## 四、四层信息分层模型

### 4.1 Layer 0: 对外公示层
**允许展示:**
- 审计维度名称
- 系统级结果摘要
- Permit 状态
- 封板摘要
- 时间戳与统计量级

**禁止展示:**
- 规则细节
- 阈值
- 调度方式
- 阻断逻辑

### 4.2 Layer 1: 内部工作台
**允许展示:**
- 执行主链状态
- 审计通过/失败
- 当前 Gate
- 红线/可修复项分类
- Permit readiness

**不应展示:**
- 规则权重
- 底层模块拓扑
- 可被逆向的判定树

### 4.3 Layer 2: 受控详情层
**允许展示:**
- Evidence Bundle
- Metrics
- Hash
- Revision lineage
- Signoff 历史
- 受控证据包

**仍不应展示:**
- pre_absorb_check 规则树
- absorb 内部处理逻辑
- L3 评分算法与权重

### 4.4 Layer 3: 禁止前端呈现区
**任何角色都不应看到:**
- 判定阈值
- 算法权重
- 探针代码
- 阻断触发路径
- 绕过路径
- 内部执行拓扑
- API 调用依赖顺序图

---

## 五、三权分立可视化要求

### 5.1 必须常驻展示的权力边界
```
Execution: 可运行，可产出，不可批准放行
Audit: 可检查证据，可签发审计决定，不可签发 Permit
Compliance: 可签发/撤销 Permit，可定义放行条件，不可修改执行产出
```

### 5.2 必须保留的系统独特性
- 三权分立边界
- 8 Gate 结构
- EvidenceRef 语义
- Permit as only release credential
- Revision + Hash 绑定
- Red Lines vs Fixable Gaps

---

## 六、EvidenceRef 规范

### 6.1 EvidenceRef 可见性级别
| 级别 | 含义 | 展示方式 |
|-----|------|---------|
| visible | 完整可见 | 全量展示，支持展开 |
| summary-only | 仅摘要 | 仅显示摘要，详情隐藏 |
| restricted | 受限访问 | 需额外权限验证 |

### 6.2 EvidenceRef 字段结构
- Evidence ID
- Source Type
- Summary
- Strength: Weak/Medium/Strong
- Visibility: visible/summary-only/restricted
- Linked Gate

---

## 七、状态标签规范

**统一使用 (禁止混用营销词):**

| 状态标签 | 使用场景 | 禁用的替代词 |
|---------|---------|------------|
| Draft | 资产草稿 | - |
| In Audit | 审计中 | - |
| Passed | 审计通过 | Success, Done, Completed |
| Fix Required | 需修复 | - |
| Blocked | 阻断 | - |
| Ready for Permit | 待放行 | - |
| Permit Active | 许可生效 | Live, Approved |
| Permit Revoked | 许可撤销 | - |
| Permit Expired | 许可过期 | - |

---

## 八、合规约束摘要

### 8.1 禁止前端呈现的敏感信息
- 规则阈值 (threshold)
- 算法权重 (weight)
- 探针代码 (probe code)
- 阻断触发路径 (blocking trigger path)
- 绕过路径 (bypass path)
- 内部执行拓扑 (internal execution topology)
- API 调用依赖顺序 (API call dependency order)

### 8.2 API 层裁剪责任
**必须:**
- 由 API 按角色返回不同 payload
- 敏感字段不得进入前端响应

**不应:**
- 在前端通过角色判断后再裁剪字段
- 全量下发给前端再隐藏

---

## 九、交付物验收清单

- [x] 1. 一级导航结构已定义 (含导航裁剪说明)
- [x] 2. 页面职责边界已明确
- [x] 3. 四类用户路径已设计 (新增首页访问者路径)
- [x] 4. 页面优先级已排序 (含视觉权重语义澄清)
- [x] 5. 暂缓模块清单已列出
- [x] 6. 四层信息分层模型已定义
- [x] 7. 三权分立可视化要求已明确
- [x] 8. EvidenceRef 规范已定义
- [x] 9. 状态标签规范已统一
- [x] 10. 合规约束已摘要
- [x] 11. 首页 vs 应用内叙事分离原则已显式陈述 (R1 新增)

---

**文档版本:** v1.1 (R1 返工修订)
**最后更新:** 2026-03-12

**EvidenceRef:** 本规格基于以下文档合成:
- `docs/2026-03-12/前端重构_AI军团任务分发单_v2.md` (L1-696)
- `docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md` (L1-1163)
- `docs/2026-03-12/治理与放行中枢的前端设计.md` (完整文档，33768 字节) **[R1 补充]**
- `multi-ai-collaboration.md` (L1-451)
- `docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md` (L1-29)
- `docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md` (L1-30)

---

## 十、R1 返工修订记录

### 10.1 修复的问题点

| 问题 | 修复内容 | 位置 |
|-----|---------|------|
| EvidenceRef 不完整 | 补充对`治理与放行中枢的前端设计.md`的引用 | Section 九 EvidenceRef |
| 首页叙事分离原则未明确 | 新增 Section 2.4 显式陈述首页 vs 应用内叙事分离原则 | Section 2.4 |
| 导航定义不一致 | 新增 Section 3.1.1 导航裁剪说明，解释 7 项 vs 9 项导航 | Section 3.1.1 |
| 视觉权重与优先级冲突 | 明确"视觉权重"与"页面优先级"的语义差异 | Section 3.1.2 |
| 缺少首页访问者路径 | 新增 Section 3.3.0 首页访问者/潜在客户路径 | Section 3.3.0 |

### 10.2 事实澄清

**关于 Compliance attestation 中的事实错误:**
- 参考文档 `docs/2026-03-12/治理与放行中枢的前端设计.md` 确实存在
- 文件大小: 33768 字节，修改时间: 2026-03-12 15:56
- 该文件包含核心设计原则和完整 9 项导航定义
- 本次返工已将其纳入 EvidenceRef 并反映在 IA 规格中
