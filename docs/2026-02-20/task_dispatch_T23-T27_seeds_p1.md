# L4.5 SEEDS v0（P1）任务分派总表

> 任务编号: `L45-D5-SEEDS-P1-20260220-005`  
> 主控模式: Task Skill Spec（并行执行）  
> 唯一合并权: `vs--cc3`

---

## 1. 波次看板

| 波次 | 任务 | 执行者 | 依赖 | 预计时长 | 状态 | Gate Decision |
|------|------|--------|------|----------|------|---------------|
| Wave 1 | T23 | vs--cc3 | - | 75min | ⏳ 待启动 | - |
| Wave 1 | T24 | vs--cc1 | - | 70min | ⏳ 待启动 | - |
| Wave 1 | T25 | vs--cc2 | - | 70min | ⏳ 待启动 | - |
| Wave 1 | T26 | Kior-B | - | 80min | ⏳ 待启动 | - |
| Wave 2 | T27 | Kior-C | T23,T24,T25,T26 | 90min | ⏳ 待启动 | - |

状态标记: `⏳ 待启动 | 🔄 执行中 | 📤 已提交 | ✅ ALLOW | ⚠️ REQUIRES_CHANGES | ❌ DENY`

---

## 2. 并行规则

1. `T23-T26` 并行执行。
2. 任一并行任务未提交，不得启动 `T27`。
3. 任一 P1 种子未满足 `落盘格式 + 1写入点 + 1读取点`，`T27` 不得 `ALLOW`。

---

## 3. 全局常量（所有任务共用）

```yaml
job_id: "L45-D5-SEEDS-P1-20260220-005"
skill_id: "l45_seeds_p1_guardrails"
seed_doc: "docs/SEEDS_v0.md"
```

---

## 4. 收口清单（T27）

1. `docs/2026-02-20/L45_SEEDS_P1_INTEGRATION_REPORT_v1.md`
2. `docs/2026-02-20/verification/T27_gate_decision.json`
3. `docs/2026-02-20/verification/T27_execution_report.yaml`
4. `docs/2026-02-20/tasks/各小队任务完成汇总_T23-T27.md`

