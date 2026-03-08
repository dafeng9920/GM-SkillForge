# L4.5 Day-1 任务分派总表

> 任务编号: L45-D1-N8N-BOUNDARY  
> 主控模式: Skill 化 Task Skill Spec  
> 唯一合并权: `vs--cc3`

---

## 1. 波次看板

| 波次 | 任务 | 执行者 | 依赖 | 预计时长 | 状态 | Gate Decision |
|------|------|--------|------|----------|------|---------------|
| Wave 1 | T1 | vs--cc3 | - | 90min | ✅ ALLOW | ALLOW |
| Wave 1 | T2 | vs--cc2 | - | 70min | ✅ ALLOW | ALLOW |
| Wave 1 | T3 | Kior-B | T2 | 60min | ✅ ALLOW | ALLOW |
| Wave 1 | T4 | vs--cc1 | - | 60min | ✅ ALLOW | ALLOW |
| Wave 2 | T5 | Kior-A | T1,T3,T4 | 75min | ✅ ALLOW | ALLOW |
| Wave 3 | T6 | Kior-C | T5 | 90min | ✅ ALLOW | ALLOW |

状态标记: `⏳ 待启动 | 🔄 执行中 | 📤 已提交 | ✅ ALLOW | ⚠️ REQUIRES_CHANGES | ❌ DENY`

---

## 2. 执行顺序规则

1. 先并行执行 Wave 1，全部提交后再开 Wave 2。
2. Wave 2 通过后再开 Wave 3。
3. 任一任务 Gate Decision 非 `ALLOW`，下游不得启动。
4. 所有任务必须提交 Execution Report（遵循 `multi-ai-collaboration.md`）。

---

## 3. 全局常量（所有任务共用）

```yaml
job_id: "L45-D1-N8N-BOUNDARY-20260220-001"
skill_id: "l45_n8n_orchestration_boundary"
fixed_inputs:
  - repo_url
  - commit_sha
  - at_time
```

---

## 4. 收口清单（Wave 3 最终检查）

1. `docs/2026-02-20/L45_N8N_WORKFLOW_RUN_REPORT_v1.md`
2. `docs/2026-02-20/L45_FRONT_BACK_N8N_INTEGRATION_REPORT_v1.md`
3. `docs/2026-02-20/L45_DAY1_CLOSEOUT_v1.md`
4. `docs/2026-02-20/verification/T6_gate_decision.json`

---

## 5. 最终判定

```yaml
job_id: "L45-D1-N8N-BOUNDARY-20260220-001"
all_tasks_completed: true
all_gate_decisions: "ALLOW"
l45_day1_ready: "YES"
ready_for_merge: true
verified_by_codex:
  command: "python -m pytest -q skillforge/tests/test_gate_permit.py skillforge/tests/test_l4_api_smoke.py skillforge/tests/test_membership_regression.py skillforge/tests/test_n8n_orchestration.py"
  result: "45 passed in 0.08s"
```

---

## 6. 可调用 Skill 清单（统一调度入口）

本批次沿用统一清单：`docs/templates/dispatch_skill_catalog.md`  
该批次无额外特化映射。  
