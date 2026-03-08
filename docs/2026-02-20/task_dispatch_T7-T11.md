# L4.5 Day-2 任务分派总表（T7-T11）

> 任务编号: L45-D2-ORCH-MINCAP  
> 主控模式: Skill 化 Task Skill Spec  
> 目标: 打通并生产化 3 个最小编排能力（`run_intent` / `fetch_pack` / `query_rag`）

---

## 1. 波次看板

| 波次 | 任务 | 执行者 | 依赖 | 预计时长 | 状态 | Gate Decision |
|------|------|--------|------|----------|------|---------------|
| Wave 1 | T7 | vs--cc3 | - | 90min | ✅ ALLOW | ALLOW |
| Wave 1 | T8 | vs--cc1 | - | 90min | ✅ ALLOW | ALLOW |
| Wave 1 | T9 | vs--cc2 | - | 90min | ✅ ALLOW | ALLOW |
| Wave 2 | T10 | Kior-B | T7,T8,T9 | 80min | ✅ ALLOW | ALLOW |
| Wave 3 | T11 | Kior-C | T10 | 90min | ✅ ALLOW | ALLOW |

状态标记: `⏳ 待启动 | 🔄 执行中 | 📤 已提交 | ✅ ALLOW | ⚠️ REQUIRES_CHANGES | ❌ DENY`

---

## 2. 执行顺序规则

1. Wave 1 并行完成后，才能启动 T10。
2. T10 通过后，才能启动 T11。
3. 任一任务 Gate Decision 非 `ALLOW`，下游不得启动。
4. 所有任务必须提交 Execution Report。

---

## 3. 全局常量（所有任务共用）

```yaml
job_id: "L45-D2-ORCH-MINCAP-20260220-002"
skill_id: "l45_orchestration_min_capabilities"
fixed_inputs:
  - repo_url
  - commit_sha
  - at_time
required_outputs:
  - run_id
  - gate_decision
  - evidence_ref
```

---

## 4. 收口清单（T11 最终检查）

1. `docs/2026-02-20/L45_RUN_INTENT_PRODUCTION_REPORT_v1.md`
2. `docs/2026-02-20/L45_FETCH_PACK_PRODUCTION_REPORT_v1.md`
3. `docs/2026-02-20/L45_QUERY_RAG_PRODUCTION_REPORT_v1.md`
4. `docs/2026-02-20/L45_N8N_MINCAP_E2E_REPORT_v1.md`
5. `docs/2026-02-20/verification/T11_gate_decision.json`

---

## 5. 最终判定

```yaml
job_id: "L45-D2-ORCH-MINCAP-20260220-002"
all_tasks_completed: true
all_gate_decisions: "ALLOW"
l45_day2_ready: "YES"
ready_for_merge: true
verified_by_codex:
  command: "python -m pytest -q tests/gates/test_intake_scan.py tests/gates/test_logic.py tests/gates/test_experience_capture.py tests/gates/test_experience_template_reader_integration.py skillforge/tests/test_gate_permit.py skillforge/tests/test_l4_api_smoke.py skillforge/tests/test_membership_regression.py skillforge/tests/test_n8n_orchestration.py"
  result: "91 passed in 0.26s"
```
