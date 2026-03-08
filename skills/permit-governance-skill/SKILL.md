# permit-governance-skill

> **版本**: v1.1.0
> **冻结时间**: 2026-02-18
> **继承自**: Phase-1 业务意图运行
> **能力范围**: 签发 + 验签 + 阻断

---

## 1. 概述

本 Skill 封装 Permit 治理的完整能力，确保 **no-permit-no-release** 语义不变。

### 1.1 核心能力

| 能力 | 说明 | 实现模块 |
|------|------|----------|
| **签发** | Gate 通过后签发 permit_token | `PermitIssuer` |
| **验签** | 发布前校验 permit 有效性 | `GatePermit` |
| **阻断** | 无有效 permit 时阻断发布 | `GatePermit` |

### 1.2 核心约束

```yaml
no-permit-no-release: true
fail_closed: true
evidence_first: true
```

---

## 2. 触发场景

| 场景 | 触发条件 | 执行能力 |
|------|----------|----------|
| **发布前校验** | 发布流程启动 | 验签 + 阻断 |
| **签发联调** | Gate 链通过 (PASSED_NO_PERMIT) | 签发 |
| **阻断验证** | permit 缺失/无效 | 阻断 |
| **回滚审计** | 需要 permit 追溯 | 验签 |

---

## 3. 输入契约

### 3.1 签发输入 (Issue)

```yaml
input_issue:
  # 执行上下文
  run_id: string           # 运行ID（必填）
  intent_id: string        # 意图ID（必填）
  repo_url: string         # 仓库URL（必填）
  commit_sha: string       # 提交SHA（必填）
  at_time: string          # 时间锚点（必填，ISO8601 UTC）

  # Gate 结果
  final_gate_decision: string   # Gate决策（必填，PASSED/PASSED_NO_PERMIT）
  release_blocked_by: string    # 阻断原因（可选，有值则不签发）
  audit_pack_ref: string        # 审计包引用（必填）
  gate_count: int              # Gate数量（可选，默认8）
  evidence_count: int          # Evidence数量（可选）

  # 签发配置
  ttl_seconds: int             # 有效期（必填，1-86400秒）
  allowed_actions: [string]    # 允许动作（可选，默认["release"]）
  environment: string          # 目标环境（可选，默认development）
  gate_profile: string         # Gate配置（可选，默认batch2_8gate）
```

### 3.2 验签输入 (Validate)

```yaml
input_validate:
  # Permit Token
  permit_token: string | null  # Permit Token（可为空，触发E001）

  # 执行上下文
  run_id: string              # 运行ID（必填）
  repo_url: string            # 仓库URL（必填）
  commit_sha: string          # 提交SHA（必填）
  requested_action: string    # 请求动作（必填，默认release）
  current_time: string        # 当前时间（可选，默认UTC now）
```

---

## 4. 输出契约

### 4.1 签发输出 (Issue)

```yaml
output_issue:
  success: bool                    # 签发成功标志
  permit_id: string | null         # Permit ID
  permit_token: string | null      # JWT Token（失败时为null）
  issued_at: string | null         # 签发时间（ISO8601）
  expires_at: string | null        # 过期时间（ISO8601）
  signature: object | null         # 签名信息
  error_code: string | null        # 错误码（I001-I005）
  error_message: string | null     # 错误描述
  evidence_refs: [object]          # Evidence引用列表
```

### 4.2 验签输出 (Validate)

```yaml
output_validate:
  gate_name: string                # Gate名称（permit_gate）
  gate_decision: string            # Gate决策（ALLOW/BLOCK）
  permit_validation_status: string # 校验状态（VALID/INVALID）
  release_allowed: bool            # 是否允许发布
  release_blocked_by: string       # 阻断原因（有则返回）
  error_code: string | null        # 错误码（E001-E007）
  permit_id: string | null         # Permit ID（校验通过时有值）
  evidence_refs: [object]          # Evidence引用列表
  validation_timestamp: string     # 校验时间戳
```

---

## 5. Fail-Closed 条款

### 5.1 签发阻断条件（I001-I005）

| 错误码 | 条件 | 行为 |
|--------|------|------|
| **I001** | `final_gate_decision` 不是 PASSED/PASSED_NO_PERMIT | permit_token = null |
| **I001** | `release_blocked_by` 非空 | permit_token = null |
| **I001** | `audit_pack_ref` 为空 | permit_token = null |
| **I002** | subject 字段不完整 | permit_token = null |
| **I003** | `ttl_seconds` 非法（<=0 或 >86400） | permit_token = null |
| **I004** | 签名密钥不可用 | permit_token = null |
| **I005** | 签名失败 | permit_token = null |

### 5.2 验签阻断条件（E001-E007）

| 错误码 | 条件 | 行为 | release_blocked_by |
|--------|------|------|-------------------|
| **E001** | permit_token 缺失或为空 | **阻断** | PERMIT_REQUIRED |
| **E002** | permit 格式无效/字段缺失 | **阻断** | PERMIT_INVALID |
| **E003** | 签名校验失败 | **阻断** | PERMIT_INVALID |
| **E004** | permit 已过期 | **阻断** | PERMIT_EXPIRED |
| **E005** | 作用域不匹配 | **阻断** | PERMIT_SCOPE_MISMATCH |
| **E006** | 主体不匹配 | **阻断** | PERMIT_SUBJECT_MISMATCH |
| **E007** | permit 已撤销 | **阻断** | PERMIT_REVOKED |

### 5.3 核心约束说明

```
no-permit-no-release:
  - release_allowed 默认 false
  - 只有 permit 校验完全通过时 release_allowed = true
  - 任一检查失败立即阻断，不继续后续检查
```

---

## 6. Evidence 字段要求

### 6.1 签发 Evidence

```yaml
evidence_issue:
  issue_key: "PERMIT-ISSUE-{permit_id}-{timestamp}"
  source_locator: "issuer://skillforge-permit-service"
  content_hash: "sha256:{hash}"
  tool_revision: "1.0.0"
  timestamp: "{ISO8601}"
  decision_snapshot:
    check: "issuance"
    passed: bool
    permit_id: string
    expires_at: string
```

### 6.2 验签 Evidence

```yaml
evidence_validate:
  issue_key: "PERMIT-VAL-{permit_id}-{timestamp}"
  source_locator: "permit://{permit_id}"
  content_hash: "sha256:{hash}"
  tool_revision: "1.0.0"
  timestamp: "{ISO8601}"
  decision_snapshot:
    check: "all_passed" | "{check_type}"
    permit_id: string
    subject_match: bool
    scope_match: bool
```

---

## 7. 实现引用

### 7.1 模块映射

| 能力 | 模块路径 | 类名 |
|------|----------|------|
| 签发 | `skillforge/src/skills/gates/permit_issuer.py` | `PermitIssuer` |
| 验签 | `skillforge/src/skills/gates/gate_permit.py` | `GatePermit` |
| 批量签发 | `skillforge/src/skills/gates/batch_permit_issuer.py` | `BatchPermitIssuer` |

### 7.2 契约文件

| 文件 | 说明 |
|------|------|
| `docs/2026-02-18/permit_contract_v1_spec.md` | Permit 契约规格 |
| `docs/2026-02-18/contracts/permit_contract_v1.yml` | YAML 契约定义 |

### 7.3 验收报告

| 报告 | 路径 |
|------|------|
| GatePermit 实现 | `docs/2026-02-18/permit_gate_implementation_report_v1.md` |
| PermitIssuer 实现 | `docs/2026-02-18/permit_issuer_implementation_report_v1.md` |
| Phase-1 执行 | `docs/2026-02-18/business_phase1_execution_report_v1.md` |
| Phase-1 验收 | `docs/2026-02-18/business_phase1_acceptance_report_v1.md` |

---

## 8. 验证步骤

### 8.1 正常路径验证

```bash
# Step 1: 签发 permit
python -m skillforge.src.skills.gates.permit_issuer \
  --signing-key "test-key-2026" \
  --final-decision "PASSED" \
  --audit-pack-ref "audit-test-001" \
  --repo-url "github.com/test/repo" \
  --commit-sha "a1b2c3d4e5f6..." \
  --run-id "RUN-TEST-001" \
  --intent-id "test-release" \
  --ttl 3600

# 预期: success=true, permit_token 非空

# Step 2: 验签 permit
python -m skillforge.src.skills.gates.gate_permit \
  --permit-file permit.json \
  --repo-url "github.com/test/repo" \
  --commit-sha "a1b2c3d4e5f6..." \
  --run-id "RUN-TEST-001"

# 预期: gate_decision=ALLOW, release_allowed=true
```

### 8.2 E001 阻断验证（无 permit）

```bash
# 无 permit_token 验签
python -m skillforge.src.skills.gates.gate_permit \
  --repo-url "github.com/test/repo" \
  --commit-sha "a1b2c3d4e5f6..." \
  --run-id "RUN-TEST-001"

# 预期:
# - gate_decision = BLOCK
# - release_allowed = false
# - release_blocked_by = PERMIT_REQUIRED
# - error_code = E001
```

### 8.3 E003 阻断验证（签名异常）

```bash
# 使用篡改的 permit
cat > bad_permit.json << 'EOF'
{
  "permit_id": "PERMIT-TEST-001",
  "signature": {
    "algo": "RS256",
    "value": "INVALID_SIGNATURE",
    "key_id": "bad-key"
  }
}
EOF

python -m skillforge.src.skills.gates.gate_permit \
  --permit-file bad_permit.json \
  --repo-url "github.com/test/repo" \
  --commit-sha "a1b2c3d4e5f6..." \
  --run-id "RUN-TEST-001"

# 预期:
# - gate_decision = BLOCK
# - release_allowed = false
# - release_blocked_by = PERMIT_INVALID
# - error_code = E003
```

---

## 9. 验收清单

### 9.1 功能验收

- [x] 签发条件校验（I001-I005）
- [x] 验签阻断逻辑（E001-E007）
- [x] Evidence 生成正确
- [x] permit_token 格式符合契约

### 9.2 Fail-Closed 验收

- [x] E001: 无 permit → BLOCK
- [x] E003: 签名异常 → BLOCK
- [x] I001: Gate 未通过 → permit_token = null

### 9.3 集成验收

- [x] Phase-1 业务验收通过
- [x] 治理链联调通过
- [x] no-permit-no-release 约束满足

---

## 10. 风险与限制

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 签名密钥泄露 | 高 | 密钥轮换 + 审计日志 |
| TTL 配置过长 | 中 | 默认 1 小时，最大 24 小时 |
| 时钟不同步 | 中 | 使用 NTP 同步 |

---

*文档版本: v1.1.0 | 更新时间: 2026-02-18 | 执行者: Kiro-2*
