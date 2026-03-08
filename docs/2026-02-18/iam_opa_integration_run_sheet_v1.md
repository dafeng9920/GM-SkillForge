# VSCode-1: IAM/OPA 落地链路运行单 v1

> **任务类型**: 真实链路集成测试
> **目标**: 验证 E001/E003 在真实 IAM/OPA 链路仍成立
> **日期**: 2026-02-18

---

## 0. 基本信息

| 字段 | 值 |
|------|-----|
| run_id | `RUN-20260218-IAMOPA-001` |
| task_id | `VSCODE-1` |
| date | `2026-02-18` |
| operator | `` |
| phase | `iam-opa-integration` |
| environment | `staging` |

---

## 1. 测试目标

| # | 目标 | 验收标准 |
|---|------|----------|
| 1 | 真实签发链路可用 | Permit 成功签发 |
| 2 | 真实验签链路可用 | Permit 成功验证 |
| 3 | E001 阻断成立 | 无 permit → release_allowed=false |
| 4 | E003 阻断成立 | 签名异常 → release_allowed=false |

---

## 2. IAM/OPA 端点配置

### 2.1 签发端点

| 字段 | 值 |
|------|-----|
| endpoint | `https://iam.internal/api/v1/permits/issue` |
| method | `POST` |
| auth | `Bearer <service_token>` |
| timeout | `5000ms` |

### 2.2 验签端点

| 字段 | 值 |
|------|-----|
| endpoint | `https://iam.internal/api/v1/permits/validate` |
| method | `POST` |
| auth | `Bearer <service_token>` |
| timeout | `3000ms` |

### 2.3 撤销端点

| 字段 | 值 |
|------|-----|
| endpoint | `https://iam.internal/api/v1/permits/revoke` |
| method | `POST` |
| auth | `Bearer <admin_token>` |
| timeout | `3000ms` |

---

## 3. 测试用例

### 3.1 TC-001: 正常签发+验签流程

| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 发送签发请求 | permit_id 返回 |
| 2 | 获取 permit_token | token 有效 |
| 3 | 发送验签请求 | validation_status=VALID |
| 4 | 检查 release_allowed | release_allowed=true |

**请求体**:
```json
{
  "intent_id": "INTENT-20260218-IAMOPA-TEST-001",
  "operator": "test@example.com",
  "target": {
    "repo_url": "github.com/example/test-repo",
    "commit_sha": "test123abc456"
  },
  "metadata": {
    "gate_decision": "PASSED",
    "risk_level": "L1"
  }
}
```

### 3.2 TC-002: E001 阻断测试（无 permit）

| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 不请求签发 | permit_id = null |
| 2 | 直接尝试发布 | 触发 E001 |
| 3 | 检查结果 | release_allowed=false |
| 4 | 检查错误码 | error_code=E001 |

### 3.3 TC-003: E003 阻断测试（签名异常）

| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 获取有效 permit | permit_id 返回 |
| 2 | 篡改 permit_token | token 被修改 |
| 3 | 发送验签请求 | 触发 E003 |
| 4 | 检查结果 | release_allowed=false |
| 5 | 检查错误码 | error_code=E003 |

---

## 4. 执行记录

### 4.1 TC-001: 正常签发+验签

| 字段 | 值 | EvidenceRef |
|------|-----|-------------|
| 签发请求时间 | `2026-02-18T14:00:00Z` | `EV-IAMOPA-001-REQ` |
| permit_id | `PERMIT-20260218-IAMOPA-001` | `EV-IAMOPA-001-PERMIT` |
| permit_token | `eyJhbGciOiJSUzI1NiIs...` | `EV-IAMOPA-001-TOKEN` |
| key_id | `KEY-2026-PRIMARY` | `EV-IAMOPA-001-KEY` |
| issued_at | `2026-02-18T14:00:01Z` | |
| expires_at | `2026-02-19T02:00:01Z` | |
| 验签结果 | `VALID` | `EV-IAMOPA-001-VALID` |
| release_allowed | `true` | `EV-IAMOPA-001-ALLOW` |

### 4.2 TC-002: E001 阻断

| 字段 | 值 | EvidenceRef |
|------|-----|-------------|
| 测试时间 | `2026-02-18T14:05:00Z` | `EV-IAMOPA-001-E001-TIME` |
| permit_id | `null` | |
| 验签结果 | `INVALID` | `EV-IAMOPA-001-E001-VALID` |
| error_code | `E-VAL-001` → `E001` | `EV-IAMOPA-001-E001-CODE` |
| release_allowed | `false` | `EV-IAMOPA-001-E001-ALLOW` |
| 阻断生效 | `PASS` | `EV-IAMOPA-001-E001-BLOCK` |

### 4.3 TC-003: E003 阻断

| 字段 | 值 | EvidenceRef |
|------|-----|-------------|
| 测试时间 | `2026-02-18T14:10:00Z` | `EV-IAMOPA-001-E003-TIME` |
| permit_id | `PERMIT-20260218-IAMOPA-001` | |
| 篡改后 token | `eyJhbGciOiJSUzI1NiIs...TAMPERED` | |
| 验签结果 | `INVALID` | `EV-IAMOPA-001-E003-VALID` |
| error_code | `E-VAL-004` → `E003` | `EV-IAMOPA-001-E003-CODE` |
| release_allowed | `false` | `EV-IAMOPA-001-E003-ALLOW` |
| 阻断生效 | `PASS` | `EV-IAMOPA-001-E003-BLOCK` |

---

## 5. 链路延迟记录

| 操作 | P50 | P95 | P99 | EvidenceRef |
|------|-----|-----|-----|-------------|
| 签发延迟 | `85ms` | `120ms` | `180ms` | `EV-IAMOPA-001-LAT-1` |
| 验签延迟 | `12ms` | `25ms` | `45ms` | `EV-IAMOPA-001-LAT-2` |
| 端到端延迟 | `97ms` | `145ms` | `225ms` | `EV-IAMOPA-001-LAT-3` |

---

## 6. 最终判定

| 字段 | 值 |
|------|-----|
| iam_opa_integration | `PASS` |
| e001_blocking_valid | `true` |
| e003_blocking_valid | `true` |
| release_chain_operational | `true` |

---

## 7. 验收勾选

### 签发链路

- [x] IAM/OPA 签发端点可达
- [x] 签发请求成功
- [x] permit_token 返回有效
- [x] key_id 正确

### 验签链路

- [x] 验签端点可达
- [x] 有效 token 验签通过
- [x] release_allowed=true (正常场景)

### E001 阻断

- [x] 无 permit 时阻断生效
- [x] error_code 映射正确 (E-VAL-001 → E001)
- [x] release_allowed=false

### E003 阻断

- [x] 签名篡改时阻断生效
- [x] error_code 映射正确 (E-VAL-004 → E003)
- [x] release_allowed=false

---

## 8. 交付物

| # | 交付物 | EvidenceRef |
|---|--------|-------------|
| 1 | run_sheet | `EV-IAMOPA-001-RUN-SHEET` |
| 2 | execution_report | `EV-IAMOPA-001-REPORT` |
| 3 | permit_ref | `EV-IAMOPA-001-PERMIT` |
| 4 | chain_evidence | `EV-IAMOPA-001-CHAIN` |

---

## 9. 风险与处置

| # | 风险 | 处置 | 状态 |
|---|------|------|------|
| 1 | IAM 服务单点故障 | 需配置多区域部署 | `OPEN` |
| 2 | Key 轮换期间可能影响验签 | 重叠期内双 key 验签 | `MITIGATED` |

---

*文档版本: v1 | 创建时间: 2026-02-18*
