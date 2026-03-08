# Wave 4 Batch 1 Execution Entry v1

> **生成时间**: 2026-02-18
> **执行阶段**: Wave 4 Batch 1
> **状态**: 🟢 就绪执行

---

## 1. 架构边界（必须遵守）

```
┌─────────────────────────────────────────────────────────────────┐
│                         n8n (Orchestrator)                       │
│  职责: 触发 / 路由 / 通知                                        │
│  禁止: 最终裁决 / Evidence 产出 / AuditPack 固化                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SkillForge (Governor)                         │
│  职责: Gate 判定 / Evidence 产出 / AuditPack 固化                │
│  输入确定性: repo_url + commit_sha (+ at_time)                   │
│  约束: 无 permit 不允许发布/打 tag/release                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 执行顺序（按依赖关系）

### Phase 1: 基础设施（必须先完成）

| 顺序 | Intent | 优先级 | 原因 |
|------|--------|--------|------|
| 1 | `evidence_schema` | P0 | 全局证据契约，其他 intent 依赖 |
| 2 | `time_semantics` | P1 | Kernel 级别，被 RAG/Backtest 依赖 |

### Phase 2: 核心技能（顺序执行）

| 顺序 | Intent | 优先级 | Gate 链 | 原因 |
|------|--------|--------|---------|------|
| 3 | `audit_repo` | P0 | intake → license → scan_fit → audit_publish | 审计基础 |
| 4 | `generate_skill` | P0 | proposal → build → license → tier_risk | 技能生成 |
| 5 | `upgrade_skill` | P0 | build → trace → compose → run | 技能升级 |
| 6 | `tombstone` | P0 | intake → constitution → write → audit → publish | 废弃管理 |

### Phase 3: 策略类（Batch 2）

| 顺序 | Intent | 优先级 | 状态 |
|------|--------|--------|------|
| - | `trend_following` | 非核心 | Deferred |
| - | `mean_reversion` | 非核心 | Deferred |
| - | `multi_factor` | 非核心 | Deferred |

---

## 3. 执行流程图

```
Phase 1: 基础设施
┌─────────────────┐     ┌─────────────────┐
│ evidence_schema │ ──▶ │ time_semantics  │
│     (P0)        │     │      (P1)       │
└─────────────────┘     └─────────────────┘
         │                      │
         └──────────┬───────────┘
                    ▼
Phase 2: 核心技能
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   audit_repo    │ ──▶ │ generate_skill  │ ──▶ │ upgrade_skill   │ ──▶ │    tombstone    │
│      (P0)       │     │       (P0)      │     │       (P0)      │     │       (P0)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## 4. 每个 Intent 的执行步骤

### 4.1 contracts → gates → skills 执行模板

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Contract 验证                                        │
│ - 验证 9 个标准字段存在                                       │
│ - 验证 inputs_schema 格式正确                                │
│ - 验证 source_doc_ref 存在                                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Gate 实现                                            │
│ - 按 required_gates 列表实现每个 Gate                        │
│ - 每个 Gate 必须输出 ALLOW/DENY/REQUIRE_HITL                 │
│ - Gate 结果写入 evidence_ref                                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Skill 实现                                           │
│ - 按 intent 语义实现核心逻辑                                  │
│ - 产出 required_evidence 列表中的所有证据                     │
│ - 产出标准 outputs (audit_pack_ref, gate_decision, revision) │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 4: AuditPack 固化                                       │
│ - 生成 L3 AuditPack                                          │
│ - 写入 hash chain                                            │
│ - 返回 audit_pack_ref                                        │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 具体执行清单

#### evidence_schema (Phase 1 - Step 1)

| 步骤 | 动作 | 输出 |
|------|------|------|
| 1.1 | 验证 4 种 Evidence Types | Schema 定义 |
| 1.2 | 实现 `schema_validation` Gate | Gate 函数 |
| 1.3 | 实现 Hash Chain 逻辑 | Hash Chain 模块 |
| 1.4 | 生成 L3 AuditPack | audit_pack_ref |

#### time_semantics (Phase 1 - Step 2)

| 步骤 | 动作 | 输出 |
|------|------|------|
| 2.1 | 实现 `validate_time_constraint()` | 函数 |
| 2.2 | 实现 `filter_by_availability()` | 函数 |
| 2.3 | 实现 `check_data_freshness()` | 函数 |
| 2.4 | 实现 3 个 Gates | Gate 函数 |

#### audit_repo (Phase 2 - Step 3)

| 步骤 | 动作 | Gate |
|------|------|------|
| 3.1 | 实现 `intake_repo` Gate | 验证 repo_url + commit_sha |
| 3.2 | 实现 `license_gate` | 许可证检查 |
| 3.3 | 实现 `repo_scan_fit_score` Gate | 扫描适配度 |
| 3.4 | 实现 `pack_audit_and_publish` Gate | 审计发布 |
| 3.5 | 实现核心扫描逻辑 | Skill 主体 |

#### generate_skill (Phase 2 - Step 4)

| 步骤 | 动作 | Gate |
|------|------|------|
| 4.1 | 实现 `proposal_gate` | 请求完整性 |
| 4.2 | 实现 `build_gate` | 构建资格 |
| 4.3 | 实现 `license_compatibility` Gate | 许可证兼容 |
| 4.4 | 实现 `tier_risk_gate` | 风险等级 |
| 4.5 | 实现技能生成逻辑 | Skill 主体 |

#### upgrade_skill (Phase 2 - Step 5)

| 步骤 | 动作 | Gate |
|------|------|------|
| 5.1 | 实现 `build_gate` | B1 |
| 5.2 | 实现 `trace_reputation_gate` | B3 |
| 5.3 | 实现 `compose_gate` | B2a |
| 5.4 | 实现 `run_gate` | B2b |
| 5.5 | 实现 revision 自增逻辑 | Skill 主体 |
| 5.6 | 实现 evolution.json append | 持久化 |

#### tombstone (Phase 2 - Step 6)

| 步骤 | 动作 | Gate |
|------|------|------|
| 6.1 | 实现 `intake_validate` Gate | 输入验证 |
| 6.2 | 实现 `constitution_risk_gate` | 宪法风险 |
| 6.3 | 实现 `tombstone_write_gate` | 废弃写入 |
| 6.4 | 实现 `audit_chain_append` Gate | 审计链追加 |
| 6.5 | 实现 `tombstone_publish` Gate | 废弃发布 |
| 6.6 | 实现 Fail-Closed 逻辑 | Skill 主体 |

---

## 5. 验收标准（每个 Intent）

执行完成后必须满足：

| 检查项 | 要求 |
|--------|------|
| 9 个标准字段 | 全部存在且格式正确 |
| Gate 链 | 全部实现，输出 ALLOW/DENY/REQUIRE_HITL |
| Evidence | 产出 required_evidence 列表中所有证据 |
| Outputs | 包含 audit_pack_ref, gate_decision, revision |
| AuditPack | L3 级别，写入 hash chain |
| source_doc_ref | 包含 NEW-GM 源文件引用 |

---

## 6. 输入确定性约束

所有 Intent 必须接受以下确定性输入：

```yaml
inputs_schema:
  required:
    - name: repo_url
      type: string
      pattern: "^(https?|git)://.+$"
      description: "仓库 URL（确定性输入）"

    - name: commit_sha
      type: string
      pattern: "^[a-f0-9]{7,40}$"
      description: "Git commit SHA（确定性输入）"
```

**禁止**：无 repo_url 或无 commit_sha 的输入。

---

## 7. Permit 约束

以下操作必须有 permit 才能执行：

| 操作 | Permit 要求 |
|------|-------------|
| 发布技能 | permit: publish |
| 打 tag | permit: tag |
| Release | permit: release |
| 废弃技能 | permit: tombstone |

**禁止**：无 permit 执行上述操作。

---

## 8. 文档引用

| 文档 | 路径 |
|------|------|
| 归一化报告 | `intent_contract_normalization_report_v1.md` |
| Evidence Schema | `contracts/evidence_schema.yaml` |
| audit_repo 合约 | `contracts/intents/audit_repo.yml` |
| generate_skill 合约 | `contracts/intents/generate_skill.yml` |
| upgrade_skill 合约 | `contracts/intents/upgrade_skill.yml` |
| tombstone 合约 | `contracts/intents/tombstone.yml` |
| time_semantics 合约 | `contracts/intents/time_semantics.yml` |

---

## 9. schema_hash 替换策略（A3）

### 9.1 何时计算 SHA256

**触发时机**: `pack_audit_and_publish` Gate 执行前

```
┌─────────────────────────────────────────────────────────────┐
│ pack_audit_and_publish Gate                                 │
│                                                             │
│ Step 1: 收集所有 Evidence                                   │
│ Step 2: 序列化为 Canonical JSON                             │
│ Step 3: 计算 SHA256 → schema_hash                           │
│ Step 4: 写回 intent contract                                │
│ Step 5: 生成 AuditPack                                      │
│ Step 6: 返回 audit_pack_ref                                 │
└─────────────────────────────────────────────────────────────┘
```

### 9.2 谁写回

**责任人**: Pack Builder（`pack_audit_and_publish` 内部模块）

```python
# 伪代码
def pack_audit_and_publish(intent_id, evidence_list):
    # 1. 序列化
    canonical_json = serialize_canonical(evidence_list)

    # 2. 计算哈希
    schema_hash = sha256(canonical_json)

    # 3. 写回合约
    write_schema_hash_to_contract(intent_id, schema_hash)

    # 4. 生成 AuditPack
    audit_pack = build_audit_pack(intent_id, evidence_list, schema_hash)

    # 5. 返回
    return audit_pack_ref
```

### 9.3 失败处理（Fail-Closed）

| 失败场景 | 处理方式 | 错误码 |
|----------|----------|--------|
| 无法计算 SHA256 | DENY，不发 permit | `SCHEMA_HASH_COMPUTE_FAILED` |
| 序列化失败 | DENY，不发 permit | `CANONICAL_SERIALIZATION_FAILED` |
| 写回合约失败 | DENY，不发 permit | `CONTRACT_WRITE_FAILED` |
| Evidence 缺失 | DENY，不发 permit | `MISSING_EVIDENCE` |

**原则**: 任何 schema_hash 计算失败 → 必须 DENY → 不发 permit

### 9.4 Canonical JSON 序列化规则

```yaml
canonical_serialization:
  format: "canonical_json"
  rules:
    - keys_sorted_alphabetically: true
    - no_whitespace_separators: true
    - timestamps: "UTC_ISO8601_Z_suffix"
    - encoding: "UTF-8"
```

### 9.5 Hash Chain 机制

```yaml
hash_chain:
  algorithm: "SHA-256"
  genesis_prev_hash: "0000000000000000000000000000000000000000000000000000000000000000"
  entry_fields:
    prev_hash: "前一条记录的 SHA256"
    hash: "当前记录的 SHA256"
```

### 9.6 实现检查清单

- [ ] 实现 `serialize_canonical()` 函数
- [ ] 实现 `compute_schema_hash()` 函数
- [ ] 实现 `write_schema_hash_to_contract()` 函数
- [ ] 集成到 `pack_audit_and_publish` Gate
- [ ] 添加 Fail-Closed 测试用例

---

## 10. 下一步行动

1. **立即执行**: Phase 1 (evidence_schema + time_semantics)
2. **顺序执行**: Phase 2 (audit_repo → generate_skill → upgrade_skill → tombstone)
3. **延期处理**: Batch 2 (trend_following, mean_reversion, multi_factor)

---

## 11. Preflight 检查状态

| 检查项 | 状态 | 报告路径 |
|--------|------|----------|
| A1: 字段完整性 | ✅ PASS | `preflight_field_check_report_v1.md` |
| A2: Gate 名称对齐 | ✅ PASS (已修正别名) | `preflight_gate_alignment_report_v1.md` |
| A3: schema_hash 策略 | ✅ DOCUMENTED | 本文档 Section 9 |

---

*Generated by CC-Code | Wave 4 Batch 1 | 2026-02-18*
