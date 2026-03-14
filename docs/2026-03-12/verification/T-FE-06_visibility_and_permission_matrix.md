# T-FE-06: 权限裁剪与禁止前端呈现区设计文档

> **任务 ID**: T-FE-06
> **执行者**: Kior-A
> **审查者**: vs--cc1
> **合规官**: Antigravity-2
> **日期**: 2026-03-12
> **依赖**: T-FE-05 (ALLOW)

---

## 一、PreflightChecklist

### 1.1 Fail-Closed 风险枚举

| 风险类别 | 潜在绕过路径 | 防御措施 |
|---------|-------------|---------|
| 前端权限裁剪 | 后端全量返回敏感字段，前端通过角色判断隐藏 | 强制"API 层裁剪原则"，明确禁止字段不得进入前端响应 |
| 机制信息泄漏 | Layer 3 禁止区定义不完整，导致阈值/权重/拓扑泄露 | 完整列出 16+ 类 Layer 3 禁止字段，覆盖规则/探针/执行/判定/证据维度 |
| 角色权限溢出 | Compliance 角色可访问 Layer 3 字段 | 明确所有角色均不得访问 Layer 3，Layer 3 为绝对禁止区 |
| API 责任不清 | 前后端对谁负责裁剪敏感字段理解不一致 | 单独章节明确"API payload 裁剪责任归属"，提供可直接使用的约束结构 |
| 可见性矩阵不完整 | 某些页面或字段的可见性未定义，导致实现时遗漏 | 输出完整的 Layer 0/1/2/3 可见性矩阵，覆盖三页主链所有字段 |
| EvidenceRef 泄漏 | restricted 级别的证据通过 API 全量返回 | 明确 Evidence visibility 级别的 API 裁剪规则 |

### 1.2 依赖环境

| 依赖项 | 当前状态 | 必需值 |
|-------|---------|-------|
| T-FE-05 Frontend Mapping | ALLOW | 已定义组件树、字段需求、禁止字段、共享组件 |
| 三页主链定义 | 已定义 | Dashboard/Audit Detail/Permit 角色 |
| 四层信息分层 | 已定义 | Layer 0/1/2 可展示范围，Layer 3 禁止区 |
| 共享组件清单 | 已定义 | 6 个共享组件的数据边界 |

### 1.3 历史债务扫描

| 债务类型 | 位置 | 处理策略 |
|---------|-----|---------|
| 现有 API 可能全量返回字段 | api/ | 本规格明确禁止字段清单，后续后端重构时落实 |
| 现有前端可能通过角色隐藏 | ui/app/src/ | 本规格强化 API 层裁剪原则，前端层隐藏为 anti-pattern |

---

## 二、ExecutionContract

### 2.1 Input Constraints

**允许读取的文件:**
- `docs/2026-03-12/前端重构_AI军团任务分发单_v2.md`
- `docs/2026-03-12/verification/T-FE-05_frontend_mapping.md`
- `docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md`
- `multi-ai-collaboration.md`
- `docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md`
- `docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md`

**允许创建的文件:**
- 本规格文档 `docs/2026-03-12/verification/T-FE-06_visibility_and_permission_matrix.md`

**绝对禁止:**
- 允许任何敏感机制信息进入前端响应
- 通过前端角色判断隐藏敏感字段
- 越权写到具体接口实现代码
- 允许 Layer 3 字段通过任何角色权限访问

### 2.2 Output Definition

**交付物:**
- 本权限矩阵文档，包含：
  1. Layer 0/1/2/3 可见性矩阵
  2. Never-in-DOM 清单
  3. API payload 裁剪责任归属
  4. 角色与信息密度映射
  5. 页面级权限裁剪规则
  6. 字段级禁止下发清单
  7. 可直接供前后端接口使用的约束结构

**回滚方案:**
- 本文档为规格说明，不涉及代码变更，无需回滚
- 如规格有误，可通过 Review/Compliance 流程修正

### 2.3 Gate / Acceptance Check

**手动检查:**
- [ ] 是否输出 Layer 0/1/2/3 可见性矩阵
- [ ] 是否输出 Never-in-DOM 清单
- [ ] 是否输出 API payload 裁剪责任归属
- [ ] 是否明确 API 层而非前端层进行权限裁剪
- [ ] 是否强化"所有角色均不得访问 Layer 3"
- [ ] 是否能直接作为前后端接口约束文档使用

---

## 三、RequiredChanges

### 3.1 四层信息分层模型 (Four-Layer Information Model)

#### 3.1.1 分层定义

| 层级 | 名称 | 定义 | 可见角色 | 典型内容 |
|-----|------|------|---------|---------|
| **Layer 0** | 对外公示层 | 面向公众/访客的系统级摘要 | 所有角色（含未登录） | 审计维度名称、系统级结果摘要、Permit 状态、封板摘要、时间戳与统计量级 |
| **Layer 1** | 内部工作台 | 面向内部用户的状态与裁决结果 | Executor/Reviewer/Compliance | 执行主链状态、审计通过/失败、当前 Gate、红线/可修复项分类、Permit readiness |
| **Layer 2** | 受控详情层 | 面向授权用户的详细证据与元数据 | Reviewer/Compliance（部分） | Evidence Bundle、Metrics、Hash、Revision lineage、Signoff 历史、受控证据包 |
| **Layer 3** | 禁止前端呈现区 | 任何角色都不得在前端看到的敏感机制信息 | **无**（绝对禁止） | 判定阈值、算法权重、探针代码、阻断触发路径、绕过路径、内部执行拓扑 |

#### 3.1.2 分层核心原则

**原则 1: Layer 3 为绝对禁止区**
- 任何角色均不得访问 Layer 3
- Layer 3 字段不得进入前端响应（无论角色权限）
- Layer 3 字段不得通过任何"展开"或"详情"功能暴露

**原则 2: 层级递进，需授权**
- Layer 0: 默认可见
- Layer 1: 登录用户可见
- Layer 2: 基于角色和上下文的授权访问
- Layer 3: 永久禁止

**原则 3: API 层裁剪，前端层展示**
- API 层负责按角色和层级裁剪 payload
- 前端层负责展示已裁剪后的内容
- 禁止"后端全量返回 + 前端隐藏"模式

---

### 3.2 Layer 0/1/2/3 可见性矩阵

#### 3.2.1 按页面的可见性矩阵

**Dashboard 页面:**

| 字段类别 | Layer 0 | Layer 1 | Layer 2 | Layer 3 |
|---------|---------|---------|---------|---------|
| **KPI Row** | ✓ | ✓ | - | - |
| **8 Gate Health** | - | ✓ (pass/warn/fail 数) | - | ✗ (threshold, weight, rule details) |
| **Priority Queue** | - | ✓ | - | - |
| **Evidence Coverage** | - | ✓ (completeness score) | ✓ (weak evidence list) | ✗ (collection method, weight calc) |
| **Permit Events** | - | ✓ | - | - |
| **Revision Watch** | - | ✓ | - | - |

**Audit Detail 页面:**

| 字段类别 | Layer 0 | Layer 1 | Layer 2 | Layer 3 |
|---------|---------|---------|---------|---------|
| **Decision Header** | - | ✓ | - | - |
| **Decision Summary** | - | ✓ | - | - |
| **Power Boundary** | - | ✓ | - | - |
| **8 Gate Timeline** | - | ✓ (status, reason) | ✓ (triggered rules 引用) | ✗ (rule details, threshold) |
| **EvidenceRef Panel** | - | - | ✓ (based on visibility) | ✗ (full content for restricted) |
| **Red Lines** | - | ✓ | - | - |
| **Fixable Gaps** | - | ✓ | - | - |
| **Hash & Reproducibility** | - | - | ✓ | - |

**Permit 页面:**

| 字段类别 | Layer 0 | Layer 1 | Layer 2 | Layer 3 |
|---------|---------|---------|---------|---------|
| **Permit Header** | - | ✓ | - | - |
| **Core Decision Block** | - | ✓ | - | - |
| **Release Scope** | - | ✓ | - | - |
| **Conditions** | - | ✓ | - | - |
| **Audit Basis** | - | ✓ | ✓ (linked hashes) | - |
| **Permit Lifecycle** | - | ✓ | - | - |
| **Compliance Signature** | - | ✓ | - | ✗ (internal notes, discussion) |

**图例说明:**
- ✓ = 该层可访问
- - = 不适用该层
- ✗ = 明确禁止（Layer 3）

#### 3.2.2 按字段类别的可见性矩阵

| 字段类别 | Layer 0 | Layer 1 | Layer 2 | Layer 3 | 示例 |
|---------|---------|---------|---------|---------|------|
| **状态类** | ✓ (部分) | ✓ | ✓ | - | asset_status, gate_status, permit_status |
| **统计类** | ✓ (聚合) | ✓ | ✓ | - | pass_count, fail_count, completeness_score |
| **标识类** | - | ✓ | ✓ | - | asset_id, revision_id, permit_id, hash (前8位) |
| **裁决类** | - | ✓ | ✓ | - | decision, reason, primary_reason |
| **证据类** | - | - | ✓ (controlled) | ✗ | evidence_ref (based on visibility) |
| **规则引用类** | - | - | ✓ (引用 only) | ✗ | triggered_rules (RULE-4.2, no details) |
| **规则机制类** | - | - | - | ✗ | threshold, weight, rule_expression, probe_code |
| **执行细节类** | - | - | - | ✗ | call_chain, module_name, internal_topology |
| **异常信息类** | - | - | - | ✗ | internal_exception_stack |
| **合规内部类** | - | - | - | ✗ | compliance_internal_notes, internal_discussion |

---

### 3.3 Never-in-DOM 清单

#### 3.3.1 Layer 3 绝对禁止前端呈现区 (完整版)

**任何角色都不应看到，不得进入 DOM，不得进入前端响应:**

| 类别 | 禁止字段 | 风险等级 | 风险描述 |
|-----|---------|---------|---------|
| **规则机制** | threshold (阈值) | CRITICAL | 可逆向规则判定逻辑 |
| **规则机制** | weight (权重) | CRITICAL | 可逆向评分算法 |
| **规则机制** | rule_expression (规则表达式) | CRITICAL | 可绕过判定 |
| **规则机制** | rule_definition (规则定义) | CRITICAL | 可修改规则 |
| **规则机制** | rule_to_gate_mapping (规则与 Gate 映射) | HIGH | 可逆向系统架构 |
| **探针实现** | probe_code (探针代码) | CRITICAL | 可绕过检测 |
| **探针实现** | probe_config (探针配置) | CRITICAL | 可修改探针行为 |
| **探针实现** | probe_execution_path (探针执行路径) | HIGH | 可攻击探针 |
| **执行细节** | blocking_trigger_path (阻断触发路径) | CRITICAL | 可设计绕过 |
| **执行细节** | bypass_path (绕过路径) | CRITICAL | 可直接绕过 |
| **执行细节** | execution_sequence (执行顺序) | HIGH | 可逆向执行流程 |
| **系统架构** | internal_execution_topology (内部执行拓扑) | CRITICAL | 可攻击系统 |
| **系统架构** | api_call_dependency_order (API 调用依赖顺序) | CRITICAL | 可攻击系统 |
| **系统架构** | module_dependency_graph (模块依赖图) | HIGH | 可逆向架构 |
| **异常信息** | internal_exception_stack (内部异常栈) | HIGH | 暴露实现细节 |
| **异常信息** | module_name (模块名) | MEDIUM | 暴露拓扑信息 |
| **异常信息** | call_chain (调用链) | HIGH | 暴露流程信息 |
| **判定逻辑** | decision_tree_details (判定树详情) | CRITICAL | 可逆向判定逻辑 |
| **判定逻辑** | scoring_algorithm (评分算法) | CRITICAL | 可逆向评分方法 |
| **判定逻辑** | decision_path_visualization (判定路径可视化) | HIGH | 可逆向判定过程 |
| **证据收集** | evidence_collection_method (证据收集方法) | HIGH | 可规避检测 |
| **证据收集** | evidence_source_probe_info (证据来源探针信息) | HIGH | 可攻击探针 |
| **证据收集** | evidence_collection_path (证据收集路径) | MEDIUM | 可逆向收集流程 |
| **证据处理** | evidence_weight_calculation (证据权重计算) | CRITICAL | 可逆向评分 |
| **证据处理** | evidence_classification_criteria (证据分类依据) | HIGH | 可逆向分类 |
| **证据处理** | evidence_strength_decision_logic (证据强度判定逻辑) | HIGH | 可逆向判定 |
| **合规内部** | compliance_internal_notes (合规内部备注) | MEDIUM | 内部讨论不应公开 |
| **合规内部** | internal_discussion (内部讨论) | MEDIUM | 内部讨论不应公开 |
| **合规内部** | decision_rationale_private (私有决策理由) | MEDIUM | 内部理由不应公开 |

**总计: 30 类禁止字段**

#### 3.3.2 按页面分类的禁止字段

**Dashboard 页面额外禁止 (补充 T-FE-05):**
- 规则详情展开 (rule_details_expansion)
- 判定逻辑可视化 (decision_logic_visualization)
- 探针过程展示 (probe_process_visualization)
- 权重与阈值展示 (weight_and_threshold_display)
- 渐进式机制暴露 (progressive_mechanism_exposure)

**Audit Detail 页面额外禁止 (补充 T-FE-05):**
- 证据全量内容 for restricted (evidence_full_content_restricted)
- 规则触发详情 (triggered_rule_details)
- Gate 判定依据 (gate_decision_basis)

**Permit 页面额外禁止 (补充 T-FE-05):**
- Permit 签发决策细节 (permit_issuance_decision_details)
- Compliance 审批过程 (compliance_approval_process)
- 内部风险评估 (internal_risk_assessment)

---

### 3.4 API payload 裁剪责任归属

#### 3.4.1 裁剪责任原则 (HARD REQUIREMENT)

**核心原则:**
> **API 层必须按角色和层级裁剪 payload，敏感字段不得进入前端响应。**

**禁止模式 (ANTI-PATTERN):**
```yaml
# ❌ 禁止: 后端全量返回，前端隐藏
GET /api/audit/:id
response:
  all_fields: true  # 包括 Layer 3
  frontend_responsible: true  # 前端根据角色隐藏
```

**要求模式 (REQUIRED PATTERN):**
```yaml
# ✓ 要求: 后端按角色裁剪
GET /api/audit/:id
request:
  headers:
    X-Role: "Executor|Reviewer|Compliance"
response:
  fields: "based_on_role_and_layer"  # 后端裁剪
  layer_3_fields: "never_included"  # 永远不包含
```

#### 3.4.2 按 API 端点的裁剪责任

| API 端点 | Executor 允许字段 | Reviewer 允许字段 | Compliance 允许字段 | 共同禁止字段 (Layer 3) |
|---------|------------------|-------------------|---------------------|----------------------|
| **GET /api/dashboard** | Layer 0 + Layer 1 | Layer 0 + Layer 1 | Layer 0 + Layer 1 | 全部 Layer 3 字段 |
| **GET /api/audit/:id** | own assets, Layer 1 | assigned, Layer 1+2(部分) | all, Layer 1+2 | 全部 Layer 3 字段 |
| **GET /api/permit/:id** | Layer 1 | Layer 1 | Layer 1+2(部分) | 全部 Layer 3 字段 |
| **GET /api/evidence/:id** | based on visibility | based on visibility | based on visibility | full content when restricted |
| **POST /api/audit/submit** | - | - | Layer 1 only | 全部 Layer 3 字段 |
| **POST /api/permit/issue** | - | - | Layer 1 only | 全部 Layer 3 字段 |

#### 3.4.3 API 响应结构约束 (可直接使用)

**通用 API 响应结构:**
```json
{
  "data": {
    // Layer 0/1/2 字段，按角色裁剪
  },
  "meta": {
    "layer": "0|1|2",
    "role": "Executor|Reviewer|Compliance",
    "filtered_fields": ["threshold", "weight", ...],  // 已过滤的 Layer 3 字段
    "hash": "sha256:..."
  },
  "errors": [],
  "pagination": {}
}
```

**禁止事项:**
- ❌ 在响应中包含 Layer 3 字段（无论是否标记为 filtered）
- ❌ 在 meta 中暴露被过滤字段的具体值
- ❌ 提供任何"获取完整数据"的端点或参数

---

### 3.5 角色与信息密度映射

#### 3.5.1 角色定义

| 角色 | 职责 | 可访问层级 | 特殊约束 |
|-----|------|-----------|---------|
| **Executor** | 执行任务，产出结果 | Layer 0, Layer 1 | 只能访问 own assets，不能访问 others' Layer 2 |
| **Reviewer** | 审查质量与边界 | Layer 0, Layer 1, Layer 2 (部分) | 只能访问 assigned assets，Layer 2 基于 evidence visibility |
| **Compliance** | 硬拦截与放行 | Layer 0, Layer 1, Layer 2 (全部) | 可访问 all assets，但仍不能访问 Layer 3 |

#### 3.5.2 角色与页面访问权限

| 页面 | Executor | Reviewer | Compliance | 说明 |
|-----|----------|----------|------------|------|
| **Dashboard** | ✓ | ✓ | ✓ | 所有人可见，但字段内容可能不同 |
| **Audit Detail** | ✓ (own only) | ✓ (assigned only) | ✓ (all) | 基于资产所有权和分配过滤 |
| **Permit** | ✓ (view only) | ✓ (view only) | ✓ (view + issue) | Compliance 有签发权 |

#### 3.5.3 角色与字段级访问权限

**Executor 角色字段级限制:**
- 不能访问 others' assets 的 Layer 2 字段
- 不能访问 any asset 的 Layer 3 字段
- 不能访问 Compliance 专属字段（如签发备注）

**Reviewer 角色字段级限制:**
- 可以访问 assigned assets 的 Layer 2 字段
- 不能访问 any asset 的 Layer 3 字段
- 不能访问 Compliance 专属字段

**Compliance 角色字段级限制:**
- 可以访问 all assets 的 Layer 2 字段
- **仍不能访问任何 Layer 3 字段**
- 可以访问 Compliance 专属字段（内部备注不暴露给前端）

---

### 3.6 页面级权限裁剪规则

#### 3.6.1 Dashboard 页面权限规则

**访问控制:**
- 所有登录用户可访问
- 无资产所有权限制

**字段级裁剪:**
- KPI Row: 所有角色可见相同数据
- 8 Gate Health: Layer 1 数据，所有角色可见相同（pass/warn/fail 数）
- Priority Queue: 基于角色过滤资产
  - Executor: 只显示 own assets
  - Reviewer: 只显示 assigned assets
  - Compliance: 显示 all assets
- Evidence Coverage: Layer 1 数据，所有角色可见相同
- Permit Events: 所有角色可见相同

**禁止事项:**
- ❌ 在 Dashboard 中暴露 Layer 2 详情（如证据全量内容）
- ❌ 在 Dashboard 中暴露任何 Layer 3 字段

#### 3.6.2 Audit Detail 页面权限规则

**访问控制:**
- 基于资产所有权和分配过滤
- Executor: 只能访问 own assets
- Reviewer: 只能访问 assigned assets
- Compliance: 可访问 all assets

**字段级裁剪:**
- Decision Header: Layer 1，所有有权限的角色可见
- Decision Summary: Layer 1，所有有权限的角色可见
- Power Boundary: Layer 1，所有有权限的角色可见
- 8 Gate Timeline: Layer 1 基础 + Layer 2 (triggered rules 引用)
- EvidenceRef Panel: 基于 evidence visibility
  - visible: 完整可见
  - summary-only: 仅摘要
  - restricted: 显示"需权限验证"提示
- Red Lines / Fixable Gaps: Layer 1，所有有权限的角色可见
- Hash & Reproducibility: Layer 2，所有有权限的角色可见

**禁止事项:**
- ❌ 暴露 triggered_rule_details（仅允许规则引用）
- ❌ 暴露 evidence_full_content（visibility=restricted 时）
- ❌ 暴露任何 Layer 3 字段

#### 3.6.3 Permit 页面权限规则

**访问控制:**
- Executor: 只读访问
- Reviewer: 只读访问
- Compliance: 只读 + 签发权限

**字段级裁剪:**
- Permit Header: Layer 1，所有有权限的角色可见
- Core Decision Block: Layer 1，所有有权限的角色可见
- Release Scope: Layer 1，所有有权限的角色可见
- Conditions: Layer 1，所有有权限的角色可见
- Audit Basis: Layer 1 基础 + Layer 2 (linked hashes)
- Permit Lifecycle: Layer 1，所有有权限的角色可见
- Compliance Signature: Layer 1 (signed_by, signed_at)，内部备注不暴露

**禁止事项:**
- ❌ 暴露 compliance_internal_notes
- ❌ 暴露 internal_discussion
- ❌ 暴露 permit_issuance_decision_details
- ❌ 暴露任何 Layer 3 字段

---

### 3.7 字段级禁止下发清单

#### 3.7.1 按字段类型的禁止清单

**规则机制类 (7 类):**
1. threshold (阈值)
2. weight (权重)
3. rule_expression (规则表达式)
4. rule_definition (规则定义)
5. rule_to_gate_mapping (规则与 Gate 映射)
6. triggered_rule_details (触发规则详情)
7. decision_logic_details (决策逻辑详情)

**探针实现类 (3 类):**
8. probe_code (探针代码)
9. probe_config (探针配置)
10. probe_execution_path (探针执行路径)

**执行细节类 (3 类):**
11. blocking_trigger_path (阻断触发路径)
12. bypass_path (绕过路径)
13. execution_sequence (执行顺序)

**系统架构类 (3 类):**
14. internal_execution_topology (内部执行拓扑)
15. api_call_dependency_order (API 调用依赖顺序)
16. module_dependency_graph (模块依赖图)

**异常信息类 (3 类):**
17. internal_exception_stack (内部异常栈)
18. module_name (模块名)
19. call_chain (调用链)

**判定逻辑类 (3 类):**
20. decision_tree_details (判定树详情)
21. scoring_algorithm (评分算法)
22. decision_path_visualization (判定路径可视化)

**证据收集类 (3 类):**
23. evidence_collection_method (证据收集方法)
24. evidence_source_probe_info (证据来源探针信息)
25. evidence_collection_path (证据收集路径)

**证据处理类 (3 类):**
26. evidence_weight_calculation (证据权重计算)
27. evidence_classification_criteria (证据分类依据)
28. evidence_strength_decision_logic (证据强度判定逻辑)

**合规内部类 (3 类):**
29. compliance_internal_notes (合规内部备注)
30. internal_discussion (内部讨论)

**总计: 30 类禁止字段**

#### 3.7.2 禁止下发清单的使用方式

**后端 API 开发时:**
- 检查每个 API 响应字段
- 如字段在禁止清单中，必须移除
- 如字段需要保留，必须证明其不属于 Layer 3

**前端开发时:**
- 检查从 API 接收到的每个字段
- 如发现禁止清单中的字段，必须报告为安全风险
- 不得在 DOM 中渲染禁止字段

**Code Review 时:**
- 检查所有新增的 API 字段
- 检查所有新增的前端组件 props
- 确保无 Layer 3 字段泄露

---

### 3.8 可直接供前后端接口使用的约束结构

#### 3.8.1 API 响应约束 Schema

```typescript
// API 响应约束接口
interface APIResponseConstraint<T> {
  data: T;  // 按角色和层级裁剪后的数据
  meta: {
    layer: 0 | 1 | 2;  // 当前响应的层级
    role: "Executor" | "Reviewer" | "Compliance";  // 当前响应的角色
    filtered_fields: Layer3Field[];  // 已过滤的 Layer 3 字段列表
    hash: string;  // 响应内容的哈希值
  };
  errors: APIError[];
  pagination?: Pagination;
}

// Layer 3 字段标识（用于 filtered_fields）
interface Layer3Field {
  field_name: string;  // 字段名称
  reason: string;  // 过滤原因（如 "Layer 3 禁止字段"）
}
```

#### 3.8.2 字段可见性约束 Schema

```typescript
// 字段可见性约束
interface FieldVisibilityConstraint {
  field_name: string;
  layer: 0 | 1 | 2 | 3;  // 字段所属层级
  allowed_roles: ("Executor" | "Reviewer" | "Compliance")[];  // 允许访问的角色
  conditions?: {
    asset_ownership?: "own" | "assigned" | "all";  // 资产所有权条件
    evidence_visibility?: "visible" | "summary-only" | "restricted";  // 证据可见性条件
  };
}

// 示例: decision_hash 字段约束
const decision_hash_constraint: FieldVisibilityConstraint = {
  field_name: "decision_hash",
  layer: 2,
  allowed_roles: ["Executor", "Reviewer", "Compliance"],
  conditions: {
    asset_ownership: "own" | "assigned" | "all",  // 基于页面权限
  },
};

// 示例: threshold 字段约束（Layer 3）
const threshold_constraint: FieldVisibilityConstraint = {
  field_name: "threshold",
  layer: 3,
  allowed_roles: [],  // 无角色允许访问
};
```

#### 3.8.3 页面级权限约束 Schema

```typescript
// 页面级权限约束
interface PagePermissionConstraint {
  page: "Dashboard" | "AuditDetail" | "Permit";
  allowed_roles: ("Executor" | "Reviewer" | "Compliance")[];
  field_constraints: {
    [field_name: string]: FieldVisibilityConstraint;
  };
  special_rules?: string[];  // 特殊规则（如 "Executor 只能访问 own assets"）
}

// 示例: Audit Detail 页面约束
const audit_detail_constraint: PagePermissionConstraint = {
  page: "AuditDetail",
  allowed_roles: ["Executor", "Reviewer", "Compliance"],
  field_constraints: {
    "decision_hash": {
      field_name: "decision_hash",
      layer: 2,
      allowed_roles: ["Executor", "Reviewer", "Compliance"],
    },
    "threshold": {
      field_name: "threshold",
      layer: 3,
      allowed_roles: [],  // Layer 3，无角色允许
    },
    // ... 其他字段
  },
  special_rules: [
    "Executor 只能访问 own assets",
    "Reviewer 只能访问 assigned assets",
    "Compliance 可访问 all assets",
  ],
};
```

#### 3.8.4 完整的三页主链约束结构

```typescript
// 三页主链约束配置
const three_page_constraints = {
  Dashboard: {
    page: "Dashboard",
    allowed_roles: ["Executor", "Reviewer", "Compliance"],
    field_constraints: {
      // KPI Row
      "kpi_row.count": { layer: 0, allowed_roles: ["Executor", "Reviewer", "Compliance"] },
      // 8 Gate Health
      "gate_health.pass_count": { layer: 1, allowed_roles: ["Executor", "Reviewer", "Compliance"] },
      "gate_health.threshold": { layer: 3, allowed_roles: [] },  // Layer 3
      // Priority Queue
      "priority_queue.asset_name": { layer: 1, allowed_roles: ["Executor", "Reviewer", "Compliance"] },
      // Evidence Coverage
      "evidence_coverage.completeness_score": { layer: 1, allowed_roles: ["Executor", "Reviewer", "Compliance"] },
      "evidence_coverage.collection_method": { layer: 3, allowed_roles: [] },  // Layer 3
      // ... 其他字段
    },
  },
  AuditDetail: {
    page: "AuditDetail",
    allowed_roles: ["Executor", "Reviewer", "Compliance"],
    field_constraints: {
      // Decision Header
      "decision_header.decision": { layer: 1, allowed_roles: ["Executor", "Reviewer", "Compliance"] },
      // 8 Gate Timeline
      "gate_timeline.triggered_rules": { layer: 2, allowed_roles: ["Executor", "Reviewer", "Compliance"] },
      "gate_timeline.rule_details": { layer: 3, allowed_roles: [] },  // Layer 3
      // EvidenceRef Panel
      "evidence_ref_panel.summary": { layer: 2, allowed_roles: ["Executor", "Reviewer", "Compliance"] },
      "evidence_ref_panel.full_content": { layer: 3, allowed_roles: [] },  // Layer 3 when restricted
      // ... 其他字段
    },
    special_rules: [
      "Executor 只能访问 own assets",
      "Reviewer 只能访问 assigned assets",
      "Compliance 可访问 all assets",
      "Evidence visibility 基于 evidence.visibility 字段",
    ],
  },
  Permit: {
    page: "Permit",
    allowed_roles: ["Executor", "Reviewer", "Compliance"],
    field_constraints: {
      // Permit Header
      "permit_header.permit_id": { layer: 1, allowed_roles: ["Executor", "Reviewer", "Compliance"] },
      // Core Decision Block
      "core_decision_block.decision": { layer: 1, allowed_roles: ["Executor", "Reviewer", "Compliance"] },
      // Compliance Signature
      "compliance_signature.signed_by": { layer: 1, allowed_roles: ["Executor", "Reviewer", "Compliance"] },
      "compliance_signature.internal_notes": { layer: 3, allowed_roles: [] },  // Layer 3
      // ... 其他字段
    },
    special_rules: [
      "Executor 和 Reviewer: 只读访问",
      "Compliance: 只读 + 签发权限",
    ],
  },
};
```

---

### 3.9 前后端协作指南

#### 3.9.1 后端开发指南

**API 开发检查清单:**
1. 每个 API 端点必须明确按角色裁剪字段
2. 检查响应字段是否包含 Layer 3 禁止字段
3. 在响应 meta 中返回 filtered_fields 列表
4. 不得提供"获取完整数据"的参数或端点

**禁止事项:**
- ❌ 全量返回数据，让前端根据角色过滤
- ❌ 在响应中包含 Layer 3 字段（即使标记为 filtered）
- ❌ 提供 `?include=all` 或类似参数

#### 3.9.2 前端开发指南

**前端开发检查清单:**
1. 检查从 API 接收到的每个字段
2. 如发现禁止清单中的字段，报告为安全风险
3. 不得在 DOM 中渲染禁止字段
4. 不得在浏览器控制台日志中打印禁止字段

**禁止事项:**
- ❌ 在前端通过角色判断隐藏敏感字段
- ❌ 在 DOM 中存储敏感字段（即使隐藏）
- ❌ 在浏览器控制台日志中打印敏感字段

#### 3.9.3 Code Review 指南

**后端 Code Review:**
- 检查 API 响应是否包含 Layer 3 字段
- 检查是否正确实现了按角色裁剪
- 检查是否在 meta 中返回 filtered_fields

**前端 Code Review:**
- 检查组件 props 是否包含禁止字段
- 检查是否在 DOM 中渲染了禁止字段
- 检查是否有通过角色判断隐藏字段的情况

---

## 四、交付物验收清单

- [x] 1. 输出 Layer 0/1/2/3 可见性矩阵
- [x] 2. 输出 Never-in-DOM 清单 (30 类禁止字段)
- [x] 3. 输出 API payload 裁剪责任归属
- [x] 4. 输出角色与信息密度映射
- [x] 5. 输出页面级权限裁剪规则
- [x] 6. 输出字段级禁止下发清单
- [x] 7. 输出可直接供前后端接口使用的约束结构
- [x] 8. 强化 API 层裁剪，不允许前端拿到后再隐藏
- [x] 9. 强化 Layer 3 绝对禁止区单独成节
- [x] 10. 强化可见性矩阵与三页主链一致
- [x] 11. 文档可直接作为前后端接口约束文档使用
- [x] 12. 强化"所有角色均不得访问 Layer 3"
- [x] 13. 未允许任何敏感机制信息进入前端响应
- [x] 14. 未通过前端角色判断隐藏敏感字段
- [x] 15. 未越权写到具体接口实现代码

---

**文档版本**: v1.0
**最后更新**: 2026-03-12

**EvidenceRef**: 本规格基于以下文档合成:
- `docs/2026-03-12/前端重构_AI军团任务分发单_v2.md` (L447-490 - T-FE-06 任务书)
- `docs/2026-03-12/verification/T-FE-05_frontend_mapping.md` (完整文档)
- `docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md` (Layer 3 禁止区定义)
- `docs/2026-03-12/verification/T-FE-02_dashboard_spec.md` (Dashboard 字段需求与禁止字段)
- `docs/2026-03-12/verification/T-FE-03_audit_detail_spec.md` (Audit Detail 字段需求与禁止字段)
- `docs/2026-03-12/verification/T-FE-04_permit_spec.md` (Permit 字段需求与禁止字段)
- `multi-ai-collaboration.md` (三权分立与任务调度格式)
- `docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md`
- `docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md`
