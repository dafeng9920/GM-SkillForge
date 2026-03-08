# Business Phase 1 治理链联调报告 v1

> **日期**: 2026-02-18
> **执行角色**: VSCode-2 (并行组C)
> **联调目标**: Permit 签发与验签联调成功 + AuditPack 完整引用 + replay pointer 可复核

---

## 1. 联调三元组

| 字段 | 值 |
|------|-----|
| **run_id** | `RUN-20260218-E80553A1` |
| **permit_id** | `PERMIT-20260218-DB2B2A22` |
| **replay_pointer** | `replay://RUN-20260218-E80553A1/governance_linkage_test` |

---

## 2. AuditPack 引用

```json
{
  "audit_pack_ref": "audit-8127c4e3",
  "schema_version": "1.0.0",
  "provenance": {
    "repo_url": "https://github.com/gm-skillforge/SkillForge",
    "commit_sha": "8ee2128a8b57494342467ea313a9e0b9f2d6b3d6",
    "intent_id": "governance_linkage_test"
  },
  "gate_decisions": [
    {
      "gate_name": "permit_gate",
      "gate_decision": "ALLOW",
      "permit_validation_status": "VALID",
      "release_allowed": true
    }
  ],
  "generated_at": "2026-02-18T15:02:15Z"
}
```

---

## 3. 联调测试结果

### 3.1 正常路径: permit VALID -> release_allowed=true

| 检查项 | 期望值 | 实际值 | 结果 |
|--------|--------|--------|------|
| gate_decision | ALLOW | ALLOW | ✅ PASS |
| permit_validation_status | VALID | VALID | ✅ PASS |
| release_allowed | true | true | ✅ PASS |
| error_code | null | null | ✅ PASS |

**结论**: 正常路径 **PASS**

### 3.2 失败路径A: 无 permit -> E001 -> release_allowed=false

| 检查项 | 期望值 | 实际值 | 结果 |
|--------|--------|--------|------|
| gate_decision | BLOCK | BLOCK | ✅ PASS |
| error_code | E001 | E001 | ✅ PASS |
| release_allowed | false | false | ✅ PASS |
| release_blocked_by | PERMIT_REQUIRED | PERMIT_REQUIRED | ✅ PASS |

**结论**: E001 路径 **PASS**

### 3.3 失败路径B: 签名异常 -> E003 -> release_allowed=false

| 检查项 | 期望值 | 实际值 | 结果 |
|--------|--------|--------|------|
| gate_decision | BLOCK | BLOCK | ✅ PASS |
| error_code | E003 | E003 | ✅ PASS |
| release_allowed | false | false | ✅ PASS |
| release_blocked_by | PERMIT_INVALID | PERMIT_INVALID | ✅ PASS |

**结论**: E003 路径 **PASS**

---

## 4. no-permit-no-release 约束验证

| 验证项 | 状态 |
|--------|------|
| E001 路径阻断发布 | ✅ 验证通过 |
| E003 路径阻断发布 | ✅ 验证通过 |
| 正常路径允许发布 | ✅ 验证通过 |

### 结论: **Yes** - 满足 no-permit-no-release 硬约束

---

## 5. 模块契约引用

### 5.1 GatePermit (permit_gate)

- **实现文件**: `skillforge/src/skills/gates/gate_permit.py`
- **契约文件**: `docs/2026-02-18/contracts/permit_contract_v1.yml`
- **错误码映射**:
  - E001 -> PERMIT_REQUIRED
  - E002 -> PERMIT_INVALID (格式)
  - E003 -> PERMIT_INVALID (签名)
  - E004 -> PERMIT_EXPIRED
  - E005 -> PERMIT_SCOPE_MISMATCH
  - E006 -> PERMIT_SUBJECT_MISMATCH
  - E007 -> PERMIT_REVOKED

### 5.2 PermitIssuer (permit_issuer)

- **实现文件**: `skillforge/src/skills/gates/permit_issuer.py`
- **签名算法**: HS256 (HMAC-SHA256)
- **TTL 上限**: 86400 秒 (24小时)

### 5.3 Replay API

- **实现文件**: `gm_plugin_core_seed/src/api/routes/orchestration_replay.py`
- **Endpoint**: `GET /orchestration/replay?session_id={}&turn_seq={}`
- **开关**: `GM_OS_REPLAY_ENABLED=1`

---

## 6. 回传格式汇总

```
1) run_id: RUN-20260218-E80553A1
   permit_id: PERMIT-20260218-DB2B2A22
   replay_pointer: replay://RUN-20260218-E80553A1/governance_linkage_test

2) 正常路径结果: PASS (gate_decision=ALLOW, release_allowed=true)

3) E001 结果: PASS (gate_decision=BLOCK, error_code=E001, release_allowed=false)
   E003 结果: PASS (gate_decision=BLOCK, error_code=E003, release_allowed=false)

4) AuditPack 引用: audit-8127c4e3

5) 是否满足 no-permit-no-release: Yes
```

---

## 7. 附录: 测试代码片段

```python
# Permit 签发
issuer = PermitIssuer(signing_key='skillforge-governance-test-key-2026')
issuance_result = issuer.issue_permit({
    'final_gate_decision': 'PASSED',
    'audit_pack_ref': 'audit-8127c4e3',
    'repo_url': 'https://github.com/gm-skillforge/SkillForge',
    'commit_sha': '8ee2128a8b57494342467ea313a9e0b9f2d6b3d6',
    'run_id': 'RUN-20260218-E80553A1',
    'intent_id': 'governance_linkage_test',
    'ttl_seconds': 3600,
})

# Permit 验证
gate = GatePermit()
result = gate.execute({
    'permit_token': permit_dict,
    'repo_url': repo_url,
    'commit_sha': commit_sha,
    'run_id': run_id,
    'requested_action': 'release',
})
```

---

**报告生成时间**: 2026-02-18T15:02:15Z
**报告版本**: v1
