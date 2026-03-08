# permit-governance-skill 调用说明

> **版本**: v1.0.0
> **更新时间**: 2026-02-18

---

## 1. 概述

本目录包含 permit-governance-skill 的标准调用脚本和说明。

**注意**: 本 Skill 不重新实现逻辑，而是对现有模块的封装调用。

---

## 2. 模块引用

### 2.1 签发模块

```python
from skillforge.src.skills.gates.permit_issuer import PermitIssuer, issue_permit

# 方式 1: 使用类
issuer = PermitIssuer(signing_key="your-secret-key")
result = issuer.issue_permit({
    "run_id": "RUN-TEST-001",
    "intent_id": "test-release",
    "repo_url": "github.com/test/repo",
    "commit_sha": "a1b2c3d4e5f6...",
    "final_gate_decision": "PASSED",
    "audit_pack_ref": "audit-test-001",
    "ttl_seconds": 3600
})

# 方式 2: 使用便捷函数
result = issue_permit(
    final_gate_decision="PASSED",
    audit_pack_ref="audit-test-001",
    repo_url="github.com/test/repo",
    commit_sha="a1b2c3d4e5f6...",
    run_id="RUN-TEST-001",
    intent_id="test-release",
    ttl_seconds=3600,
    signing_key="your-secret-key"
)
```

### 2.2 验签模块

```python
from skillforge.src.skills.gates.gate_permit import GatePermit, validate_permit

# 方式 1: 使用类
gate = GatePermit()
result = gate.execute({
    "permit_token": permit_token_string,
    "run_id": "RUN-TEST-001",
    "repo_url": "github.com/test/repo",
    "commit_sha": "a1b2c3d4e5f6...",
    "requested_action": "release"
})

# 方式 2: 使用便捷函数
result = validate_permit(
    permit_token=permit_token_string,
    repo_url="github.com/test/repo",
    commit_sha="a1b2c3d4e5f6...",
    run_id="RUN-TEST-001",
    requested_action="release"
)
```

---

## 3. CLI 调用

### 3.1 签发 CLI

```bash
# 基本调用
python -m skillforge.src.skills.gates.permit_issuer \
  --signing-key "your-secret-key" \
  --final-decision "PASSED" \
  --audit-pack-ref "audit-test-001" \
  --repo-url "github.com/test/repo" \
  --commit-sha "a1b2c3d4e5f6..." \
  --run-id "RUN-TEST-001" \
  --intent-id "test-release" \
  --ttl 3600 \
  --output permit.json

# 参数说明
# --signing-key: 签名密钥（必填）
# --key-id: 密钥ID（可选，默认 skillforge-permit-key-2026）
# --final-decision: Gate决策（必填，PASSED/PASSED_NO_PERMIT）
# --audit-pack-ref: 审计包引用（必填）
# --repo-url: 仓库URL（必填）
# --commit-sha: 提交SHA（必填）
# --run-id: 运行ID（必填）
# --intent-id: 意图ID（必填）
# --ttl: 有效期秒数（可选，默认 3600）
# --actions: 允许动作（可选，默认 release）
# --output: 输出文件路径（可选）
```

### 3.2 验签 CLI

```bash
# 基本调用
python -m skillforge.src.skills.gates.gate_permit \
  --permit-file permit.json \
  --repo-url "github.com/test/repo" \
  --commit-sha "a1b2c3d4e5f6..." \
  --run-id "RUN-TEST-001" \
  --action "release" \
  --output result.json

# 参数说明
# --permit-file: permit JSON 文件路径（可选，不提供则触发 E001）
# --repo-url: 仓库URL（必填）
# --commit-sha: 提交SHA（必填）
# --run-id: 运行ID（必填）
# --action: 请求动作（可选，默认 release）
# --current-time: 当前时间（可选，ISO8601 UTC）
# --output: 输出文件路径（可选）

# 退出码
# 0: release_allowed = true
# 1: release_allowed = false
```

---

## 4. API 调用

### 4.1 签发 API

```python
# 输入
issue_input = {
    "run_id": "RUN-20260218-BIZ-PHASE1-001",
    "intent_id": "INTENT-20260218-SKILL-UPDATE-001",
    "repo_url": "github.com/example/skillforge-skills",
    "commit_sha": "c3d4e5f67890123456789012345678901234abcd",
    "at_time": "2026-02-18T17:00:00Z",
    "final_gate_decision": "PASSED",
    "audit_pack_ref": "audit-10465f76",
    "ttl_seconds": 43200,
    "allowed_actions": ["release"],
    "environment": "staging"
}

# 输出
issue_output = {
    "success": True,
    "permit_id": "PERMIT-20260218-BIZ-PHASE1-001",
    "permit_token": "{...JSON...}",
    "issued_at": "2026-02-18T17:00:05Z",
    "expires_at": "2026-02-19T05:00:05Z",
    "signature": {
        "algo": "HS256",
        "value": "...",
        "key_id": "skillforge-permit-key-2026"
    },
    "evidence_refs": [...]
}
```

### 4.2 验签 API

```python
# 输入
validate_input = {
    "permit_token": "{...JSON...}",
    "run_id": "RUN-20260218-BIZ-PHASE1-001",
    "repo_url": "github.com/example/skillforge-skills",
    "commit_sha": "c3d4e5f67890123456789012345678901234abcd",
    "requested_action": "release"
}

# 输出（成功）
validate_output = {
    "gate_name": "permit_gate",
    "gate_decision": "ALLOW",
    "permit_validation_status": "VALID",
    "release_allowed": True,
    "release_blocked_by": None,
    "error_code": None,
    "permit_id": "PERMIT-20260218-BIZ-PHASE1-001",
    "evidence_refs": [...],
    "validation_timestamp": "2026-02-18T17:00:05Z"
}

# 输出（失败 - E001）
validate_output_e001 = {
    "gate_name": "permit_gate",
    "gate_decision": "BLOCK",
    "permit_validation_status": "INVALID",
    "release_allowed": False,
    "release_blocked_by": "PERMIT_REQUIRED",
    "error_code": "E001",
    "evidence_refs": [...],
    "validation_timestamp": "2026-02-18T17:00:05Z"
}
```

---

## 5. 验证脚本

### 5.1 正常路径验证

```bash
#!/bin/bash
# test_normal_path.sh

# 签发
python -m skillforge.src.skills.gates.permit_issuer \
  --signing-key "test-key-2026" \
  --final-decision "PASSED" \
  --audit-pack-ref "audit-test-001" \
  --repo-url "github.com/test/repo" \
  --commit-sha "a1b2c3d4e5f6789012345678901234567890abcd" \
  --run-id "RUN-TEST-001" \
  --intent-id "test-release" \
  --ttl 3600 \
  --output /tmp/permit.json

# 验签
python -m skillforge.src.skills.gates.gate_permit \
  --permit-file /tmp/permit.json \
  --repo-url "github.com/test/repo" \
  --commit-sha "a1b2c3d4e5f6789012345678901234567890abcd" \
  --run-id "RUN-TEST-001"

# 预期: 退出码 0, release_allowed=true
```

### 5.2 E001 阻断验证

```bash
#!/bin/bash
# test_e001_blocked.sh

# 无 permit 验签
python -m skillforge.src.skills.gates.gate_permit \
  --repo-url "github.com/test/repo" \
  --commit-sha "a1b2c3d4e5f6789012345678901234567890abcd" \
  --run-id "RUN-TEST-001"

# 预期: 退出码 1, release_allowed=false, error_code=E001
```

### 5.3 E003 阻断验证

```bash
#!/bin/bash
# test_e003_blocked.sh

# 创建无效签名的 permit
cat > /tmp/bad_permit.json << 'EOF'
{
  "permit_id": "PERMIT-TEST-001",
  "expires_at": "2026-12-31T23:59:59Z",
  "subject": {
    "repo_url": "github.com/test/repo",
    "commit_sha": "a1b2c3d4e5f6789012345678901234567890abcd",
    "run_id": "RUN-TEST-001"
  },
  "scope": {
    "allowed_actions": ["release"]
  },
  "revocation": {
    "revoked": false
  },
  "signature": {
    "algo": "RS256",
    "value": "INVALID_SIGNATURE",
    "key_id": "bad-key"
  }
}
EOF

# 验签
python -m skillforge.src.skills.gates.gate_permit \
  --permit-file /tmp/bad_permit.json \
  --repo-url "github.com/test/repo" \
  --commit-sha "a1b2c3d4e5f6789012345678901234567890abcd" \
  --run-id "RUN-TEST-001"

# 预期: 退出码 1, release_allowed=false, error_code=E003
```

---

## 6. 依赖

- Python 3.10+
- 无外部依赖（仅使用标准库）

---

*文档版本: v1.0.0 | 创建时间: 2026-02-18*
