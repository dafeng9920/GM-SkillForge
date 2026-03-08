# L3 G1: Canary 发布演练归档

> **归档日期**: 2026-02-19
> **源报告日期**: 2026-02-18
> **归档者**: vs--cc1
> **阶段**: L3

---

## 1. 归档信息

```yaml
archive_info:
  source_ref: "docs/2026-02-18/canary_release_execution_report_v1.md"
  drill_type: "canary"
  execution_date: "2026-02-18"
  archive_date: "2026-02-19"
  result: "PASS"
```

---

## 2. 演练摘要

| 检查项 | 结果 |
|--------|------|
| Permit 签发 | PASS |
| Permit 校验 | VALID |
| Canary 发布 | PASS |
| 观察窗口 | CONTINUE |
| 回滚演练 | PASS |
| Fail-Closed | PASS |
| **最终判定** | **PASSED** |

---

## 3. 关键指标

### 3.1 发布参数

| 指标 | 值 |
|------|-----|
| canary_scope | single repo |
| target | NEW-GM/staging |
| rollout_ratio | 100% (staging) |
| release_window | 2026-02-18T11:58:53Z - 2026-02-18T12:03:53Z |

### 3.2 Permit 证据

| 指标 | 值 |
|------|-----|
| permit_id | PERMIT-20260218-6C57D43A |
| issued_at | 2026-02-18T11:58:53Z |
| expires_at | 2026-02-18T12:58:53Z |
| signature_algo | HS256 |

### 3.3 观察窗口指标

| 指标 | 值 | 阈值 | 状态 |
|------|-----|------|------|
| error_rate | 0.1% | < 1% | PASS |
| latency_p95 | 150ms | < 500ms | PASS |
| success_rate | 99.9% | > 99% | PASS |

### 3.4 Fail-Closed 验证

| 场景 | 预期 | 实际 | 结果 |
|------|------|------|------|
| E001 无 permit | 阻断 | 阻断 | PASS |
| E003 签名篡改 | 阻断 | 阻断 | PASS |

---

## 4. 证据引用

```yaml
evidence_refs:
  - permit_id: PERMIT-20260218-6C57D43A
  - release_id: RELEASE-RUN-20260218-CANARY-001
  - replay_pointer: replay://RUN-20260218-CANARY-001@2026-02-18T11:58:53Z
  - source_report: docs/2026-02-18/canary_release_execution_report_v1.md
```

---

## 5. 结论

**PROMOTE** — Canary 发布成功，观察窗口指标正常，可提升至更大范围。

---

## 6. 后续行动

1. 扩大发布范围至 production-canary
2. 接入真实监控告警系统
3. 验证 tombstone 机制

---

*归档时间: 2026-02-19 | 归档者: vs--cc1*
