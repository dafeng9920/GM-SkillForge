# L4 前后端契约冻结 v1

> **版本**: v1.0
> **冻结时间**: 2026-02-19T20:00:00Z
> **状态**: FROZEN
> **签核人**: Kior-B

---

## 1. 概述

本文档冻结 L4 阶段前后端合并所需的三个核心契约。

### 1.1 契约文件清单

| # | 契约文件 | 用途 | SHA256 |
|---|----------|------|--------|
| 1 | `src/contracts/cognition/10d_schema.json` | 10维认知输出Schema | TBD_SHA256 |
| 2 | `src/contracts/governance/work_item_schema.json` | Work Item Schema | TBD_SHA256 |
| 3 | `src/contracts/api/l4_endpoints.yaml` | L4 API端点定义 | TBD_SHA256 |

---

## 2. 10d_schema.json 字段清单

### 2.1 请求字段 (Cognition10dRequest)

| 字段 | 类型 | 必填 | 描述 | 验证规则 |
|------|------|------|------|----------|
| repo_url | string(uri) | ✓ | 仓库URL | 有效URI |
| commit_sha | string | ✓ | 提交SHA | 40字符hex |
| at_time | string(datetime) | ✓ | 时间点 | ISO-8601 |
| rubric_version | string | ✓ | 评分版本 | semver |
| requester_id | string | ✓ | 请求者ID | 非空 |

### 2.2 响应字段 (Cognition10dResponse)

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| intent_id | string(const) | ✓ | 固定值 "cognition_10d" |
| status | enum | ✓ | PASSED / REJECTED |
| repo_url | string(uri) | ✓ | 仓库URL |
| commit_sha | string | ✓ | 提交SHA |
| at_time | string(datetime) | ✓ | 时间点 |
| rubric_version | string | ✓ | 评分版本 |
| dimensions | array[10] | ✓ | 10维评估结果 |
| overall_pass_count | integer | ✓ | 通过维度数 (0-10) |
| rejection_reasons | array | ✓ | 拒绝原因列表 |
| audit_pack_ref | string | ✓ | 审计包引用 |
| generated_at | string(datetime) | ✓ | 生成时间 |

### 2.3 Dimension 子字段

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| dim_id | enum | ✓ | L1-L10 |
| label | string | ✓ | 维度标签 |
| score | number(0-100) | ✓ | 得分 |
| threshold | number(0-100) | ✓ | 阈值 |
| verdict | enum | ✓ | PASS / FAIL |
| evidence_ref | string | ✓ | 证据引用 |

---

## 3. work_item_schema.json 字段清单

### 3.1 WorkItem 核心字段

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| work_item_id | string | ✓ | 格式: WI-XXXXXXXX |
| intent | string(500) | ✓ | 工作意图 |
| inputs | object | ✓ | 输入定义 |
| constraints | object | ✓ | 约束条件 |
| acceptance | object | ✓ | 验收标准 |
| evidence | object | ✓ | 证据引用 |
| adopted_from | object | ✓ | 来源信息 |

### 3.2 Constraints 子字段

| 字段 | 类型 | 必填 | 默认值 |
|------|------|------|--------|
| timeout_seconds | integer(1-3600) | ✓ | - |
| max_retries | integer(0-10) | ✓ | - |
| fail_mode | enum | ✗ | CLOSED |
| blocking | boolean | ✗ | true |
| dependencies | array | ✗ | - |

### 3.3 EvidenceRef 子字段

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| ref_id | string | ✓ | 格式: EV-XXX |
| type | enum | ✓ | audit_pack/log/artifact/metric/screenshot/report/signature |
| path | string | ✓ | 路径或URI |
| hash.algorithm | enum | ✗ | SHA-256/SHA-512/MD5 |
| hash.value | string | ✗ | 哈希值 |

---

## 4. l4_endpoints.yaml 端点清单

### 4.1 链路 A: POST /cognition/generate

**请求**: Cognition10dRequest
**响应**: Cognition10dResponse
**错误码**:
- 400: 参数无效
- 401: 未认证
- 500: 服务器错误

### 4.2 链路 B: POST /work/adopt

**请求**:
```json
{
  "reason_card_id": "RC-XXX",
  "requester_id": "user-xxx",
  "context": { ... },
  "options": { ... }
}
```

**响应**:
```json
{
  "work_item_id": "WI-XXXXXXXX",
  "status": "ADOPTED",
  "adopted_from": { ... },
  "evidence_refs": [ ... ],
  "created_at": "2026-02-19T12:00:00Z"
}
```

**错误码**:
- 400: 无效请求
- 409: 已存在
- 422: 无法派生字段

### 4.3 链路 C: POST /work/execute

**请求**:
```json
{
  "work_item_id": "WI-XXXXXXXX",
  "permit_token": "xxx",
  "execution_context": {
    "repo_url": "...",
    "commit_sha": "...",
    "run_id": "...",
    "requested_action": "release"
  }
}
```

**响应**:
```json
{
  "ok": true,
  "data": { ... },
  "gate_decision": "ALLOW",
  "release_allowed": true,
  "evidence_ref": "EV-XXX",
  "run_id": "RUN-XXX"
}
```

---

## 5. 统一错误信封标准

### 5.1 失败响应格式

```json
{
  "ok": false,
  "error_code": "E001|E002|E003|E004|E005|E006|E007",
  "blocked_by": "PERMIT_REQUIRED|PERMIT_INVALID|PERMIT_EXPIRED|PERMIT_SCOPE_MISMATCH|PERMIT_SUBJECT_MISMATCH|PERMIT_REVOKED",
  "message": "Human readable error message",
  "evidence_ref": "EV-XXX",
  "run_id": "RUN-XXX"
}
```

### 5.2 成功响应格式

```json
{
  "ok": true,
  "data": { ... },
  "gate_decision": "ALLOW|BLOCK",
  "release_allowed": true|false,
  "evidence_ref": "EV-XXX",
  "run_id": "RUN-XXX"
}
```

### 5.3 错误码映射

| 错误码 | blocked_by | 含义 | 前端显示 |
|--------|------------|------|----------|
| E001 | PERMIT_REQUIRED | 无permit | no permit 阻断条 |
| E002 | PERMIT_INVALID | 格式无效 | 格式错误阻断条 |
| E003 | PERMIT_INVALID | 签名无效 | signature invalid 阻断条 |
| E004 | PERMIT_EXPIRED | 已过期 | 过期阻断条 |
| E005 | PERMIT_SCOPE_MISMATCH | 作用域不匹配 | scope阻断条 |
| E006 | PERMIT_SUBJECT_MISMATCH | 主体不匹配 | subject阻断条 |
| E007 | PERMIT_REVOKED | 已撤销 | 撤销阻断条 |

---

## 6. 前端映射要求

### 6.1 E001 映射
```typescript
if (response.error_code === 'E001') {
  // 显示 no permit 阻断条
  // 禁用 Execute 按钮
}
```

### 6.2 E003 映射
```typescript
if (response.error_code === 'E003') {
  // 显示 signature invalid 阻断条
  // 禁用 Execute 按钮
}
```

---

## 7. 版本与哈希

```yaml
contract_versions:
  10d_schema:
    path: src/contracts/cognition/10d_schema.json
    version: v1.0
    hash: TBD_SHA256

  work_item_schema:
    path: src/contracts/governance/work_item_schema.json
    version: v1.0
    hash: TBD_SHA256

  l4_endpoints:
    path: src/contracts/api/l4_endpoints.yaml
    version: v1.0
    hash: TBD_SHA256
```

---

## 8. 冻结签核

```yaml
freeze_signoff:
  version: "v1.0"
  frozen_at: "2026-02-19T20:00:00Z"
  signer: "Kior-B"
  status: "FROZEN"
  note: "契约冻结，后续变更需创建v2版本"
```

---

*文档生成时间: 2026-02-19T20:00:00Z*
*签核人: Kior-B*
