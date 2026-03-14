# T-FE-05: 前端组件树与数据边界映射

> **任务 ID**: T-FE-05
> **执行者**: vs--cc2
> **审查者**: Antigravity-1
> **合规官**: Kior-C
> **日期**: 2026-03-12
> **依赖**: T-FE-02 (ALLOW), T-FE-03 (ALLOW), T-FE-04 (ALLOW)

---

## 一、PreflightChecklist

### 1.1 Fail-Closed 风险枚举

| 风险类别 | 潜在绕过路径 | 防御措施 |
|---------|-------------|---------|
| 前端权限裁剪 | 通过前端角色判断隐藏敏感字段，但后端仍全量返回 | 强制"API 层裁剪而非前端层裁剪"原则，明确哪些字段必须后端过滤 |
| 机制信息泄漏 | 组件树设计时未明确禁止字段，导致实现时暴露 threshold/weight/topology | 每个组件必须列出禁止字段清单，共享组件必须明确数据边界 |
| 混淆共享与专属 | 将页面专属组件误设计为共享组件，导致过度抽象 | 明确区分"三页共享组件"与"页面专属组件" |
| 越权进入实现层 | 组件树描述过细，涉及具体实现代码 | 限定在组件名称/字段需求/禁止字段层面，不写实现细节 |
| Builder 叙事残留 | 共享组件设计时遗留 builder-first 的交互模式 | 所有共享组件必须服务治理型前端，禁止 Generate/Build/Create 模式 |

### 1.2 依赖环境

| 依赖项 | 当前状态 | 必需值 |
|-------|---------|-------|
| T-FE-02 Dashboard Spec | ALLOW | 已定义 Dashboard 模块与字段 |
| T-FE-03 Audit Detail Spec | ALLOW | 已定义 Audit Detail 模块与字段 |
| T-FE-04 Permit Spec | ALLOW | 已定义 Permit 模块与字段 |
| 三页主链定义 | 已定义 | Dashboard/Audit Detail/Permit 角色 |
| 四层信息分层 | 已定义 | Layer 0/1/2 可展示范围，Layer 3 禁止区 |

### 1.3 历史债务扫描

| 债务类型 | 位置 | 处理策略 |
|---------|-----|---------|
| 现有前端可能混用权限裁剪 | ui/app/src/ | 本规格明确 API 层裁剪责任，后续 T-FE-06 强化 |
| 现有组件可能未区分禁止字段 | ui/app/src/components/ | 本规格列出 Never-in-DOM 清单，T-FE-06 落实 |

---

## 二、ExecutionContract

### 2.1 Input Constraints

**允许读取的文件:**
- `docs/2026-03-12/前端重构_AI军团任务分发单_v2.md`
- `docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md`
- `docs/2026-03-12/verification/T-FE-02_dashboard_spec.md`
- `docs/2026-03-12/verification/T-FE-03_audit_detail_spec.md`
- `docs/2026-03-12/verification/T-FE-04_permit_spec.md`
- `docs/2026-03-12/verification/T-FE-01_ia_spec.md`
- `multi-ai-collaboration.md`
- `docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md`
- `docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md`

**允许创建的文件:**
- 本规格文档 `docs/2026-03-12/verification/T-FE-05_frontend_mapping.md`

**绝对禁止:**
- 修改现有前端代码实现
- 定义具体组件视觉实现细节（如 CSS、动画效果）
- 定义具体组件代码实现（如 hooks、utils）
- 让前端接收 threshold/weight/internal topology
- 通过前端角色判断隐藏敏感字段
- 越权写到具体组件实现代码

### 2.2 Output Definition

**交付物:**
- 本前端映射文档，包含：
  1. 逐页组件树
  2. 逐页字段需求
  3. 逐页禁止字段
  4. 共享组件清单（6 个）
  5. 页面间共享状态机
  6. API 层裁剪责任清单
  7. Never-in-DOM 字段清单

**回滚方案:**
- 本文档为规格说明，不涉及代码变更，无需回滚
- 如规格有误，可通过 Review/Compliance 流程修正

### 2.3 Gate / Acceptance Check

**自动检查:**
```bash
# 检查是否出现 builder-first 禁用词
rg -n "builder|canvas|marketplace" docs/2026-03-12/verification/T-FE-05_frontend_mapping.md
# 预期: 仅出现在 deny 或禁用语境
```

**手动检查:**
- [ ] 是否明确 Never-in-DOM 字段清单
- [ ] 是否明确 API 层而非前端层进行权限裁剪
- [ ] 是否区分共享组件与页面专属组件
- [ ] 是否数据边界服务治理型前端而非 builder 型前端
- [ ] 是否禁止前端接收 threshold/weight/internal topology
- [ ] 是否禁止通过前端角色判断隐藏敏感字段

---

## 三、RequiredChanges

### 3.1 Dashboard 页面组件树与数据边界

#### 3.1.1 Dashboard 页面组件树

```
DashboardPage
├── TopNav (共享组件)
│   ├── Logo
│   ├── PrimaryNavigation (Overview/Audit/Release - 最高视觉权重)
│   ├── SecondaryNavigation (Forge/Registry/Policies/History - 次级视觉权重)
│   ├── Search
│   ├── Alerts
│   └── UserMenu
├── WorkspaceBar
│   ├── WorkspaceSelector
│   ├── ProjectSelector
│   ├── TimeRangeSelector
│   ├── FilterButton
│   └── PrimaryCTA (Run Audit)
├── PageTitle (Overview + subtitle)
├── StatusBanner (条件渲染: 高风险/待签发/Permit失效)
├── KPIRow
│   ├── KPICard (In Review)
│   ├── KPICard (Blocked) - 红色强调
│   ├── KPICard (Fix Required)
│   ├── KPICard (Ready for Permit) - 绿色强调
│   └── KPICard (Permitted)
├── MainGrid
│   ├── Row1
│   │   ├── GateHealthCard (8 Gate Health)
│   │   │   ├── GateFunnelChart (仅 pass/warn/fail 分布可视化)
│   │   │   ├── GateSummaryList (展开态)
│   │   │   │   └── GateSummaryItem
│   │   │   └── TopFailureReason (仅 reason 描述，无规则详情)
│   │   └── PriorityQueueCard
│   │       └── AssetList
│   │           └── AssetListItem
│   │               ├── AssetName
│   │               ├── StatusLabel (共享组件)
│   │               ├── CurrentGate
│   │               ├── RiskLevel
│   │               ├── NextAction
│   │               ├── Owner
│   │               ├── LastUpdated
│   │               └── RowActions
│   │                   ├── OpenAuditLink
│   │                   ├── ReviewGapsLink
│   │                   └── IssuePermitLink
│   ├── Row2
│   │   ├── EvidenceCoverageCard
│   │   │   ├── CompletenessScore (0-100)
│   │   │   ├── WeakEvidenceCount
│   │   │   ├── EvidenceDistributionChart (仅 no evidence/summary-only/sufficient 分布)
│   │   │   └── WeakEvidenceList
│   │   └── GapHotspotsCard
│   │       └── GapClusterList
│   │           └── GapClusterItem
│   └── Row3
│       ├── PermitEventsCard
│       │   └── PermitEventList
│       │       └── PermitEventItem
│       │           ├── PermitID
│       │           ├── Asset
│       │           ├── StatusLabel (共享组件)
│       │           ├── SignedBy
│       │           ├── Time
│       │           └── ViewPermitLink
│       └── RevisionWatchCard
│           └── RevisionList
│               └── RevisionItem
└── FooterInfo (可选)
```

#### 3.1.2 Dashboard 页面字段需求

| 组件 | 字段需求 | 类型 | 说明 |
|-----|---------|------|-----|
| **KPICard** | status | enum | In Review / Blocked / Fix Required / Ready for Permit / Permitted |
| | count | number | 该状态资产数量 |
| | subtitle | string | 状态说明文案 |
| **GateHealthCard** | gate_name | string | Gate 1-8 名称 |
| | pass_count | number | 通过数量 |
| | warn_count | number | 警告数量 |
| | fail_count | number | 失败数量 |
| | affected_asset_count | number | 受影响资产数量 |
| | top_failure_reason | string | 最常见失败原因（仅描述，无规则详情） |
| **PriorityQueueCard.AssetListItem** | asset_name | string | 资产名称 |
| | revision | string | 版本号 (R-014) |
| | current_status | enum | Blocked / Fix Required / Ready for Permit |
| | current_gate | string | 当前卡住的门禁 (Gate 4) |
| | risk_level | enum | Critical / High / Medium / Low |
| | next_action | string | 下一步操作建议 |
| | owner | string | 负责人 |
| | last_updated | timestamp | 最后更新时间 |
| **EvidenceCoverageCard** | completeness_score | number (0-100) | 证据完整性评分 |
| | weak_evidence_count | number | 弱证据数量 |
| | distribution | object | { no_evidence: count, summary_only: count, sufficient: count } |
| **PermitEventItem** | permit_id | string | 许可证 ID |
| | asset | string | 资产名称 |
| | status | enum | Issued / Revoked / Expired / Replaced |
| | signed_by | string | 签发者 |
| | time | timestamp | 时间戳 |

#### 3.1.3 Dashboard 页面禁止字段 (Never-in-DOM)

| 组件 | 禁止字段 | 原因 |
|-----|---------|------|
| **GateHealthCard** | threshold (阈值) | 防止逆向判定逻辑 |
| | weight (权重) | 防止逆向评分算法 |
| | rule_expression (规则表达式) | 防止绕过判定 |
| | probe_code (探针代码) | 防止逆向检测方法 |
| | decision_logic (判定逻辑) | 防止机制暴露 |
| | triggered_rule_details (触发规则详情) | 防止规则细节泄露 |
| | rule_to_gate_mapping (规则与Gate映射) | 防止拓扑暴露 |
| | decision_path_visualization (判定路径可视化) | 防止流程逆向 |
| **EvidenceCoverageCard** | evidence_internal_content (证据内部内容) | 防止证据细节暴露 |
| | evidence_collection_method (证据收集方法) | 防止检测路径暴露 |
| | evidence_weight_calculation (证据权重计算) | 防止评分算法暴露 |
| | evidence_source_probe_info (证据来源探针信息) | 防止探针信息暴露 |
| | evidence_classification_criteria (证据分类依据) | 防止分类逻辑暴露 |
| | evidence_strength_decision_logic (证据强度判定逻辑) | 防止判定逻辑暴露 |
| | evidence_collection_path_visualization (证据收集路径可视化) | 防止流程暴露 |

---

### 3.2 Audit Detail 页面组件树与数据边界

#### 3.2.1 Audit Detail 页面组件树

```
AuditDetailPage
├── TopNav (共享组件)
├── Breadcrumb
│   ├── Registry
│   ├── AssetName
│   └── Revision (R-014)
├── DecisionHeader
│   ├── AssetName
│   ├── AssetType
│   ├── RevisionID
│   ├── CurrentStatus (StatusLabel - 共享组件)
│   ├── AuditVersion
│   ├── DecisionHash (HashDisplay - 共享组件)
│   ├── AuditedAt
│   ├── Owner (可选)
│   ├── Reviewer (可选)
│   └── HeaderActions
│       ├── ReviewGapsButton
│       ├── ExportAuditPackButton
│       ├── ReRunAuditButton
│       └── SubmitForPermitButton
├── SummaryAndBoundaryRow
│   ├── DecisionSummaryCard
│   │   ├── FinalDecision (StatusLabel - 共享组件)
│   │   ├── PrimaryReason
│   │   ├── EvidenceSufficiency
│   │   ├── PermitReadiness
│   │   └── SummaryTags
│   │       ├── CriticalIssuesCount
│   │       ├── FixableGapsCount
│   │       └── EvidenceRefCount
│   └── PowerBoundaryCard (三权分立 - 共享组件)
│       ├── ExecutionColumn
│       ├── AuditColumn
│       └── ComplianceColumn
├── MainContentRow
│   ├── GateTimelineCard (8 Gate Timeline)
│   │   └── GateCardList
│   │       └── GateCard
│   │           ├── GateName
│   │           ├── GateStatus (StatusLabel - 共享组件)
│   │           ├── Reason
│   │           ├── TriggeredRules (仅规则引用，无详情)
│   │           ├── EvidenceCount
│   │           ├── EvidenceRefList (EvidenceRefPanel - 共享组件)
│   │           └── FixSuggestion
│   └── EvidenceRefPanel (共享组件, sticky)
│       └── EvidenceRefList
│           └── EvidenceRefItem
│               ├── EvidenceID
│               ├── SourceType
│               ├── Summary
│               ├── Strength
│               ├── Visibility (visible/summary-only/restricted)
│               └── LinkedGate
├── IssueBreakdownRow
│   ├── RedLinesCard
│   │   └── IssueList
│   │       └── RedLineItem
│   │           ├── IssueTitle
│   │           ├── Impact (CRITICAL/HIGH)
│   │           ├── TriggeredGate
│   │           ├── Rules (仅规则引用)
│   │           ├── WhyBlocking
│   │           └── RequiredDisposition
│   └── FixableGapsCard
│       └── GapList
│           └── FixableGapItem
│               ├── GapTitle
│               ├── Severity (Low/Medium/High)
│               ├── RelatedGate
│               ├── SuggestedFix
│               └── ExpectedOutcome
├── GovernanceSnapshotRow
│   ├── ContractControlSnapshotCard
│   │   ├── ContractSummary
│   │   ├── ConstitutionVersion
│   │   ├── RulePackVersion
│   │   ├── ControlSpecVersion
│   │   ├── LinkedManifest
│   │   └── AuditScope
│   └── HashReproducibilityCard
│       ├── DemandHash (HashDisplay - 共享组件)
│       ├── ContractHash (HashDisplay - 共享组件)
│       ├── DecisionHash (HashDisplay - 共享组件)
│       ├── RevisionLineage
│       ├── LinkedManifestID
│       └── BindingNotice
└── FooterActionBar (共享组件)
    ├── GoToGapAnalysisButton
    ├── AssignOwnerButton
    ├── ReRunAuditButton
    └── SubmitForPermitButton
```

#### 3.2.2 Audit Detail 页面字段需求

| 组件 | 字段需求 | 类型 | 说明 |
|-----|---------|------|-----|
| **DecisionHeader** | asset_name | string | 资产名称 |
| | asset_type | enum | Skill / Workflow / Agent Asset |
| | revision_id | string | 版本号 (R-014) |
| | current_status | enum | Draft / In Audit / Passed / Fix Required / Blocked / Ready for Permit |
| | audit_version | string | 审计版本 (v1.0) |
| | decision_hash | string(hash) | 前8位+省略+hover全量 |
| | audited_at | timestamp | 审计完成时间 |
| | owner | string | 资产负责人 |
| | reviewer | string | 审查人 |
| **DecisionSummaryCard** | final_decision | enum | Passed / Blocked / Fix Required |
| | primary_reason | text | 一句话原因 |
| | evidence_sufficiency | enum | Sufficient for approval / Sufficient for rejection / Insufficient |
| | permit_readiness | text | Permit 资格说明 |
| **GateCard** | gate_name | string | Gate 名称 |
| | gate_status | enum | Pass / Fail / Warn / Skip |
| | reason | text | 简要说明 |
| | triggered_rules | list[string] | 规则引用 (RULE-4.2, RULE-4.7) - 仅引用，无详情 |
| | evidence_count | number | 证据数量 |
| | fix_suggestion | text | 修复建议 |
| **RedLineItem** | issue_title | string | 问题描述 |
| | impact | enum | CRITICAL / HIGH |
| | triggered_gate | string | 触发的 Gate |
| | rules | list[string] | 规则引用 - 仅引用 |
| | why_blocking | text | 为什么这是红线 |
| | required_disposition | text | 必须的处理方式 |
| **FixableGapItem** | gap_title | string | 缺口描述 |
| | severity | enum | Low / Medium / High |
| | related_gate | string | 相关的 Gate |
| | suggested_fix | text | 建议的修复方式 |
| | expected_outcome | text | 修复后的预期结果 |
| **ContractControlSnapshotCard** | contract_summary | text | 合同摘要 |
| | constitution_version | string | 宪法版本号 (v2.1) |
| | rule_pack_version | string | 规则包版本号 (v1.0.3) |
| | control_spec_version | string | 控制规格版本号 (v3.5) |
| | linked_manifest | string(ref) | 关联清单 ID |
| | audit_scope | text | 审计范围说明 |

#### 3.2.3 Audit Detail 页面禁止字段 (Never-in-DOM)

| 组件 | 禁止字段 | 原因 |
|-----|---------|------|
| **GateCard** | rule_threshold (规则阈值) | Layer 3 禁止 |
| | rule_weight (规则权重) | Layer 3 禁止 |
| | rule_details (规则详情) | Layer 3 禁止 |
| | probe_code (探针代码) | Layer 3 禁止 |
| | internal_topology (内部拓扑) | Layer 3 禁止 |
| **EvidenceRefItem** | evidence_full_content (证据全量内容) | visibility=restricted 时禁止 |
| | evidence_collection_path (证据收集路径) | Layer 3 禁止 |
| | evidence_source_details (证据来源详情) | Layer 3 禁止 |
| **所有组件** | internal_exception_stack (内部异常栈) | Layer 3 禁止 |
| | module_name (模块名) | Layer 3 禁止 |
| | call_chain (调用链) | Layer 3 禁止 |

---

### 3.3 Permit 页面组件树与数据边界

#### 3.3.1 Permit 页面组件树

```
PermitPage
├── TopNav (共享组件)
├── Breadcrumb
│   ├── Release
│   ├── Permit
│   └── PermitID (PMT-2026-0312-014)
├── PermitHeader (证书抬头)
│   ├── PermitID
│   ├── AssetName
│   ├── Revision
│   ├── Status (StatusLabel - 共享组件)
│   ├── EffectiveDate
│   ├── SignedBy
│   ├── Scope
│   └── HeaderActions
│       ├── ExportPermitButton
│       ├── ViewLinkedAuditButton
│       ├── RevokePermitButton
│       └── ViewHistoryButton
├── CoreDecisionBlock (核心决策块)
│   ├── MainConclusion
│   ├── SubStatement ("Audit pass is not release approval. Permit is.")
│   ├── BindingNotice (revision + hashes)
│   └── ActionAdvice ("Allowed for release within declared scope only")
├── MainGridRow1
│   ├── ReleaseScopeCard
│   │   ├── Environment
│   │   ├── AssetBoundary
│   │   ├── RevisionScope
│   │   ├── InvocationBoundary
│   │   └── ValidUseContext
│   └── ConditionsCard
│       ├── MustHoldConditions
│       ├── ReAuditTriggers
│       ├── InvalidationTriggers
│       ├── UndeclaredExecution
│       └── MonitoringRequirements
├── MainGridRow2
│   ├── AuditBasisCard
│   │   ├── LinkedAuditID
│   │   ├── AuditResult
│   │   ├── DecisionHash (HashDisplay - 共享组件)
│   │   ├── ContractHash (HashDisplay - 共享组件)
│   │   ├── AuditVersion
│   │   ├── ReviewedAt
│   │   └── OpenAuditDetailLink
│   └── EvidencePolicyBasisCard
│       ├── EvidenceSummaryCount
│       ├── EvidenceSufficiencyLevel
│       ├── RulepackVersion
│       ├── ConstitutionVersion
│       └── ComplianceNote
├── MainGridRow3
│   ├── PermitLifecycleCard
│   │   └── LifecycleTimeline
│   │       ├── AuditCompletedNode
│   │       ├── PassedAuditNode
│   │       ├── ReadyForPermitNode
│   │       ├── PermitIssuedNode (高亮当前状态，显示签发者)
│   │       ├── ActiveNode (当前状态)
│   │       └── OptionalTerminalNode (Revoked/Expired/Superseded)
│   └── ComplianceSignatureCard
│       ├── SignedBy
│       ├── SignedAt
│       ├── SignatureNote
│       ├── ApprovalRemarks
│       └── ReleaseComments
└── ResidualRiskReminder
    ├── KnownOperationalRisks
    ├── MonitoringExpectations
    └── ReAuditTriggers
```

#### 3.3.2 Permit 页面字段需求

| 组件 | 字段需求 | 类型 | 说明 |
|-----|---------|------|-----|
| **PermitHeader** | permit_id | string | 许可证 ID (PMT-2026-0312-014) |
| | asset_name | string | 资产名称 |
| | revision | string | 版本号 (R-014) |
| | status | enum | Pending / Active / Revoked / Expired / Superseded |
| | effective_date | timestamp | 生效日期 |
| | signed_by | string | 签发者 (Compliance-01) |
| | scope | enum | Production / Internal / Client Delivery |
| **CoreDecisionBlock** | main_conclusion | string | Permit granted / denied / revoked |
| | sub_statement | string | 固定文案: "Audit pass is not release approval. Permit is." |
| | binding_notice | string | 绑定说明 (revision R-014, contract_hash xxx, decision_hash xxx) |
| | action_advice | string | "Allowed for release within declared scope only" |
| **ReleaseScopeCard** | environment | enum | Production / Internal / Client Delivery |
| | asset_boundary | string | Payment Agent Skill (R-014 only) |
| | revision_scope | string | R-014 only |
| | invocation_boundary | string | Declared only |
| | valid_use_context | string | Internal operations only / Client-facing delivery |
| **ConditionsCard** | must_hold_conditions | list[string] | 必须保持的条件 |
| | re_audit_triggers | list[string] | 重审触发器 |
| | invalidation_triggers | list[string] | 失效触发器 |
| | undeclared_execution | string | 未声明执行路径说明 |
| | monitoring_requirements | list[string] | 监控要求 |
| **AuditBasisCard** | linked_audit_id | string | 关联审计 ID (AUD-2026-0312-014) |
| | audit_result | enum | Passed / Conditional pass |
| | decision_hash | string(hash) | 决策哈希 |
| | contract_hash | string(hash) | 合同哈希 |
| | audit_version | string | 审计版本 (v1.0) |
| | reviewed_at | timestamp | 审计时间 |
| **EvidencePolicyBasisCard** | evidence_summary_count | number | 证据摘要数量 |
| | evidence_sufficiency_level | enum | Sufficient / Conditional |
| | rulepack_version | string | 规则包版本 (v1.0) |
| | constitution_version | string | 宪法版本 (v2.1) |
| | compliance_note | string | 合规备注 |
| **PermitLifecycleCard** | timeline_nodes | list[object] | 时间线节点，每节点含 status/timestamp/actor/note |
| **ComplianceSignatureCard** | signed_by | string | 签发者 |
| | signed_at | timestamp | 签发时间 |
| | signature_note | string | 签名备注 |
| | approval_remarks | string | 批准备注 |
| | release_comments | string | 放行评论 |
| **ResidualRiskReminder** | known_operational_risks | list[string] | 已知运营风险 |
| | monitoring_expectations | list[string] | 监控期望 |
| | re_audit_triggers | list[string] | 重审触发器 |

#### 3.3.3 Permit 页面禁止字段 (Never-in-DOM)

| 组件 | 禁止字段 | 原因 |
|-----|---------|------|
| **所有组件** | rule_threshold (规则阈值) | Layer 3 禁止 |
| | rule_weight (规则权重) | Layer 3 禁止 |
| | rule_details (规则详情) | Layer 3 禁止 |
| | decision_logic_details (决策逻辑详情) | Layer 3 禁止 |
| | compliance_internal_notes (合规内部备注) | Layer 3 禁止 |
| | internal_discussion (内部讨论) | Layer 3 禁止 |

---

### 3.4 共享组件清单

#### 3.4.1 共享组件定义

本节定义三页（Dashboard / Audit Detail / Permit）共用的 6 个组件。

| 共享组件 | 使用页面 | 职责 | 禁止字段 |
|---------|---------|------|---------|
| **StatusLabel** | 全部三页 | 统一状态标签展示 | 禁止使用 Success/Done/Approved/Live 等营销词 |
| **HashDisplay** | Audit Detail, Permit | 统一 Hash 展示格式 | 禁止省略任一 Hash 字段 |
| **EvidenceRefPanel** | Audit Detail | 证据引用面板 | 禁止所有证据全量展示，必须区分 visibility 级别 |
| **PowerBoundary** | Audit Detail | 三权分立边界展示 | 禁止弱化或隐藏三权分立 |
| **PermitHeader** | Permit | Permit 证书抬头 | 禁止使用大绿勾/庆祝动画/营销式语言 |
| **FooterActionBar** | Audit Detail | 页面底部动作栏 | 禁止在 Blocked 状态显示"提交 Permit" |

#### 3.4.2 StatusLabel 组件规格

**组件名称:** `StatusLabel`

**使用场景:** 全部三页的状态标签展示

**字段需求:**

| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| status | enum | Y | Draft / In Audit / Passed / Fix Required / Blocked / Ready for Permit / Permit Active / Permit Revoked / Permit Expired |
| variant | enum | N | default / critical (Blocked 用) / success (Ready for Permit 用) |

**禁止状态词:**
- ❌ Success
- ❌ Done
- ❌ Completed
- ❌ Approved
- ❌ Live

**状态映射表:**

| 业务状态 | status 值 | variant | 视觉处理 |
|---------|-----------|---------|---------|
| 草稿 | Draft | default | 灰色 |
| 审计中 | In Audit | default | 蓝色 |
| 审计通过 | Passed | default | 绿色 |
| 需修复 | Fix Required | default | 橙色 |
| 阻断 | Blocked | critical | 红色 |
| 待放行 | Ready for Permit | success | 绿色 |
| 许可生效 | Permit Active | default | 绿色 |
| 许可撤销 | Permit Revoked | critical | 红色 |
| 许可过期 | Permit Expired | default | 灰色 |

#### 3.4.3 HashDisplay 组件规格

**组件名称:** `HashDisplay`

**使用场景:** Audit Detail, Permit

**字段需求:**

| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| hash_type | string | Y | demand_hash / contract_hash / decision_hash |
| hash_value | string(hash) | Y | 完整哈希值 |
| display_format | string | N | 前8位+省略 (默认) |

**展示规范:**
- 默认显示: `sha256:a1b2c3d4...`
- hover 显示全量
- 可复制
- 可跳转 linked object

**禁止事项:**
- ❌ 只显示哈希值的前几位而不标注省略
- ❌ 禁止复制哈希值
- ❌ 不提供跳转 linked object 的入口

#### 3.4.4 EvidenceRefPanel 组件规格

**组件名称:** `EvidenceRefPanel`

**使用场景:** Audit Detail

**字段需求:**

| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| evidence_refs | list[EvidenceRef] | Y | 证据引用列表 |

**EvidenceRef 对象结构:**

| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| id | string | Y | 证据 ID (EVD-003) |
| source_type | enum | Y | Log / File / Metric / Snapshot |
| summary | text | Y | 证据摘要 |
| strength | enum | Y | Weak / Medium / Strong |
| visibility | enum | Y | visible / summary-only / restricted |
| linked_gate | string | Y | 关联的 Gate |

**可见性级别处理:**
- `visible`: 完整可见，支持展开全量内容
- `summary-only`: 仅显示摘要，详情隐藏，点击可请求授权
- `restricted`: 显示"需权限验证"提示，当前角色不可见

**禁止事项:**
- ❌ 把所有证据全量展示
- ❌ 忽略 visibility 级别
- ❌ 让受限证据绕过权限验证

#### 3.4.5 PowerBoundary 组件规格

**组件名称:** `PowerBoundary`

**使用场景:** Audit Detail

**职责:** 三权分立边界展示

**内容结构:**
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

**禁止事项:**
- ❌ 弱化或隐藏三权分立
- ❌ 暗示执行者可以批准放行
- ❌ 暗示审查者可以签发 Permit

#### 3.4.6 PermitHeader 组件规格

**组件名称:** `PermitHeader`

**使用场景:** Permit

**职责:** Permit 证书抬头

**字段需求:**

| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| permit_id | string | Y | 许可证 ID (PMT-2026-0312-014) |
| asset_name | string | Y | 资产名称 |
| revision | string | Y | 版本号 (R-014) |
| status | StatusLabel | Y | 当前状态 |
| effective_date | timestamp | Y | 生效日期 |
| signed_by | string | Y | 签发者 (Compliance-01) |
| scope | string | Y | 放行范围 (Production / Internal / Client Delivery) |

**右侧动作:**

| CTA | 目标 | 条件 |
|-----|------|-----|
| Export Permit | 导出 Permit 为 PDF/文档 | 所有状态 |
| View Linked Audit | 跳转 Audit Detail | 所有状态 |
| Revoke Permit | 撤销当前 Permit | Active 状态 |
| View History | 查看 Permit 变更历史 | 所有状态 |

**禁止事项:**
- ❌ 使用"已批准"、"通过"、"成功"等营销式表达
- ❌ 使用大绿勾、庆祝动画等成功页样式
- ❌ 隐藏 Revision 或 Permit ID

#### 3.4.7 FooterActionBar 组件规格

**组件名称:** `FooterActionBar`

**使用场景:** Audit Detail

**职责:** 页面底部动作栏，根据状态动态变化

**CTA 状态机:**

| 当前状态 | 可用动作 |
|---------|---------|
| Blocked | View Critical Fixes, Export Fix Brief, Re-run After Changes |
| Fix Required | Go to Gap Analysis, Assign Owner, Re-submit to Audit |
| Passed | Export AuditPack, Submit for Permit |
| Ready for Permit | Open Permit Draft, Issue Permit |

**禁止事项:**
- ❌ 在 Blocked 状态显示"提交 Permit"
- ❌ 暗示"审计通过即放行"

---

### 3.5 页面间共享状态机

#### 3.5.1 资产状态机 (Asset State Machine)

**核心状态流转:**

```
Draft
  ↓ (submit for audit)
In Audit
  ↓ (audit completes)
  ├─→ Passed
  │     ↓ (submit for permit)
  │     Ready for Permit
  │       ↓ (permit issued)
  │       Permit Active
  │         ↓ (permit revoked/expired)
  │         Permit Revoked / Expired
  │
  ├─→ Fix Required
  │     ↓ (fixes applied)
  │     In Audit (重新进入)
  │
  └─→ Blocked
        ↓ (critical fixes applied)
        In Audit (重新进入)
```

**状态字段:** `current_status` (enum)

**状态标签映射:** 见 StatusLabel 组件规格

#### 3.5.2 Permit 状态机 (Permit State Machine)

**核心状态流转:**

```
Pending
  ↓ (compliance signs)
Permit Issued
  ↓ (effective date reached)
Active
  ↓ (revoked/expired/superseded)
Revoked / Expired / Superseded
```

**状态字段:** `status` (enum)

**关键事件:**
- `permit_issued`: 签发时间 (signed_at)
- `effective_date`: 生效时间
- `revoked_at`: 撤销时间 (如被撤销)
- `expires_at`: 过期时间 (如有时限)

#### 3.5.3 跨页面状态同步

| 页面 | 监听状态 | 状态变化后动作 |
|-----|---------|---------------|
| Dashboard | 所有资产状态 | KPI Row 更新，Priority Queue 重新排序 |
| Audit Detail | 单资产状态 | Decision Header 更新，Footer ActionBar 更新 |
| Permit | 单资产 Permit 状态 | Permit Header 更新，Core Decision Block 更新 |

**状态同步方式:**
- 页面级状态管理 (Context/Store)
- WebSocket / Server-Sent Events 推送
- 定时轮询 (fallback)

---

### 3.6 API 层裁剪责任清单

#### 3.6.1 裁剪责任原则

**核心原则:**
> **由 API 按角色返回不同 payload，敏感字段不得进入前端响应。**

**不应:**
- 在前端通过角色判断后再裁剪字段
- 全量下发给前端再隐藏

#### 3.6.2 按 API 端点裁剪清单

| API 端点 | 角色 | 允许返回的字段 | 禁止返回的字段 |
|---------|------|---------------|---------------|
| **GET /api/dashboard** | Executor/Reviewer/Compliance | 见 Dashboard 字段需求 | 见 Dashboard 禁止字段 |
| **GET /api/audit/:id** | Executor | own assets only | Layer 3 字段 |
| **GET /api/audit/:id** | Reviewer | assigned assets only | Layer 3 字段 |
| **GET /api/audit/:id** | Compliance | all assets | Layer 3 字段 |
| **GET /api/permit/:id** | Executor/Reviewer/Compliance | 见 Permit 字段需求 | 见 Permit 禁止字段 |
| **GET /api/evidence/:id** | 基于 visibility | visible/summary-only/restricted | 全量内容 (restricted 时) |

#### 3.6.3 角色与可见性映射

| 角色 | 可访问页面 | 可访问层级 |
|-----|-----------|-----------|
| **Executor** | Dashboard, Audit Detail (own assets) | Layer 0, Layer 1, Layer 2 (部分) |
| **Reviewer** | Dashboard, Audit Detail (assigned) | Layer 0, Layer 1, Layer 2 (部分) |
| **Compliance** | Dashboard, Audit Detail, Permit | Layer 0, Layer 1, Layer 2 (全部) |

**注意:** 所有角色均不得访问 Layer 3。

---

### 3.7 Never-in-DOM 字段清单

#### 3.7.1 Layer 3 绝对禁止前端呈现区

**任何角色都不应看到:**

| 类别 | 禁止字段 | 风险 |
|-----|---------|------|
| 规则机制 | threshold (阈值) | 可逆向规则逻辑 |
| 规则机制 | weight (权重) | 可逆向评分算法 |
| 规则机制 | rule_expression (规则表达式) | 可绕过判定 |
| 探针实现 | probe_code (探针代码) | 可绕过检测 |
| 探针实现 | probe_config (探针配置) | 可修改探针行为 |
| 执行细节 | blocking_trigger_path (阻断触发路径) | 可设计绕过 |
| 执行细节 | bypass_path (绕过路径) | 可直接绕过 |
| 系统架构 | internal_execution_topology (内部执行拓扑) | 可攻击系统 |
| 系统架构 | api_call_dependency_order (API调用依赖顺序) | 可攻击系统 |
| 异常信息 | internal_exception_stack (内部异常栈) | 暴露实现细节 |
| 异常信息 | module_name (模块名) | 暴露拓扑信息 |
| 异常信息 | call_chain (调用链) | 暴露流程信息 |
| 判定逻辑 | decision_tree_details (判定树详情) | 可逆向判定逻辑 |
| 判定逻辑 | scoring_algorithm (评分算法) | 可逆向评分方法 |
| 证据收集 | evidence_collection_method (证据收集方法) | 可规避检测 |
| 证据收集 | evidence_source_probe_info (证据来源探针信息) | 可攻击探针 |
| 证据处理 | evidence_weight_calculation (证据权重计算) | 可逆向评分 |
| 证据处理 | evidence_classification_criteria (证据分类依据) | 可逆向分类 |

#### 3.7.2 按页面分类的禁止字段

**Dashboard 页面额外禁止:**
- 规则详情 (rule_details)
- 判定逻辑可视化 (decision_logic_visualization)
- 探针过程展示 (probe_process_visualization)
- 权重与阈值展示 (weight_and_threshold_display)

**Audit Detail 页面额外禁止:**
- 内部异常栈 (internal_exception_stack)
- 模块名 (module_name)
- 调用链 (call_chain)
- 证据全量内容 (evidence_full_content) - visibility=restricted 时

**Permit 页面额外禁止:**
- 合规内部备注 (compliance_internal_notes)
- 内部讨论 (internal_discussion)
- 决策逻辑详情 (decision_logic_details)

---

## 四、交付物验收清单

- [x] 1. Dashboard 页面组件树已定义
- [x] 2. Dashboard 页面字段需求已定义
- [x] 3. Dashboard 页面禁止字段已列出
- [x] 4. Audit Detail 页面组件树已定义
- [x] 5. Audit Detail 页面字段需求已定义
- [x] 6. Audit Detail 页面禁止字段已列出
- [x] 7. Permit 页面组件树已定义
- [x] 8. Permit 页面字段需求已定义
- [x] 9. Permit 页面禁止字段已列出
- [x] 10. 共享组件清单已单列 (6 个)
- [x] 11. 每个共享组件规格已定义
- [x] 12. 页面间共享状态机已定义
- [x] 13. API 层裁剪责任已明确
- [x] 14. Never-in-DOM 字段清单已列出
- [x] 15. 未让前端接收 threshold/weight/internal topology
- [x] 16. 未通过前端角色判断隐藏敏感字段
- [x] 17. 未越权写到具体组件实现
- [x] 18. 数据边界服务治理型前端而非 builder 型前端

---

**文档版本:** v1.0
**最后更新:** 2026-03-12

**EvidenceRef:** 本规格基于以下文档合成:
- `docs/2026-03-12/前端重构_AI军团任务分发单_v2.md` (L397-443 - T-FE-05 任务书)
- `docs/2026-03-12/verification/T-FE-02_dashboard_spec.md` (完整文档)
- `docs/2026-03-12/verification/T-FE-03_audit_detail_spec.md` (完整文档)
- `docs/2026-03-12/verification/T-FE-04_permit_spec.md` (完整文档)
- `docs/2026-03-12/verification/T-FE-01_ia_spec.md` (四层信息分层模型)
- `docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md` (Layer 3 禁止区定义)
- `multi-ai-collaboration.md` (三权分立与任务调度格式)
- `docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md`
- `docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md`
