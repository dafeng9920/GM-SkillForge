# Intent Contract Normalization Report v1

> **生成时间**: 2026-02-18
> **执行者**: CC-Code
> **范围**: P0/P1 意图合同归一化

---

## 1. 归一化标准（9 个必需字段）

| 字段 | 说明 | 旧字段映射 |
|------|------|------------|
| `intent_id` | 意图唯一标识 | `intent_name` → `intent_id` |
| `summary` | 意图摘要 | `description` / `intent_description` → `summary` |
| `contract_version` | 合约版本 | `version` / `intent_version` → `contract_version` |
| `schema_hash` | Schema 哈希 | 新增，暂填 `TBD_SHA256` |
| `inputs_schema` | 输入模式 | `input_schema` / `inputs` → `inputs_schema` |
| `required_gates` | 必需 Gate | `gates` / `pipeline` → `required_gates` |
| `minimum_level` | 最低审计级别 | `level` / `audit_level` → `minimum_level` |
| `required_evidence` | 必需证据 | `evidence` / `required_artifacts` → `required_evidence` |
| `outputs` | 输出 | `outputs_schema` / `output_schema` → `outputs` |

---

## 2. P0 合约归一化结果

### 2.1 audit_repo (A1)

| 字段 | Before | After |
|------|--------|-------|
| `intent_id` | `audit_repo` ✅ | `audit_repo` ✅ |
| `summary` | `summary` ✅ | `summary` ✅ |
| `contract_version` | `v1` ✅ | `v1` ✅ |
| `schema_hash` | `sha256:...placeholder` | `TBD_SHA256` |
| `inputs_schema` | ✅ 有 | ✅ 统一格式 |
| `required_gates` | ✅ 数组格式 | ✅ 数组格式 |
| `minimum_level` | `L3` ✅ | `L3` ✅ |
| `required_evidence` | ✅ 数组格式 | ✅ 数组格式 |
| `outputs` | `outputs_schema` ❌ | `outputs` ✅ |

**改动摘要**:
- ❌ 删除旧字段 `intent_name`
- ✅ `outputs_schema` → `outputs`
- ✅ 新增 `architecture_boundary` 说明
- ✅ 新增 `repo_url` + `commit_sha` 确定性输入

---

### 2.2 generate_skill (A2)

| 字段 | Before | After |
|------|--------|-------|
| `intent_id` | `intent_name: generate_skill` ❌ | `intent_id: generate_skill` ✅ |
| `summary` | `description` ❌ | `summary` ✅ |
| `contract_version` | `intent_version: "1.0.0"` ❌ | `contract_version: v1.0.0` ✅ |
| `schema_hash` | ❌ 缺失 | `TBD_SHA256` ✅ |
| `inputs_schema` | `input_schema` ❌ | `inputs_schema` ✅ |
| `required_gates` | `gates` (对象格式) ❌ | `required_gates` (数组) ✅ |
| `minimum_level` | ❌ 缺失 | `L3` ✅ |
| `required_evidence` | `evidence_refs` (格式不同) | `required_evidence` ✅ |
| `outputs` | `output_schema` ❌ | `outputs` ✅ |

**改动摘要**:
- ✅ `intent_name` → `intent_id`
- ✅ `description` → `summary`
- ✅ `intent_version` → `contract_version`
- ✅ 新增 `schema_hash`
- ✅ `input_schema` → `inputs_schema`
- ✅ `gates` (对象) → `required_gates` (数组)
- ✅ 新增 `minimum_level: L3`
- ✅ `output_schema` → `outputs`

---

### 2.3 upgrade_skill (A3)

| 字段 | Before | After |
|------|--------|-------|
| `intent_id` | `intent_name: upgrade_skill` ❌ | `intent_id: upgrade_skill` ✅ |
| `summary` | `description` ❌ | `summary` ✅ |
| `contract_version` | ❌ 缺失 | `v1.0.0` ✅ |
| `schema_hash` | ❌ 缺失 | `TBD_SHA256` ✅ |
| `inputs_schema` | `input_schema` ❌ | `inputs_schema` ✅ |
| `required_gates` | ❌ 缺失 | ✅ Gate 链定义 |
| `minimum_level` | ❌ 缺失 | `L3` ✅ |
| `required_evidence` | ❌ 缺失 | ✅ 定义 |
| `outputs` | `output_schema` ❌ | `outputs` ✅ |

**改动摘要**:
- ✅ `intent_name` → `intent_id`
- ✅ `description` → `summary`
- ✅ 新增 `contract_version`
- ✅ 新增 `schema_hash`
- ✅ `input_schema` → `inputs_schema`
- ✅ 新增 `required_gates` (B1 → B3 → B2a → B2b)
- ✅ 新增 `minimum_level: L3`
- ✅ 新增 `required_evidence`
- ✅ `output_schema` → `outputs`

---

### 2.4 tombstone (A4)

| 字段 | Before | After |
|------|--------|-------|
| `intent_id` | `tombstone` ✅ | `tombstone` ✅ |
| `summary` | ✅ 有 | ✅ 统一格式 |
| `contract_version` | `"0.1.0"` ✅ | `v1.0.0` ✅ |
| `schema_hash` | ✅ 有 | `TBD_SHA256` ✅ |
| `inputs_schema` | ✅ 有 | ✅ 统一格式 |
| `required_gates` | ✅ 数组格式 | ✅ 数组格式 |
| `minimum_level` | `L3` ✅ | `L3` ✅ |
| `required_evidence` | ✅ 有 | ✅ 统一格式 |
| `outputs` | `outputs_schema` ❌ | `outputs` ✅ |

**改动摘要**:
- ❌ 删除旧字段 `intent_name`
- ✅ `outputs_schema` → `outputs`
- ✅ 新增 `architecture_boundary` 说明

---

## 3. P1 合约归一化结果

### 3.1 time_semantics (A9)

| 字段 | Before | After |
|------|--------|-------|
| `intent_id` | `intent_name: time_manager` ❌ | `intent_id: time_semantics` ✅ |
| `summary` | ❌ 缺失 | ✅ 新增 |
| `contract_version` | ❌ 缺失 | `v1.0.0` ✅ |
| `schema_hash` | ❌ 缺失 | `TBD_SHA256` ✅ |
| `inputs_schema` | ❌ 缺失 | ✅ 新增 |
| `required_gates` | ❌ 缺失 | ✅ 新增 |
| `minimum_level` | ❌ 缺失 | `L3` ✅ |
| `required_evidence` | ❌ 缺失 | ✅ 新增 |
| `outputs` | ❌ 缺失 | ✅ 新增 |

**改动摘要**:
- ✅ `intent_name` → `intent_id`
- ✅ 新增所有 9 个标准字段
- ✅ 保留 `core_concepts`, `invariant`, `use_cases` 扩展字段

---

## 4. Evidence Schema 归一化结果

| 字段 | Before | After |
|------|--------|-------|
| `schema_id` | ❌ 缺失 | `evidence_schema` ✅ |
| `schema_version` | `v1` ✅ | `v1` ✅ |
| `contract_version` | ❌ 缺失 | `v1.0.0` ✅ |
| `schema_hash` | ❌ 缺失 | `TBD_SHA256` ✅ |
| Evidence Types | 3 个 | 4 个 (新增 UpgradeManifest) |

**改动摘要**:
- ✅ 新增 `schema_id`, `contract_version`, `schema_hash`
- ✅ 每个 Evidence Type 新增 `minimum_level`, `required_gates`, `outputs`
- ✅ 新增 `UpgradeManifest` 类型

---

## 5. Deferred 项目（延期处理）

| Intent | 优先级 | 延期原因 |
|--------|--------|----------|
| `trend_following` | 非核心 | 策略类，待 Batch 2 处理 |
| `mean_reversion` | 非核心 | 策略类，待 Batch 2 处理 |
| `multi_factor` | 非核心 | 策略类，待 Batch 2 处理 |

**处理策略**: 保留原文件，待 Wave 4 Batch 2 时按统一标准归一化。

---

## 6. 字段映射统计

| 旧字段 | 出现次数 | 新字段 |
|--------|----------|--------|
| `intent_name` | 3 | `intent_id` |
| `description` | 2 | `summary` |
| `intent_version` / `version` | 2 | `contract_version` |
| `input_schema` | 3 | `inputs_schema` |
| `output_schema` / `outputs_schema` | 4 | `outputs` |
| `gates` (对象格式) | 1 | `required_gates` (数组格式) |

---

## 7. 新增统一内容

所有归一化合约均包含以下新增内容：

### 7.1 确定性输入（所有 P0/P1）
```yaml
inputs_schema:
  required:
    - name: repo_url
      type: string
      pattern: "^(https?|git)://.+$"
    - name: commit_sha
      type: string
      pattern: "^[a-f0-9]{7,40}$"
```

### 7.2 架构边界说明（所有 P0/P1）
```yaml
architecture_boundary: |
  - n8n 仅作为 Orchestrator（触发/路由/通知），不做最终裁决
  - SkillForge 是 Governor（Gate 判定、Evidence 产出、AuditPack 固化）
  - 输入确定性：repo_url + commit_sha (+ at_time)
  - 无 permit 不允许发布/打 tag/release
```

### 7.3 标准输出（所有 P0/P1）
```yaml
outputs:
  - name: audit_pack_ref
    type: string
    description: "L3 AuditPack 引用标识"
  - name: gate_decision
    type: string
    enum: ["ALLOW", "DENY", "REQUIRE_HITL"]
    description: "Gate 最终决策"
  - name: revision
    type: integer
    description: "合约版本号"
```

---

## 8. 验收检查清单

- [x] P0/P1 每个 intent 都包含 9 个标准字段
- [x] 无 intent 继续使用 `intent_name`/`input_schema`/`outputs_schema` 等旧字段
- [x] 每个 P0/P1 intent 都能看出 `required_gates` + `required_evidence` + `outputs` 三段闭环
- [x] 报告中明确列出 deferred 项与原因
- [x] 全文不出现"复制旧代码/直接复用旧实现"的建议

---

## 9. 修改文件清单

| 文件路径 | 状态 |
|----------|------|
| `contracts/intents/audit_repo.yml` | ✅ 已归一化 |
| `contracts/intents/generate_skill.yml` | ✅ 已归一化 |
| `contracts/intents/upgrade_skill.yml` | ✅ 已归一化 |
| `contracts/intents/tombstone.yml` | ✅ 已归一化 |
| `contracts/intents/time_semantics.yml` | ✅ 已归一化 |
| `contracts/evidence_schema.yaml` | ✅ 已归一化 |
| `contracts/intents/trend_following.yml` | 📋 Deferred |
| `contracts/intents/mean_reversion.yml` | 📋 Deferred |
| `contracts/intents/multi_factor.yml` | 📋 Deferred |

---

*Generated by CC-Code | 2026-02-18*
