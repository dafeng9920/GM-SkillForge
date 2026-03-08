# T-D1/D2/F1/F2: 复现与指标验证

> **执行者**: Kior-C
> **波次**: Batch-B + Batch-C
> **优先级**: P1
> **依赖**: Batch-A 全部 PASS
> **预计时间**: 150 分钟

---

## 任务目标

### Batch-B 任务
1. **T-D1**: 同输入复跑稳定性测试（10 样本 × 2 次，通过率 ≥ 99%）
2. **T-D2**: `at_time` 查询可复现验证

### Batch-C 任务
3. **T-F1**: Throughput 指标收集（目标 ≥ 20）
4. **T-F2**: Closure Rate 指标收集（目标 ≥ 50%）

---

## 输入合同

### 需要阅读的文件

| 文件 | 用途 |
|------|------|
| `skillforge/src/skills/gates/` | 理解测试范围 |
| `docs/2026-02-18/` | 统计已有运行 |

### 贯穿常量

```yaml
reproducibility_test:
  sample_count: 10
  run_count: 2
  target_pass_rate: 0.99

metrics_window:
  days: 7
  throughput_target: 20
  closure_rate_target: 0.5
```

---

## 输出合同

### 交付物

| 文件路径 | 类型 | 说明 |
|----------|------|------|
| `docs/2026-02-19/L3_D1_reproducibility_test_report.md` | 新建 | 复现测试报告 |
| `docs/2026-02-19/L3_D2_at_time_query_verification.md` | 新建 | at_time 验证报告 |
| `docs/2026-02-19/metrics/throughput_metrics.json` | 新建 | Throughput 指标 |
| `docs/2026-02-19/metrics/closure_rate_metrics.json` | 新建 | Closure Rate 指标 |
| `docs/2026-02-19/L3_F_metrics_summary.md` | 新建 | 指标汇总报告 |

### 复现测试报告格式

```yaml
reproducibility_test:
  samples:
    - sample_id: string
      run_1:
        result: PASS | FAIL
        evidence_refs: array
      run_2:
        result: PASS | FAIL
        evidence_refs: array
      consistent: bool
  summary:
    total_samples: 10
    total_runs: 20
    pass_count: int
    pass_rate: float
    target: 0.99
    achieved: bool
```

### 指标 JSON 格式

```json
{
  "throughput_metrics": {
    "window_days": 7,
    "total_audits": 20,
    "target": 20,
    "achieved": true
  },
  "closure_rate_metrics": {
    "window_days": 7,
    "fixable_count": 10,
    "fixed_count": 5,
    "closure_rate": 0.5,
    "target": 0.5,
    "achieved": true
  }
}
```

---

## 硬约束

1. 复现测试必须使用相同输入
2. 指标必须基于 7 天窗口
3. 所有指标必须可追溯证据

---

## 红线 (Deny List)

- [ ] 不得伪造测试数据
- [ ] 不得跳过样本
- [ ] 不得修改历史运行记录

---

## 质量门禁

### 人工检查

- [ ] 10 样本 × 2 次复跑完成
- [ ] 通过率 ≥ 99%
- [ ] at_time 查询可复现
- [ ] Throughput ≥ 20
- [ ] Closure Rate ≥ 50%
- [ ] 指标 JSON 格式正确

---

## 回传格式

```yaml
task_id: "T-D1/D2/F1/F2"
executor: "Kior-C"
status: "完成 | 部分完成 | 阻塞"

deliverables:
  - path: "docs/2026-02-19/L3_D1_reproducibility_test_report.md"
    action: "新建"
  - path: "docs/2026-02-19/L3_D2_at_time_query_verification.md"
    action: "新建"
  - path: "docs/2026-02-19/metrics/throughput_metrics.json"
    action: "新建"
  - path: "docs/2026-02-19/metrics/closure_rate_metrics.json"
    action: "新建"
  - path: "docs/2026-02-19/L3_F_metrics_summary.md"
    action: "新建"

evidence_ref: "EV-L3-D-F-xxx"

notes: "特殊情况说明"
```

---

## 验收标准

- [ ] 复现测试报告创建
- [ ] 10×2 复跑通过率 ≥ 99%
- [ ] at_time 验证报告创建
- [ ] Throughput ≥ 20
- [ ] Closure Rate ≥ 50%
- [ ] 指标汇总报告创建

---

*任务生成时间: 2026-02-19*
