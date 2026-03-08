---
description: 多 AI 协作执行大型任务的标准流程（Skill 版 v3，三权分立 + A/B Guard）
---

# GM 多 AI 协作工作流 v3（Skill 化）

> 核心理念：**每个任务 = 一个 Skill，每次交付 = 一个 Audit Pack**
> 核心治理：**提案受 A Guard 约束，执行受 B Guard 约束，三权分立先于开发速度。**

## 0. 强制对齐文档（Single Source of Truth）

本流程必须同时遵守以下文档，冲突时按顺序优先：
1. `docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md`
2. `docs/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md`
3. 本文档 `multi-ai-collaboration.md`

关键口径：
- 无 `ComplianceAttestation(PASS)` 不执行。
- 需要副作用动作时，无 `permit=VALID` 不执行。
- 无 `EvidenceRef` 不算完成。

## 适用场景
- 大型功能开发（预计 > 2 小时）
- 需要前后端/多模块协作
- 有明确交付物和验收标准

---

## 1. 三权分立（MUST）

每个任务必须存在三种独立权力，不得混同：
- `Execution`（执行权）：只按合同实施改动，无放行权。
- `Review`（审查权）：检查质量与边界，可打回，无执行权。
- `Compliance`（合规权）：按 B Guard 做硬拦截，有一票否决权。

执行顺序固定为：
1. Review 完成审查意见（不放行）
2. Compliance 产出 `ComplianceAttestation`
3. 仅当 `Compliance=PASS` 时，Execution 才能执行

缺失任一角色记录，任务直接 `DENY`。

---

## 1.1 执行模式（Mode）

调度单必须声明 `mode`，仅允许以下两种：

1. `strict`（默认）
- 逐任务执行 `Review -> Compliance -> Execution`
- 适合高风险、破坏性、副作用明显的任务
- 优先保证风险可控与早发现

2. `batch-fastlane`
- 先批量 `Execution`（同波次并行）  
- 再批量 `Review`（同波次一次审查）  
- 最后批量 `Compliance`（同波次一次合规收尾）
- 适合中低风险、标准化、同构任务批处理

`batch-fastlane` 硬约束：
1. 任务书必须包含统一 DoD 与统一证据模板。
2. 任一任务被 Review 判定 `DENY/REQUIRES_CHANGES`，该波次统一回滚到修复队列。
3. 发现高风险动作（Shell/File delete/DB/Network）时，自动降级回 `strict`。
4. Final Gate 仍按三权记录完整性裁决，不可放宽。

---

## 2. 参与角色

### 主控官（Orchestrator）
- **Codex/主控官**：方案设计、Task Skill Spec 生成、三权分立编排、Final Gate 验收
- **用户**：提出需求、最终决策、分发任务书给执行者

### 执行者名单（8 人）

| 执行者 | IDE | 擅长领域 | 适合任务类型 |
|--------|-----|----------|-------------|
| **vs--cc1** | VSCode | 数据层、存储、CI/CD | Schema / DB / 配置文件 |
| **vs--cc2** | VSCode | 工具封装、适配器 | Adapter / 工具类 / 桥接 |
| **vs--cc3** | VSCode | 核心逻辑、API | 编排器 / 复杂业务模块 |
| **Kior-A** | Kior | 集成、胶水代码 | 跨模块桥接 / 格式转换 |
| **Kior-B** | Kior | 外部对接 | 第三方 API / n8n / webhook |
| **Kior-C** | Kior | 测试、文档、验收 | 端到端示例 / 测试 / 文档 |
| **Antigravity-1** | Antigravity | 核心编排、主链路实现 | Orchestrator / DAG / Gate 主流程 |
| **Antigravity-2** | Antigravity | 合同与策略治理 | Schema / Policy / Guard 集成 |

### 任务分配策略

> 原则：分散分配、职责隔离、先合规后执行。

1. 并行任务分给不同执行者，最大化并行度。
2. Review 与 Execution 不可为同一执行者。
3. Compliance 不参与具体代码实现。
4. 主控官负责编排与验收，不替代执行者提交代码。
5. 三个 IDE（VSCode / Kior / Antigravity）应尽量交叉分配，避免单 IDE 成为瓶颈。

---

## 3. 六步流程（Skill 化 + Guard）

### Step 1. 需求对齐（用户 ↔ 主控官）
- 用户描述需求
- 主控官提问澄清
- 产出：需求理解文档

### Step 2. A Guard 提案生成（主控官）
- 严格输出三段：`PreflightChecklist / ExecutionContract / RequiredChanges`
- 未通过 A Guard 约束，不得进入任务分派
- 产出：`task_dispatch.md` + `tasks/T{N}_{executor}.md`

### Step 3. Review 审查（审查者）
- 审查任务合同完整性、边界、验收映射、deny list
- 输出：审查意见与需要补充项（不放行）

### Step 4. B Guard 合规复查（合规者）
- 按 B Guard 对执行前条件做硬校验
- 输出：`ComplianceAttestation`（PASS/FAIL + EvidenceRef）
- FAIL 时只能输出 `RequiredChanges`，不得执行

### Step 5. Execution 执行（执行者）
- 仅在 `Compliance=PASS` 且（需要时）`permit=VALID` 执行
- 执行完成后提交 `ExecutionReport + EvidenceRef`

### Step 6. Final Gate 验收（主控官）
- 主控官验收所有任务及三权记录
- 输出最终裁决：`ALLOW | REQUIRES_CHANGES | DENY`
- 产出：`verification/final_gate_decision.json`

---

## 4. Task Skill Spec（任务书 Schema，v3）

每个任务书必须包含以下结构（新增三权角色与合规要求）：

```yaml
task_id: "T{N}"
executor: "{执行者名}"
reviewer: "{审查者名}"
compliance_officer: "{合规者名}"
wave: "Wave {X}"
depends_on: ["T{N-1}"]
estimated_minutes: 30

input:
  description: "一句话描述目标"
  context_files:
    - path: "schemas/xxx.schema.json"
      purpose: "理解目标 Schema 结构"
  constants:
    job_id: "550e8400-..."
    skill_id: "tech_seo_audit"
  guard_refs:
    - "docs/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md"
    - "docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md"

output:
  deliverables:
    - path: "path/to/file.json"
      type: "新建|修改"
      schema_ref: "schemas/xxx.schema.json"
  constraints:
    - "pytest -q 必须全绿"
    - "不得修改现有 schema 文件"
    - "无 EvidenceRef 不得宣称完成"

deny:
  - "不得引入新依赖"
  - "不得修改其他执行者的文件"
  - "不得绕过 Compliance PASS 直接执行"

gate:
  auto_checks:
    - command: "pytest -q"
      expect: "passed"
    - command: "python tools/validate.py --all"
      expect: "0 失败"
  manual_checks:
    - "数据流端到端贯通"

compliance:
  required: true
  attestation_path: "docs/{date}/verification/T{N}_compliance_attestation.json"
  permit_required_for_side_effects: true
```

---

## 5. ComplianceAttestation（MUST）

```yaml
task_id: "T{N}"
compliance_officer: "{合规者名}"
decision: "PASS|FAIL"
reasons:
  - "string"
evidence_refs:
  - id: "EV-..."
    kind: "LOG|FILE|DIFF|SNIPPET|URL"
    locator: "path:line or URL"
contract_hash: "sha256:..."
reviewed_at: "2026-02-22T10:00:00Z"
required_changes:
  - issue_key: "SF_..."
    reason: "string"
    next_action: "string"
```

若 `decision=FAIL`，Execution 阶段必须阻断。

---

## 6. Execution Report（执行者汇报 Schema）

执行者完成任务后，必须按以下格式汇报：

```yaml
task_id: "T{N}"
executor: "{执行者名}"
status: "完成|部分完成|阻塞"

# 交付物清单
deliverables:
  - path: "path/to/file.json"
    action: "新建|修改"
    lines_changed: 120

# Gate 自检结果（执行者先跑一遍）
gate_self_check:
  - command: "pytest -q"
    result: "24 passed"
  - command: "python tools/validate.py --all"
    result: "24 passed, 0 failed"

# 备注
notes: "如有特殊情况说明"
```

---

## 7. Quality Gate 裁决

主控官验收后输出 Gate Decision：

| decision | 含义 | 后续动作 |
|----------|------|---------|
| `ALLOW` | 通过 | 任务关闭，触发下游任务 |
| `REQUIRES_CHANGES` | 需修改 | 返回修改清单，执行者修复后重新提交 |
| `DENY` | 拒绝 | 任务作废，需主控官重新设计 |

### 裁决依据

1. 交付物齐全：`output.deliverables` 均存在。
2. Schema 合规：满足 `schema_ref`。
3. Gate Check 全绿：自动化检查通过。
4. 三权记录完整：每个任务有 `review + compliance + execution` 证据。
5. 合规先行：无 `Compliance PASS` 不得出现执行动作证据。
6. 副作用放行：需 permit 的任务必须有 `permit=VALID` 证据。

---

## 8. 文档结构（新增合规产物）

```
docs/{日期}/
├── action_plan.md
├── task_dispatch.md
├── tasks/
│   ├── T1_{执行者}.md
│   ├── T2_{执行者}.md
│   └── ...
└── verification/
    ├── T1_execution_report.yaml
    ├── T1_gate_decision.json
    ├── T1_compliance_attestation.json
    ├── ...
    └── final_gate_decision.json
```

---

## 9. 进度跟踪（含三权状态）

主控官维护进度看板（在 `task_dispatch.md` 中）：

| 波次 | 任务 | Execution | Review | Compliance | 状态 | Gate Decision |
|------|------|-----------|--------|------------|------|---------------|
| Wave 1 | T1 | vs--cc1 | vs--cc2 | Kior-C | ALLOW | ALLOW |
| Wave 1 | T2 | vs--cc3 | Kior-A | Kior-B | 执行中 | - |
| Wave 2 | T3 | Kior-A | vs--cc1 | Kior-C | 待启动 | - |

状态标记：待启动 | 审查中 | 合规中 | 执行中 | 已提交 | ALLOW | REQUIRES_CHANGES | DENY

---

## 10. 一句话执行口令（全员必须遵守）

没有 `Compliance PASS`、没有（需要时）`permit VALID`、没有 `EvidenceRef`，就不执行、不通过、不结案。

---

## 11. 附录 A：给 Agent 的提示词模板（可直接复制）

以下模板中的 `[]` 必须由主控官填写后再发送。

### 11.1 给 Execution Agent（执行者）

```text
你是任务 [task_id] 的执行者 [executor_name]。

请阅读并严格执行：
- [task_file_path]
- docs/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md
- docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md
- docs/[date]/verification/REPORT_TEMPLATES.md

执行约束：
1) 仅允许修改任务书中 output.deliverables 指定的文件。
2) 不得越权改动其他任务文件。
3) 无 EvidenceRef 不得宣称完成。
4) 完成后写入：
   - docs/[date]/verification/[task_id]_execution_report.yaml
5) 如阻塞，必须写清 required_changes 与证据。

完成后回复：
- 已写入文件路径
- gate_self_check 摘要
- 需要 reviewer/compliance 处理的项
```

### 11.2 给 Review Agent（审查者）

```text
你是任务 [task_id] 的审查者 [reviewer_name]。

请审查以下输入：
- [task_file_path]
- docs/[date]/verification/[task_id]_execution_report.yaml
- docs/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md

审查要求：
1) 检查 deliverables 是否齐全且未越权。
2) 检查 gate_self_check 是否与任务 gate 对齐。
3) 检查是否存在“无证据宣称完成”。
4) 输出 GateDecision 到：
   - docs/[date]/verification/[task_id]_gate_decision.json
5) decision 仅可为 ALLOW / REQUIRES_CHANGES / DENY。

回复格式：
- decision
- reasons
- evidence_refs
```

### 11.3 给 Compliance Agent（合规者）

```text
你是任务 [task_id] 的合规官 [compliance_officer_name]。

请按 B Guard 严格复查：
- [task_file_path]
- docs/[date]/verification/[task_id]_execution_report.yaml
- docs/[date]/verification/[task_id]_gate_decision.json
- docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md

硬规则：
1) 无 Compliance PASS 不得执行放行。
2) 需要副作用动作时，无 permit=VALID 直接 FAIL。
3) 无 EvidenceRef 直接 FAIL。

输出文件：
- docs/[date]/verification/[task_id]_compliance_attestation.json

decision 仅可为 PASS 或 FAIL，并附 reasons/evidence_refs/contract_hash/reviewed_at。
```

### 11.4 给 Final Gate（主控官）

```text
你是本批次主控官 [orchestrator_name]，任务范围 [task_ids]。

请汇总以下文件并做最终裁决：
- docs/[date]/verification/[task_id]_execution_report.yaml
- docs/[date]/verification/[task_id]_gate_decision.json
- docs/[date]/verification/[task_id]_compliance_attestation.json

裁决规则：
- 任一任务缺少三权记录 -> DENY
- 任一任务 compliance != PASS -> REQUIRES_CHANGES
- 全部满足 -> ALLOW

输出：
- docs/[date]/verification/final_gate_decision.json
```

---

## 12. 附录 B：依赖顺序模板（每次任务都要填）

### 12.1 任务依赖表模板

```markdown
| Wave | Task | Execution | Review | Compliance | Depends On | 状态 |
|---|---|---|---|---|---|---|
| [Wave 1] | [Txx] | [name] | [name] | [name] | [-] | [待启动] |
| [Wave 1] | [Txx] | [name] | [name] | [name] | [[Txx]] | [待启动] |
| [Wave 2] | [Txx] | [name] | [name] | [name] | [[Txx,Tyy]] | [待启动] |
```

### 12.2 放行顺序模板

```text
Wave 1 放行条件：
- [Txx] == ALLOW
- [Tyy] == ALLOW

Wave 2 放行条件：
- [Taa] == ALLOW
- [Tbb] == ALLOW

Final Gate 条件：
- 所有任务 execution_report + gate_decision + compliance_attestation 齐全
- 所有 compliance_attestation.decision == PASS
```

### 12.3 DAG 口径（避免反复问“谁先做”）

```text
前置规则：
1) 未满足 depends_on 的任务不得启动。
2) 同一 Wave 内，无依赖冲突的任务可以并行。
3) 后置任务必须等待其所有依赖任务 ALLOW。
4) 任一依赖任务为 REQUIRES_CHANGES，则后置任务保持阻塞。
```

### 12.4 Fastlane 依赖模板（batch-fastlane）

```text
Wave X 执行阶段（并行）：
- Txx, Txy, Txz 并行执行并提交 execution_report

Wave X Review 阶段（汇总）：
- Reviewer 对 Txx/Txy/Txz 批量审查 -> 批量 gate_decision

Wave X Compliance 阶段（汇总）：
- Compliance 对本波次批量合规复核 -> 批量 compliance_attestation

Wave X 放行条件：
- 本波次所有任务 gate_decision == ALLOW
- 本波次所有任务 compliance_attestation.decision == PASS
```
