# 基线校准报告 v1

> **版本**: v1.0
> **日期**: 2026-02-20
> **执行者**: 基线校准小队

---

## 1. 执行摘要

完成首批经验模板/基线校准，保证后续系统可自动运行。

---

## 2. 基线样本统计

| 指标 | 数值 |
|------|------|
| **entries** | 66 |
| **rejected_entries** | 19 (含 1 条测试注入) |
| **schema_version** | experience-capture-v0 |

### 2.1 Gate Node 分布

| Gate Node | Count |
|-----------|-------|
| constitution_risk_gate | 26 |
| permit_gate | 16 |
| draft_skill_spec | 14 |
| repo_scan_fit_score | 6 |
| intake_repo | 4 |

### 2.2 FixKind 分布

| FixKind | Count |
|---------|-------|
| GATE_DECISION | 52 |
| ADD_CONTRACT | 14 |

---

## 3. 落盘验证

### 3.1 文件验证

| 文件 | 路径 | 状态 |
|------|------|------|
| evolution.json | `AuditPack/experience/evolution.json` | ✅ 存在 |
| SKILL.md | `AuditPack/experience/SKILL.md` | ✅ 存在 |

### 3.2 结构验证

- [x] `evolution.json` 包含 `schema_version`
- [x] `evolution.json` 包含 `entries` 数组
- [x] `evolution.json` 包含 `rejected_entries` 数组
- [x] `SKILL.md` 包含 By Gate / By FixKind 统计

---

## 4. 检索验证

### 4.1 按 IssueKey 检索

```
Query: issue_key='SCAN-*'
Results: 3

- SCAN-20260220052203 | repo_scan_fit_score | fit score below threshold
- SCAN-20260220052203 | repo_scan_fit_score | repo scan passed with fit score 1.000
- SCAN-20260220052156 | repo_scan_fit_score | fit score below threshold
```

**状态**: ✅ PASS

### 4.2 按 FixKind 检索

```
Query: fix_kind='ADD_CONTRACT'
Results: 3

- SKILL-1771564923149 | ADD_CONTRACT | draft spec generated from scan report
- SKILL-1771564923155 | ADD_CONTRACT | draft spec generated from scan report
- SKILL-1771564923159 | ADD_CONTRACT | draft spec generated from scan report
```

**状态**: ✅ PASS

### 4.3 组合检索 (IssueKey + FixKind + GateNode)

```
Query: gate_node='permit_gate', fix_kind='GATE_DECISION'
Results: 5

- PERMIT-BLOCK-E001-xxx | permit_gate | error=E001 | Permit token is missing
- PERMIT-BLOCK-E003-xxx | permit_gate | error=E003 | Signature verification failed
- PERMIT-VAL-PERMIT-xxx | permit_gate | error=N/A | permit validation passed
- ...
```

**状态**: ✅ PASS

---

## 5. rejected_entries 验证

### 5.1 无 evidence_ref 样例注入

```python
capture.capture(
    issue_key='BASELINE-TEST-NO-EVIDENCE',
    evidence_ref=None,
    gate_node='baseline_calibration',
    summary='baseline calibration test - no evidence provided',
    fix_kind='GATE_DECISION',
)
```

**结果**:
```
Capture result: {'status': 'MISSING_EVIDENCE', 'captured': False}
```

### 5.2 验证进入 rejected_entries

| 检查项 | 结果 |
|--------|------|
| 条目进入 rejected_entries | ✅ |
| status = MISSING_EVIDENCE | ✅ |
| captured_at 有值 | ✅ |

**状态**: ✅ PASS

### 5.3 rejected_entries 统计

| 状态 | Count |
|------|-------|
| MISSING_EVIDENCE | 19 |

典型 rejected_entry 示例:

| issue_key | gate_node | status | error_code |
|-----------|-----------|--------|------------|
| INTAKE_REPO-xxx | intake_repo | MISSING_EVIDENCE | ERR_COMMIT_SHA_MISSING |
| INTAKE_REPO-xxx | intake_repo | MISSING_EVIDENCE | ERR_REPO_URL_INVALID |
| DRAFT_SKILL_SPEC-xxx | draft_skill_spec | MISSING_EVIDENCE | GATE.DRAFT_SPEC.FIT_SCORE_TOO_LOW |

---

## 6. 首批推荐模板 Top 5

供 scaffold/audit 使用:

### Rank 1: Permit Validation Success Pattern

| 字段 | 值 |
|------|------|
| IssueKey | PERMIT-VAL-PERMIT-20260218-001-1771564923 |
| FixKind | GATE_DECISION |
| GateNode | permit_gate |
| Summary | permit validation passed |
| EvidenceRef | permit://PERMIT-20260218-001 |
| Use Case | Permit 验证成功模式 |

### Rank 2: E001 Permit Missing Pattern (fail-closed)

| 字段 | 值 |
|------|------|
| IssueKey | PERMIT-BLOCK-E001-1771564923 |
| FixKind | GATE_DECISION |
| GateNode | permit_gate |
| Summary | Permit token is missing |
| EvidenceRef | permit://none |
| Use Case | E001 无 Permit 阻断模式 (fail-closed) |

### Rank 3: E003 Signature Invalid Pattern (fail-closed)

| 字段 | 值 |
|------|------|
| IssueKey | PERMIT-BLOCK-E003-1771564923 |
| FixKind | GATE_DECISION |
| GateNode | permit_gate |
| Summary | Signature verification failed |
| EvidenceRef | permit://none |
| Use Case | E003 签名无效阻断模式 (fail-closed) |

### Rank 4: Draft Skill Spec Generation Pattern

| 字段 | 值 |
|------|------|
| IssueKey | SKILL-1771564916233 |
| FixKind | ADD_CONTRACT |
| GateNode | draft_skill_spec |
| Summary | draft spec generated from scan report |
| EvidenceRef | skill_spec://SKILL-1771564916233 |
| Use Case | Skill Spec 草稿生成模式 |

### Rank 5: Constitution Risk Rejection Pattern

| 字段 | 值 |
|------|------|
| IssueKey | RISK-1771564916249 |
| FixKind | GATE_DECISION |
| GateNode | constitution_risk_gate |
| Summary | constitution risk evaluated with score 1.000 |
| EvidenceRef | risk_assessment://RISK-1771564916249 |
| Use Case | 章程风险评估阻断模式 |

---

## 7. 模板清单汇总

| Rank | IssueKey | FixKind | Summary | EvidenceRef |
|------|----------|---------|---------|-------------|
| 1 | PERMIT-VAL-PERMIT-20260218-001-1771564923 | GATE_DECISION | permit validation passed | permit://PERMIT-20260218-001 |
| 2 | PERMIT-BLOCK-E001-1771564923 | GATE_DECISION | Permit token is missing | permit://none |
| 3 | PERMIT-BLOCK-E003-1771564923 | GATE_DECISION | Signature verification failed | permit://none |
| 4 | SKILL-1771564916233 | ADD_CONTRACT | draft spec generated from scan report | skill_spec://SKILL-1771564916233 |
| 5 | RISK-1771564916249 | GATE_DECISION | constitution risk evaluated with score 1.000 | risk_assessment://RISK-1771564916249 |

---

## 8. 校验项汇总

| # | 校验项 | 状态 |
|---|--------|------|
| 1 | evolution.json 落盘 | ✅ |
| 2 | SKILL.md 落盘 | ✅ |
| 3 | 按 IssueKey 检索 | ✅ |
| 4 | 按 FixKind 检索 | ✅ |
| 5 | 组合检索 (IssueKey + FixKind + GateNode) | ✅ |
| 6 | 无 evidence_ref 进入 rejected_entries | ✅ |
| 7 | MISSING_EVIDENCE 状态正确 | ✅ |
| 8 | 推荐模板 Top 5 输出 | ✅ |

---

## 9. 结论

```yaml
BASELINE_READY: YES

reason:
  - evolution.json 和 SKILL.md 落盘验证通过
  - 三种检索方式全部验证通过
  - 无 evidence_ref 样例正确进入 rejected_entries 且状态为 MISSING_EVIDENCE
  - 首批推荐模板 Top 5 已输出，覆盖:
    - Permit 验证成功/失败模式
    - E001/E003 fail-closed 模式
    - Skill Spec 生成模式
    - 风险评估阻断模式
  - 基线样本充足 (66 entries, 19 rejected_entries)
  - Gate Node 和 FixKind 分布合理
```

---

*报告生成时间: 2026-02-20*
*执行者: 基线校准小队*
