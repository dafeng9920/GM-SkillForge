# T-G1/G2/G3: 运行演练归档

> **执行者**: vs--cc1 (Antigravity-3)
> **波次**: Batch-C
> **优先级**: P2
> **依赖**: Batch-B 全部 PASS
> **预计时间**: 30 分钟

---

## 任务目标

归档 3 项演练报告：
1. Canary 发布演练 (T-G1)
2. Rollback 演练 (T-G2)
3. Batch 2目标演练 (T-G3)

---

## 输入合同

### 需要阅读的文件

| 文件 | 用途 |
|------|------|
| `docs/2026-02-18/canary_release_execution_report_v1.md` | 源报告 |
| `docs/2026-02-18/canary_rollback_drill_report_v1.md` | 源报告 |
| `docs/2026-02-18/batch_release_2targets_execution_report_v1.md` | 源报告 |

### 贯穿常量

```yaml
source_date: "2026-02-18"
target_date: "2026-02-19"
```

---

## 输出合同

### 交付物

| 文件路径 | 类型 | 说明 |
|----------|------|------|
| `docs/2026-02-19/L3_G1_canary_drill_archive.md` | 新建 | Canary 归档 |
| `docs/2026-02-19/L3_G2_rollback_drill_archive.md` | 新建 | Rollback 归档 |
| `docs/2026-02-19/L3_G3_batch_2targets_archive.md` | 新建 | Batch 归档 |

### 归档报告格式

```yaml
archive_structure:
  - source_ref: string      # 原报告路径
  - drill_type: string      # canary | rollback | batch
  - execution_date: string  # 执行日期
  - result: PASS | FAIL
  - key_metrics:
      - name: string
        value: any
  - evidence_refs: array
  - conclusion: string
```

---

## 硬约束

1. 必须引用原报告
2. 必须提取关键指标

---

## 红线 (Deny List)

- [ ] 不得修改原报告
- [ ] 不得遗漏关键指标

---

## 质量门禁

### 人工检查

- [ ] 3 份归档报告创建
- [ ] 原报告引用正确
- [ ] 关键指标提取完整
- [ ] 结论清晰

---

## 回传格式

```yaml
task_id: "T-G1/G2/G3"
executor: "vs--cc1"
status: "完成 | 部分完成 | 阻塞"

deliverables:
  - path: "docs/2026-02-19/L3_G1_canary_drill_archive.md"
    action: "新建"
  - path: "docs/2026-02-19/L3_G2_rollback_drill_archive.md"
    action: "新建"
  - path: "docs/2026-02-19/L3_G3_batch_2targets_archive.md"
    action: "新建"

evidence_ref: "EV-L3-G1-G2-G3-xxx"

notes: "特殊情况说明"
```

---

## 验收标准

- [ ] 3 份归档报告创建
- [ ] 原报告引用正确
- [ ] 关键指标完整

---

*任务生成时间: 2026-02-19*
