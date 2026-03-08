# L4.5 SEEDS v0（P0）任务分派总表

> 任务编号: `L45-D4-SEEDS-P0-20260220-004`  
> 主控模式: Task Skill Spec（并行执行）  
> 唯一合并权: `vs--cc3`

---

## 1. 波次看板

| 波次 | 任务 | 执行者 | 依赖 | 预计时长 | 状态 | Gate Decision |
|------|------|--------|------|----------|------|---------------|
| Wave 1 | T17 | vs--cc3 | - | 90min | ⏳ 待启动 | - |
| Wave 1 | T18 | vs--cc1 | - | 80min | ⏳ 待启动 | - |
| Wave 1 | T19 | vs--cc2 | - | 80min | ⏳ 待启动 | - |
| Wave 1 | T20 | Kior-B | - | 80min | ⏳ 待启动 | - |
| Wave 1 | T21 | Kior-A | - | 85min | ⏳ 待启动 | - |
| Wave 2 | T22 | Kior-C | T17,T18,T19,T20,T21 | 90min | ⏳ 待启动 | - |

状态标记: `⏳ 待启动 | 🔄 执行中 | 📤 已提交 | ✅ ALLOW | ⚠️ REQUIRES_CHANGES | ❌ DENY`

---

## 2. 并行规则

1. `T17-T21` 并行执行。
2. 任一任务未提交，不得启动 `T22`。
3. 任一 P0 种子未满足 `落盘格式 + 1写入点 + 1读取点`，`T22` 不得 `ALLOW`。

---

## 3. 全局常量（所有任务共用）

```yaml
job_id: "L45-D4-SEEDS-P0-20260220-004"
skill_id: "l45_seeds_p0_foundation"
seed_doc: "docs/SEEDS_v0.md"
```

---

## 4. 收口清单（T22）

1. `docs/2026-02-20/L45_SEEDS_P0_INTEGRATION_REPORT_v1.md`
2. `docs/2026-02-20/verification/T22_gate_decision.json`
3. `docs/2026-02-20/verification/T22_execution_report.yaml`
4. `docs/2026-02-20/tasks/各小队任务完成汇总_T17-T22.md`

