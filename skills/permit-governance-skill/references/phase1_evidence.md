# Phase-1 验收证据引用

> **版本**: v1.1.0
> **更新时间**: 2026-02-18

---

## 1. 运行记录

| 字段 | 值 |
|------|-----|
| run_id | `RUN-20260218-BIZ-PHASE1-001` |
| permit_id | `PERMIT-20260218-BIZ-PHASE1-001` |
| replay_pointer | `REPLAY-20260218-BIZ-PHASE1-001-SHA-m1n2o3p4` |
| audit_pack_ref | `audit-10465f76` |

---

## 2. 签发结果 (Issue)

| 指标 | 值 | EvidenceRef |
|------|-----|-------------|
| success | `true` | `EV-PHASE1-A-PERMIT` |
| permit_token | `eyJhbGciOiJSUzI1NiIs...` | `EV-PHASE1-A-TOKEN` |
| key_id | `KEY-2026-PRIMARY` | `EV-PHASE1-A-KEY` |
| issued_at | `2026-02-18T17:00:05Z` | `EV-PHASE1-A-ISSUED` |
| expires_at | `2026-02-19T05:00:05Z` | `EV-PHASE1-A-EXPIRES` |
| ttl_seconds | `43200` | - |
| issuance_latency | `95ms` | `EV-PHASE1-A-LATENCY` |

---

## 3. 校验结果 (Validate)

| 检查项 | 结果 | EvidenceRef |
|--------|------|-------------|
| permit_id 存在 | ✅ VALID | `EV-PHASE1-A-CHK-1` |
| permit 签名有效 | ✅ VALID | `EV-PHASE1-A-CHK-2` |
| permit 未过期 | ✅ VALID | `EV-PHASE1-A-CHK-3` |
| permit 匹配 intent_id | ✅ VALID | `EV-PHASE1-A-CHK-4` |
| release_allowed | ✅ `true` | `EV-PHASE1-A-CHK-5` |

---

## 4. Fail-Closed 验证

### 4.1 E001 阻断验证

| 场景 | 预期 | 实际 | 结果 |
|------|------|------|------|
| 无 permit 发布 | 阻断 | 阻断 | ✅ PASS |
| EvidenceRef | 完整 | `EV-PHASE1-B-E001` | ✅ |

**输出快照**:
```json
{
  "gate_decision": "BLOCK",
  "release_allowed": false,
  "release_blocked_by": "PERMIT_REQUIRED",
  "error_code": "E001"
}
```

### 4.2 E003 阻断验证

| 场景 | 预期 | 实际 | 结果 |
|------|------|------|------|
| 签名异常发布 | 阻断 | 阻断 | ✅ PASS |
| EvidenceRef | 完整 | `EV-PHASE1-B-E003` | ✅ |

**输出快照**:
```json
{
  "gate_decision": "BLOCK",
  "release_allowed": false,
  "release_blocked_by": "PERMIT_INVALID",
  "error_code": "E003"
}
```

---

## 5. 关联报告

| 类型 | 报告路径 |
|------|----------|
| 执行报告 | [business_phase1_execution_report_v1.md](../../../docs/2026-02-18/business_phase1_execution_report_v1.md) |
| 验收报告 | [business_phase1_acceptance_report_v1.md](../../../docs/2026-02-18/business_phase1_acceptance_report_v1.md) |
| 治理链联调 | [business_phase1_governance_linkage_report_v1.md](../../../docs/2026-02-18/business_phase1_governance_linkage_report_v1.md) |
| GatePermit 实现 | [permit_gate_implementation_report_v1.md](../../../docs/2026-02-18/permit_gate_implementation_report_v1.md) |
| PermitIssuer 实现 | [permit_issuer_implementation_report_v1.md](../../../docs/2026-02-18/permit_issuer_implementation_report_v1.md) |
| 契约文件 | [permit_contract_v1_spec.md](../../../docs/2026-02-18/permit_contract_v1_spec.md) |

---

## 6. 最小验证步骤

### 6.1 正常路径

```bash
# 1. 签发
python -m skillforge.src.skills.gates.permit_issuer \
  --signing-key "test-key" \
  --final-decision "PASSED" \
  --audit-pack-ref "audit-test" \
  --repo-url "github.com/test/repo" \
  --commit-sha "abc123..." \
  --run-id "RUN-TEST-001" \
  --intent-id "test" \
  --ttl 3600 \
  --output permit.json

# 2. 验签
python -m skillforge.src.skills.gates.gate_permit \
  --permit-file permit.json \
  --repo-url "github.com/test/repo" \
  --commit-sha "abc123..." \
  --run-id "RUN-TEST-001"

# 预期: release_allowed=true, exit_code=0
```

### 6.2 E001 验证

```bash
python -m skillforge.src.skills.gates.gate_permit \
  --repo-url "github.com/test/repo" \
  --commit-sha "abc123..." \
  --run-id "RUN-TEST-001"

# 预期: error_code=E001, release_allowed=false, exit_code=1
```

### 6.3 E003 验证

```bash
# 使用无效签名的 permit
python -m skillforge.src.skills.gates.gate_permit \
  --permit-file bad_permit.json \
  --repo-url "github.com/test/repo" \
  --commit-sha "abc123..." \
  --run-id "RUN-TEST-001"

# 预期: error_code=E003, release_allowed=false, exit_code=1
```

---

*文档版本: v1.1.0 | 更新时间: 2026-02-18*
