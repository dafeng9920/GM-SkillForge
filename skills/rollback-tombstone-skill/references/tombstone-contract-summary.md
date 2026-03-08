# Tombstone Contract Summary

> Version: v1.0.0
> Frozen: 2026-02-18
> Full Contract: docs/2026-02-18/tombstone_persistence_contract_v1.md

---

## 1. Tombstone 必填字段

### 1.1 核心字段（必须存在）

| 字段 | 类型 | 说明 | 必填 |
|------|------|------|------|
| tombstone_id | string | 唯一标识符 | ✅ |
| run_id | string | 关联的运行ID | ✅ |
| permit_id | string | 关联的 Permit ID | ✅ |
| release_id | string | 关联的发布ID | ✅ |
| status | enum | RELEASED / ROLLED_BACK | ✅ |
| created_at | timestamp | ISO8601 UTC | ✅ |
| prev_hash | string | 前序记录哈希 | ✅ |
| signature | string | 链式签名 | ✅ |

### 1.2 目标字段

| 字段 | 类型 | 说明 | 必填 |
|------|------|------|------|
| target.repo_url | string | 目标仓库URL | ✅ |
| target.commit_sha | string | 目标提交SHA | ✅ |

### 1.3 元数据字段（可选但建议）

| 字段 | 类型 | 说明 |
|------|------|------|
| metadata.rollback_reason | string | 回滚原因 |
| metadata.rollback_duration_ms | int | 回滚耗时 |
| metadata.original_version | string | 原始版本 |
| metadata.rollback_version | string | 回滚目标版本 |

---

## 2. 可重试/不可重试规则

### 2.1 可重试场景

| 场景 | 错误码 | 重试次数 | 重试间隔 |
|------|--------|----------|----------|
| 网络超时 | R002 | 3 | 1s |
| 存储暂时不可用 | R002 | 3 | 2s |
| 签名服务暂时不可用 | R002 | 3 | 1s |
| 并发写入冲突 | R002 | 5 | 500ms |

### 2.2 不可重试场景（立即阻断）

| 场景 | 错误码 | 行为 |
|------|--------|------|
| 无 Permit | E001 | 立即阻断，不重试 |
| 签名验证失败 | E003 | 立即阻断，不重试 |
| Permit 过期 | E004 | 立即阻断，不重试 |
| Permit 已撤销 | E007 | 立即阻断，不重试 |
| 数据格式无效 | E002 | 立即阻断，不重试 |
| 权限不足 | A001 | 立即阻断，不重试 |

### 2.3 重试策略

```
重试策略: Exponential Backoff
初始间隔: 100ms
最大间隔: 5s
最大重试次数: 3 (可重试场景) / 0 (不可重试场景)
重试条件: 仅 R002 类错误码可重试
```

**重试流程**:
1. 首次失败 → 等待 100ms → 重试
2. 二次失败 → 等待 500ms → 重试
3. 三次失败 → 等待 1s → 重试
4. 最终失败 → 记录错误日志 + 返回失败状态

---

## 3. 状态转换

### 3.1 有效状态

```
                    ┌──────────────┐
                    │   RELEASED   │ ← 发布成功
                    └──────┬───────┘
                           │ 回滚触发
                           ▼
                    ┌──────────────┐
                    │  ROLLED_BACK │ ← 回滚完成
                    └──────┬───────┘
                           │ 超过 7 年
                           ▼
                    ┌──────────────┐
                    │   EXPIRED    │ ← 保留期结束
                    └──────────────┘
```

**状态转换规则**:
| 当前状态 | 可转换到 | 触发条件 | 可逆性 |
|----------|----------|----------|--------|
| RELEASED | ROLLED_BACK | 回滚操作 | ❌ 不可逆 |
| RELEASED | EXPIRED | 7 年后自动 | ❌ 不可逆 |
| ROLLED_BACK | EXPIRED | 7 年后自动 | ❌ 不可逆 |
| EXPIRED | - | 终态 | ❌ 不可逆 |

### 3.2 状态说明

| 状态 | 说明 |
|------|------|
| RELEASED | 发布成功 |
| ROLLED_BACK | 已回滚 |
| EXPIRED | 超过保留期 |

---

## 4. 链式结构

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Record N   │───>│  Record N+1 │───>│  Record N+2 │
├─────────────┤    ├─────────────┤    ├─────────────┤
│ prev_hash   │    │ prev_hash   │    │ prev_hash   │
│ data        │    │ data        │    │ data        │
│ signature   │    │ signature   │    │ signature   │
│ timestamp   │    │ timestamp   │    │ timestamp   │
└─────────────┘    └─────────────┘    └─────────────┘
```

### 4.1 Hash 计算

```
hash_input = SHA256(
  prev_hash +
  tombstone_id +
  run_id +
  permit_id +
  release_id +
  status +
  created_at +
  JSON.stringify(target) +
  JSON.stringify(metadata)
)

prev_hash 初始值: SHA256("GENESIS")
```

**Hash 校验规则**:
- 每条记录必须包含 `prev_hash` 字段
- `prev_hash` 必须等于上一条记录的 Hash
- 链首记录 `prev_hash` = GENESIS_HASH
- Hash 不匹配 → 检测到篡改 → 告警

### 4.2 签名验证

```
signature_input = SHA256(
  hash_input + private_key_timestamp
)

signature = RS256_SIGN(hash_input, private_key)

验证: RS256_VERIFY(hash_input, signature, public_key)
```

**签名规则**:
- 使用 RS256 (RSA + SHA256) 算法
- 私钥由签名服务持有
- 公钥公开，用于验证
- 签名不匹配 → 拒绝写入/读取



---

## 5. SLA 要求

| 指标 | 目标 | 测量周期 |
|------|------|----------|
| 写入延迟 P99 | < 100ms | 实时 |
| 读取延迟 P99 | < 50ms | 实时 |
| 写入可用性 | 99.99% | 月度 |
| 读取可用性 | 99.9% | 月度 |
| 数据持久性 | 11个9 | 年度 |

---

## 6. 保留期

| 数据类型 | 保留期 | 压缩策略 |
|----------|--------|----------|
| Tombstone 记录 | 7年 | 不压缩 |
| Tombstone 索引 | 7年 | 可压缩 |
| Tombstone 元数据 | 7年 | 可压缩 |

---

## 7. 引用

- 完整契约: docs/2026-02-18/tombstone_persistence_contract_v1.md
- 回滚演练: docs/2026-02-18/canary_rollback_drill_report_v1.md
