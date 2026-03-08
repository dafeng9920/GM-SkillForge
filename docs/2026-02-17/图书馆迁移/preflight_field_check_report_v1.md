# Preflight Field Check Report v1

> **生成时间**: 2026-02-18
> **执行者**: CC-Code
> **范围**: Wave4 Batch1 - 6 个归一化文件字段完整性检查

---

## 1. 检查标准（9 个必需字段）

| # | 字段名 | 说明 |
|---|--------|------|
| 1 | `intent_id` | 意图唯一标识 |
| 2 | `summary` | 意图摘要 |
| 3 | `contract_version` | 合约版本 |
| 4 | `schema_hash` | Schema 哈希 |
| 5 | `inputs_schema` | 输入模式 |
| 6 | `required_gates` | 必需 Gate |
| 7 | `minimum_level` | 最低审计级别 |
| 8 | `required_evidence` | 必需证据 |
| 9 | `outputs` | 输出 |

---

## 2. 检查结果总览

| 文件 | 9 字段完整性 | 状态 |
|------|-------------|------|
| `contracts/intents/audit_repo.yml` | 9/9 ✅ | PASS |
| `contracts/intents/generate_skill.yml` | 9/9 ✅ | PASS |
| `contracts/intents/upgrade_skill.yml` | 9/9 ✅ | PASS |
| `contracts/intents/tombstone.yml` | 9/9 ✅ | PASS |
| `contracts/intents/time_semantics.yml` | 9/9 ✅ | PASS |
| `contracts/evidence_schema.yaml` | N/A (Schema 文件) | PASS |

---

## 3. 详细检查结果

### 3.1 audit_repo.yml

| 字段 | 存在 | 值 |
|------|------|-----|
| `intent_id` | ✅ | `audit_repo` |
| `summary` | ✅ | 扫描仓库审计日志，分析统计信息，检测异常，生成审计报告 |
| `contract_version` | ✅ | `v1` |
| `schema_hash` | ✅ | `TBD_SHA256` |
| `inputs_schema` | ✅ | repo_url, commit_sha, at_time + optional |
| `required_gates` | ✅ | intake_repo, license_gate, repo_scan_fit_score, pack_audit_and_publish |
| `minimum_level` | ✅ | `L3` |
| `required_evidence` | ✅ | 5 项 |
| `outputs` | ✅ | 9 项（含标准 3 项 + 扩展 6 项）|

**结论**: ✅ PASS - 所有 9 个标准字段完整

---

### 3.2 generate_skill.yml

| 字段 | 存在 | 值 |
|------|------|-----|
| `intent_id` | ✅ | `generate_skill` |
| `summary` | ✅ | 从自然语言需求生成技能规格说明（SkillSpec） |
| `contract_version` | ✅ | `v1.0.0` |
| `schema_hash` | ✅ | `TBD_SHA256` |
| `inputs_schema` | ✅ | repo_url, commit_sha, skill_name, skill_intent, example_inputs/outputs, tier, side_effects, policy_pack_version + optional |
| `required_gates` | ✅ | proposal_gate, build_gate, license_compatibility, tier_risk_gate |
| `minimum_level` | ✅ | `L3` |
| `required_evidence` | ✅ | 4 项 |
| `outputs` | ✅ | 9 项（含标准 3 项 + 扩展 6 项）|

**结论**: ✅ PASS - 所有 9 个标准字段完整

---

### 3.3 upgrade_skill.yml

| 字段 | 存在 | 值 |
|------|------|-----|
| `intent_id` | ✅ | `upgrade_skill` |
| `summary` | ✅ | 技能升级意图合约 - 实现 DRAFT → ACTIVE 状态升级 |
| `contract_version` | ✅ | `v1.0.0` |
| `schema_hash` | ✅ | `TBD_SHA256` |
| `inputs_schema` | ✅ | repo_url, commit_sha, skill_id, upgrade_spec + optional |
| `required_gates` | ✅ | build_gate, trace_reputation_gate, compose_gate, run_gate |
| `minimum_level` | ✅ | `L3` |
| `required_evidence` | ✅ | 5 项 |
| `outputs` | ✅ | 5 项（含标准 3 项 + 扩展 2 项）|

**结论**: ✅ PASS - 所有 9 个标准字段完整

---

### 3.4 tombstone.yml

| 字段 | 存在 | 值 |
|------|------|-----|
| `intent_id` | ✅ | `tombstone` |
| `summary` | ✅ | 废弃技能意图 - 实现 Fail-Closed 原则下的技能永久废弃机制 |
| `contract_version` | ✅ | `v1.0.0` |
| `schema_hash` | ✅ | `TBD_SHA256` |
| `inputs_schema` | ✅ | repo_url, commit_sha, skill_id, revoke_reason, revoked_by + optional |
| `required_gates` | ✅ | intake_validate, constitution_risk_gate, tombstone_write_gate, audit_chain_append, tombstone_publish |
| `minimum_level` | ✅ | `L3` |
| `required_evidence` | ✅ | 4 项 |
| `outputs` | ✅ | 6 项（含标准 3 项 + 扩展 3 项）|

**结论**: ✅ PASS - 所有 9 个标准字段完整

---

### 3.5 time_semantics.yml

| 字段 | 存在 | 值 |
|------|------|-----|
| `intent_id` | ✅ | `time_semantics` |
| `summary` | ✅ | 时间语义内核模块 - 定义 EventTime/AvailableTime/DecisionTime 核心约束 |
| `contract_version` | ✅ | `v1.0.0` |
| `schema_hash` | ✅ | `TBD_SHA256` |
| `inputs_schema` | ✅ | repo_url, commit_sha, event_time, available_time, decision_time + optional |
| `required_gates` | ✅ | time_constraint_gate, data_freshness_gate, look_ahead_prevention |
| `minimum_level` | ✅ | `L3` |
| `required_evidence` | ✅ | 3 项 |
| `outputs` | ✅ | 6 项（含标准 3 项 + 扩展 3 项）|

**结论**: ✅ PASS - 所有 9 个标准字段完整

---

### 3.6 evidence_schema.yaml

| 字段 | 存在 | 值 |
|------|------|-----|
| `schema_id` | ✅ | `evidence_schema` |
| `schema_version` | ✅ | `v1` |
| `contract_version` | ✅ | `v1.0.0` |
| `schema_hash` | ✅ | `TBD_SHA256` |
| `canonical_serialization` | ✅ | canonical_json |
| `hash_chain` | ✅ | SHA-256 |
| `evidence_types` | ✅ | 4 种 (ScanReport, TestResult, Tombstone, UpgradeManifest) |
| `ledger_record_types` | ✅ | 3 种 (TRIGGER, DECISION, EXECUTION) |

**结论**: ✅ PASS - Schema 文件结构完整

---

## 4. 扩展字段检查

### 4.1 架构边界（architecture_boundary）

| 文件 | 存在 | 状态 |
|------|------|------|
| audit_repo.yml | ✅ | PASS |
| generate_skill.yml | ✅ | PASS |
| upgrade_skill.yml | ✅ | PASS |
| tombstone.yml | ✅ | PASS |
| time_semantics.yml | ✅ | PASS |
| evidence_schema.yaml | ✅ | PASS |

### 4.2 源文档引用（source_doc_ref）

| 文件 | 存在 | 状态 |
|------|------|------|
| audit_repo.yml | ✅ | PASS |
| generate_skill.yml | ✅ | PASS |
| upgrade_skill.yml | ✅ | PASS |
| tombstone.yml | ✅ | PASS |
| time_semantics.yml | ✅ | PASS |
| evidence_schema.yaml | ✅ | PASS |

### 4.3 确定性输入（repo_url + commit_sha）

| 文件 | repo_url | commit_sha | 状态 |
|------|----------|------------|------|
| audit_repo.yml | ✅ | ✅ | PASS |
| generate_skill.yml | ✅ | ✅ | PASS |
| upgrade_skill.yml | ✅ | ✅ | PASS |
| tombstone.yml | ✅ | ✅ | PASS |
| time_semantics.yml | ✅ | ✅ | PASS |

---

## 5. 发现问题

### 5.1 schema_hash 待填充

**状态**: 低风险（预期行为）

所有 6 个文件的 `schema_hash` 均为 `TBD_SHA256`。这是预期行为，需要在 `pack_audit_and_publish` 前计算实际 SHA256 并写回。

**建议**: 在 A3 步骤明确写回策略。

---

## 6. 验收结论

| 检查项 | 结果 |
|--------|------|
| 6 个文件全部存在 | ✅ PASS |
| 每个文件包含 9 个标准字段 | ✅ PASS |
| inputs_schema 格式正确 | ✅ PASS |
| required_gates 为数组格式 | ✅ PASS |
| minimum_level 为 L3 | ✅ PASS |
| outputs 包含标准输出 | ✅ PASS |
| 扩展字段（architecture_boundary, source_doc_ref） | ✅ PASS |
| 确定性输入（repo_url + commit_sha） | ✅ PASS |

---

## 7. 放行状态

**PREFLIGHT CHECK A1: ✅ PASS**

所有 6 个归一化文件字段完整性检查通过，可进入 A2 Gate 名称对齐检查。

---

*Generated by CC-Code | Wave4 Batch1 Preflight | 2026-02-18*
