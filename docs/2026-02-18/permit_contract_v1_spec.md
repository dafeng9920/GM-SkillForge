# Permit Contract v1 规格说明

> **版本**: 1.0.0
> **创建时间**: 2026-02-18
> **作者**: CC-Code
> **状态**: DRAFT
> **schema_hash**: TBD_SHA256（待合同冻结后回填）

---

## 1. 契约目的与边界

### 1.1 目的

本契约定义 `permit`（发布许可证）的数据结构、校验规则和 Fail-Closed 机制，确保：

1. **无 permit 不可发布**：任何发布动作必须持有有效 permit
2. **Fail-Closed**：permit 缺失/过期/签名无效/作用域不匹配一律拒绝
3. **可审计**：permit 签发与校验都可追溯到 EvidenceRef
4. **确定性**：permit 绑定 repo_url + commit_sha + at_time + run_id

### 1.2 边界

| 在边界内 | 在边界外 |
|----------|----------|
| Permit 数据结构定义 | Permit 签发服务实现 |
| 校验规则定义 | 签名密钥管理 |
| Fail-Closed 规则定义 | UI/CLI 交互 |
| 状态映射定义 | 外部系统集成 |
| Evidence 绑定定义 | 数据库存储方案 |

### 1.3 与现有系统的关系

```
┌─────────────────────────────────────────────────────────────┐
│                     SkillForge Gate Pipeline                │
├─────────────────────────────────────────────────────────────┤
│  G1 → G2 → ... → G8 → final_gate_decision                   │
│                          ↓                                  │
│            ┌─────────────────────────┐                      │
│            │  PASSED_NO_PERMIT?      │                      │
│            └─────────────────────────┘                      │
│                    ↓ Yes                ↓ No (REJECTED)     │
│            ┌─────────────────────────┐                      │
│            │  Permit 签发请求        │                      │
│            │  (需要 permit_contract) │                      │
│            └─────────────────────────┘                      │
│                    ↓                                         │
│            ┌─────────────────────────┐                      │
│            │  Permit 校验            │                      │
│            │  (本契约定义)           │                      │
│            └─────────────────────────┘                      │
│                    ↓                                         │
│        ┌───────────────────────────────────┐                │
│        │  release_allowed = true/false     │                │
│        └───────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. 字段解释

### 2.1 顶层字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `permit_id` | string | ✅ | Permit 唯一标识，格式 `PERMIT-{YYYYMMDD}-{SEQ}` |
| `issuer` | object | ✅ | 签发者信息 |
| `issued_at` | ISO8601 | ✅ | 签发时间（UTC） |
| `expires_at` | ISO8601 | ✅ | 过期时间（UTC） |
| `subject` | object | ✅ | 绑定主体 |
| `scope` | object | ✅ | 作用域 |
| `constraints` | object | ✅ | 约束条件 |
| `decision_binding` | object | ✅ | 决策绑定 |
| `signature` | object | ✅ | 签名信息 |
| `revocation` | object | ✅ | 撤销状态 |

### 2.2 issuer（签发者）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `issuer_id` | string | ✅ | 签发者标识（如 `skillforge-permit-service`） |
| `issuer_type` | enum | ✅ | 签发者类型：`SYSTEM` / `HUMAN_APPROVER` / `AUTOMATED_GATE` |

### 2.3 subject（绑定主体）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `repo_url` | string | ✅ | 目标仓库 URL |
| `commit_sha` | string | ✅ | Git commit SHA（完整 40 位） |
| `run_id` | string | ✅ | 执行 ID（如 `RUN-20260218-001`） |
| `intent_id` | string | ✅ | 意图 ID（如 `generate_skill_from_repo`） |
| `entry_path` | string | ❌ | 入口文件路径（可选） |

**说明**: 这四个字段构成 permit 的"确定性绑定"，确保 permit 不可跨任务复用。

### 2.4 scope（作用域）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `allowed_actions` | array | ✅ | 允许的动作列表（如 `["release"]`） |
| `environment` | enum | ✅ | 目标环境：`development` / `staging` / `production` |
| `gate_profile` | string | ✅ | Gate 配置版本（如 `batch2_8gate`） |

### 2.5 constraints（约束条件）

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `at_time` | ISO8601 | ✅ | - | 时间锚点，确保确定性回放 |
| `max_release_count` | integer | ❌ | 1 | 最大发布次数 |
| `time_window_seconds` | integer | ❌ | 3600 | 有效时间窗口（秒） |

### 2.6 decision_binding（决策绑定）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `final_gate_decision` | enum | ✅ | Gate 决策结果 |
| `gate_count` | integer | ✅ | 执行的 Gate 数量 |
| `audit_pack_ref` | string | ✅ | AuditPack 引用（如 `audit-10465f76`） |
| `evidence_count` | integer | ✅ | EvidenceRef 数量 |

**说明**: 将 permit 与 Gate 执行结果绑定，确保 permit 不是凭空产生。

### 2.7 signature（签名）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `algo` | enum | ✅ | 签名算法：`RS256` / `ES256` / `HS256` |
| `value` | string | ✅ | 签名值（Base64 编码） |
| `key_id` | string | ✅ | 签名密钥标识 |
| `signed_at` | ISO8601 | ✅ | 签名时间 |

**说明**: 签名覆盖除 `signature` 和 `revocation` 外的所有字段。

### 2.8 revocation（撤销状态）

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `revoked` | boolean | ✅ | false | 是否已撤销 |
| `revoked_at` | ISO8601 | ❌ | - | 撤销时间（仅 `revoked=true` 时有效） |
| `revoked_by` | string | ❌ | - | 撤销者标识 |
| `reason` | string | ❌ | - | 撤销原因 |

---

## 3. 校验流程

### 3.1 Step-by-step 流程

```
输入: permit_token, execution_context

Step 1: 存在性检查
  if permit_token == null OR permit_token == '':
    return BLOCKED(PERMIT_REQUIRED)

Step 2: 解析 Permit
  permit = parse(permit_token)
  if parse_failed:
    return BLOCKED(PERMIT_INVALID)

Step 3: 必填字段检查
  for field in required_fields:
    if permit[field] == null:
      return BLOCKED(PERMIT_INVALID)

Step 4: 签名校验
  if !verify_signature(permit):
    return BLOCKED(PERMIT_INVALID)

Step 5: 过期检查
  if current_time > permit.expires_at:
    return BLOCKED(PERMIT_EXPIRED)

Step 6: 主体匹配检查
  if permit.subject.repo_url != execution_context.repo_url:
    return BLOCKED(PERMIT_SUBJECT_MISMATCH)
  if permit.subject.commit_sha != execution_context.commit_sha:
    return BLOCKED(PERMIT_SUBJECT_MISMATCH)
  if permit.subject.run_id != execution_context.run_id:
    return BLOCKED(PERMIT_SUBJECT_MISMATCH)

Step 7: 作用域匹配检查
  if requested_action NOT IN permit.scope.allowed_actions:
    return BLOCKED(PERMIT_SCOPE_MISMATCH)

Step 8: 撤销检查
  if permit.revocation.revoked == true:
    return BLOCKED(PERMIT_REVOKED)

Step 9: 生成 Evidence
  evidence_ref = generate_validation_evidence(permit, result)

Step 10: 返回结果
  return VALID(release_allowed=true, evidence_refs=[evidence_ref])
```

### 3.2 校验顺序原则

1. **先快后慢**：存在性检查最先，签名校验靠后（计算成本高）
2. **Fail-Closed**：任一检查失败立即返回，不继续后续检查
3. **可追溯**：每步检查都记录 EvidenceRef

---

## 4. 失败码表（7项）

| 错误码 | 含义 | 触发条件 | release_blocked_by |
|--------|------|----------|-------------------|
| `E001` | 缺少 Permit | `permit_token == null` | `PERMIT_REQUIRED` |
| `E002` | Permit 格式无效 | JSON 解析失败 / 必填字段缺失 | `PERMIT_INVALID` |
| `E003` | 签名无效 | 签名校验失败 / 算法不支持 | `PERMIT_INVALID` |
| `E004` | Permit 已过期 | `current_time > expires_at` | `PERMIT_EXPIRED` |
| `E005` | 作用域不匹配 | `action NOT IN allowed_actions` | `PERMIT_SCOPE_MISMATCH` |
| `E006` | 主体不匹配 | `repo_url/commit_sha/run_id` 不一致 | `PERMIT_SUBJECT_MISMATCH` |
| `E007` | Permit 已撤销 | `revoked == true` | `PERMIT_REVOKED` |

---

## 5. 与现有 Gate/AuditPack 的连接点

### 5.1 Gate 连接

| Gate | 连接点 |
|------|--------|
| `pack_audit_and_publish` | 从 `final_gate_decision` 判断是否需要 permit |
| `pack_audit_and_publish` | 校验 permit 并设置 `release_allowed` |
| 任意 Gate | 校验失败时记录 EvidenceRef |

### 5.2 AuditPack 连接

| AuditPack 字段 | Permit 连接 |
|---------------|-------------|
| `audit_id` | 被 `decision_binding.audit_pack_ref` 引用 |
| `evidence` | 包含 permit 校验 EvidenceRef |
| `gate_decisions` | 包含 `final_gate_decision` |

### 5.3 Evidence 绑定

**Permit 签发时**:
```yaml
evidence_refs:
  - gate_decision_evidence: "ev-final-decision"
  - audit_pack_evidence: "ev-audit-pack"
  - subject_verification_evidence: "ev-subject-match"
```

**Permit 校验时**:
```yaml
evidence_refs:
  - permit_token_evidence: "ev-permit-token"
  - signature_verification_evidence: "ev-sig-verify"
  - subject_match_evidence: "ev-subject-match"
```

---

## 6. 与 PASSED_NO_PERMIT 状态的关系

### 6.1 状态转换图

```
                    ┌─────────────────┐
                    │ Gate 执行完成    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ final_gate_     │
                    │ decision = ?    │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
   ┌─────▼─────┐       ┌─────▼─────┐       ┌─────▼─────┐
   │  REJECTED │       │  PASSED   │       │ REQUIRE_  │
   │           │       │ _NO_PERMIT│       │   HITL    │
   └───────────┘       └─────┬─────┘       └───────────┘
         │                   │                   │
         │            ┌──────▼──────┐            │
         │            │ 申请 Permit │            │
         │            └──────┬──────┘            │
         │                   │                   │
         │            ┌──────▼──────┐            │
         │            │ Permit 校验 │            │
         │            └──────┬──────┘            │
         │                   │                   │
         │     ┌─────────────┼─────────────┐     │
         │     │             │             │     │
         │ ┌───▼───┐   ┌─────▼─────┐ ┌─────▼───┐ │
         │ │ VALID │   │  INVALID  │ │ EXPIRED │ │
         │ └───┬───┘   └───────────┘ └─────────┘ │
         │     │                                   │
         │ ┌───▼───────────┐                       │
         │ │ PASSED_WITH_  │                       │
         │ │    PERMIT     │                       │
         │ │ release=true  │                       │
         │ └───────────────┘                       │
         │                                           │
   ┌─────▼─────────────────────────────────────────────▼─────┐
   │ release_allowed = false                                  │
   └──────────────────────────────────────────────────────────┘
```

### 6.2 状态映射表

| gate_decision | permit_status | release_allowed | release_blocked_by | 最终状态 |
|---------------|---------------|-----------------|-------------------|---------|
| `PASSED_NO_PERMIT` | MISSING | false | `PERMIT_REQUIRED` | 等待 permit |
| `PASSED_NO_PERMIT` | VALID | true | null | `PASSED_WITH_PERMIT` |
| `PASSED_NO_PERMIT` | INVALID | false | `PERMIT_INVALID` | 阻止 |
| `PASSED_NO_PERMIT` | EXPIRED | false | `PERMIT_EXPIRED` | 阻止 |
| `REJECTED` | N/A | false | `GATE_REJECTED` | 阻止 |
| `REQUIRE_HITL` | N/A | false | `REQUIRE_HITL` | 等待审核 |

### 6.3 关键约束

1. **`PASSED_NO_PERMIT` 不能直接发布**
   - 必须先获取有效 permit
   - permit 校验通过后状态变为 `PASSED_WITH_PERMIT`

2. **permit 只能签发给 `PASSED_NO_PERMIT`**
   - `REJECTED` 和 `REQUIRE_HITL` 不能签发 permit
   - 这是硬约束，不是软性建议

3. **release_allowed 由 permit 驱动**
   - 即使 Gate 全过，无 permit 则 `release_allowed=false`
   - 只有 permit 校验通过时 `release_allowed=true`

---

## 7. 时间格式规范

所有时间字段使用 **ISO8601 UTC 格式**，必须带 `Z` 后缀：

```
正确: 2026-02-18T12:00:00Z
错误: 2026-02-18T12:00:00    (缺少 Z)
错误: 2026-02-18 12:00:00    (格式不对)
错误: 2026-02-18T20:00:00+08:00  (非 UTC)
```

---

## 8. schema_hash 回填说明

`schema_hash` 当前值为 `TBD_SHA256`，回填时机：

1. **冻结条件**：本契约经至少一次真实 permit 签发验证通过
2. **计算方式**：对 `permit_schema` 完整内容计算 SHA256
3. **回填位置**：`permit_contract_v1.yml` 的 `schema_hash` 字段
4. **版本锁定**：回填后不可修改 schema，需升级版本号

---

## 9. 参考资料

- [first_skill_run_sheet_mean_reversion_v1.md](first_skill_run_sheet_mean_reversion_v1.md)
- [first_skill_mean_reversion_run_report.md](first_skill_mean_reversion_run_report.md)
- [batch2_closing_fix_report_v1.md](batch2_closing_fix_report_v1.md)
- [permit_contract_v1.yml](contracts/permit_contract_v1.yml)

---

*Generated by CC-Code | Permit Contract v1 | 2026-02-18*
