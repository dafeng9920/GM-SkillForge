# 前端重构 AI 军团任务分发单 v2

> 对齐文档：`multi-ai-collaboration.md`
> 任务主题：GM-SkillForge 前端治理重构
> 执行模式：`strict`

---

## 0. 强制对齐文档（Single Source of Truth）

本批次必须同时遵守以下文档，冲突时按顺序优先：

1. `docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md`
2. `docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md`
3. `multi-ai-collaboration.md`
4. `docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md`
5. `docs/2026-03-12/“治理与放行中枢”的前端设计.md`

关键口径：

* 无 `ComplianceAttestation(PASS)` 不执行
* 需要副作用动作时，无 `permit=VALID` 不执行
* 无 `EvidenceRef` 不算完成
* 本轮目标是治理型前端，不是 builder 型前端

---

## 1. 顶层结论

本轮前端重构不是在优化一个 AI 工具界面，而是在建立一个：

* 治理中枢
* 审计工作台
* 放行控制层

主链页面固定为：

1. `Dashboard`
2. `Audit Detail`
3. `Permit`

硬原则：

* 不得让 `Forge` 成为视觉中心
* 不得滑回 `builder / canvas / marketplace` 叙事
* 不得把“审计通过”表达成“已经放行”
* 不得暴露规则阈值、算法权重、探针逻辑、执行拓扑
* 不得删除三权分立、EvidenceRef、Hash、Revision、Permit 绑定关系

---

## 2. 三权分立（MUST）

每个任务必须存在三种独立权力，不得混同：

* `Execution`：只按合同实施改动，无放行权
* `Review`：检查质量与边界，可打回，无执行权
* `Compliance`：按 B Guard 做硬拦截，有一票否决权

执行顺序固定为：

1. Review 完成审查意见
2. Compliance 产出 `ComplianceAttestation`
3. 仅当 `Compliance=PASS` 时，Execution 才能进入落地产物阶段

缺失任一角色记录，任务直接 `DENY`。

---

## 3. 本轮任务拆分

### Wave 1

* `T-FE-01` 前端信息架构与导航重构
* `T-FE-02` Dashboard 页面规格与治理化约束
* `T-FE-03` Audit Detail 页面规格与证据闭环约束
* `T-FE-04` Permit 页面规格与凭证语义约束

### Wave 2

* `T-FE-05` 前端组件树与数据边界映射
* `T-FE-06` 页面级权限裁剪与禁止前端呈现区设计
* `T-FE-07` 首页叙事与应用内 CTA 统一收口

### Final Gate

* 汇总全部 `execution_report / gate_decision / compliance_attestation`
* 输出前端治理重构总裁决

---

## 4. 任务依赖表

| Wave | Task | Execution | Review | Compliance | Depends On | 状态 |
|---|---|---|---|---|---|---|
| Wave 1 | T-FE-01 | Antigravity-2 | vs--cc3 | Kior-C | - | 待启动 |
| Wave 1 | T-FE-02 | vs--cc1 | Kior-A | Kior-B | T-FE-01 | 待启动 |
| Wave 1 | T-FE-03 | Antigravity-1 | vs--cc2 | Kior-C | T-FE-01 | 待启动 |
| Wave 1 | T-FE-04 | Kior-B | Antigravity-2 | vs--cc3 | T-FE-01 | 待启动 |
| Wave 2 | T-FE-05 | vs--cc2 | Antigravity-1 | Kior-C | T-FE-02,T-FE-03,T-FE-04 | 待启动 |
| Wave 2 | T-FE-06 | Kior-A | vs--cc1 | Antigravity-2 | T-FE-05 | 待启动 |
| Wave 2 | T-FE-07 | vs--cc3 | Kior-B | Kior-C | T-FE-02,T-FE-03,T-FE-04 | 待启动 |

说明：

* `Kior-C` 作为本轮主要 Compliance 角色，不参与具体规格实施
* `Antigravity-1/2` 负责守住主链治理与合同边界
* `vs--cc1/2/3` 负责规格化与可实现映射

---

## 5. 六步流程（按 multi-ai-collaboration 执行）

### Step 1. 需求对齐

已完成：

* 三页设计方向已确认
* `Gemini / Claude` 关于治理型前端的共识已合并
* 今日两份文档已并入总稿

### Step 2. A Guard 提案生成

本分发单即为本轮提案入口。

### Step 3. Review 审查

每个任务必须单独输出 `gate_decision.json`，不得口头放行。

### Step 4. B Guard 合规复查

每个任务必须单独输出 `compliance_attestation.json`。

### Step 5. Execution 执行

每个执行者只能在其任务范围内产出：

* 规格文档
* 组件树
* 数据边界
* 验收口径

本轮默认不直接写业务实现代码。

### Step 6. Final Gate 验收

主控官汇总全部任务，输出：

* `final_gate_decision.json`

---

## 6. 统一 DoD（本轮交付完成定义）

全部任务完成后，必须同时满足：

1. 产品主叙事已经从 builder 切换为治理中枢 / 审计工作台 / 放行控制层
2. `Dashboard / Audit Detail / Permit` 成为主链页面，不再被 Forge 抢走中心
3. 三权分立在页面层有明确可视化落点
4. EvidenceRef / Hash / Revision / Permit 绑定关系在页面与数据层都被保留
5. 前端明确划出“可展示信息”与“绝不进入前端的信息”
6. 首页 CTA 与应用内 CTA 均不再偏向 builder 叙事
7. 当前阶段明确暂缓 canvas / 市场 / 社区 / 炫技大屏 / 重 RBAC 门户

---

## 7. 每任务统一证据模板

所有任务都必须提交：

* `ExecutionReport`
* `GateDecision`
* `ComplianceAttestation`
* `EvidenceRef`

证据类型允许：

* `FILE`
* `DIFF`
* `SNIPPET`
* `DOC`
* `LINE_REF`

---

## 8. Task Skill Spec

以下任务书可直接复制给各执行者。

---

## T-FE-01

```yaml
task_id: "T-FE-01"
executor: "Antigravity-2"
reviewer: "vs--cc3"
compliance_officer: "Kior-C"
wave: "Wave 1"
depends_on: []
estimated_minutes: 45

input:
  description: "将前端重构目标整理成严格的信息架构、导航与页面边界方案"
  context_files:
    - path: "docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md"
      purpose: "三页主链与统一设计宪法"
    - path: "docs/2026-03-12/“治理与放行中枢”的前端设计.md"
      purpose: "产品定位、页面体系、推进顺序"
    - path: "multi-ai-collaboration.md"
      purpose: "三权分立与任务调度格式"
  guard_refs:
    - "docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md"
    - "docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md"

output:
  deliverables:
    - path: "docs/2026-03-12/verification/T-FE-01_ia_spec.md"
      type: "新建"
      schema_ref: "front-end IA spec"
  constraints:
    - "必须输出一级导航 / 页面职责 / 用户路径 / 暂缓模块"
    - "不得写视觉实现代码"
    - "不得让 Forge 成为主导航中心"
    - "无 EvidenceRef 不得宣称完成"

deny:
  - "不得输出 builder-first 叙事"
  - "不得把 canvas / marketplace 放入 v0 核心路径"
  - "不得越权定义具体组件实现"

gate:
  auto_checks:
    - command: "rg -n \"builder|canvas|marketplace\" docs/2026-03-12/verification/T-FE-01_ia_spec.md"
      expect: "仅允许出现在 deny 或禁用语境"
  manual_checks:
    - "是否明确首页讲价值，应用内讲状态/裁决/证据/放行"
    - "是否明确 Dashboard / Audit Detail / Permit 为主链"

compliance:
  required: true
  attestation_path: "docs/2026-03-12/verification/T-FE-01_compliance_attestation.json"
  permit_required_for_side_effects: false
```

---

## T-FE-02

```yaml
task_id: "T-FE-02"
executor: "vs--cc1"
reviewer: "Kior-A"
compliance_officer: "Kior-B"
wave: "Wave 1"
depends_on: ["T-FE-01"]
estimated_minutes: 45

input:
  description: "输出 Dashboard 页面规格书，确保其是治理总控台而非 BI 大屏"
  context_files:
    - path: "docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md"
      purpose: "Dashboard 骨架与模块"
    - path: "docs/2026-03-12/verification/T-FE-01_ia_spec.md"
      purpose: "IA 与页面角色边界"
  guard_refs:
    - "docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md"
    - "docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md"

output:
  deliverables:
    - path: "docs/2026-03-12/verification/T-FE-02_dashboard_spec.md"
      type: "新建"
      schema_ref: "page spec"
  constraints:
    - "必须输出页面目标 / 页面骨架 / 模块优先级 / CTA / 空状态 / 禁止展示项"
    - "必须强化 Run Audit / Review Gaps / Issue Permit / View Audit Trail"
    - "不得把 Dashboard 做成炫图表 BI 大屏"

deny:
  - "不得把 Generate / Build / Create 做成主 CTA"
  - "不得把生成动作放到 Dashboard 的最高视觉权重"

gate:
  manual_checks:
    - "是否先看状态，再看风险，再看可执行动作"
    - "是否保留 8 Gate / Priority Queue / Evidence Coverage / Permit Events / Revision Watch"

compliance:
  required: true
  attestation_path: "docs/2026-03-12/verification/T-FE-02_compliance_attestation.json"
  permit_required_for_side_effects: false
```

---

## T-FE-03

```yaml
task_id: "T-FE-03"
executor: "Antigravity-1"
reviewer: "vs--cc2"
compliance_officer: "Kior-C"
wave: "Wave 1"
depends_on: ["T-FE-01"]
estimated_minutes: 50

input:
  description: "输出 Audit Detail 页面规格书，确保结论 -> 原因 -> 证据 -> 修复 顺序成立"
  context_files:
    - path: "docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md"
      purpose: "Audit Detail 骨架与模块"
    - path: "docs/2026-03-12/verification/T-FE-01_ia_spec.md"
      purpose: "IA 与页面角色边界"
  guard_refs:
    - "docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md"
    - "docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md"

output:
  deliverables:
    - path: "docs/2026-03-12/verification/T-FE-03_audit_detail_spec.md"
      type: "新建"
      schema_ref: "page spec"
  constraints:
    - "必须输出 Decision Header / Decision Summary / 8 Gate / EvidenceRef / Red Lines / Fixable Gaps / Hash / Footer CTA"
    - "必须保留三权分立边界展示"
    - "必须明确绝对禁止前端呈现区"

deny:
  - "不得把 Evidence / Rule / Gate / Gap 混成一锅"
  - "不得把内部异常栈、模块名、调用拓扑带到用户可见层"

gate:
  manual_checks:
    - "是否先结论后细节"
    - "是否明确红线与可修复项分离"
    - "是否保留 EvidenceRef 的 visible / summary-only / restricted 语义"

compliance:
  required: true
  attestation_path: "docs/2026-03-12/verification/T-FE-03_compliance_attestation.json"
  permit_required_for_side_effects: false
```

---

## T-FE-04

```yaml
task_id: "T-FE-04"
executor: "Kior-B"
reviewer: "Antigravity-2"
compliance_officer: "vs--cc3"
wave: "Wave 1"
depends_on: ["T-FE-01"]
estimated_minutes: 45

input:
  description: "输出 Permit 页面规格书，确保其是正式放行凭证而不是 success page"
  context_files:
    - path: "docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md"
      purpose: "Permit 骨架与模块"
    - path: "docs/2026-03-12/verification/T-FE-01_ia_spec.md"
      purpose: "IA 与页面角色边界"
  guard_refs:
    - "docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md"
    - "docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md"

output:
  deliverables:
    - path: "docs/2026-03-12/verification/T-FE-04_permit_spec.md"
      type: "新建"
      schema_ref: "page spec"
  constraints:
    - "必须输出 Permit Header / Core Decision Block / Scope / Conditions / Linked Basis / Lifecycle / Signature / Residual Risk"
    - "必须突出 Audit pass is not release approval. Permit is."
    - "必须绑定 revision / contract_hash / decision_hash / audit basis"

deny:
  - "不得把 Permit 页面做成大绿勾成功页"
  - "不得出现与 revision / hash 解耦的 Permit"

gate:
  manual_checks:
    - "是否体现放行范围、附加条件、失效触发器"
    - "是否体现生命周期与签发角色"

compliance:
  required: true
  attestation_path: "docs/2026-03-12/verification/T-FE-04_compliance_attestation.json"
  permit_required_for_side_effects: false
```

---

## T-FE-05

```yaml
task_id: "T-FE-05"
executor: "vs--cc2"
reviewer: "Antigravity-1"
compliance_officer: "Kior-C"
wave: "Wave 2"
depends_on: ["T-FE-02", "T-FE-03", "T-FE-04"]
estimated_minutes: 60

input:
  description: "将三页规格映射为组件树、数据边界、共享组件与状态机"
  context_files:
    - path: "docs/2026-03-12/verification/T-FE-02_dashboard_spec.md"
      purpose: "Dashboard 规格"
    - path: "docs/2026-03-12/verification/T-FE-03_audit_detail_spec.md"
      purpose: "Audit Detail 规格"
    - path: "docs/2026-03-12/verification/T-FE-04_permit_spec.md"
      purpose: "Permit 规格"
  guard_refs:
    - "docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md"
    - "docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md"

output:
  deliverables:
    - path: "docs/2026-03-12/verification/T-FE-05_frontend_mapping.md"
      type: "新建"
      schema_ref: "frontend mapping"
  constraints:
    - "必须逐页输出组件树、字段需求、禁止字段"
    - "必须单列共享组件：状态标签 / Hash 展示 / EvidenceRef / 三权分立 / Permit Header / Footer Action Bar"
    - "必须明确哪些字段只能后端裁剪后返回"

deny:
  - "不得让前端接收 threshold / weight / internal topology"
  - "不得通过前端角色判断隐藏敏感字段"

gate:
  manual_checks:
    - "是否明确 Never-in-DOM 字段清单"
    - "是否明确 API 层而非前端层进行权限裁剪"

compliance:
  required: true
  attestation_path: "docs/2026-03-12/verification/T-FE-05_compliance_attestation.json"
  permit_required_for_side_effects: false
```

---

## T-FE-06

```yaml
task_id: "T-FE-06"
executor: "Kior-A"
reviewer: "vs--cc1"
compliance_officer: "Antigravity-2"
wave: "Wave 2"
depends_on: ["T-FE-05"]
estimated_minutes: 45

input:
  description: "输出权限裁剪与禁止前端呈现区的专门设计文档"
  context_files:
    - path: "docs/2026-03-12/verification/T-FE-05_frontend_mapping.md"
      purpose: "组件与数据边界映射"
    - path: "docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md"
      purpose: "四层信息分层模型与禁止前端呈现区"
  guard_refs:
    - "docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md"
    - "docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md"

output:
  deliverables:
    - path: "docs/2026-03-12/verification/T-FE-06_visibility_and_permission_matrix.md"
      type: "新建"
      schema_ref: "permission matrix"
  constraints:
    - "必须输出 Layer 0/1/2/3 可见性矩阵"
    - "必须输出 Never-in-DOM 清单"
    - "必须输出 API payload 裁剪责任归属"

deny:
  - "不得允许任何敏感机制信息进入前端响应"

gate:
  manual_checks:
    - "是否能直接作为前后端接口约束文档使用"

compliance:
  required: true
  attestation_path: "docs/2026-03-12/verification/T-FE-06_compliance_attestation.json"
  permit_required_for_side_effects: false
```

---

## T-FE-07

```yaml
task_id: "T-FE-07"
executor: "vs--cc3"
reviewer: "Kior-B"
compliance_officer: "Kior-C"
wave: "Wave 2"
depends_on: ["T-FE-02", "T-FE-03", "T-FE-04"]
estimated_minutes: 40

input:
  description: "统一首页叙事、应用内 CTA 语言与页面文案禁用词"
  context_files:
    - path: "docs/2026-03-12/“治理与放行中枢”的前端设计.md"
      purpose: "首页 / 导航 / CTA 方向"
    - path: "docs/2026-03-12/Dashboard-Audit Detail-Permit 三页文字线框图.md"
      purpose: "三页主链与统一语义"
  guard_refs:
    - "docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md"
    - "docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md"

output:
  deliverables:
    - path: "docs/2026-03-12/verification/T-FE-07_copy_and_cta_spec.md"
      type: "新建"
      schema_ref: "copy spec"
  constraints:
    - "必须输出首页 headline / subheadline / CTA / 场景区 / 禁用词"
    - "必须输出应用内 CTA 语言规范"
    - "必须明确 Audit pass != Permit granted"

deny:
  - "不得使用 Build / Create / Generate Now 作为首页主 CTA"
  - "不得使用 magic / instant / one-click 叙事"

gate:
  manual_checks:
    - "是否已经从 builder 叙事切换到治理叙事"
    - "是否明确首页讲价值，应用内讲状态与裁决"

compliance:
  required: true
  attestation_path: "docs/2026-03-12/verification/T-FE-07_compliance_attestation.json"
  permit_required_for_side_effects: false
```

---

## 9. Review Agent 提示词（统一）

```text
你是本波次前端治理重构任务的 Review Agent。

任务范围：
- T-FE-01
- T-FE-02
- T-FE-03
- T-FE-04
- T-FE-05
- T-FE-06
- T-FE-07

你只做审查，不做执行。

审查重点：
1. 是否滑回 builder / canvas / marketplace 叙事
2. 是否破坏 Dashboard / Audit Detail / Permit 三页主链
3. 是否把审计通过混同于 Permit 放行
4. 是否让结论 -> 原因 -> 证据 -> 修复 顺序失真
5. 是否遗漏三权分立、EvidenceRef、Hash、Revision、Permit 绑定关系
6. 是否存在空泛方案，没有形成可执行规格

对每个任务分别输出：
- task_id
- decision: ALLOW / REQUIRES_CHANGES / DENY
- reasons
- evidence_refs
- required_changes
```

---

## 10. Compliance Agent 提示词（统一）

```text
你是本波次前端治理重构任务的 Compliance Agent。

任务范围：
- T-FE-01
- T-FE-02
- T-FE-03
- T-FE-04
- T-FE-05
- T-FE-06
- T-FE-07

你按 B Guard 与前端信息安全原则做硬拦截。

硬规则：
1. 不得暴露规则阈值、算法权重、探针逻辑、执行拓扑
2. 不得把敏感信息全量下发给前端后再隐藏
3. 不得把 Permit 与 revision / hash / audit basis 解耦
4. 不得把内部异常栈、模块名、调用链带到用户可见层
5. 不得出现“审计通过即发布通过”的语言

对每个任务分别输出：
- task_id
- decision: PASS / FAIL
- violations
- evidence_refs
- required_changes

只要出现任何可被逆向核心机制的字段设计，直接 FAIL。
```

---

## 11. Final Gate 提示词

```text
你是本批次前端治理重构的主控官，任务范围：
- T-FE-01
- T-FE-02
- T-FE-03
- T-FE-04
- T-FE-05
- T-FE-06
- T-FE-07

请汇总以下文件并做最终裁决：
- docs/2026-03-12/verification/T-FE-01_execution_report.yaml
- docs/2026-03-12/verification/T-FE-01_gate_decision.json
- docs/2026-03-12/verification/T-FE-01_compliance_attestation.json
- docs/2026-03-12/verification/T-FE-02_execution_report.yaml
- docs/2026-03-12/verification/T-FE-02_gate_decision.json
- docs/2026-03-12/verification/T-FE-02_compliance_attestation.json
- docs/2026-03-12/verification/T-FE-03_execution_report.yaml
- docs/2026-03-12/verification/T-FE-03_gate_decision.json
- docs/2026-03-12/verification/T-FE-03_compliance_attestation.json
- docs/2026-03-12/verification/T-FE-04_execution_report.yaml
- docs/2026-03-12/verification/T-FE-04_gate_decision.json
- docs/2026-03-12/verification/T-FE-04_compliance_attestation.json
- docs/2026-03-12/verification/T-FE-05_execution_report.yaml
- docs/2026-03-12/verification/T-FE-05_gate_decision.json
- docs/2026-03-12/verification/T-FE-05_compliance_attestation.json
- docs/2026-03-12/verification/T-FE-06_execution_report.yaml
- docs/2026-03-12/verification/T-FE-06_gate_decision.json
- docs/2026-03-12/verification/T-FE-06_compliance_attestation.json
- docs/2026-03-12/verification/T-FE-07_execution_report.yaml
- docs/2026-03-12/verification/T-FE-07_gate_decision.json
- docs/2026-03-12/verification/T-FE-07_compliance_attestation.json

裁决规则：
- 任一任务缺少三权记录 -> DENY
- 任一任务 compliance != PASS -> REQUIRES_CHANGES
- 任一任务仍存在 builder-first / mechanism leakage 风险 -> REQUIRES_CHANGES
- 全部满足 -> ALLOW

输出：
- docs/2026-03-12/verification/final_gate_decision.json
```

---

## 12. 产物目录

本批次产物目录固定为：

```text
docs/2026-03-12/
├── 前端重构_AI军团任务分发单_v2.md
└── verification/
    ├── T-FE-01_execution_report.yaml
    ├── T-FE-01_gate_decision.json
    ├── T-FE-01_compliance_attestation.json
    ├── T-FE-02_execution_report.yaml
    ├── T-FE-02_gate_decision.json
    ├── T-FE-02_compliance_attestation.json
    ├── T-FE-03_execution_report.yaml
    ├── T-FE-03_gate_decision.json
    ├── T-FE-03_compliance_attestation.json
    ├── T-FE-04_execution_report.yaml
    ├── T-FE-04_gate_decision.json
    ├── T-FE-04_compliance_attestation.json
    ├── T-FE-05_execution_report.yaml
    ├── T-FE-05_gate_decision.json
    ├── T-FE-05_compliance_attestation.json
    ├── T-FE-06_execution_report.yaml
    ├── T-FE-06_gate_decision.json
    ├── T-FE-06_compliance_attestation.json
    ├── T-FE-07_execution_report.yaml
    ├── T-FE-07_gate_decision.json
    ├── T-FE-07_compliance_attestation.json
    └── final_gate_decision.json
```

---

## 13. 一句话执行口令

没有 `Compliance PASS`、没有 `EvidenceRef`、没有三权记录完整性，就不执行、不通过、不结案。
