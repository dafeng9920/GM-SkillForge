# Permit Issuer 实现报告 v1

> **版本**: 1.0.0
> **创建时间**: 2026-02-18
> **作者**: CC-Code
> **状态**: COMPLETED
> **关联契约**: `docs/2026-02-18/contracts/permit_contract_v1.yml`

---

## 1. 设计摘要

### 1.1 目标

实现 Permit 签发服务（PermitIssuer），与已完成的 GatePermit（校验侧）对接，满足：

1. 只在满足签发条件时签发 permit
2. permit 必须绑定 subject（repo_url/commit_sha/run_id/intent_id）
3. permit 必须包含 expires_at（TTL）
4. permit 必须带 signature（MVP 使用 HS256）
5. 签发结果可被 GatePermit 验证通过
6. 失败时 fail-closed，不产生可用 permit

### 1.2 架构

```
┌─────────────────────────────────────────────────────────────┐
│                     SkillForge Permit Pipeline              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Gate Pipeline (G1-G8)                                      │
│        │                                                    │
│        ▼                                                    │
│  final_gate_decision = PASSED_NO_PERMIT                     │
│        │                                                    │
│        ▼                                                    │
│  ┌─────────────────────────────────┐                        │
│  │  PermitIssuer.issue_permit()   │                        │
│  │  - 检查签发条件                 │                        │
│  │  - 构建 permit payload          │                        │
│  │  - HS256 签名                   │                        │
│  └─────────────────────────────────┘                        │
│        │                                                    │
│        ▼                                                    │
│  permit_token (JSON string)                                 │
│        │                                                    │
│        ▼                                                    │
│  ┌─────────────────────────────────┐                        │
│  │  GatePermit.validate_permit()  │                        │
│  │  - 解析 permit                  │                        │
│  │  - 校验签名                     │                        │
│  │  - 校验过期时间                 │                        │
│  │  - 校验 subject 匹配            │                        │
│  │  - 校验 scope 匹配              │                        │
│  │  - 校验撤销状态                 │                        │
│  └─────────────────────────────────┘                        │
│        │                                                    │
│        ▼                                                    │
│  release_allowed = true/false                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. 签发条件（硬约束）

仅当以下**全部成立**才签发：

| # | 条件 | 失败错误码 |
|---|------|-----------|
| 1 | `final_gate_decision` 为 `PASSED` 或 `PASSED_NO_PERMIT` | I001 |
| 2 | `release_blocked_by` 为空/null | I001 |
| 3 | `audit_pack_ref` 非空 | I001 |
| 4 | subject 字段完整（repo_url/commit_sha/run_id/intent_id） | I002 |
| 5 | `ttl_seconds` 合法（>0 且 ≤86400） | I003 |

**不满足任一条件时**：
- 返回签发失败
- `error_code` 明确
- `permit_token` 必须为 null

---

## 3. 错误码表（签发侧）

| 错误码 | 名称 | 含义 | 映射到校验侧 |
|--------|------|------|-------------|
| `I001` | ISSUE_CONDITION_NOT_MET | 签发条件不满足（决策/阻塞/审计包） | - |
| `I002` | SUBJECT_INCOMPLETE | subject 字段不完整 | E006 |
| `I003` | TTL_INVALID | TTL 非法（≤0 或 >86400） | - |
| `I004` | SIGNING_KEY_MISSING | 签名密钥缺失 | - |
| `I005` | SIGNING_FAILED | 签名过程异常 | E003 |

> **注意**：签发侧错误码（I001-I005）与校验侧错误码（E001-E007）分开管理。签发失败不会产生 permit_token，因此不会触发校验侧错误。

---

## 4. 实现详情

### 4.1 核心模块

| 文件 | 描述 |
|------|------|
| `skillforge/src/skills/gates/permit_issuer.py` | PermitIssuer 实现 |
| `skillforge/tests/test_permit_issuer.py` | 测试矩阵 S1-S8 |

### 4.2 核心函数

```python
class PermitIssuer:
    def issue_permit(input_data: dict) -> dict:
        """
        签发 permit。

        Returns:
            {
                success: bool,
                permit_token: str | None,  # JSON string
                permit_id: str | None,
                issued_at: str | None,
                expires_at: str | None,
                error_code: str | None,
                error_message: str | None,
                evidence_refs: list,
                signature: dict | None,
            }
        """

    def check_issuance_conditions(input_data: dict) -> tuple[bool, str, str]:
        """检查签发条件，返回 (can_issue, error_code, error_message)"""

    def _build_permit_payload(input_data, permit_id, timestamp) -> dict:
        """构建 permit payload（不含签名和撤销状态）"""

    def _sign_permit(payload: dict) -> str:
        """使用 HS256 签名，返回 Base64 编码的签名值"""
```

### 4.3 Permit 数据结构

签发的 permit 完全符合 `permit_contract_v1.yml` 定义的 schema：

```json
{
  "permit_id": "PERMIT-20260218-F4B99ED4",
  "issuer": {
    "issuer_id": "skillforge-permit-service",
    "issuer_type": "AUTOMATED_GATE"
  },
  "issued_at": "2026-02-18T09:59:06Z",
  "expires_at": "2026-02-18T10:59:06Z",
  "subject": {
    "repo_url": "https://github.com/local/NEW-GM",
    "commit_sha": "4ea179d31a66fc2616f0cf953cd0e5c5c43d8ea8",
    "run_id": "RUN-20260218-001",
    "intent_id": "generate_skill_from_repo",
    "entry_path": null
  },
  "scope": {
    "allowed_actions": ["release"],
    "environment": "development",
    "gate_profile": "batch2_8gate"
  },
  "constraints": {
    "at_time": "2026-02-18T08:41:10Z",
    "max_release_count": 1,
    "time_window_seconds": 3600
  },
  "decision_binding": {
    "final_gate_decision": "PASSED_NO_PERMIT",
    "gate_count": 8,
    "audit_pack_ref": "audit-10465f76",
    "evidence_count": 8
  },
  "signature": {
    "algo": "HS256",
    "value": "BASE64_ENCODED_SIGNATURE",
    "key_id": "skillforge-permit-key-2026",
    "signed_at": "2026-02-18T09:59:06Z"
  },
  "revocation": {
    "revoked": false,
    "revoked_at": null,
    "revoked_by": null,
    "reason": null
  }
}
```

---

## 5. 测试矩阵结果（S1-S8）

| 测试 | 描述 | 期望 | 实际 | 状态 |
|------|------|------|------|------|
| S1 | 正常签发 | success=true, permit_token 非空 | ✅ 符合 | PASS |
| S2a | 决策不满足（REJECTED） | I001, permit_token=null | ✅ 符合 | PASS |
| S2b | 决策不满足（REQUIRE_HITL） | I001, permit_token=null | ✅ 符合 | PASS |
| S2c | release_blocked_by 非空 | I001, permit_token=null | ✅ 符合 | PASS |
| S3a | subject 缺 repo_url | I002 | ✅ 符合 | PASS |
| S3b | subject 缺 commit_sha | I002 | ✅ 符合 | PASS |
| S3c | subject 缺 run_id | I002 | ✅ 符合 | PASS |
| S4a | TTL=0 | I003 | ✅ 符合 | PASS |
| S4b | TTL<0 | I003 | ✅ 符合 | PASS |
| S5 | TTL>86400 | I003 | ✅ 符合 | PASS |
| S6 | 签名密钥缺失 | I004 | ✅ 符合 | PASS |
| S7 | 签名异常 | I005 | ✅ 符合 | PASS |
| S8 | 联通验证 | GatePermit 验证通过, release_allowed=true | ✅ 符合 | PASS |

**测试结果：13/13 PASS**

---

## 6. 与 GatePermit 联通结果

### 6.1 联通流程

```
1. PermitIssuer.issue_permit(valid_input)
   -> success=true, permit_token="..."

2. GatePermit.validate_permit(permit_token, execution_context)
   -> gate_decision=ALLOW
   -> permit_validation_status=VALID
   -> release_allowed=true
   -> release_blocked_by=null
```

### 6.2 联通测试验证

| 检查项 | 结果 |
|--------|------|
| permit_token 格式 | JSON 字符串，可被 GatePermit 解析 |
| 签名校验 | HS256 签名有效（使用 stub verifier 时） |
| 过期校验 | issued_at < expires_at，校验通过 |
| subject 匹配 | repo_url/commit_sha/run_id 完全一致 |
| scope 匹配 | requested_action 在 allowed_actions 中 |
| 撤销校验 | revoked=false |
| **release_allowed** | **true** |

### 6.3 状态转换

```
PASSED_NO_PERMIT + 无 permit
    -> release_allowed=false, release_blocked_by=PERMIT_REQUIRED

PASSED_NO_PERMIT + issue permit
    -> permit_token 非空

PASSED_NO_PERMIT + valid permit
    -> release_allowed=true, release_blocked_by=null
```

---

## 7. Evidence 记录

每次签发尝试都生成 EvidenceRef：

```json
{
  "issue_key": "PERMIT-ISSUE-PERMIT-20260218-F4B99ED4-1739875146",
  "source_locator": "issuer://permit_issuer",
  "content_hash": "sha256:...",
  "tool_revision": "1.0.0",
  "timestamp": "2026-02-18T09:59:06Z",
  "decision_snapshot": {
    "check": "issuance",
    "passed": true,
    "permit_id": "PERMIT-20260218-F4B99ED4",
    "expires_at": "2026-02-18T10:59:06Z"
  }
}
```

**安全约束**：
- content_hash 只包含 payload hash，不泄漏签名密钥
- 签名密钥不会出现在日志或 Evidence 中

---

## 8. 修改文件清单

| 文件 | 操作 | 描述 |
|------|------|------|
| `skillforge/src/skills/gates/permit_issuer.py` | 新增 | PermitIssuer 实现 |
| `skillforge/tests/test_permit_issuer.py` | 新增 | 测试矩阵 S1-S8 |
| `skillforge/src/skills/gates/__init__.py` | 修改 | 导出 PermitIssuer |

---

## 9. 接入位置

```
文件: skillforge/src/skills/gates/permit_issuer.py
类: PermitIssuer
函数:
  - issue_permit(input_data) -> dict
  - check_issuance_conditions(input_data) -> tuple[bool, str, str]

便捷函数:
  - issue_permit(final_gate_decision, audit_pack_ref, repo_url, ...) -> dict
```

---

## 10. 剩余风险（最多3条）

1. **签名验证使用 stub**：当前 GatePermit 使用 stub 签名验证器，只检查结构不验证实际签名。生产环境需替换为真实 RS256/ES256 验证。

2. **无外部撤销列表（CRL）**：当前撤销状态仅通过 permit 内的 `revocation.revoked` 字段判断，无外部 CRL 查询机制。

3. **签名密钥管理**：MVP 阶段签名密钥通过参数传入，生产环境需要更安全的密钥管理方案（如 Vault、KMS）。

---

## 11. 非 dry-run 发布前验证

**是否可进入"非 dry-run 发布前验证"？**

> **Yes** — PermitIssuer 实现完成，测试矩阵 S1-S8 全部通过，与 GatePermit 联通验证成功（release_allowed=true）。签发条件硬约束已落地，失败时 fail-closed 不产生可用 permit。

---

## 12. 附件

- 契约：`docs/2026-02-18/contracts/permit_contract_v1.yml`
- 规范：`docs/2026-02-18/permit_contract_v1_spec.md`
- 校验侧实现：`docs/2026-02-18/permit_gate_implementation_report_v1.md`

---

*Generated by CC-Code | Permit Issuer v1 | 2026-02-18*
