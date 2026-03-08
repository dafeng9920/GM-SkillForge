# Permit Contract v1 验收清单

> **版本**: 1.0.0
> **创建时间**: 2026-02-18
> **关联契约**: `docs/2026-02-18/contracts/permit_contract_v1.yml`

---

## 验收说明

本清单用于验证 `permit_contract_v1` 的正确性与完整性。每项测试需：
1. 明确输入条件
2. 预期输出结果
3. EvidenceRef 记录
4. 可回放验证

---

## 1. 正常签发与校验通过

### 测试场景
Gate 全部通过后，正常签发 permit 并校验通过

### 输入条件
```yaml
final_gate_decision: PASSED_NO_PERMIT
permit_token: <valid_permit>
execution_context:
  repo_url: "https://github.com/local/NEW-GM"
  commit_sha: "4ea179d31a66fc2616f0cf953cd0e5c5c43d8ea8"
  run_id: "RUN-20260218-001"
  requested_action: "release"
```

### 预期输出
```yaml
permit_validation_status: VALID
release_allowed: true
release_blocked_by: null
evidence_refs: ["ev-permit-valid-xxx"]
```

### 验收标准
- [ ] `permit_validation_status` = `VALID`
- [ ] `release_allowed` = `true`
- [ ] `release_blocked_by` = `null`
- [ ] 生成 `permit_validation_evidence` EvidenceRef

---

## 2. 缺失 Permit

### 测试场景
执行上下文中无 permit_token

### 输入条件
```yaml
final_gate_decision: PASSED_NO_PERMIT
permit_token: null
```

### 预期输出
```yaml
permit_validation_status: INVALID
release_allowed: false
release_blocked_by: PERMIT_REQUIRED
error_code: E001
```

### 验收标准
- [ ] `release_allowed` = `false`
- [ ] `release_blocked_by` = `PERMIT_REQUIRED`
- [ ] 不执行后续校验（Fail-Closed 快速失败）
- [ ] 记录 EvidenceRef

---

## 3. 过期 Permit

### 测试场景
permit_token 存在但已超过 expires_at

### 输入条件
```yaml
permit_token:
  expires_at: "2026-02-18T10:00:00Z"
current_time: "2026-02-18T12:00:00Z"
```

### 预期输出
```yaml
permit_validation_status: INVALID
release_allowed: false
release_blocked_by: PERMIT_EXPIRED
error_code: E004
```

### 验收标准
- [ ] `release_allowed` = `false`
- [ ] `release_blocked_by` = `PERMIT_EXPIRED`
- [ ] 签名校验在过期检查之前（先快后慢原则）
- [ ] 记录 EvidenceRef

---

## 4. 伪造签名

### 测试场景
permit_token 签名被篡改或使用未知密钥

### 输入条件
```yaml
permit_token:
  signature:
    algo: "RS256"
    value: "TAMPERED_SIGNATURE"
    key_id: "unknown-key"
```

### 预期输出
```yaml
permit_validation_status: INVALID
release_allowed: false
release_blocked_by: PERMIT_INVALID
error_code: E003
```

### 验收标准
- [ ] `release_allowed` = `false`
- [ ] `release_blocked_by` = `PERMIT_INVALID`
- [ ] 签名校验失败立即返回
- [ ] 记录签名校验失败的 EvidenceRef

---

## 5. 作用域不匹配

### 测试场景
permit 的 allowed_actions 不包含请求的动作

### 输入条件
```yaml
permit_token:
  scope:
    allowed_actions: ["deploy"]
execution_context:
  requested_action: "release"
```

### 预期输出
```yaml
permit_validation_status: INVALID
release_allowed: false
release_blocked_by: PERMIT_SCOPE_MISMATCH
error_code: E005
```

### 验收标准
- [ ] `release_allowed` = `false`
- [ ] `release_blocked_by` = `PERMIT_SCOPE_MISMATCH`
- [ ] 精确匹配（非模糊匹配）
- [ ] 记录 EvidenceRef

---

## 6. commit_sha 不匹配

### 测试场景
permit 绑定的 commit_sha 与执行上下文不一致

### 输入条件
```yaml
permit_token:
  subject:
    commit_sha: "aaa1111111111111111111111111111111111111"
execution_context:
  commit_sha: "4ea179d31a66fc2616f0cf953cd0e5c5c43d8ea8"
```

### 预期输出
```yaml
permit_validation_status: INVALID
release_allowed: false
release_blocked_by: PERMIT_SUBJECT_MISMATCH
error_code: E006
```

### 验收标准
- [ ] `release_allowed` = `false`
- [ ] `release_blocked_by` = `PERMIT_SUBJECT_MISMATCH`
- [ ] 完整 40 位 SHA 比对（非前缀匹配）
- [ ] 记录 EvidenceRef

---

## 7. 已撤销 Permit

### 测试场景
permit 的 revocation.revoked = true

### 输入条件
```yaml
permit_token:
  revocation:
    revoked: true
    revoked_at: "2026-02-18T11:00:00Z"
    revoked_by: "security-team"
    reason: "CVE-2026-xxxx detected"
```

### 预期输出
```yaml
permit_validation_status: INVALID
release_allowed: false
release_blocked_by: PERMIT_REVOKED
error_code: E007
```

### 验收标准
- [ ] `release_allowed` = `false`
- [ ] `release_blocked_by` = `PERMIT_REVOKED`
- [ ] 撤销检查在所有检查最后
- [ ] 记录 EvidenceRef

---

## 8. release_allowed 必须为 false 的场景汇总

### 测试场景
验证所有 `release_allowed=false` 的场景

### 场景清单

| # | 场景 | release_allowed | release_blocked_by |
|---|------|-----------------|-------------------|
| 1 | permit_token = null | false | PERMIT_REQUIRED |
| 2 | permit_token = "" | false | PERMIT_REQUIRED |
| 3 | JSON 解析失败 | false | PERMIT_INVALID |
| 4 | 必填字段缺失 | false | PERMIT_INVALID |
| 5 | 签名无效 | false | PERMIT_INVALID |
| 6 | 已过期 | false | PERMIT_EXPIRED |
| 7 | repo_url 不匹配 | false | PERMIT_SUBJECT_MISMATCH |
| 8 | commit_sha 不匹配 | false | PERMIT_SUBJECT_MISMATCH |
| 9 | run_id 不匹配 | false | PERMIT_SUBJECT_MISMATCH |
| 10 | action 不在 allowed_actions | false | PERMIT_SCOPE_MISMATCH |
| 11 | revoked = true | false | PERMIT_REVOKED |
| 12 | gate_decision = REJECTED | false | GATE_REJECTED |

### 验收标准
- [ ] 所有 12 个场景 `release_allowed` = `false`
- [ ] 每个场景有对应的 `release_blocked_by` 值
- [ ] 无遗漏场景

---

## 9. EvidenceRef 完整性

### 测试场景
验证 permit 校验过程生成的 EvidenceRef

### 输入条件
正常 permit 校验流程

### 预期 EvidenceRef 结构
```yaml
evidence:
  evidence_id: "ev-permit-validation-xxx"
  evidence_type: "permit_validation"
  timestamp: "2026-02-18T12:00:00Z"
  data:
    permit_id: "PERMIT-20260218-001"
    validation_result: "VALID"
    checks_performed:
      - check: "existence"
        result: "PASS"
      - check: "signature"
        result: "PASS"
      - check: "expiry"
        result: "PASS"
      - check: "subject_match"
        result: "PASS"
      - check: "scope_match"
        result: "PASS"
      - check: "revocation"
        result: "PASS"
    release_allowed: true
  schema_hash: "sha256:xxx"
```

### 验收标准
- [ ] EvidenceRef 包含 `evidence_id`
- [ ] EvidenceRef 包含 `timestamp`（ISO8601 UTC）
- [ ] EvidenceRef 包含 `checks_performed` 列表
- [ ] 每个检查项有 `check` 和 `result`
- [ ] 最终 `release_allowed` 值明确

---

## 10. Replay 可复核性

### 测试场景
使用相同输入在任意时间点重新校验，得到相同结果

### 输入条件
```yaml
permit_token: <valid_permit>
at_time: "2026-02-18T08:41:10Z"
```

### 预期行为
1. 在任意时间点重放校验
2. 使用 `at_time` 作为时间锚点
3. 结果与首次校验一致

### 验收标准
- [ ] 校验结果可基于 `at_time` 确定性复现
- [ ] 不依赖 `current_time`（除了实时校验场景）
- [ ] EvidenceRef 可被后续审计读取
- [ ] AuditPack 包含完整 permit 校验链条

---

## 验收汇总表

| # | 测试项 | 状态 | 备注 |
|---|--------|------|------|
| 1 | 正常签发+校验通过 | ⬜ 待验证 | |
| 2 | 缺 permit | ⬜ 待验证 | |
| 3 | 过期 permit | ⬜ 待验证 | |
| 4 | 伪造签名 | ⬜ 待验证 | |
| 5 | 作用域不匹配 | ⬜ 待验证 | |
| 6 | commit_sha 不匹配 | ⬜ 待验证 | |
| 7 | 已撤销 permit | ⬜ 待验证 | |
| 8 | release_allowed=false 场景汇总 | ⬜ 待验证 | 12 个场景 |
| 9 | EvidenceRef 完整性 | ⬜ 待验证 | |
| 10 | Replay 可复核性 | ⬜ 待验证 | |

---

## 签署

| 角色 | 签署人 | 日期 | 状态 |
|------|--------|------|------|
| 契约设计 | CC-Code | 2026-02-18 | DRAFT |
| 技术审核 | ⬜ | ⬜ | ⬜ |
| 安全审核 | ⬜ | ⬜ | ⬜ |
| 最终批准 | ⬜ | ⬜ | ⬜ |

---

*Generated by CC-Code | Permit Contract v1 | 2026-02-18*
