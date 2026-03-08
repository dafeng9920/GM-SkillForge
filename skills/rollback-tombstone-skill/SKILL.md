# rollback-tombstone-skill

> 版本: v1.0.0
> 冻结时间: 2026-02-18
> 继承自: Phase-1 回滚演练

---

## 触发条件

- 发布后需要回滚
- 失败注入触发回滚
- 演练模式强制回滚

---

## 输入契约

```yaml
input:
  run_id: string           # 运行ID（必填）
  permit_id: string        # Permit ID（必填）
  release_id: string       # 发布ID（必填）
  rollback_reason: string  # 回滚原因
  rollback_strategy: string  # immediate / graceful
  target_revision: string  # 目标版本（PREVIOUS / 指定版本）
```

---

## 输出契约

```yaml
output:
  rollback_status: string     # PASSED / FAILED
  rollback_duration_ms: int   # 回滚耗时
  tombstone_id: string        # Tombstone ID
  tombstone_status: string    # RELEASED / ROLLED_BACK
  replay_pointer: string      # 回放指针
  replay_consistency: bool    # 回放一致性
  post_rollback_metrics_ok: bool  # 回滚后指标正常
```

---

## Fail-Closed 条件

| 条件 | 行为 |
|------|------|
| 无 permit 回滚 | 阻断（E001） |
| 签名异常回滚 | 阻断（E003） |
| 回滚失败 | Tombstone 记录失败状态 |
| 回放不一致 | replay_consistency = false |

---

## Evidence 字段要求

```yaml
evidence:
  run_id: string          # 必须贯穿全链路
  permit_id: string       # 关联 Permit
  replay_pointer: string  # 回放指针
  tombstone_ref: string   # Tombstone 引用
  rollback_log_ref: string  # 回滚日志
```

---

## Tombstone 记录结构

```yaml
tombstone:
  tombstone_id: string
  run_id: string
  permit_id: string
  release_id: string
  status: RELEASED | ROLLED_BACK
  created_at: string
  prev_hash: string      # 前序哈希
  signature: string      # 签名
  immutable: true        # 不可篡改
  metadata:
    rollback_reason: string
    rollback_duration_ms: int
    original_version: string
    rollback_version: string
```

---

## 回放一致性校验

| 检查项 | 预期 |
|--------|------|
| original_permit_verifiable | true |
| original_evidence_traceable | true |
| timestamp_consistency | CONSISTENT |
| run_id_match | true |
| permit_id_match | true |

---

## 验证步骤

1. **前提检查**: permit 校验通过
2. **回滚触发**: 记录触发原因
3. **回滚执行**: 按策略执行回滚
4. **Tombstone 写入**: 记录回滚状态
5. **回放验证**: 验证 replay_consistency
6. **指标检查**: post_rollback_metrics_ok
7. **证据生成**: 生成 EvidenceRef

---

## 指标要求

| 指标 | Baseline | Target |
|------|----------|--------|
| 回滚时间 | 5 min | < 2 min |
| Tombstone 写入 | 100ms | < 50ms |
| 回放时间 | 120s | < 60s |

---

## 实现引用

- **演练报告**: `docs/2026-02-18/business_phase1_rollback_drill_report_v1.md`
- **回滚运行单**: `docs/2026-02-18/canary_rollback_drill_run_sheet_v1.md`

---

## 验收标准

- [ ] 回滚演练 PASSED
- [ ] rollback_status = PASSED
- [ ] Tombstone 写入成功
- [ ] replay_consistency = true
- [ ] 回滚时间 < 2 min
- [ ] E001/E003 阻断验证通过
