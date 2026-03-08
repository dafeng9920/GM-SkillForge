# Permit 签发链路集成规范 v1

> **文档类型**: 最小集成规范
> **目标系统**: IAM/OPA（或等同签发系统）
> **版本**: v1
> **日期**: 2026-02-18

---

## 1. 概述

### 1.1 目标

将本地 `PERMIT-*` 流程切换到 IAM/OPA 真实签发链路，实现：
- 签发：通过 IAM/OPA 颁发发布许可证
- 验签：在发布前验证 permit 有效性
- 撤销：支持紧急撤销已签发 permit

### 1.2 范围

| 项 | 范围内 | 范围外 |
|----|--------|--------|
| Permit 签发 | ✅ | - |
| Permit 验签 | ✅ | - |
| Permit 撤销 | ✅ | - |
| Key 轮换 | - | 后续版本 |
| 多租户隔离 | - | 后续版本 |

---

## 2. 签发流程

### 2.1 签发条件（Issuance Conditions）

| 条件 ID | 条件名 | 类型 | 必须满足 |
|---------|--------|------|----------|
| C001 | `intent_verified` | boolean | ✅ |
| C002 | `gate_passed` | boolean | ✅ |
| C003 | `operator_authorized` | boolean | ✅ |
| C004 | `risk_level_acceptable` | boolean | ✅ |
| C005 | `time_window_valid` | boolean | ✅ |
| C006 | `no_active_blocklist` | boolean | ✅ |

### 2.2 签发请求格式

```json
{
  "request_id": "REQ-20260218-001",
  "intent_id": "INTENT-20260218-CANARY-001",
  "operator": "user@example.com",
  "target": {
    "repo_url": "github.com/example/repo",
    "commit_sha": "a1b2c3d4..."
  },
  "metadata": {
    "gate_decision": "PASSED",
    "risk_level": "L2",
    "requested_at": "2026-02-18T10:00:00Z"
  }
}
```

### 2.3 签发响应格式

```json
{
  "permit_id": "PERMIT-20260218-001",
  "permit_token": "eyJhbGciOiJSUzI1NiIs...",
  "key_id": "KEY-2026-PRIMARY",
  "issued_at": "2026-02-18T10:00:05Z",
  "expires_at": "2026-02-18T22:00:05Z",
  "ttl_seconds": 43200,
  "signature": "SHA256:abc123...",
  "conditions": ["C001", "C002", "C003", "C004", "C005", "C006"]
}
```

---

## 3. Key 管理

### 3.1 Key 标识

| 字段 | 描述 | 示例 |
|------|------|------|
| key_id | 密钥唯一标识 | `KEY-2026-PRIMARY` |
| key_type | 密钥类型 | `RSA-2048` / `ECDSA-P256` |
| key_status | 密钥状态 | `ACTIVE` / `ROTATING` / `DEPRECATED` |
| key_created_at | 创建时间 | `2026-01-01T00:00:00Z` |
| key_expires_at | 过期时间 | `2027-01-01T00:00:00Z` |

### 3.2 Key 状态机

```
┌─────────┐    轮换开始    ┌──────────┐    轮换完成    ┌────────────┐
│  ACTIVE │ ────────────> │ ROTATING │ ────────────> │ DEPRECATED │
└─────────┘               └──────────┘               └────────────┘
     │                         │
     │                         │ 签发新 key
     │                         ▼
     └────────────────────> ┌─────────┐
                             │  ACTIVE │ (新 key)
                             └─────────┘
```

### 3.3 Key 轮换策略

| 策略 | 值 |
|------|-----|
| 轮换周期 | 90 天 |
| 重叠期 | 7 天（新旧 key 均可验签） |
| 通知期 | 轮换前 14 天 |

---

## 4. TTL（Time To Live）

### 4.1 TTL 配置

| 场景 | TTL | 说明 |
|------|-----|------|
| Canary Release | 12 小时 | 单目标小流量 |
| Batch Release | 24 小时 | 多目标批量 |
| Emergency Release | 4 小时 | 紧急发布 |
| Dry Run | 1 小时 | 测试流程 |

### 4.2 TTL 计算规则

```
expires_at = issued_at + TTL
```

- `issued_at`: 签发时间（UTC）
- `TTL`: 按场景配置
- `expires_at`: 过期时间（UTC）

---

## 5. 撤销机制

### 5.1 撤销触发条件

| 条件 ID | 触发条件 | 自动/手动 |
|---------|----------|-----------|
| R001 | 安全事件 | 自动 |
| R002 | 操作员主动撤销 | 手动 |
| R003 | 发布失败 | 自动 |
| R004 | Key 泄露 | 自动 |
| R005 | 合规要求 | 手动 |

### 5.2 撤销请求格式

```json
{
  "revoke_request_id": "REVOKE-20260218-001",
  "permit_id": "PERMIT-20260218-001",
  "reason": "SECURITY_INCIDENT",
  "revoked_by": "security@example.com",
  "revoked_at": "2026-02-18T11:00:00Z"
}
```

### 5.3 撤销响应格式

```json
{
  "revoke_status": "REVOKED",
  "permit_id": "PERMIT-20260218-001",
  "revoked_at": "2026-02-18T11:00:01Z",
  "propagation_delay_ms": 100
}

### 5.4 撤销传播

- **传播延迟**: < 100ms（P99）
- **传播机制**: 推送到所有验签节点
- **回退策略**: 本地缓存 + 定期轮询（1 分钟）

---

## 6. 失败码映射

### 6.1 签发失败码

| 错误码 | 描述 | 用户提示 | 重试 |
|--------|------|----------|------|
| E-IAM-001 | 签发服务不可用 | 服务暂时不可用，请稍后重试 | ✅ |
| E-IAM-002 | 操作员未授权 | 您没有发布权限 | ❌ |
| E-IAM-003 | Gate 未通过 | 发布前检查未通过 | ❌ |
| E-IAM-004 | 风险等级过高 | 风险等级不满足发布条件 | ❌ |
| E-IAM-005 | 时间窗口无效 | 不在允许的发布时间窗口内 | ❌ |
| E-IAM-006 | 目标在黑名单 | 目标仓库已被禁止发布 | ❌ |
| E-IAM-007 | Key 轮换中 | 密钥正在轮换，请稍后重试 | ✅ |

### 6.2 验签失败码

| 错误码 | 描述 | 用户提示 | 行为 |
|--------|------|----------|------|
| E-VAL-001 | Permit 不存在 | 许可证不存在 | BLOCK |
| E-VAL-002 | Permit 已过期 | 许可证已过期 | BLOCK |
| E-VAL-003 | Permit 已撤销 | 许可证已被撤销 | BLOCK |
| E-VAL-004 | 签名无效 | 许可证签名验证失败 | BLOCK |
| E-VAL-005 | Key 已废弃 | 签名密钥已废弃 | BLOCK |
| E-VAL-006 | intent_id 不匹配 | 许可证与发布意图不匹配 | BLOCK |

### 6.3 失败码到 Fail-Closed 映射

| 内部错误码 | Fail-Closed 错误码 | release_allowed |
|------------|---------------------|-----------------|
| E-IAM-001 | E001 | `false` |
| E-IAM-002 | E001 | `false` |
| E-IAM-003 | E001 | `false` |
| E-VAL-001 | E001 | `false` |
| E-VAL-002 | E001 | `false` |
| E-VAL-003 | E001 | `false` |
| E-VAL-004 | E003 | `false` |
| E-VAL-005 | E003 | `false` |

---

## 7. API 规范

### 7.1 签发 API

```
POST /api/v1/permits/issue
Content-Type: application/json
Authorization: Bearer <operator_token>
```

### 7.2 验签 API

```
POST /api/v1/permits/validate
Content-Type: application/json
Authorization: Bearer <service_token>

Request:
{
  "permit_id": "PERMIT-20260218-001",
  "permit_token": "eyJhbGciOiJSUzI1NiIs...",
  "intent_id": "INTENT-20260218-CANARY-001"
}
```

### 7.3 撤销 API

```
POST /api/v1/permits/revoke
Content-Type: application/json
Authorization: Bearer <admin_token>
```

---

## 8. 集成检查清单

### 8.1 签发集成

- [ ] IAM/OPA 服务可达
- [ ] 签发请求格式正确
- [ ] 签发响应解析正确
- [ ] permit_token 存储安全
- [ ] TTL 配置已同步

### 8.2 验签集成

- [ ] 验签 API 可达
- [ ] permit_token 传递正确
- [ ] 错误码映射已配置
- [ ] Fail-Closed 开关开启
- [ ] 失败日志已记录

### 8.3 撤销集成

- [ ] 撤销 API 可达
- [ ] 撤销事件订阅已配置
- [ ] 本地缓存更新机制已验证

---

## 9. 监控与告警

### 9.1 关键指标

| 指标 | 阈值 | 告警级别 |
|------|------|----------|
| 签发成功率 | < 99% | P1 |
| 签发延迟 P99 | > 500ms | P2 |
| 验签成功率 | < 99.9% | P1 |
| 验签延迟 P99 | > 100ms | P2 |
| 撤销传播延迟 | > 100ms | P2 |

### 9.2 审计日志

所有签发、验签、撤销操作必须记录审计日志，包含：
- permit_id
- operator
- timestamp
- 操作类型
- 结果
- EvidenceRef

---

## 10. 决策记录

| 决策项 | 决策 | 理由 |
|--------|------|------|
| Key 类型 | RSA-2048 | 兼容性好，安全性足够 |
| TTL 默认值 | 12 小时 | 平衡安全与可用性 |
| 撤销传播延迟 | < 100ms | 满足紧急响应需求 |
| 失败码映射 | 统一到 E001/E003 | 简化 Fail-Closed 逻辑 |

---

*文档版本: v1 | 创建时间: 2026-02-18*
