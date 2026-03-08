# audit_repo E2E Dry Run Report v1

> ⚠️ **Status: PLACEHOLDER (NOT EXECUTED)**
> - **Reason**: E2E dry-run not started; Gate implementation pending
> - **Exit Criteria**: 需包含 `gate_decision` + `EvidenceRef 链` + `L3 AuditPack` 才可改为 PASSED/FAILED
> - 本文档仅为占位，不代表通过验收

> **生成时间**: 2026-02-18
> **执行者**: CC-Code
> **范围**: Wave4 Batch1 - audit_repo 端到端干跑

---

## 1. 干跑状态

**当前状态**: ⏸️ PENDING IMPLEMENTATION

**原因**: Gate 实现尚未完成，无法执行 E2E 干跑。

---

## 2. 干跑前置条件

### 2.1 必须完成

| # | 前置条件 | 状态 | 备注 |
|---|----------|------|------|
| 1 | intake_repo Gate 实现 | ⬜ | - |
| 2 | license_gate Gate 实现 | ⬜ | - |
| 3 | repo_scan_fit_score Gate 实现 | ⬜ | - |
| 4 | pack_audit_and_publish Gate 实现 | ⬜ | - |
| 5 | Evidence Schema 实现 | ⬜ | - |
| 6 | Hash Chain 模块实现 | ⬜ | - |

### 2.2 输入数据准备

```yaml
dry_run_input:
  repo_url: "https://github.com/example/test-repo"
  commit_sha: "abc1234567"
  at_time: "2026-02-18T00:00:00Z"
  audit_log_path: "test/fixtures/audit_log.json"
  max_timeline_entries: 10
```

---

## 3. 预期输出

### 3.1 最终 gate_decision

```json
{
  "gate_decision": "ALLOW",
  "gate_chain": [
    {"gate": "intake_repo", "decision": "ALLOW", "timestamp": "2026-02-18T00:00:01Z"},
    {"gate": "license_gate", "decision": "ALLOW", "timestamp": "2026-02-18T00:00:02Z"},
    {"gate": "repo_scan_fit_score", "decision": "ALLOW", "score": 85, "timestamp": "2026-02-18T00:00:03Z"},
    {"gate": "pack_audit_and_publish", "decision": "ALLOW", "timestamp": "2026-02-18T00:00:04Z"}
  ]
}
```

### 3.2 EvidenceRef 链

```json
{
  "evidence_refs": [
    {
      "ref_id": "EV-001",
      "type": "intake_validation",
      "source_locator": "intake_repo/output.json",
      "hash": "sha256:abc123...",
      "tool_revision": "intake_repo@v1.0.0",
      "timestamp": "2026-02-18T00:00:01Z"
    },
    {
      "ref_id": "EV-002",
      "type": "license_check",
      "source_locator": "license_gate/output.json",
      "hash": "sha256:def456...",
      "tool_revision": "license_gate@v1.0.0",
      "timestamp": "2026-02-18T00:00:02Z"
    },
    {
      "ref_id": "EV-003",
      "type": "scan_report",
      "source_locator": "repo_scan_fit_score/output.json",
      "hash": "sha256:ghi789...",
      "tool_revision": "repo_scan_fit_score@v1.0.0",
      "timestamp": "2026-02-18T00:00:03Z"
    },
    {
      "ref_id": "EV-004",
      "type": "audit_pack",
      "source_locator": "pack_audit_and_publish/audit_pack.json",
      "hash": "sha256:jkl012...",
      "tool_revision": "pack_audit_and_publish@v1.0.0",
      "timestamp": "2026-02-18T00:00:04Z"
    }
  ]
}
```

### 3.3 L3 AuditPack Manifest

```json
{
  "audit_pack": {
    "pack_id": "AP-audit_repo-20260218000000",
    "intent_id": "audit_repo",
    "level": "L3",
    "schema_hash": "sha256:xyz789...",
    "created_at": "2026-02-18T00:00:04Z",
    "hash_chain": {
      "prev_hash": "0000000000000000000000000000000000000000000000000000000000000000",
      "curr_hash": "sha256:jkl012..."
    },
    "manifest": {
      "evidence_count": 4,
      "gate_chain_length": 4,
      "final_decision": "ALLOW"
    }
  }
}
```

---

## 4. Fail-Closed 验证场景

### 4.1 输入缺失场景

| 场景 | 输入 | 预期 gate_decision | 预期 error_code |
|------|------|-------------------|-----------------|
| 缺少 repo_url | `{commit_sha: "abc"}` | DENY | `MISSING_REPO_URL` |
| 缺少 commit_sha | `{repo_url: "https://..."}` | DENY | `MISSING_COMMIT_SHA` |
| repo_url 格式错误 | `{repo_url: "invalid"}` | DENY | `INVALID_REPO_URL` |
| commit_sha 格式错误 | `{commit_sha: "xyz"}` | DENY | `INVALID_COMMIT_SHA` |

### 4.2 许可证不兼容场景

| 场景 | 输入 | 预期 gate_decision | 预期 error_code |
|------|------|-------------------|-----------------|
| GPL 许可证 | `{license: "GPL-3.0"}` | DENY | `LICENSE_INCOMPATIBLE` |
| 未知许可证 | `{license: "UNKNOWN"}` | REQUIRE_HITL | `LICENSE_UNKNOWN` |

### 4.3 扫描失败场景

| 场景 | 输入 | 预期 gate_decision | 预期 error_code |
|------|------|-------------------|-----------------|
| 适配度低于阈值 | `{fit_score: 50}` | DENY | `FIT_SCORE_TOO_LOW` |
| 扫描超时 | `{timeout: true}` | DENY | `SCAN_TIMEOUT` |

### 4.4 证据缺失场景

| 场景 | 缺失证据 | 预期 gate_decision | 预期 error_code |
|------|----------|-------------------|-----------------|
| 缺少 scan_report | scan_report | DENY | `MISSING_EVIDENCE` |
| 缺少 audit_log_file | audit_log_file | DENY | `MISSING_EVIDENCE` |

---

## 5. 验收条件

干跑通过必须满足以下条件：

| # | 条件 | 验证方式 |
|---|------|----------|
| 1 | 有最终 gate_decision | gate_decision 字段存在且为 ALLOW/DENY/REQUIRE_HITL |
| 2 | 有完整 EvidenceRef 链 | evidence_refs 数组长度 >= required_evidence 数量 |
| 3 | 有 L3 AuditPack | audit_pack_ref 可解析且 level == L3 |
| 4 | 任一关键证据缺失时 FAIL | Fail-Closed 测试用例全部通过 |

---

## 6. 干跑执行命令（待实现完成后）

```bash
# 执行 E2E 干跑
python -m skillforge.skills.audit_repo \
  --repo-url "https://github.com/example/test-repo" \
  --commit-sha "abc1234567" \
  --at-time "2026-02-18T00:00:00Z" \
  --dry-run \
  --output audit_repo_e2e_result.json

# 验证结果
python -m skillforge.skills.validate_audit_pack \
  --input audit_repo_e2e_result.json \
  --expected-level L3
```

---

## 7. 下一步行动

| 优先级 | 动作 | 负责者 |
|--------|------|--------|
| P0 | 实现 intake_repo Gate | Batch1 实现 |
| P0 | 实现 license_gate Gate | Batch1 实现 |
| P0 | 实现 repo_scan_fit_score Gate | Batch1 实现 |
| P0 | 实现 pack_audit_and_publish Gate | Batch1 实现 |
| P0 | 准备干跑测试数据 | Batch1 实现 |
| P0 | 执行 E2E 干跑 | Batch1 实现 |

---

## 8. 状态

**E2E DRY RUN: ⏸️ PENDING IMPLEMENTATION**

等待 Gate 实现完成后执行。

---

## 9. 变更记录

| 日期 | 变更 | 说明 |
|------|------|------|
| 2026-02-18 | 占位创建 | 本次仅占位，不代表通过验收 |

---

*Generated by CC-Code | Wave4 Batch1 | 2026-02-18*
