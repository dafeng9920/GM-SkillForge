# HANDOFF_INTERFACES_v1

## 1. 目的

本文件定义当前系统的 4 个正式合拢点：

1. `candidate handoff`
2. `validation handoff`
3. `review handoff`
4. `release / audit handoff`

本文件只定义接口边界，不改冻结文档正文，不改正式写口。

---

## 2. Candidate Handoff

### 2.1 作用

生成线把候选产物正式移交给下游验证与治理链。

### 2.2 输入对象

- `IntentDraft`
- `ContractBundle`
- `CandidateSkill`
- `BuildValidationReport`
- 可选：`ProductionRecord`

### 2.3 输出对象

- `governance_candidate_ref`
- `candidate_handoff_record`

### 2.4 触发条件

必须同时满足：

- `ContractBundle` 已生成
- `CandidateSkill` 已生成
- `BuildValidationReport.handoff_ready = true`
- 无 `BLOCKER` 级 build 问题

### 2.5 允许写者

- 生成线中的 `delivery_service`
- 受控的 `state-manager`（仅写 handoff 运行态）

### 2.6 禁止写者

- `nl--skill`
- `skill-creator`
- `orchestrator / n8n`
- `gate-engine`
- 任意 skill 本体

### 2.7 失败返回

统一返回：

```json
{
  "handoff_stage": "candidate_handoff",
  "status": "failed",
  "code": "CANDIDATE_HANDOFF_FAILED",
  "reason": "string",
  "blocking_items": ["string"],
  "next_action": "fix_candidate_and_retry"
}
```

---

## 3. Validation Handoff

### 3.1 作用

治理线接管候选产物，执行正式 validation / gate 前置验证。

### 3.2 输入对象

- `CandidateSkill`
- `ContractBundle`
- `BuildValidationReport`
- `EvidenceRef[]`（最小草案或创建侧证据）

### 3.3 输出对象

- `ValidationReport`
- `validated | validation_failed`

### 3.4 触发条件

必须同时满足：

- 已完成 `candidate handoff`
- 输入对象可解析
- 必要 schema 存在
- 候选物未被标记为 rejected / broken

### 3.5 允许写者

- `validator`

### 3.6 禁止写者

- `nl--skill`
- `contract-builder`
- `skill-compiler`
- `skill-creator`
- `orchestrator / n8n`

### 3.7 失败返回

统一返回：

```json
{
  "handoff_stage": "validation_handoff",
  "status": "failed",
  "code": "VALIDATION_FAILED",
  "reason": "string",
  "validation_errors": ["string"],
  "next_action": "return_to_generation_line"
}
```

---

## 4. Review Handoff

### 4.1 作用

治理线把关键对象送入 Review / Owner Review 流程。

### 4.2 输入对象

- `Validated Candidate`
- `GateResult`
- `EvidenceRef[]`
- 可选：`AuditPack Draft`

### 4.3 输出对象

- `ReviewRecord`
- `manual_approval`
- `review_decision`

### 4.4 触发条件

满足其一即可：

- 命中需要人工复核的 gate 规则
- 命中高风险或高影响对象
- 发布前要求 Owner Review

### 4.5 允许写者

- `admin-review-console`
- 受审计约束的人工审批模块

### 4.6 禁止写者

- `nl--skill`
- `skill-creator`
- `orchestrator / n8n`
- 任意 workflow 节点

### 4.7 失败返回

统一返回：

```json
{
  "handoff_stage": "review_handoff",
  "status": "failed",
  "code": "REVIEW_NOT_GRANTED",
  "reason": "string",
  "review_record_required": true,
  "next_action": "manual_review_required"
}
```

---

## 5. Release / Audit Handoff

### 5.1 作用

治理线完成最终裁决，并产出正式发布结果与最小审计交付。

### 5.2 输入对象

- `Validated Candidate`
- `GateResult`
- `ReviewRecord`（若要求 review）
- `EvidenceRef[]`
- `AuditPack Draft`

### 5.3 输出对象

- `ReleaseDecision`
- `ReleaseRecord`
- `released | rejected | revised | tombstoned`
- `AuditPack`

### 5.4 触发条件

必须同时满足：

- validation 已通过
- gate 结果存在
- evidence 完整
- 若要求 review，则 review 已完成

### 5.5 允许写者

- `release-manager`
- 特定生命周期场景下的 `revision-manager`
- `evidence-collector`（仅写 `AuditPack`，不写 release decision）

### 5.6 禁止写者

- `nl--skill`
- `skill-creator`
- `orchestrator / n8n`
- `validator`
- `gate-engine`（只能写 gate result，不能写 release）

### 5.7 失败返回

统一返回：

```json
{
  "handoff_stage": "release_audit_handoff",
  "status": "failed",
  "code": "RELEASE_NOT_GRANTED",
  "reason": "string",
  "gate_result": "fail | blocked | incomplete",
  "evidence_complete": false,
  "next_action": "fix_and_resubmit_or_reject"
}
```

---

## 6. 四个 Handoff 的边界总表

| Handoff | 上游结束点 | 下游接管点 | 最终允许写者 | 明确禁止写者 |
| --- | --- | --- | --- | --- |
| candidate handoff | 生成线 | 治理线前置接收 | `delivery_service` / `state-manager` | `nl--skill` / `skill-creator` / `n8n` |
| validation handoff | candidate 已交付 | `validator` | `validator` | 生成线所有模块 / `skill-creator` / `n8n` |
| review handoff | validation / gate 已完成 | `admin-review-console` | `admin-review-console` | `nl--skill` / `skill-creator` / `n8n` |
| release / audit handoff | review 结束或无需 review | `release-manager` / `evidence-collector` | `release-manager` / `revision-manager` / `evidence-collector(AuditPack only)` | `nl--skill` / `skill-creator` / `n8n` / workflow |

---

## 7. 明确禁止的越权路径

- `nl--skill -> released`
- `nl--skill -> validated`
- `skill-creator -> released`
- `skill-creator -> gate_result`
- `orchestrator / n8n -> released`
- `orchestrator / n8n -> final decision`
- `BuildValidation -> governance pass`
- `workflow node finished -> business success`

---

## 8. 当前使用口径

当前系统的合拢方式固定为：

- 生成线到 `DeliveryManifest` 结束
- 治理线从 `candidate / validation handoff` 接管
- 打包层只处理封装与交付
- 编排层只处理调度与流程组织

本文件只做接口定义，不授予任何新增越权写口。
