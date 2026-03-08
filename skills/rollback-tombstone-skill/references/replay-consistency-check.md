# Replay Consistency Check

> Version: v1.0.0
> Frozen: 2026-02-18
> Related: docs/2026-02-18/tombstone_persistence_contract_v1.md

---

## 1. 回放一致性检查最小步骤

### Step 1: replay_pointer 有效性验证



### Step 2: Permit 可重新验证



### Step 3: Evidence 可追溯



### Step 4: 时间戳一致性



### Step 5: run_id/permit_id 匹配



### Step 6: 链式完整性



---

## 2. 回放一致性判定矩阵

| 检查项 | 通过条件 | 失败行为 |
|--------|----------|----------|
| replay_pointer_valid | format + exists | replay_consistency = false |
| permit_reverifiable | signature + not expired + not revoked | replay_consistency = false |
| evidence_traceable | all refs accessible | replay_consistency = false |
| timestamp_consistency | CONSISTENT | replay_consistency = false |
| id_match | all IDs match | replay_consistency = false |
| chain_integrity | chain unbroken | replay_consistency = false |

---

## 3. 回放时间要求

| 场景 | 时间要求 | 超时处理 |
|------|----------|----------|
| 单条记录回放 | < 10ms | 标记超时，重试 |
| 批量回放（1000条） | < 1s | 分批处理 |
| 全量回放 | < 10分钟 | 后台任务 |

---

## 4. 回放一致性保证

### 4.1 一致性保证级别

| 保证级别 | 描述 |
|----------|------|
| **写后读一致性** | 写入成功后立即可读 |
| **单调读** | 读取不会看到更旧的数据 |
| **因果一致性** | 相关操作按因果顺序可见 |

### 4.2 验证方法

| 验证项 | 要求 | 验证方法 |
|--------|------|----------|
| replay_pointer 有效性 | 100% | 签名校验 |
| 数据完整性 | 100% | Hash 校验 |
| 顺序正确性 | 100% | 序号校验 |
| 无数据丢失 | 100% | 完整性校验 |

---

## 5. 回放失败处理

### 5.1 失败场景

| 场景 | 错误码 | 处理 |
|------|--------|------|
| replay_pointer 格式无效 | RP001 | 返回格式错误 |
| permit 无法验证 | RP002 | 返回签名错误 |
| evidence 不可访问 | RP003 | 返回引用错误 |
| 时间戳不一致 | RP004 | 返回一致性错误 |
| ID 不匹配 | RP005 | 返回匹配错误 |
| 链式断裂 | RP006 | 返回完整性错误 |

### 5.2 失败恢复



---

## 6. 回放验证脚本示例



---

## 7. 最小回滚演练步骤

### 7.1 演练准备



### 7.2 演练执行



### 7.3 演练验证



---

## 8. 引用文档

- Tombstone 契约: docs/2026-02-18/tombstone_persistence_contract_v1.md
- 回滚演练报告: docs/2026-02-18/canary_rollback_drill_report_v1.md
- 治理链联调报告: docs/2026-02-18/business_phase1_governance_linkage_report_v1.md
